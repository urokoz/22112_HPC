#!/usr/bin/env python
import gzip
import sys
import time

start_time = time.time()

def kmer_dist(kmer1, kmer2):
    return sum([int(a != b) for a,b in zip(kmer1, kmer2)])


def openfile(filename, mode):
    try:
        if filename.endswith('.gz'):
            fh = gzip.open(filename, mode=mode)
        else:
            fh = open(filename, mode)
    except:
        print("Can't open file:", filename)
    return fh


# check input and extract commandline arguments
if len(sys.argv) != 2:
    sys.exit("Usage: ex12_2.py <input fasta file>")

filename = sys.argv[1]

# open files with byteread
try:
    infile = openfile(filename, "rb")
except IOError as err:
    sys.exit("Cant open file: " + str(err))


person_dict = dict()
for line in infile:
    if line.startswith(b"@"):
        barcode = line.split(b":")[-1].strip()

        try:
            person_dict[barcode] += 1
        except:
            person_dict[barcode] = 1

person_list = sorted(person_dict.items(), key=lambda x: x[1], reverse=True)

count_time = time.time()

for


k_near = dict()
for (key, val) in person_list:



    uniq_flag = True
    for seq in k_near.keys():
        if kmer_dist(key, seq) = 1:
            k_near[seq].append(key)
            uniq_flag = False
            break
    if uniq_flag:
        k_near[key] = []

k_near_time = time.time()

for k,v in sorted(k_near.items(), key=lambda x: len(x[1])):
    print(k,person_dict[k],sep="\t")

print("Number of unique barcodes:", len(k_near.keys()))
print("Barcode count time:", count_time-start_time)
print("K-near time:", k_near_time-count_time)
print("Total time:", k_near_time-start_time)
