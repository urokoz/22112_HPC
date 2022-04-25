#!/usr/bin/env python
import sys
import os
import time
import itertools

def num2dna(num):
    bi_num = "{:b}".format(num)
    dna = ""
    for i in range(0, len(binum)-2, 2):
        base = binum



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

kmer_dict = dict()
# toN = bytes.maketrans(b'MRYKVHDBacgtmrykvhdbxnsw',b'NNNNNNNNACGTNNNNNNNNNNNN')
for i, pos in enumerate(index_list):
    print("# Working on sequence {}".format(i+1))
    # open file, extract sequence and remove newlines
    with open(filename, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(None, delete=b"\n")

    # count the occurences of the possible kmers
    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]   #extract sequence

        # add kmer occurence to the kmer dict. Add an entry if the entry doesn't
        # already exist
        try:
            kmer_dict[kmer] += 1
        except:
            kmer_dict[kmer] = 1

# filter out any non atcg kmers
filtered_kmer_dict = dict()
for kmer_list in itertools.product("atcg", repeat=k):
    kmer = "".join(kmer_list).encode()
    filtered_kmer_dict[kmer] = kmer_dict.get(kmer, 0)

for kmer, val in filtered_kmer_dict.items():
    if val == 1:
        print(kmer)
