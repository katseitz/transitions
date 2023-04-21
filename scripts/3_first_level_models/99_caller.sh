#!/bin/bash
#SBATCH --account=p31833
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=1GB
#SBATCH --time=1:00:00

module purge
#activates nilearn conda env
eval "$(conda shell.bash hook)"
conda activate /home/sir8526/.conda/envs/nilearn
python 1_smoothing.py