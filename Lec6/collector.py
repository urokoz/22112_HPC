#!/usr/bin/env python
import sys
import os

if len(sys.argv) != 3:
    sys.exit("Usage: collector.py <input directory with fasta files> <output fasta file>")

try:
    outfile = open(sys.argv[2], "wb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))

# walk through dir containing only complemented files
for root, dirs, files in os.walk(sys.argv[1]):
    for name in sorted(files):
        infile_name = os.path.join(root, name)  # get name of file
        # open file, write to collective file and close + delete original file
        infile = open(infile_name, "rb")
        outfile.write(b"".join(infile.readlines()))
        infile.close()
        os.remove(infile_name)
outfile.close()
