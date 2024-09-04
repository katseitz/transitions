#!/bin/bash
#SBATCH --account=p31833
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=5GB
#SBATCH --job-name="MIDfirstlevel" 
#SBATCH --time=4:00:00
#SBATCH --mail-user=katharina.seitz@northwestern.edu 

python MID_fl_copy.py