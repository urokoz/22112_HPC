#!/usr/bin/env python
import sys
import joblib as jl
import os
import time

prog_start = time.time()

def rev_comp_write(input_file, pos, trans_table):
    with open(input_file, "r+b") as infile:
        infile.seek(pos[2])     # go to start of sequence
        seq = infile.read(pos[3] - pos[2])  # read sequence

        seq = seq.translate(trans_table, delete=b"\n")    # translate line to complement

        seq = seq[::-1]     # reverse the sequence

        seq_list = [seq[i:i+60] for i in range(0, len(seq), 60)]    # split seq into 60 aa long segments

        infile.seek(pos[2])     # go back to start of sequence
        infile.write(b"\n".join(seq_list))   # write seq to outfile overwriting the sequence


if len(sys.argv) != 2:
    sys.exit("Usage: ex9_3.py <input fasta file>")

# open files with byteread
try:
    infile = open(sys.argv[1], "rb")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

index_start = time.time()
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
index_end = time.time()

# create translation table to complement
trans_table = bytes.maketrans(b"agctyrwskmdvhb", b"tcgarywsmkhbdv")

# reverse complement the fasta entries parallelised to 8 jobs at a time
files = jl.Parallel(n_jobs=8)(jl.delayed(rev_comp_write)(sys.argv[1], positions, trans_table) for positions in index_list)

rev_comp_end = time.time()

print("Indexing:", index_end - index_start)                         # 0.489
print("Reverse complement and write:", rev_comp_end - index_end)    # 6.168
print("Total:", rev_comp_end - prog_start)                          # 6.657
