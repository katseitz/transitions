#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p normal
#SBATCH -t 16:00:00
#SBATCH --array=1%10
#SBATCH --job-name="fmriprep_tran_\${SLURM_ARRAY_TASK_ID}"
#SBATCH --output=fmriprep.%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=12G

module purge
module load singularity/latest
echo "modules loaded" 
echo "beginning preprocessing"

export SINGULARITYENV_TEMPLATEFLOW_HOME=/projects/b1108/templateflow

IFS=$'\n' read -d '' -r -a input_args < list_subs.txt

#WITHOUT FMAP
singularity run --cleanenv --containall -B /projects/b1108:/projects/b1108 \
-B /projects/b1108/studies/transitions/data/preprocessed/neuroimaging:/base \
-B /projects/b1108/studies/transitions/scripts/2_fmriprep_and_QC:/scripts \
-B /projects/b1108/studies/transitions/data/preprocessed/neuroimaging/fmriprep_23_2_0_nofmap:/out \
-B /projects/b1108/studies/transitions/data/raw/neuroimaging/bids:/data \
-B /projects/b1108/templateflow:/projects/b1108/templateflow \
/projects/b1108/software/singularity_images/fmriprep_23.2.0.sif \
/data /out participant --nthreads 4 --omp-nthreads 3 --mem_mb 30000 \
--participant-label ${input_args[$SLURM_ARRAY_TASK_ID]} --bids-filter-file /scripts/bids_filter_file_ses-1.json \
--fs-license-file /projects/b1108/software/freesurfer_license/license.txt \
--fs-subjects-dir /base/freesurfer_23_2 \
--output-spaces MNI152NLin6Asym MNI152NLin2009cAsym\
-w /base/work  --ignore fieldmaps --skip_bids_validation