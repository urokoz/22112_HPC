#!/usr/bin/env python
import sys

# check inputs
if len(sys.argv) != 3:
    sys.exit("Usage: ex7_1.py <input fasta file> <output file>")

# open files with byteread
try:
    infile = open(sys.argv[1], "rb")
    outfile = open(sys.argv[2], "w")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

index_list = []   # list for indexes
first_flag = False
line = infile.readline()
while line != b"":
    # If a header is seen extract the indexes of the header sequences around the header
    if line.startswith(b">"):
        if first_flag:    # for every header after the first
            seqend = infile.tell() - len(line) - 1
            index_list.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))    # saves index for fasta entry

            seq_start = infile.tell()
            headerstart = seq_start - len(line)
            headerend = seq_start - 1
        else:   # For the fist header
            seq_start = infile.tell()
            headerstart = seq_start - len(line)
            headerend = seq_start - 1
            first_flag = True

    line = infile.readline()

# gets seqend for the last sequence and adds to the list
seqend = infile.tell()
index_list.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))

outfile.write("\n".join(index_list))

infile.close()
outfile.close()
