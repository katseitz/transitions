#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p normal
#SBATCH -t 48:00:00
#SBATCH --mem=32G
#SBATCH -J fno_fmap

module purge
module load singularity/latest
echo "modules loaded" 
echo "beginning preprocessing"


#WITHOUT FMAP
singularity run --cleanenv -B /projects/b1108:/projects/b1108 \
/projects/b1108/software/singularity_images/fmriprep-23.0.1.simg \
/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids \
/projects/b1108/studies/transitions2/data/processed/neuroimaging/23_fmriprep_nodc participant \
--participant-label ${1} --fs-license-file /projects/b1108/software/freesurfer_license/license.txt \
-w /projects/b1108/studies/transitions2/data/processed/neuroimaging/23_fmriprep_nodc/work --ignore fieldmaps --skip_bids_validation