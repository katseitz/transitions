#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p normal
#SBATCH -t 1:00:00
#SBATCH --mem=3G
#SBATCH -J tran_1


DIR=$1 #check if $ needed. 
echo $DIR
SUB=$2
echo $SUB
#Pipeline calls, one after another. 
source /projects/b1108/studies/transitions2/scripts/1_dicom_to_bids/1_dic_to_nifti.sh $DIR $SUB 
python 2_nifti_to_bids_naming.py $SUB
source 3_deface.sh $SUB



