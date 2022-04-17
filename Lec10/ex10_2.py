#!/usr/bin/env python
import sys
import os
import joblib as jl
import time
import itertools
import numpy as np
import pickle

start_time = time.time()

def overrep_kmer(infile_name, global_dict_path, pos, k, job_nr):
    print("Working on {}".format(job_nr))

    with open(infile_name, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])

    seq = seq.translate(None, delete=b"\n")

    nt_dict = dict()
    for nt in b"atcg":
        nt_dict[nt] = seq.count(nt)
    
    kmer_dict = dict()
    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]

        try:
            kmer_dict[kmer] += 1
        except:
            kmer_dict[kmer] = 1


    # semaphore-based memory efficient global kmer count
    while True:
        try:
            os.mkdir("/tmp/ex_10_semaphore")
            print("Worker {} created semaphore".format(job_nr))

            with open(global_dict_path, "rb") as f:
                global_kmer_dict = pickle.load(f)

            for kmer in global_kmer_dict.keys():
                global_kmer_dict[kmer] += kmer_dict.get(kmer, 0)

            with open(global_dict_path, "wb") as f:
                pickle.dump(global_kmer_dict, f)

            os.rmdir("/tmp/ex_10_semaphore")
            print("Worker {} released semaphore".format(job_nr))
            break

        except:
            print("Worker {} sleeping waiting for semaphore".format(job_nr))
            time.sleep(0.1)

    print("Finished {}".format(job_nr))
    return nt_dict


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

index_end_time = time.time()

global_kmer_dict = dict()
for kmer in itertools.product("atcg", repeat=k):
    global_kmer_dict["".join(kmer).encode()] = 0

global_dict_path = "/tmp/global_kmer_dict.pkl"
with open(global_dict_path, "wb") as f:
    pickle.dump(global_kmer_dict, f)

try:
    os.rmdir("/tmp/ex_10_semaphore")
except:
    pass

dir_created_time = time.time()

nt_dicts = jl.Parallel(n_jobs=8)(jl.delayed(overrep_kmer)(filename, global_dict_path, pos, k, job_nr+1) for job_nr, pos in enumerate(index_list))

total_nt_dict = dict()
for nt in b"atcg":
    total_nt_dict[nt] = sum([dict.get(nt, 0) for dict in nt_dicts])

with open(global_dict_path, "rb") as f:
    global_kmer_dict = pickle.load(f)

tot_nt = sum(total_nt_dict.values())
tot_kmer = sum(global_kmer_dict.values())

overreps = []
for kmer, count in global_kmer_dict.items():
    random_chance = np.prod([total_nt_dict[nt]/tot_nt for nt in kmer])

    actual_rep = count/tot_kmer
    if actual_rep > (2*random_chance):
        overreps.append((kmer,actual_rep/random_chance))

overreps = sorted(overreps, key=lambda x:x[1], reverse = True)

for kmer, rep in overreps:
    print(kmer.decode(), rep, sep="\t")
