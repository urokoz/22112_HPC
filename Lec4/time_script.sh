#!/bin/bash

echo "For loop cp:"
rm ./human_cp.fsa
time python for_loop_file_cp.py
echo ""

echo "while loop cp:"
rm ./human_cp.fsa
time python while_loop_file_cp.py
echo ""

echo "Binary loop cp:"
rm ./human_cp.fsa
time python binary_for_loop_file_cp.py
echo ""

echo "Chunk loop cp:"
rm ./human_cp.fsa
time python chunk_while_loop_file_cp.py
echo ""

echo "UNIX cp:"
rm ./human_cp.fsa
time cp /home/projects/pr_course/human.fsa ./human_cp.fsa
echo ""

rm ./human_cp.fsa
