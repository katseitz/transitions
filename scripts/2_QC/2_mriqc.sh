#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p short
#SBATCH -t 04:00:00
#SBATCH --mem=20G
#SBATCH -J qc-tran
#SBATCH	--mail-type=END,FAIL
#SBATCH	--mail-user=katharinaseitz@northwestern.edu

SUB=$1
SES=$2

module purge
module load singularity/latest
echo "modules loaded"
cd /projects/b1108

singularity run --cleanenv -B /projects/b1108:/projects/b1108/ \
/projects/b1108/software/singularity_images/kat_test/mriqc-23.0.1.simg \
-v /projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/ \
-v /projects/b1108/studies/transitions2/data/processed/neuroimaging/mriqc/$SUB/ \
participant --participant-label ${1} 

