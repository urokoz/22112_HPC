import hashlib
import timeit
import sys


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



t1 = timeit.Timer("sha1(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha1")
t224 = timeit.Timer("sha224(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha224")
t256 = timeit.Timer("sha256(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha256")
t512 = timeit.Timer("sha512(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import sha512")
thash = timeit.Timer("try_hash(b'cgtaacgcgccgtaacgcgccgtaacgcgc')", "from __main__ import try_hash")

print(t1.timeit(number=1000000))
print(t224.timeit(number=1000000))
print(t256.timeit(number=1000000))
print(t512.timeit(number=1000000))
print(thash.timeit(number=1000000))
