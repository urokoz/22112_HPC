#!/usr/bin/env python
import sys
import os
import joblib as jl


def rev_comp(comp_files, trans_table):
    # initiate complement and counts
    a_count = 0
    t_count = 0
    c_count = 0
    g_count = 0
    u_count = 0

    with open(comp_files[0], "rb") as infile:
        header = infile.readline().strip()
        seq = infile.read()

    os.remove(comp_files[0])
    seq = b"".join(seq.split()).translate(trans_table)    # translate line to complement

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
    with open(comp_files[1], "wb") as outfile:
        outfile.write(header + b" complement " + counts.encode("ascii") + b"\n")    # write header to outfile
        outfile.write(b"".join(seq_list))   # Write seq to outfile


if len(sys.argv) != 3:
    sys.exit("Usage: ex9_1.py <input fasta file> <output fasta file>")

try:
    infile = open(sys.argv[1], "rb")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

# create translation table to complement
trans_table = bytes.maketrans(b"agctyrwskmdvhb", b"tcgarywsmkhbdv")

if not os.path.exists("/tmp/to_comp"):
    os.mkdir("/tmp/to_comp")
if not os.path.exists("/tmp/comped"):
    os.mkdir("/tmp/comped")

seq_list = []
comp_list = []
index = 0
# run through the file line-by-line
for line in infile:
    line = line.strip()
    # If a header is seen
    if line.startswith(b">"):
        # Write the header, counts and complement gene to the outfile and reset
        if len(seq_list) > 0:
            outfile_name = "/tmp/to_comp/to_complement{:04d}.fsa".format(index)
            comp_file_name = "/tmp/comped/comp{:04d}.fsa".format(index)

            comp_list.append([outfile_name, comp_file_name])

            # Open output file and write a single fasta sequence
            try:
                outfile = open(outfile_name, "wb")
            except IOError as err:
                sys.exit("Cant open file: " + str(err))

            outfile.write(b"\n".join(seq_list))
            outfile.close()
            seq_list = []
            index += 1
        seq_list.append(line)
    else:
        # count known and unknown bases
        seq_list.append(line)

if len(seq_list) > 0:
    outfile_name = "/tmp/to_comp/to_complement{:04d}.fsa".format(index)
    comp_file_name = "/tmp/comped/comp{:04d}.fsa".format(index)

    comp_list.append([outfile_name, comp_file_name])

    # Open output file and write a single fasta sequence
    try:
        outfile = open(outfile_name, "wb")
    except IOError as err:
        sys.exit("Cant open file: " + str(err))

    outfile.write(b"\n".join(seq_list))
    outfile.close()

jl.Parallel(n_jobs=8)(jl.delayed(rev_comp)(files, trans_table) for files in comp_list)

outfile = open(sys.argv[2], "wb")
try:
    outfile = open(sys.argv[2], "wb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))

for _, infile_name in comp_list:
    infile = open(infile_name, "rb")
    outfile.write(infile.read())
    infile.close()
    os.remove(infile_name)



os.rmdir("/tmp/to_comp")
os.rmdir("/tmp/comped")
