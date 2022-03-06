#!/usr/bin/env python

# open files as byte type (these will be changed to the computerome paths)
infile = open("/home/mathias/22112_High_performance_computing/Lec5/humantest.fsa", "rb")
outfile = open("/home/mathias/22112_High_performance_computing/Lec5/humantest_complement.fsa", "wb")

# initiate complement and counts
a_count = 0
t_count = 0
c_count = 0
g_count = 0
u_count = 0
gene_complement = b""

# create translation table to complement
code_str = b"agctyrwskmdvhb"
complement_str = b"tcgarywsmkhbdv"
trans_table = bytes.maketrans(code_str, complement_str)

# run through the file line-by-line
for line in infile:
    # If a header is seen
    if line.startswith(">"):
        # Write the header, counts and complement gene to the outfile and reset
        if gene_complement != b"":
            counts = "A:{} T:{} C:{} G:{} U:{}".format(a_count, t_count, c_count, g_count, u_count)     # create counts
            outfile.write(header + b" complement " + counts.encode("ascii") + b"\n" + gene_complement)
            gene_complement = b""
            a_count = 0
            t_count = 0
            c_count = 0
            g_count = 0
            u_count = 0

        header = line.strip()   # save header
    else:
        # count known and unknown bases
        a_count += line.count(b"a")
        t_count += line.count(b"t")
        c_count += line.count(b"c")
        g_count += line.count(b"g")
        u_count += len(line.strip()) - (line.count(b"a") + line.count(b"t") + line.count(b"c") + line.count(b"g"))

        c_line = line.translate(trans_table)    # translate line to complement
        gene_complement = gene_complement + c_line

# as no header is met after the last seq print the last header and seq
if gene_complement != "":
    counts = "A:{} T:{} C:{} G:{} U:{}".format(a_count, t_count, c_count, g_count, u_count)
    outfile.write(header + b" complement " + counts.encode("ascii") + b"\n" + gene_complement)

infile.close()
outfile.close()
