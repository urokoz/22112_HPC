#!/usr/bin/env python

infile = open("/home/projects/pr_course/human.fsa", "r")
outfile = open("human_cp.fsa", "w")

for line in infile:
    outfile.write(line)

infile.close()
outfile.close()
