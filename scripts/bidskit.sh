#!/bin/bash
#SBATCH --account=p31833 ## Required: your allocation/account name, i.e. eXXXX, pXXXX or bXXXX
#SBATCH --partition=normal ## Required: (buyin, short, normal, long, gengpu, genhimem, etc)
#SBATCH --time=2:00:00 ## Required: How long will the job need to run (remember different partitions have restrictions on this parameter)
#SBATCH --nodes=1 ## how many computers/nodes do you need (no default)
#SBATCH --ntasks-per-node=1 ## how many cpus or processors do you need on per computer/node (default value 1)
#SBATCH --mem=2G ## how much RAM do you need per computer/node (this affects your FairShare score so be careful to not ask for more than you need))
#SBATCH --job-name=transitions_bidskit ## When you run squeue -u  this is how you can identify the job

# A regular comment in Bash

module load dcm2niix
bidskit -d /projects/b1108/studies/transitions/data/raw/neuroimaging/bids
