#!/usr/bin/env python
import sys
import os
import time
import itertools

start_time = time.time()

def num2dna(num, k):
    """ Converts an int to a DNA kmer.
        input:
        num         int
        k           int

        output:
        dna         str
    """
    # convert to binary of the correct length to represent the kmer
    bi_num = bin(num)[2:]
    bi_num = "0"*(k*2-len(bi_num)) + bi_num

    dna = ""
    # convert binary to dna one base at a time
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
try:
    k = int(sys.argv[2])
except ValueError:
    sys.exit("k has to be an integer over 0")

if not k > 0:
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
kmer_array = bytearray(4**k)   # initiate bytearray
base4 = bytes.maketrans(b'acgt',b'0123')
# go through the kmers in each fasta entry
for i, pos in enumerate(index_list):
    print("# Working on sequence {}/{}".format(i+1, n_seq))
    # open file, extract sequence and remove newlines
    with open(filename, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(base4, delete=b"\n")

    # count the occurences of the possible kmers
    for i in range(len(seq)-(k-1)):
        kmer = seq[i:i+k]   #extract sequence

        try:
            # convert sequence to int using base 4
            # non ATCG kmers will fail here
            idx = int(kmer, base = 4)
            # count the kmer occurences in the byte array
            if kmer_array[idx] == 255:   # max count 255
                pass
            else:
                kmer_array[idx] += 1
        except:
            pass

kmer_count_time = time.time()

bytearray_size = sys.getsizeof(kmer_array)

# print kmers that only appear once
for i, val in enumerate(kmer_array):
    if val == 1:
        print(num2dna(i, k))

find_singles = time.time()

                                                                                # time for 10mer
print("# Indexing and setup:", round(setup_end_time - start_time, 5))           # 1.73636 s
print("# kmer count:", round(kmer_count_time - setup_end_time, 5))              # 1311.29641 s
print("# Find singles:", round(find_singles - kmer_count_time, 5))              # 0.06882 s
print("# Total:", round(find_singles - start_time, 5))                          # 1313.10158 s
print("# Memory usage of bytearray:", bytearray_size)                           # 1 048 633 bytes

# one kmer occurs: cgtaacgcgc

# changing the kmer size to 16 uses 4^16 bytes of memory. Which is significantly
# less than when using a dict.
