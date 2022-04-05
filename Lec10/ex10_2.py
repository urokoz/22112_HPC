#!/usr/bin/env python
import sys
import os
import joblib as jl
import time
import itertools
import numpy as np

start_time = time.time()

def overrep_kmer(infile_name, pos, k, i):
    print("Working on {}".format(i))
    with open(infile_name, "rb") as infile:
        infile.seek(pos[0])
        header = infile.read(pos[1] - pos[0])
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])

    seq = seq.translate(None, delete=b"\n")

    seq_n = len(seq)
    Pnt_dict = dict()


    nt_count = [seq.count(nt) for nt in b"atcg"]

    kmer_count = [seq.count("".join(kmer).encode()) for kmer in itertools.product("atcg", repeat=k)]
    print("Finished {}".format(i))
    return nt_count, kmer_count


if len(sys.argv) != 3:
    sys.exit("Usage: ex9_3.py <input fasta file> <k>")

filename = sys.argv[1]
k = int(sys.argv[2])
# open files with byteread
try:
    infile = open(filename, "rb")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

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

index_list = sorted(index_list, key=lambda x:(x[3]-x[2]), reverse = True)

tot_nt_count = []
tot_kmer_count = []


hello = jl.Parallel(n_jobs=11)(jl.delayed(overrep_kmer)(filename, pos, k, i+1) for i, pos in enumerate(index_list))

# print(hello)

for (nt_count, kmer_count) in hello:
    if tot_nt_count == []:
        tot_nt_count = nt_count
    else:
        tot_nt_count = [old_count + new_count for old_count, new_count in zip(tot_nt_count, nt_count)]

    if tot_kmer_count == []:
        tot_kmer_count = kmer_count
    else:
        tot_kmer_count = [old_count + new_count for old_count, new_count in zip(tot_kmer_count, kmer_count)]

tot_nt = sum(tot_nt_count)
tot_kmer = sum(tot_kmer_count)

Pnt_dict = dict()
for nt, count in zip("atcg", tot_nt_count):
    Pnt_dict[nt] = count/tot_nt


overreps = []
for count, kmer in zip(tot_kmer_count, itertools.product("atcg", repeat=k)):
    random_chance = np.prod([Pnt_dict[nt] for nt in kmer])

    actual_rep = count/tot_kmer
    if actual_rep > (2*random_chance):
        overreps.append(("".join(kmer),actual_rep/random_chance))

overreps = sorted(overreps, key=lambda x:x[1], reverse = True)

for kmer, rep in overreps:
    print(kmer, rep, sep="\t")
print("Time:", time.time()-start_time)
