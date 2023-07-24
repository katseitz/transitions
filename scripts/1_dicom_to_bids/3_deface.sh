#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p short
#SBATCH -t 00:10:00
#SBATCH --mem=1G
#SBATCH -J t_deface

SUB=$1 #check if $ needed. 
echo $SUB
SES=$2 #check if $ needed. 
echo $SES

module purge
module load fsl

pydeface /projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB/ses-1/anat/sub-${SUB}_${SES}_run-1_T1w.nii.gz
mv /projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB/ses-1/anat/sub-${SUB}_${SES}_run-1_T1w_defaced.nii.gz \
/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB/ses-1/anat/sub-${SUB}_${SES}_run-1_T1w.nii.gz