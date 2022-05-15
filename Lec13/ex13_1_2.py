#!/usr/bin/env python
import sys
import time

print("# ex13_1_2.py", file=sys.stderr)
start_time = time.time()


def kmer_dist(kmer1, kmer2):
    return sum([int(a != b) for a,b in zip(kmer1, kmer2)])


# check input and extract commandline arguments
if len(sys.argv) != 2:
    sys.exit("Usage: ex13_1_2.py <barcode count file>")

filename = sys.argv[1]

# open files with byteread
try:
    infile = open(filename, "rb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))

# load in list of barcode counts
person_list = []
for line in infile:
    line = line.split()
    person_list.append((line[0],int(line[1])))

load_time = time.time()

# find the split between true and false barcodes (big jump from one count to next)
for i in range(1, len(person_list)):
    if (person_list[i][1]/person_list[i-1][1]) < 0.2:
        true_hits = person_list[:i]

split_time = time.time()

# map close false barcodes to the true hits based on distance.
# also map true hits to self.(important for ex13_2.py)
close_list = []
for (barcode, _) in person_list:
    for (true_barcode, _) in true_hits:
        if kmer_dist(true_barcode, barcode) <= 1:
            close_list.append("{}\t{}".format(barcode.decode(), true_barcode.decode(), sep="\t"))
            break

print("\n".join(close_list))
k_near_time = time.time()

print("# Number of unique barcodes:", len(true_hits), file=sys.stderr)
print("# Load time:", load_time-start_time, file=sys.stderr)
print("# Find split time:", split_time-load_time, file=sys.stderr)
print("# Map close time:", k_near_time-split_time, file=sys.stderr)
print("# Total time:", k_near_time-start_time, file=sys.stderr)
