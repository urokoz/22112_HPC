#!/usr/bin/env python
import sys
import os
import joblib as jl
import time
import itertools
import numpy as np


def overrep_kmer(infile_name, nt_dict, kmer_dict, pos, k):

    with open(infile_name, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])

    seq = seq.translate(None, delete=b"\n")

    for nt in b"atcg":
        nt_dict[nt] += seq.count(nt)

    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]

        try:
            kmer_dict[kmer] += 1
        except:
            kmer_dict[kmer] = 1

    return nt_dict, kmer_dict


if len(sys.argv) != 3:
    sys.exit("Usage: ex10_1.py <input fasta file> <k>")

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

kmer_dict = dict()
nt_dict = dict()
for nt in b"atcg":
    nt_dict[nt] = 0


for i, pos in enumerate(index_list):
    print("Working on sequence {}".format(i+1))
    nt_dict, kmer_dict = overrep_kmer(filename, nt_dict, kmer_dict, pos, k)

filtered_kmer_dict = dict()
for kmer_list in itertools.product("atcg", repeat=k):
    kmer = "".join(kmer_list).encode()
    filtered_kmer_dict[kmer] = kmer_dict[kmer]

tot_nt = sum(nt_dict.values())
tot_kmer = sum(filtered_kmer_dict.values())

overreps = []
for kmer, count in filtered_kmer_dict.items():
    random_chance = np.prod([nt_dict[nt]/tot_nt for nt in kmer])

    actual_rep = count/tot_kmer
    if actual_rep > (2*random_chance):
        overreps.append((kmer, actual_rep/random_chance))

overreps = sorted(overreps, key=lambda x:x[1], reverse = True)

for kmer, rep in overreps:
    print(kmer.decode(), rep, sep="\t")
