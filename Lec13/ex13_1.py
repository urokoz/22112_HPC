#!/usr/bin/env python
import gzip
import sys
import time

print("# ex13_1.py", file=sys.stderr)
start_time = time.time()


def openfile(filename, mode):
    """ Open gzip or normal files.
    """
    try:
        if filename.endswith('.gz'):
            fh = gzip.open(filename, mode=mode)
        else:
            fh = open(filename, mode)
    except:
        sys.exit("Can't open file:", filename)
    return fh


def chunk_read(infile):
    """ Read file using chunk read to find and count barcodes.
        Output counts as a dict.
    """
    # initiate flags and position in file
    person_dict = dict()
    headerstart_flag = True
    headerend_flag = False
    pos = 0
    rest = b""
    chunk_size = 1024*1024
    while True:
        chunk = rest + infile.read(chunk_size) # read chunk
        rest = b""
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
                prev_index = index
                index = chunk.find(b"\n", index)    # find first newline after "@"

                if index == -1:     # newline not found
                    rest = chunk[prev_index:]
                    break
                else:       # newline found
                    # extract barcodes and count in dict
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

    infile.close()
    return person_dict


# check input and extract commandline arguments
if len(sys.argv) != 2:
    sys.exit("Usage: ex13_1.py <input fasta file>")

filename = sys.argv[1]

# open files with byteread
try:
    infile = openfile(filename, "rb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))


person_dict = chunk_read(infile)

count_time = time.time()

# sort dict, format for printing, join and print in one go.
person_list = sorted(person_dict.items(), key=lambda x: x[1], reverse=True)
print_list = ["{}\t{}".format(barcode.decode(), count) for (barcode, count) in person_list]
print("\n".join(print_list))

print_time = time.time()

print("# Barcode count time:", count_time-start_time, file=sys.stderr)
print("# Sort and print time:", print_time-count_time, file=sys.stderr)
print("# Total time:", print_time-start_time, file=sys.stderr)
