#!/bin/sh
#PBS -A pr_course -W group_list=pr_course
#PBS -e /dev/null -o /dev/null
#PBS -d /home/projects/pr_course/people/matbor/lec13/
#PBS -l nodes=1:ppn=10,mem=20GB
#PBS -l walltime=4:00:00
module load tools anaconda3/2021.11
/home/projects/pr_course/people/matbor/lec13/ex_1.py /home/projects/pr_course/ngs1.fastq.gz > /home/projects/pr_course/people/matbor/lec13/barcode_count.tab 2>> /home/projects/pr_course/people/matbor/lec13/log.txt
/home/projects/pr_course/people/matbor/lec13/ex_1_2.py /home/projects/pr_course/people/matbor/lec13/barcode_count.tab > /home/projects/pr_course/people/matbor/lec13/barcode_lookup.tab 2>> /home/projects/pr_course/people/matbor/lec13/log.txt
/home/projects/pr_course/people/matbor/lec13/ex_2.py /home/projects/pr_course/ngs1.fastq.gz /home/projects/pr_course/people/matbor/lec13/barcode_lookup.tab /home/projects/pr_course/people/matbor/lec13/demulti/ >> log.txt
