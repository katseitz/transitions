#!/bin/bash
#SBATCH --account=p31833
#SBATCH --partition=long
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=40GB
#SBATCH --job-name="MIDfirstlevel" 
#SBATCH --time=70:00:00
#SBATCH --mail-user=katharina.seitz@northwestern.edu 

python MID_first_levels.py