#!/usr/bin/env python
import sys
import os
import time

def num2dna(num, k):
    bi_num = bin(num)[2:]
    bi_num = "0"*(k*2-len(bi_num)) + bi_num
    print(bi_num)

    dna = ""
    for i in range(0, len(bi_num)-1, 2):
        base = bi_num[i:i+2]

        if base == "00":
            dna += "a"
        elif base == "01":
            dna += "c"
        elif base == "10":
            dna += "g"
        elif base == "11":
            dna += "t"

    return dna


input = sys.argv[1]

k = len(input)

print(input)

base4 = bytes.maketrans(b'acgt',b'0123')

kmer = input.translate(base4)

int_dna = int(kmer, base = 4)

print(int_dna)

print(num2dna(int_dna, k))
