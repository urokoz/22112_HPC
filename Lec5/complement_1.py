#!/usr/bin/env python

# open relevant files (these will be changed to the computerome paths)
infile = open("/home/mathias/22112_High_performance_computing/Lec5/humantest.fsa", "r")
outfile = open("/home/mathias/22112_High_performance_computing/Lec5/humantest_complement.fsa", "w")

# Initiate the complement gene
gene_complement = ""

# run through the file line-by-line
for line in infile:
    # If a header is seen
    if line.startswith(">"):
        # Write the header and complement gene to the outfile
        if gene_complement != "":      # to not run for the first header
            print(header, "complement",file=outfile)
            print(gene_complement,file=outfile,end="")
            gene_complement = ""

        header = line.strip()   #save header
    else:
        # run though each character in the line and complement using IUPAC code
        c_line = ""
        for char in line.strip():
            if char == "a":
                c_line += "t"
            elif char == "g":
                c_line += "c"
            elif char == "c":
                c_line += "g"
            elif char == "t":
                c_line += "a"
            elif char == "y":
                c_line += "r"
            elif char == "r":
                c_line += "y"
            elif char == "w":
                c_line += "w"
            elif char == "s":
                c_line += "s"
            elif char == "k":
                c_line += "m"
            elif char == "m":
                c_line += "k"
            elif char == "d":
                c_line += "h"
            elif char == "v":
                c_line += "b"
            elif char == "h":
                c_line += "d"
            elif char == "b":
                c_line += "v"
            else:
                c_line += char
        gene_complement += c_line + "\n"    # end line with newline

# as no header is met after the last seq print the last header and seq
if gene_complement != "":
    print(header, "complement", file=outfile)
    print(gene_complement,file=outfile,end="")
    gene_complement = ""
#close files
infile.close()
outfile.close()
