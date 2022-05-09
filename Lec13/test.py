#!/usr/bin/env python3
# encoding: utf-8
##  w  w w.  de m  o2s  .  c om
#
"""
"""

import gzip

with gzip.open('../data/ngs1test.fastq.gz', 'rb') as input_file:
    print('Entire file:')
    all_data = input_file.read()

    expected = all_data[5:105]

    # rewind to beginning
    input_file.seek(0)

    # move ahead 5 bytes
    input_file.seek(5)
    print('Starting at position 5 for 10 bytes:')
    partial = input_file.read(100)
    print(partial)

    print()
    print(expected == partial)
