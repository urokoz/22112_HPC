#!/usr/bin/env python
import sys
import time
import gzip

start_time = time.time()


def treat_entry(entry, close_dict):
    idx = entry.find(b"\n")
    header = entry[:idx-8]
    barcode = entry[idx-8:idx]
    body = entry[idx:]

    correct_barcode = close_dict.get(barcode)

    if correct_barcode:
        entry = header + correct_barcode + body
        return (correct_barcode, entry.strip())
    else:
        return False, False


def openfile(filename, mode):
    try:
        if filename.endswith('.gz'):
            fh = gzip.open(filename, mode=mode)
        else:
            fh = open(filename, mode)
    except:
        sys.exit("Can't open file:", filename)
    return fh


# check input and extract commandline arguments
if len(sys.argv) != 3:
    sys.exit("Usage: ex13_2.py <input fasta file> <barcode lookup file>")

filename = sys.argv[1]
barcode_file = sys.argv[2]

# open files with byteread
try:
    infile = openfile(filename, "rb")

    barcode_dict = dict()
    with open(barcode_file, "rb") as f:
        for line in f:
            line = line.split()
            barcode_dict[line[0]] = line[1]
except IOError as err:
    sys.exit("Cant open file: " + str(err))


# initiate flags and position in file
demultiplex_dict = dict()
stored = 0
rest = b""
first_flag = True
chunk_size = 1024*1024
while True:
    chunk = rest + infile.read(chunk_size) # read chunk
    rest = b""
    index = 0

    while True:     # seek through end of chunk
        # look for the start of a header
            prev_index = index
            index = chunk.find(b"@", prev_index+1)
            if index == -1:     # header not found
                rest = chunk[prev_index:]
                break
            else:
                entry = chunk[prev_index:index]

                barcode, entry = treat_entry(entry, barcode_dict)

                if barcode:
                    try:
                        demultiplex_dict[barcode].append(entry)
                    except:
                        demultiplex_dict[barcode] = [entry]

                        for barcode, entries in demultiplex_dict.items():
                            outfile_name = barcode.decode() + "_fastq.gz"
                            outfile = openfile(outfile_name, "ab")

                            outfile.write(b"\n".join(entries) + b"\n")
                            outfile.close()
                            stored_counter = 0
                            demultiplex_dict = dict()


    if len(chunk) < chunk_size:
        break

    stored += chunk_size      # keep track of position in file

    if stored > (1024**3):
        """ Parallelize this code!!!!
        """
        for barcode, entries in demultiplex_dict.items():
            outfile_name = barcode.decode() + "_fastq.gz"
            outfile = openfile(outfile_name, "ab")

            outfile.write(b"\n".join(entries) + b"\n")
            outfile.close()
            stored_counter = 0
            demultiplex_dict = dict()



entry = chunk[prev_index:]

barcode, entry = treat_entry(entry, barcode_dict)

if barcode:
    try:
        demultiplex_dict[barcode].append(entry)
    except:
        demultiplex_dict[barcode] = [entry]


for barcode, entries in demultiplex_dict.items():
    outfile_name = barcode.decode() + "_fastq.gz"
    outfile = openfile(outfile_name, "ab")

    outfile.write(b"\n".join(entries) + b"\n")
    outfile.close()
