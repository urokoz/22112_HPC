#!/usr/bin/env python
import sys
import subprocess

def submit(command, runtime, cores, ram, directory='', modules='', group='pr_course',
    jobscript='jobscript', output='/dev/null', error='/dev/null'):
    """
    Function to submit a job to the Queueing System - with jobscript file
    Parameters are:
    command:   The command/program you want executed together with any parameters.
               Must use full path unless the directory is given and program is there.
    directory: Working directory - where should your program run, place of your data.
               If not specified, uses current directory.
    modules:   String of space separated modules needed for the run.
    runtime:   Time in minutes set aside for execution of the job.
    cores:     How many cores are used for the job.
    ram:       How much memory in GB is used for the job.
    group:     Accounting - which group pays for the compute.
    jobscript: Standard name for the jobscript that needs to be made.
               You should number your jobscripts if you submit more than one.
    output:    Output file of your job.
    error:     Error file of your job.
    """
    runtime = int(runtime)
    cores = int(cores)
    ram = int(ram)
    if cores > 10:
        print("Can't use more than 10 cores on a node")
        sys.exit(1)
    if ram > 120:
        print("Can't use more than 120 GB on a node")
        sys.exit(1)
    if runtime < 1:
        print("Must allocate at least 1 minute runtime")
        sys.exit(1)
    minutes = runtime % 60
    hours = int(runtime/60)
    walltime = "{:d}:{:02d}:00".format(hours, minutes)
    if directory == '':
        directory = os.getcwd()
    # Making a jobscript
    script = '#!/bin/sh\n'
    script += '#PBS -A ' + group + ' -W group_list=' + group + '\n'
    script += '#PBS -e ' + error + ' -o ' + output + '\n'
    script += '#PBS -d ' + directory + '\n'
    script += '#PBS -l nodes=1:ppn=' + str(cores) + ',mem=' + str(ram) + 'GB' + '\n'
    script += '#PBS -l walltime=' + walltime + '\n'
    if modules != '':
        script += 'module load ' + modules + '\n'
    script += command + '\n'
    if not jobscript.startswith('/'):
        jobscript = directory + '/' + jobscript
    with open(jobscript, 'wt') as jobfile:
        jobfile.write(script)
    # The submit
    job = subprocess.run(['qsub', jobscript],stdout=subprocess.PIPE, universal_newlines=True)
    jobid = job.stdout.split('.')[0]
    return jobid


def unix_call(command):
    job = subprocess.run(command.split())


if len(sys.argv) != 3:
    sys.exit("Usage: admin_prog.py <input fasta file> <work dir>")

try:
    infile = open(sys.argv[1], "rb")
except IOError as err:
    sys.exit("Cant open file:" + str(err))

work_dir = sys.argv[2]

seq_list = []
index = 0
# run through the file line-by-line
for line in infile:
    line = line.strip()
    # If a header is seen
    if line.startswith(b">"):
        # Write the header, counts and complement gene to the outfile and reset
        if len(seq_list) > 0:
            # Name temporary files
            outfile_name = work_dir + "to_comp/to_complement{:04d}.fsa".format(index)
            comp_file_name = work_dir + "comped/comp{:04d}.fsa".format(index)
            # Open output file and write a single fasta sequence
            try:
                outfile = open(outfile_name, "wb")
            except IOError as err:
                sys.exit("Cant open file: " + str(err))

            outfile.write(b"\n".join(seq_list))
            outfile.close()
            seq_list = []

            # Queue job
            submit(work_dir + "rev_comp_worker.py {} {}".format(outfile_name, comp_file_name),
                    runtime = 30, cores=1, ram=10, directory=work_dir,
                    modules="tools anaconda3/4.0.0", group='pr_course',
                    jobscript='job_{}'.format(index), output='/dev/null', error='/dev/null')

            index += 1

        seq_list.append(line)
    else:
        seq_list.append(line)
infile.close()

if len(seq_list) > 0:
    # Name temporary files
    outfile_name = "to_comp/to_complement{:04d}.fsa".format(index)
    comp_file_name = "comped/comp{:04d}.fsa".format(index)
    # Open output file and write a single fasta sequence
    try:
        outfile = open(outfile_name, "wb")
    except IOError as err:
        sys.exit("Cant open file: " + str(err))

    outfile.write(b"\n".join(seq_list))
    outfile.close()
    seq_list = []

    # Queue job
    submit(work_dir + "rev_comp_worker.py {} {}".format(outfile_name, comp_file_name),
            runtime = 30, cores=1, ram=10, directory=work_dir,
            modules="tools anaconda3/4.0.0", group='pr_course',
            jobscript='job_{}'.format(index), output='/dev/null', error='/dev/null')
