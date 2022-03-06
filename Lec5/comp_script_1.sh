#!/bin/sh
#PBS -W group_list=pr_course -A pr_course
#PBS -l nodes=1:ppn=1,mem=10GB,walltime=00:30:00
### Below line eliminates annoying STDIN files, but use only when program works
#PBS -e /dev/null -o /dev/null
### Send mail (or not)
#PBS –m ae –M s183447@dtu.dk
load module python36
/home/projects/pr_course/people/matbor/complement_1.py
