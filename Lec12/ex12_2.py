#!/usr/bin/env python

########################################################################

# Since the number of bits needed to represent the number of bit is 35 and we
# need 4 hash functions we can do that by using a hash function with at least
# 140 bits and taking 4x35 non overlapping bits.
# After testing sha1, sha224, sha256, sha512 and the built in hash() I found
# that running the hash() function 4 times yielding 64 bits per function was the
# fastest.

########################################################################

import sys
import os
import time
import numpy as np

start_time = time.time()

def calc_bloom(n_elem = 3139742750, p = 0.01, verbose = False):
    # Calculate size of bloom filter
    m = np.ceil((-n_elem*np.log(p))/(np.log(2)**2))
    # round m up to the nearest power of 2
    m_bit_size = int(np.ceil(np.log2(m)))
    m_bits = 2**m_bit_size
    m_bytes = int(m_bits/8)

    # calculate how many hash funcions and actual p
    k = int(np.ceil(-np.log(p)/np.log(2)))
    p_test = (1-np.exp(-k*n_elem/m_bits))**k

    # reduce amount of hash functions if possible
    if p_test < p:
        while True:
            k_test = k-1
            p_test = (1-np.exp(-k_test*n_elem/m_bits))**k_test

            if p_test < p:
                k = k_test
            else:
                break

    if verbose:
        print("Blooms filter size:")                        # human.fsa output
        print("k:", k)                                      # 4
        print("p_true:", (1-np.exp(-k*n_elem/m_bits))**k)   # 0.00878607406931
        print("m_bit_size:", m_bit_size)                    # 35
        print("bits per filter:", m_bits)                   # 34359738368
        print("bytes per filter:", m_bytes)                 # 4294967296

    return k, m_bit_size, m_bits, m_bytes


def multi_hash(kmer, k, hash_size):
    # hash kmer
    # change to int because otherwise hash() is unpredictable....
    kmer_int = int.from_bytes(kmer, byteorder=sys.byteorder)
    return [hash((kmer_int, i)) & hash_size for i in range(k)]


def setbits(bloomfilter, hashes):
    # set bits according to hash
    for hash_number in hashes:
        byteposition = hash_number >> 3
        bitposition = hash_number & 7
        bloomfilter[byteposition] |= 1 << bitposition


# check input and extract commandline arguments
if len(sys.argv) != 2:
    sys.exit("Usage: ex12_2.py <input fasta file>")

filename = sys.argv[1]

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

# Calculate bloomfilter parameters
hum_fsa_size = seqend
p = 0.01
k, m_bit_size, m_bits, m_bytes = calc_bloom(hum_fsa_size, p)
hash_size = m_bits-1

setup_end_time = time.time()

mersize = 30
n_seq = len(index_list)
bloom_filter = bytearray(m_bytes)   # initiate bloom filter
# go through the kmers in each fasta entry
for i, pos in enumerate(index_list):
    print("# Working on sequence {}/{}".format(i+1, n_seq))
    # open file, extract sequence and remove newlines
    with open(filename, "rb") as infile:
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])
    seq = seq.translate(None, delete=b"\n")

    # hash kmers and add to bloom filter
    for i in range(len(seq)-(mersize-1)):
        kmer = seq[i:i+mersize]   #extract sequence

        hashes = multi_hash(kmer, k, hash_size)

        setbits(bloom_filter, hashes)

bloom_time = time.time()

# save bloom filter
with open("bloom_filter.bin", "wb") as outfile:
    outfile.write(bloom_filter)

end_time = time.time()


print("# Indexing and setup:", round(setup_end_time - start_time, 5))
print("# create bloom:", round(bloom_time - setup_end_time, 5))
print("# Total:", round(end_time - start_time, 5))
