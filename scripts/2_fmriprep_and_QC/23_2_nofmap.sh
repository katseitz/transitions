#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p normal
#SBATCH -t 16:00:00
#SBATCH --array=0-9%10
#SBATCH --job-name="fmriprep_tran_\${SLURM_ARRAY_TASK_ID}"
#SBATCH --output=fmriprep.%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=12G

module purge
module load singularity/latest
echo "modules loaded" 
echo "beginning preprocessing"

IFS=$'\n' read -d '' -r -a input_args < list_subs.txt

#WITHOUT FMAP
singularity run --cleanenv -B /projects/b1108:/projects/b1108 \
-B /projects/b1108/studies/transitions2/data/processed/neuroimaging/ses-1_v23_2_0_nofmap:/out \
-B /projects/b1108/studies/transitions2/data/raw/neuroimaging/bids:/data \
-B /projects/b1108/studies/transitions2/data/processed/neuroimaging/ses-1_v23_2_0_nofmap/work:/work \
/projects/b1108/software/singularity_images/fmriprep_23.2.0.sif \
/data /out participant --nthreads 4 --omp-nthreads 3 --mem_mb 30000 \
--participant-label ${input_args[$SLURM_ARRAY_TASK_ID]} --bids-filter-file bids_filter_file_ses-1.json \
--fs-license-file /projects/b1108/software/freesurfer_license/license.txt \
--output-spaces MNI152NLin6Asym \
-w /work --ignore fieldmaps --skip_bids_validation