#!/usr/bin/env python

infile = open("/home/projects/pr_course/human.fsa", "rb")
outfile = open("human_cp.fsa", "wb")

while True:
    chunck = infile.read(10000)
    outfile.write(chunck)
    if len(chunck) < 10000:
        break
infile.close()
outfile.close()
