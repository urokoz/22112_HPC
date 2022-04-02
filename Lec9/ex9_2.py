#!/usr/bin/env python
import sys
import joblib as jl
import os
import time


def rev_comp(input_file, pos, trans_table, index=0):
    # initiate complement and counts
    a_count = 0
    t_count = 0
    c_count = 0
    g_count = 0
    u_count = 0

    with open(input_file, "rb") as infile:
        infile.seek(pos[0])
        header = infile.read(pos[1] - pos[0])
        infile.seek(pos[2])
        seq = infile.read(pos[3] - pos[2])

    seq = seq.translate(trans_table, delete=b"\n")    # translate line to complement

    # Count bases
    a_count += seq.count(b"a")
    t_count += seq.count(b"t")
    c_count += seq.count(b"c")
    g_count += seq.count(b"g")
    u_count += len(seq) - (a_count + t_count + c_count + g_count)

    seq = seq[::-1]
    seq_list = []
    for i in range(0, len(seq), 60):
        seq_list.append(seq[i:i+60] + b"\n")

    counts = "A:{} T:{} C:{} G:{} U:{}".format(a_count, t_count, c_count, g_count, u_count)     # create counts
    output_file = "/tmp/rev_comp_{:04d}.fsa".format(index)
    # output_file = sys.argv[2]
    # with open(output_file, "ab+") as outfile:
    with open(output_file, "wb") as outfile:
        outfile.write(header + b" complement " + counts.encode("ascii") + b"\n")    # write header to outfile
        outfile.write(b"".join(seq_list))   # Write seq to outfile

    return output_file

if len(sys.argv) != 3:
    sys.exit("Usage: ex9_2.py <input fasta file> <output file>")

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
infile.close()

index_list.append([headerstart, headerend, seq_start, seqend])

index_end = time.time()

# create translation table to complement
trans_table = bytes.maketrans(b"agctyrwskmdvhb", b"tcgarywsmkhbdv")

files = jl.Parallel(n_jobs=8)(jl.delayed(rev_comp)(sys.argv[1], positions, trans_table, i) for i, positions in enumerate(index_list))

rev_comp_end = time.time()

try:
    outfile = open(sys.argv[2], "wb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))

for infile_name in files:
    infile = open(infile_name, "rb")
    outfile.write(infile.read())
    infile.close()
    os.remove(infile_name)
write_end = time.time()

print("Indexing:", index_end - index_start)
print("Reverse complement:", rev_comp_end - index_end)
print("Final write:", write_end - rev_comp_end)
