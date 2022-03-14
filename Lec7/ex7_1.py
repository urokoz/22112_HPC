#!/usr/bin/env python
import sys


def unix_call(command):
    job = subprocess.Popen(command.split())


if len(sys.argv) != 3:
    sys.exit("Usage: ex7_1.py <input fasta file> <output file>")

try:
    infile = open(sys.argv[1], "rb")
    outfile = open(sys.argv[2], "w")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

info = []
flag = False
line = infile.readline()
while line != b"":
    # If a header is seen
    if line.startswith(b">"):
        if flag:
            seqend = infile.tell() - len(line) - 1
            info.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))
            seq_start = infile.tell()
            headerstart = seq_start - len(line)
            headerend = seq_start - 1
        else:
            seq_start = infile.tell()
            headerstart = seq_start - len(line)
            headerend = seq_start - 1
            flag = True

    line = infile.readline()

seqend = infile.tell()
info.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))

outfile.write("\n".join(info))

infile.close()
outfile.close()



# NOTES:
# Look into chuck reading
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
