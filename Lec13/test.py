#!/usr/bin/env python3

# initiate flags and position in file
person_dict = dict()
headerstart_flag = True
headerend_flag = False
pos = 0
rest = ""
chunk_size = 1024*1024
while True:
    chunk = rest + infile.read(chunk_size) # read chunk
    rest = ""
    index = 0

    while True:     # seek through end of chunk
        if headerstart_flag:    # look for the start of a header
            index = chunk.find(b"@", index)
            if index == -1:     # header not found
                break
            else:
                headerstart_flag = False
                headerend_flag = True

        if headerend_flag:      # look for end of header
            index = chunk.find(b"\n", index)    # find first newline after "@"

            if index == -1:     # newline not found
                rest = chunk[-8:]
                break
            else:       # newline found
                barcode = chunk[index-8:index]
                try:
                    person_dict[barcode] += 1
                except:
                    person_dict[barcode] = 1
                headerstart_flag = True
                headerend_flag = False

    if len(chunk) < chunk_size:
        break

    pos += chunk_size      # keep track of position in file
