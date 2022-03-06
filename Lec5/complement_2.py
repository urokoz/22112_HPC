#!/usr/bin/env python

# open relevant files (these will be changed to the computerome paths)
infile = open("/home/mathias/22112_High_performance_computing/Lec5/human.fsa", "r")
outfile = open("/home/mathias/22112_High_performance_computing/Lec5/human_complement.fsa", "w")

# initiate complement and counts
a_count = 0
t_count = 0
c_count = 0
g_count = 0
u_count = 0
gene_complement = ""

# run through the file line-by-line
for line in infile:
    # If a header is seen
    if line.startswith(">"):
        # Write the header, counts and complement gene to the outfile and reset
        if gene_complement != "":
            print(header, "complement", "A:%s" % a_count, "T:%s" % t_count,
                 "C:%s" % c_count, "G:%s" % g_count, "N:%s" % u_count,file=outfile)
            print(gene_complement,file=outfile,end="")
            gene_complement = ""
            a_count = 0
            t_count = 0
            c_count = 0
            g_count = 0
            u_count = 0

        header = line.strip()   # save header
    else:
        c_line = ""
        # run though each character in the line and complement using IUPAC code
        # also count bases
        for char in line.strip():
            if char == "a":
                a_count += 1
                c_line += "t"
            elif char == "g":
                g_count += 1
                c_line += "c"
            elif char == "c":
                c_count += 1
                c_line += "g"
            elif char == "t":
                t_count += 1
                c_line += "a"
            elif char == "y":
                u_count += 1
                c_line += "r"
            elif char == "r":
                u_count += 1
                c_line += "y"
            elif char == "w":
                u_count += 1
                c_line += "w"
            elif char == "s":
                u_count += 1
                c_line += "s"
            elif char == "k":
                u_count += 1
                c_line += "m"
            elif char == "m":
                u_count += 1
                c_line += "k"
            elif char == "d":
                u_count += 1
                c_line += "h"
            elif char == "v":
                u_count += 1
                c_line += "b"
            elif char == "h":
                u_count += 1
                c_line += "d"
            elif char == "b":
                u_count += 1
                c_line += "v"
            else:
                u_count += 1
                c_line += char
        gene_complement += c_line + "\n"    # end line with newline

# as no header is met after the last seq print the last header and seq
if gene_complement != "":
    print(header, "complement", "A:%s" % a_count, "T:%s" % t_count,
         "C:%s" % c_count, "G:%s" % g_count, "N:%s" % u_count,file=outfile)
    print(gene_complement,file=outfile,end="")

infile.close()
outfile.close()
