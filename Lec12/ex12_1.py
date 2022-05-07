import hashlib
import timeit
import sys
import numpy as np


def sha1(s):
    return int.from_bytes(hashlib.sha1(s).digest(), byteorder=sys.byteorder)

def sha224(s):
    return int.from_bytes(hashlib.sha1(s).digest(), byteorder=sys.byteorder)

def sha256(s):
    return int.from_bytes(hashlib.sha256(s).digest(), byteorder=sys.byteorder)

def sha512(s):
    return int.from_bytes(hashlib.sha512(s).digest(), byteorder=sys.byteorder)

def try_hash(s):
    return (hash((s,0)), hash((s,1)), hash((s,2)), hash((s,3)))


n_est = 3139742750
p = 0.01

# Calculate size of bloom filter
m = np.ceil((-n_elem*np.log(p))/(np.log(2)**2))
# round m up to the nearest power of 2
m_bit_size = int(np.ceil(np.log2(m)))
m_bits = 2**m_bit_size
m_bytes = int(m_bits/8)

# calculate how many hash funcions and actual p
k = int(np.ceil(-np.log(p)/np.log(2)))
p_test = (1-np.exp(-k*n_elem/m_bits))**k

# reduce amount of hash functions if possible
if p_test < p:
    while True:
        k_test = k-1
        p_test = (1-np.exp(-k_test*n_elem/m_bits))**k_test

        if p_test < p:
            k = k_test
        else:
            break


print("Blooms filter parameters:")                  # human.fsa
print("k:", k)                                      # 4
print("p_true:", (1-np.exp(-k*n_est/m_bits))**k)    # 0.008786074069311768
print("m_bit_size:", m_bit_size)                    # 35
print("bits per filter:", m_bits)                   # 34359738368
print("bytes per filter:", m_bytes)                 # 4294967296

# Since the number of bits needed to represent the number of bit is 35 and we
# need 4 hash functions we can do that by using a hash function with at least
# 140 bits and taking 4x35 non overlapping bits.

t1 = timeit.Timer("sha1(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha1")
t224 = timeit.Timer("sha224(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha224")
t256 = timeit.Timer("sha256(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha256")
t512 = timeit.Timer("sha512(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha512")
thash = timeit.Timer("try_hash(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import try_hash")

print("sha1:", t1.timeit(number=1000000))           # 0.9794068000010157
print("sha224:", t224.timeit(number=1000000))       # 0.9812292000024172
print("sha256:", t256.timeit(number=1000000))       # 1.047936999999365
print("sha512:", t512.timeit(number=1000000))       # 1.1865009000030113
print("hash:", thash.timeit(number=1000000))        # 0.26603309999700286

# After testing sha1, sha224, sha256, sha512 and the built in hash() I found that
# running the hash() function yielding 64 bits per function was the fastest.
