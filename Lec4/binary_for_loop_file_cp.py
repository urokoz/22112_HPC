#!/usr/bin/env python

infile = open("/home/projects/pr_course/human.fsa", "rb")
outfile = open("human_cp.fsa", "wb")

for line in infile:
    outfile.write(line)

infile.close()
outfile.close()
