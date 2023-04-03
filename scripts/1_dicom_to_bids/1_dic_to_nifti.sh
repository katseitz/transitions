#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p short
#SBATCH -t 1:00:00
#SBATCH --mem=1G
#SBATCH -J t_nifti

module purge
module load dcm2niix

DIR=$1 #check if $ needed. 
echo $DIR
SUB=$2
echo $SUB

scan_folders=/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/$DIR/*/* 
echo $scan_folders

if [ ! -d "/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB" ]; then
    mkdir /projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB
fi
if [ ! -d "/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB/ses-1" ]; then
    mkdir /projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB/ses-1     
fi

for SCAN in $scan_folders; do # Whitespace-safe but not recursive.
    echo $SCAN
    OUTPUT=/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/sub-$SUB/ses-1
    echo $OUTPUT
    dcm2niix -b y -z o -w 1 -f %n--%d--s%s--e%e -o $OUTPUT $SCAN
done

#Error: Unknown command line argument: '-b,'
# Error: invalid option '-o (null)'
