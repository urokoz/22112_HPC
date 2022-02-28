#!/usr/bin/env python

infile = open("/home/projects/pr_course/human.fsa", "r")
outfile = open("human_cp.fsa", "w")

line = infile.readline()
while line != "":
    outfile.write(line)
    line = infile.readline()

infile.close()
outfile.close()
