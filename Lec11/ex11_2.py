#!/usr/bin/env python
import sys
import os
import time
import itertools


def num2dna(num, k):
    bi_num = bin(num)[2:]
    bi_num = "0"*(k*2-len(bi_num)) + bi_num

    dna = ""
    for i in range(0, len(bi_num)-1, 2):
        base = bi_num[i:i+2]

        if base == "00":
            dna += "a"
        elif base == "01":
            dna += "c"
        elif base == "10":
            dna += "g"
        elif base == "11":
            dna += "t"

    return dna


# check input and extract commandline arguments
if len(sys.argv) != 3:
    sys.exit("Usage: ex11_2.py <input fasta file> <k>")

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

index_array = bytearray(4**k)

kmer_dict = dict()
base4 = bytes.maketrans(b'acgt',b'0123')
for i, pos in enumerate(index_list):
    print("# Working on sequence {}".format(i+1))
    # open file, extract sequence and remove newlines
    with open(filename, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(base4, delete=b" \t\n")

    # count the occurences of the possible kmers
    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]   #extract sequence

        try:
            index_array[int(kmer, base = 4)] += 1

        except:
            pass

for i, val in enumerate(index_array):
    if val == 1:
        print(num2dna(i, k))
