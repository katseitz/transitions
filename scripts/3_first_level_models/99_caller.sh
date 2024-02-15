#!/bin/bash
#SBATCH --account=p31833
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=15GB
#SBATCH --job-name="MIDfirstlevel" 
#SBATCH --time=24:00:00
#SBATCH --mail-user=katharina.seitz@northwestern.edu 

python MID_first_levels.py