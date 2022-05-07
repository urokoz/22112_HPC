#!/usr/bin/env python
import sys
import os
import time
import numpy as np

def arebitsset(bloomfilter, hashes):
    # check if bits are set for any of the hashes
    for hash_number in hashes:
        byteposition = hash_number >> 3
        bitposition = hash_number & 7
        # if any hash not in filter return 0
        if (bloomfilter[byteposition] & (1 << bitposition)) == 0:
            return 0
    return 1

def multi_hash(kmer, k, hash_size):
    # change to int because otherwise hash() is unpredictable....
    kmer_int = int.from_bytes(kmer, byteorder=sys.byteorder)
    return [hash((kmer_int, i)) & hash_size for i in range(k)]


# check input and extract commandline arguments
if len(sys.argv) != 3:
    sys.exit("Usage: ex12_2.py <bloom filter> <query file>")

bloom_file_name = sys.argv[1]
query_file_name = sys.argv[2]

# open files with byteread
try:
    with open(bloom_file_name, "rb") as bloom_file:
        bloom_filter = bytearray(bloom_file.read())
    infile = open(query_file_name, "rb")
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

mersize = 30
k = 4
hash_size = 34359738367
n_seq = len(index_list)
# create translation table to complement
trans_table = bytes.maketrans(b"agctyrwskmdvhb", b"tcgarywsmkhbdv")
# go through the kmers in each fasta entry
for i, pos in enumerate(index_list):
    print("# Working on sequence {}/{}".format(i+1, n_seq))
    # extract header, sequence and remove newlines
    with open(query_file_name, "rb") as infile:
        infile.seek(pos[0])
        header = infile.read(pos[1] - pos[0]).strip()
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(None, delete=b"\n")

    match_list = []
    # hash kmers and check if they are in bloom filter
    for i in range(len(seq)-(mersize-1)):
        kmer = seq[i:i+mersize]   #extract sequence

        hashes = multi_hash(kmer, k, hash_size)

        match_list.append(arebitsset(bloom_filter, hashes))

    # reverse complement seq
    seq = seq.translate(trans_table, delete=b"\n")[::-1]

    # hash kmers and check if they are in bloom filter
    for i in range(len(seq)-(mersize-1)):
        kmer = seq[i:i+mersize]   #extract sequence

        hashes = multi_hash(kmer, k, hash_size)

        match_list.append(arebitsset(bloom_filter, hashes))

    # print header and percent matches
    print(header.decode(), "{:.3f} %".format(np.mean(match_list)*100), sep="\t")
