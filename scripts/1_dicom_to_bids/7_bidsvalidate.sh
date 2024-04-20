#!/bin/bash
#SBATCH --account=p31833                                  ## YOUR ACCOUNT pXXXX or bXXXX
#SBATCH --partition=normal                                ## PARTITION (buyin, short, normal, w10001, etc)
#SBATCH --array=1                                         ## number of jobs to run "in parallel"
#SBATCH --nodes=1                                         ## how many computers do you need
#SBATCH --ntasks-per-node=1                               ## how many cpus or processors do you need on each computer
#SBATCH --time=00:30:00                                   ## how long does this need to run (remember different partitions have restrictions on this param)
#SBATCH --mem-per-cpu=1G                                 ## how much RAM do you need per CPU (this effects your FairShare score so be careful to not ask for more than you need))
#SBATCH --job-name="validate bids"                        ## use the task id in the name of the job
#SBATCH --mail-type=FAIL                                  ## you can receive e-mail alerts from SLURM when your job begins and when your job finishes (completed, failed, etc)
#SBATCH --mail-user=katharina.seitz@northwestern.edu    ## your email

module load singularity/latest

singularity exec --writable-tmpfs --cleanenv \
  -B /projects/b1108/studies/TEAM/data/raw/neuroimaging/bids \
  /projects/b1108/software/singularity_images/validator_v1.9.3.sif \
  bids-validator /projects/b1108/studies/TEAM/data/raw/neuroimaging/bids \
  --verbose
  
