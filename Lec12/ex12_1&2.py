#!/usr/bin/env python
import sys
import os
import time
import numpy as np
import hashlib

n_est = 3139742750
p = 0.01

m = np.ceil((-n_est*np.log(p))/(np.log(2)**2))
m_bits = int(np.ceil(np.log2(m)))
print("m_bits:", m_bits)
m_true = 2**m_bits

k = int(np.ceil(-np.log(p)/np.log(2)))

print("k:", k)


p_test = (1-np.exp(-k*n_est/m_true))**k

print("p_test:", p_test)

if p_test < p:
    while True:
        k_test = k-1

        p_test = (1-np.exp(-k_test*n_est/m_true))**k_test

        if p_test < p:
            k = k_test
        else:
            break

print("k:", k)
print("p_true:", (1-np.exp(-k*n_est/m_true))**k)

print("bytes per filter:", m_true/8)

#
# # check input and extract commandline arguments
# if len(sys.argv) != 2:
#     sys.exit("Usage: ex11_2.py <input fasta file>")
#
# # open files with byteread
# try:
#     infile = open(sys.argv[1], "rb")
# except IOError as err:
#     sys.exit("Cant open file: " + str(err))
