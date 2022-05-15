#!/usr/bin/env python
import sys
import time
import gzip
import joblib as jl

print("# ex13_2.py")
start_time = time.time()


def treat_entry(entry, close_dict):
    """ Exchange close false barcodes with true barcodes and keep true barcodes
        as they are mapped to themselves anyway.
        If no barcode is associated with the barcode for the entry, then the
        barcode in the entry is a false one that is not close to the true ones.
    """
    # split up entry
    idx = entry.find(b"\n")
    header = entry[:idx-8]
    barcode = entry[idx-8:idx]
    body = entry[idx:]

    # find if barcode is true or mapped to a true barcode
    correct_barcode = close_dict.get(barcode)

    if correct_barcode:
        entry = header + correct_barcode + body
        return (correct_barcode, entry.strip())
    else:
        return False, False


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


def write_demultiplexed(barcode, entries, out_dir):
    """ Add a number of entries associated to a barcode to a file for that
        barcode.
    """
    outfile_name = out_dir + barcode.decode() + "_fastq.gz"
    outfile = openfile(outfile_name, "ab")
    outfile.write(b"\n".join(entries) + b"\n")
    outfile.close()


# check input and extract commandline arguments
if len(sys.argv) != 4:
    sys.exit("Usage: ex13_2.py <input fasta file> <barcode lookup file> <output dir>")

filename = sys.argv[1]
barcode_file = sys.argv[2]
out_dir = sys.argv[3]

# open files with byteread
try:
    infile = openfile(filename, "rb")

    # load in dict of mapped barcodes
    barcode_dict = dict()
    with open(barcode_file, "rb") as f:
        for line in f:
            line = line.split()
            barcode_dict[line[0]] = line[1]
except IOError as err:
    sys.exit("Cant open file: " + str(err))

setup_time = time.time()

index_time = 0
write_time = 0
index_start_time = time.time()

# initiate flags and position in file
demultiplex_dict = dict()
stored = 0
rest = b""
first_flag = True
chunk_size = 1024*1024
bytes_demultiplexed = 0
n_entries = 0
n_true_entries = 0
while True:

    chunk = rest + infile.read(chunk_size) # read chunk
    rest = b""
    index = 0

    while True:     # seek through end of chunk
        # look for the start of a header
        prev_index = index
        index = chunk.find(b"@", prev_index+1)
        if index == -1:     # header not found
            rest = chunk[prev_index:]   # handle splits in middle of entry
            break
        else:
            # extract entries from file and prepare for demultiplexing
            entry = chunk[prev_index:index]

            barcode, entry = treat_entry(entry, barcode_dict)
            n_entries += 1
            if barcode:
                n_true_entries += 1
                try:
                    demultiplex_dict[barcode].append(entry)
                except:
                    demultiplex_dict[barcode] = [entry]


    if len(chunk) < chunk_size:
        break

    stored += chunk_size      # keep track of position in file

    # if stored data takes up much space write to files
    if stored > (1024**3):
        index_time += time.time()-index_start_time
        write_start_time = time.time()

        # write entries demultiplexed using paralellization using load balancing
        jl.Parallel(n_jobs=8)(jl.delayed(write_demultiplexed)(barcode, \
            entries, out_dir) for barcode, entries in sorted(demultiplex_dict.items(), key=lambda x: len(x[1]), reverse=True))

        # reset
        demultiplex_dict = dict()
        bytes_demultiplexed += stored
        print("# Bytes demultiplexed:", bytes_demultiplexed)
        stored = 0

        write_time += time.time()-write_start_time
        index_start_time = time.time()

infile.close()


# extract last entry from file and prepare for demultiplexing
entry = chunk[prev_index:]
barcode, entry = treat_entry(entry, barcode_dict)
if barcode:
    try:
        demultiplex_dict[barcode].append(entry)
    except:
        demultiplex_dict[barcode] = [entry]


index_time += time.time()-index_start_time
write_start_time = time.time()

# write entries demultiplexed using paralellization using load balancing
jl.Parallel(n_jobs=8)(jl.delayed(write_demultiplexed)(barcode, \
    entries, out_dir) for barcode, entries in sorted(demultiplex_dict.items(), key=lambda x: len(x[1]), reverse=True))

bytes_demultiplexed += stored
print("# Bytes demultiplexed:", bytes_demultiplexed)

write_time += time.time()-write_start_time

print()
print("# Demultiplexed files can be found in folder:")
print("#", out_dir)
print()
print("# Setup time:", setup_time-start_time)
print("# Indexing time:", index_time)
print("# Writing time:", write_time)
print("# Total time:", time.time()-start_time)
print()
print("# Demultiplexed {}/{} entries".format(n_true_entries, n_entries))
