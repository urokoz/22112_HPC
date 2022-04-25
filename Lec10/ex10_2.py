#!/usr/bin/env python
import sys
import os
import time
import joblib as jl
import itertools
import numpy as np
import pickle

start_time = time.time()


def overrep_kmer(infile_name, global_dict_path, pos, k, job_nr):
    """ Count the occurences of each possible 5mer and count the occurences of
        each nucleotide in a sequence. Safely save the kmer dict to a file that
        is accessible to other jobs.

        Inputs:
        infile_name         File containing fasta sequence
        pos                 Vector containing the indexes of the sequence
        k                   Size of the kmer

        Outputs:
        nt_dict             Dictionary containing the occurences of nucleotides
    """
    print("# Working on {}".format(job_nr))

    # open file, extract sequence and remove newlines
    with open(infile_name, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(None, delete=b"\n")

    # add the occurences of the 4 nucleotides
    nt_dict = dict()
    for nt in b"atcg":
        nt_dict[nt] = seq.count(nt)

    # count the occurences of the possible kmers
    kmer_dict = dict()
    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]   #extract sequence

        # add kmer occurence to the kmer dict. Add an entry if the entry doesn't
        # already exist
        try:
            kmer_dict[kmer] += 1
        except:
            kmer_dict[kmer] = 1

    # semaphore-based memory efficient saving of kmer occurence to a file
    # accessible to other jobs. This prevents having to store a large dict for
    # each job by adding the kmer occurences for this job to a global dict.
    # creating and removing a directory is used as a semaphore to prevent errors
    # from two jobs adding to the dict at the same time.
    while True:
        try:
            # create semaphore
            os.mkdir("/tmp/ex_10_semaphore")    #
            print("# Worker {} created semaphore".format(job_nr))

            # load global kmer dict
            with open(global_dict_path, "rb") as f:
                global_kmer_dict = pickle.load(f)

            # merge local and global kmer dicts. This also filters out non atcg
            # kmers as the global dict only includes atcg kmers as keys.
            for kmer in global_kmer_dict.keys():
                global_kmer_dict[kmer] += kmer_dict.get(kmer, 0)

            # save global kmer dict
            with open(global_dict_path, "wb") as f:
                pickle.dump(global_kmer_dict, f)

            # release semaphore
            os.rmdir("/tmp/ex_10_semaphore")
            print("# Worker {} released semaphore".format(job_nr))
            break

        except:     # wait for semaphore to be free
            print("# Worker {} sleeping waiting for semaphore".format(job_nr))
            time.sleep(0.1)

    print("# Finished {}".format(job_nr))
    return nt_dict

# check input and extract commandline arguments
if len(sys.argv) != 3:
    sys.exit("Usage: ex10_2.py <input fasta file> <k>")

filename = sys.argv[1]
k = int(sys.argv[2])

# open files with byteread
try:
    infile = open(filename, "rb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))

# initiate flags and position in file
index_list = []
headerstart_flag = True
headerend_flag = False
pos = 0
first_flag = True
chunk_size = 200000
while True:
    chunk = infile.read(chunk_size) # read chunk
    index = 0

    while True:     # seek through end of chunk
        if headerstart_flag:    # look for the start of a header
            index = chunk.find(b">", index)

            if index == -1:     # header not found
                break
            else:       # header found
                if not first_flag:  # find end of sequence and write index of entry to list
                    seqend = pos + index - 1
                    index_list.append([headerstart, headerend, seq_start, seqend])
                else:
                    first_flag = False

                headerstart = pos + index
                headerstart_flag = False
                headerend_flag = True

        if headerend_flag:      # look for end of header
            index = chunk.find(b"\n", index)    # find first newline after ">"

            if index == -1:     # newline not found
                break
            else:       # newline found
                headerend = pos + index
                seq_start = headerend + 1
                headerstart_flag = True
                headerend_flag = False

    if len(chunk) < chunk_size:
        break

    pos += chunk_size      # keep track of position in file

# gets seqend for the last sequence and adds to the list
seqend = pos + len(chunk)
index_list.append([headerstart, headerend, seq_start, seqend])
infile.close()
# sort in order to load balance
index_list = sorted(index_list, key=lambda x:(x[3]-x[2]), reverse = True)


# initiate global kmer dict as containing all possible k long atcg kmers as
# byte strings
global_kmer_dict = dict()
for kmer in itertools.product("atcg", repeat=k):
    global_kmer_dict["".join(kmer).encode()] = 0

# save global kmer dict
global_dict_path = "/tmp/global_kmer_dict.pkl"
try:
    with open(global_dict_path, "wb") as f:
        pickle.dump(global_kmer_dict, f)
except IOError as err:
    sys.exit("Error saving global kmer dictionary: " + str(err))

# make sure semaphore works
try:
    os.mkdir("/tmp/ex_10_semaphore")
    os.rmdir("/tmp/ex_10_semaphore")
except IOError as err:
    sys.exit("Error creating semaphore: " + str(err))

setup_end_time = time.time()

# count the occurences of the kmers and nucleotides for each entry in the fasta
# using parallization
nt_dicts = jl.Parallel(n_jobs=8)(jl.delayed(overrep_kmer)(filename, global_dict_path, pos, k, job_nr+1) for job_nr, pos in enumerate(index_list))

occurence_count_time = time.time()

# collect nucleotide occurences to one dict
total_nt_dict = dict()
for nt in b"atcg":
    total_nt_dict[nt] = sum([dict.get(nt, 0) for dict in nt_dicts])

# load global kmer dict
with open(global_dict_path, "rb") as f:
    global_kmer_dict = pickle.load(f)

# calculate total amount of nucleotides and kmers
tot_nt = sum(total_nt_dict.values())
tot_kmer = sum(global_kmer_dict.values())

# calculate if kmers are overrepresented and add overrepresented kmers to a list
overreps = []
for kmer, count in global_kmer_dict.items():
    # calculate the expected occurence of a given kmer
    expected_rep = np.prod([total_nt_dict[nt]/tot_nt for nt in kmer])

    actual_rep = count/tot_kmer     # calculate the actual occurence
    if actual_rep > (2*expected_rep):   # add overrepresented kmers to list
        overreps.append((kmer, actual_rep/expected_rep))

overreps = sorted(overreps, key=lambda x:x[1], reverse = True)  # sort by overrepresention

overreps_time = time.time()

# print overrepresented kmers and their overrepresention
for kmer, rep in overreps:
    print(kmer.decode(), round(rep, 3), sep="\t")

                                                                                            # time for 7mer
print("# Indexing and setup:", round(setup_end_time - start_time, 5))                       # 0.46656 s
print("# kmer and nucleotide count:", round(occurence_count_time - setup_end_time, 5))      # 319.11068 s
print("# Overrepresention:", round(overreps_time - occurence_count_time, 5))                # 0.10617 s
print("# Total:", round(overreps_time - start_time, 5))                                     # 319.68341 s
