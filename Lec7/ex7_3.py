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

# initiate flags
index_list = []
headerstart_flag = True
headerend_flag = False
pos = 0
first_flag = True
chunk_size = 1000000
while True:
    chunk = infile.read(chunk_size)
    index = 0

    while True:
        if headerstart_flag:
            index = chunk.find(b">", index)

            if index == -1:
                break
            else:
                if not first_flag:
                    seqend = pos + index - 1
                    index_list.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))
                else:
                    first_flag = False

                headerstart = pos + index
                headerstart_flag = False
                headerend_flag = True

        if headerend_flag:
            index = chunk.find(b"\n", index)

            if index == -1:
                break
            else:
                headerend = pos + index
                seq_start = headerend + 1
                headerstart_flag = True
                headerend_flag = False

    if len(chunk) < chunk_size:
        break

    pos += chunk_size

seqend = pos + len(chunk)
index_list.append(" ".join([str(headerstart), str(headerend), str(seq_start), str(seqend)]))

outfile.write("\n".join(index_list))

infile.close()
outfile.close()
