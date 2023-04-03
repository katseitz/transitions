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
#insert logic here --> might be PID/PID for dir or PID/e***
source 1_dic_to_nifit.sh $DIR $SUB

python 2_nifti_to_bids_naming.py $SUB

source 3_deface.sh $SUB



