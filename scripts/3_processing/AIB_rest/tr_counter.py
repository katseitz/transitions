### This script conducts the post-processing steps after fmriprep for rest
###
### kat
### January 2024

# Python version: 3.8.4
import os
import json
import glob
import pandas as pd #1.0.5
import nibabel as nib #3.2.1
import numpy as np

#from get_qual_metrics import get_qual_metrics


def main():
    ses = "ses-1" #bids ses-1
    outdir = '/projects/b1108/studies/transitions2/data/processed/neuroimaging/MID_processing/'
    subject_files = glob.glob(outdir + '*/*/*')
    tr_counts = [["ID", "run", "cleaned_shape"]]

    for sub_file in subject_files:
        ID = sub_file.split("/")[-1][0:9]
        run = sub_file.split("/")[-1][26:32]
        rest_img = nib.load(sub_file)
        print(ID, run, rest_img.shape)
                    
                    
                    
            
main()