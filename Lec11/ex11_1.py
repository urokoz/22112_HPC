#!/usr/bin/env python
import sys
import os
import time
import itertools

start_time = time.time()

# check input and extract commandline arguments
if len(sys.argv) != 3:
    sys.exit("Usage: ex11_2.py <input fasta file> <k>")

filename = sys.argv[1]
try:
    k = int(sys.argv[2])
except ValueError:
    sys.exit("k has to be an integer over 0")

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

setup_end_time = time.time()
n_seq = len(index_list)
kmer_dict = dict()
# go through the kmers in each fasta entry
for i, pos in enumerate(index_list):
    print("# Working on sequence {}/{}".format(i+1, n_seq))
    # open file, extract sequence and remove newlines
    with open(filename, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(None, delete=b"\n")

    # count the occurences of the possible kmers
    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]   #extract sequence

        # add kmer occurence to the kmer dict.
        # add an entry if the entry doesn't already exist
        try:
            kmer_dict[kmer] += 1
        except:
            kmer_dict[kmer] = 1

kmer_count_time = time.time()

dict_size = sys.getsizeof(kmer_dict)

# filter out any non atcg kmers
filtered_kmer_dict = dict()
for kmer_list in itertools.product("atcg", repeat=k):
    kmer = "".join(kmer_list).encode()
    filtered_kmer_dict[kmer] = kmer_dict.get(kmer, 0)
# print kmers that only appear once
for kmer, val in filtered_kmer_dict.items():
    if val == 1:
        print(kmer.decode())

find_singles = time.time()

                                                                                # time for 10mer
print("# Indexing and setup:", round(setup_end_time - start_time, 5))           # 2.74714 s
print("# kmer count:", round(kmer_count_time - setup_end_time, 5))              # 1408.58258 s
print("# Find singles:", round(find_singles - kmer_count_time, 5))              # 0.88604 s
print("# Total:", round(find_singles - start_time, 5))                          # 1412.21576 s
print("# Memory usage of dict:", dict_size)                                     # 41 943 136 bytes

# one kmer occurs: cgtaacgcgc

# changing the kmer size to 16 uses a lot of memory using a dict. To the point
# of running out of ram on a 16 gb system.
