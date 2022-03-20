#!/usr/bin/env python
import sys

# check inputs
if len(sys.argv) != 7:
    sys.exit("Usage: ex7_2.py <input fasta file> <output fasta file> <header start> <header end> <seq start> <seq end>")

# open files with byteread
try:
    infile = open(sys.argv[1], "rb")
    outfile = open(sys.argv[2], "wb")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

# load indexes
header_start = int(sys.argv[3])
header_end = int(sys.argv[4])
seq_start = int(sys.argv[5])
seq_end = int(sys.argv[6])

# go to index and write entry
infile.seek(header_start)
outfile.write(infile.read(seq_end-header_start))
