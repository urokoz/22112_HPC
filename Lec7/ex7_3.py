#!/usr/bin/env python
import sys


if len(sys.argv) != 3:
    sys.exit("Usage: ex7_3.py <input fasta file> <output file>")

# open files with byteread
try:
    infile = open(sys.argv[1], "rb")
    outfile = open(sys.argv[2], "w")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

# initiate flags and position in file
index_list = []
headerstart_flag = True
headerend_flag = False
pos = 0
first_flag = True
chunk_size = 1000000
while True:
    chunk = infile.read(chunk_size) # read chunk
    index = 0

    while True:     # seek through end of chunk
        if headerstart_flag:    # look for the start of a header
            index = chunk.find(b">", index)

            if index == -1:     # header not found
                break
            else:       # header found
                if not first_flag:  # find end of sequence and write index of entry to list
                    seqend = pos + index - 1
                    index_list.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))
                else:
                    first_flag = False

                headerstart = pos + index
                headerstart_flag = False
                headerend_flag = True

        if headerend_flag:      # look for end of header
            index = chunk.find(b"\n", index)    # find first newline after ">"

            if index == -1:     # newline not found
                break
            else:       # newline found
                headerend = pos + index
                seq_start = headerend + 1
                headerstart_flag = True
                headerend_flag = False

    if len(chunk) < chunk_size:
        break

    pos += chunk_size      # keep track of position in file

# gets seqend for the last sequence and adds to the list
seqend = pos + len(chunk)
index_list.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))

outfile.write("\n".join(index_list))    # write to outfile

infile.close()
outfile.close()
