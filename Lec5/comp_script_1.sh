#!/bin/sh
#PBS -W group_list=pr_course -A pr_course
#PBS -l nodes=1:ppn=1,mem=10GB,walltime=00:30:00
### Below line eliminates annoying STDIN files, but use only when program works
#PBS -e /dev/null -o /dev/null
### Send mail (or not)
#PBS –m ae –M s183447@dtu.dk
load module python36
/home/projects/pr_course/people/matbor/complement_1.py  # or the other files

### TEST SCORES:
### $ time python complement_1.py
### real	0m0,344s
### user	0m0,343s
### sys	0m0,000s
### $ time python complement_2.py
### real	0m0,452s
### user	0m0,434s
### sys	0m0,017s
### $ time python complement_3.py
### real	0m0,176s
### user	0m0,131s
### sys	0m0,016s
