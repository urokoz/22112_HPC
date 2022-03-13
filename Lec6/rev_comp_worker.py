#!/usr/bin/env python
import sys
import os


if len(sys.argv) != 3:
    sys.exit("Usage: rev_comp_worker.py <input fasta file> <output fasta file>")

try:
    infile = open(sys.argv[1], "rb")
    outfile = open(sys.argv[2], "wb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))


# initiate complement and counts
a_count = 0
t_count = 0
c_count = 0
g_count = 0
u_count = 0
gene = b""

# create translation table to complement
trans_table = bytes.maketrans(b"agctyrwskmdvhb", b"tcgarywsmkhbdv")

# run through the file line-by-line
for line in infile:
    line = line.strip()
    # If a header is seen
    if line.startswith(b">"):
        header = line   # save header
    else:
        # count known and unknown bases
        gene += line

infile.close()
os.remove(sys.argv[1])  # remove file after use

complement = gene.translate(trans_table)    # translate line to complement

# Count bases
a_count += gene.count(b"a")
t_count += gene.count(b"t")
c_count += gene.count(b"c")
g_count += gene.count(b"g")
u_count += len(gene) - (a_count + t_count + c_count + g_count)

counts = "A:{} T:{} C:{} G:{} U:{}".format(a_count, t_count, c_count, g_count, u_count)     # create counts
outfile.write(header + b" complement " + counts.encode("ascii") + b"\n")    # write header to outfile
# reverse strand and change format to fasta
complement = complement[::-1]
seq_list = []
for i in range(0, len(complement), 60):
    seq_list.append(complement[i:i+60] + b"\n")

outfile.write(b"".join(seq_list))   # Write seq to outfile
outfile.close()
