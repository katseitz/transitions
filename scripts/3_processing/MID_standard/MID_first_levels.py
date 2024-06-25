### This script conducts the post-processing steps after fmriprep for rest
###
### kat seitz
### January - April 2024

# Python version: 3.8.4
import os
import json
import glob
import pandas as pd #1.0.5
import nibabel as nib #3.2.1
import numpy as np
import csv
import matplotlib.pyplot as plt

from nilearn.datasets import load_mni152_brain_mask
from nilearn.input_data import NiftiLabelsMasker #0.8.1
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.image import concat_imgs, mean_img, resample_img
from nilearn.plotting import plot_design_matrix
from nilearn import plotting
from nilearn import signal
from nilearn import image
from nilearn.interfaces.bids import save_glm_to_bids
import scipy.signal as sgnl #1.5.4
#from get_qual_metrics import get_qual_metrics

ANT_REW = 1 #1 for anticipation, 0 for reward
events_base = '/projects/b1108/studies/transitions/data/raw/neuroimaging/bids/'

def mid_fl(sub, ses, funcindir, sesoutdir):
    tr_list = []
    flist = os.listdir(funcindir)
    i = 1
    while(i <= len(glob.glob(funcindir + "*_ses-1_task-mid_run-*_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"))):
        print("working on run 0" + str(i) + " for participant " + sub)
        
        #### READ IN FILES
        #Load in MID file, and mask
        file_mid = os.path.join(funcindir, [x for x in flist if ('preproc_bold.nii.gz' in x and 'task-mid_run-0' + str(i) in x)][0])
        mid_img = nib.load(file_mid)
        #file_mid_mask = os.path.join(funcindir, [x for x in flist if ('brain_mask.nii.gz' in x and 'task-mid_run-0' + str(i) in x)][0])
        #mid_mask_img = nib.load(file_mid_mask)
        mid_mask_img = load_mni152_brain_mask(resolution=None, threshold=0.2)
        # Load confounds for MID and read in as pandas df
        confounds_mid_path = os.path.join(funcindir, [x for x in flist if ('task-mid_run-0' + str(i) + '_desc-confounds_timeseries.tsv' in x)][0])
        confounds_mid_df = pd.read_csv(confounds_mid_path, sep='\t')
        # Load parameters for MID #TODO change out ses
        param_mid_file = open(os.path.join(funcindir, sub+'_ses-1_task-mid_run-0' + str(i) + '_space-MNI152NLin2009cAsym_desc-preproc_bold.json'),)
        param_mid_df = json.load(param_mid_file)
        # Get TRs
        tr = param_mid_df['RepetitionTime']
        #Load events file
        events = pd.read_csv(events_base + sub + '/ses-1/func/' + sub + '_ses-1_task-mid_run-0'+ str(i) + '_events.tsv', sep='\t')
        #collapse trials into win/lose groups
        if(ANT_REW):
            substring = "rew"
            filter = events['trial_type'].str.contains(substring)
            events = events[~filter]
            events.replace("ant_win_5", "ant_win_5or15", inplace=True) #merge 1.5 5 groups
            events.replace("ant_win_1.5", "ant_win_5or15", inplace=True)
            events.replace("ant_lose_5", "ant_lose_5or15", inplace=True)
            events.replace("ant_lose_1.5", "ant_lose_5or15", inplace=True)
        else:
            substring = "ant"
            filter = events['trial_type'].str.contains(substring)
            events = events[~filter]
            events.replace("rew_win_5_Hit", "rew_win_5or1.5_Hit", inplace=True) #merge 1.5 5 groups
            events.replace("rew_win_1.5_Hit", "rew_win_5or1.5_Hit", inplace=True)
            events.replace("rew_win_5_Miss", "rew_win_5or1.5_Miss", inplace=True)
            events.replace("rew_lose_1.5_Miss", "rew_lose_5or1.5_Miss", inplace=True)
            events.replace("rew_lose_5_Hit", "rew_lose_5or1.5_Hit", inplace=True) 
            events.replace("rew_lose_1.5_Hit", "rew_lose_5or1.5_Hit", inplace=True)
            events.replace("rew_lose_5_Miss", "rew_lose_5or1.5_Miss", inplace=True)
            events.replace("rew_lose_1.5_Miss", "rew_lose_5or1.5_Miss", inplace=True)

        #### MANAGE CONFOUNDS AND MOTION
        # https://www.sciencedirect.com/science/article/pii/S1053811919306822
        confound_vars = ['trans_x','trans_y','trans_z', 'rot_x','rot_y','rot_z', 'global_signal'] # TODO change csf and whitematter 
        deriv_vars = ['{}_derivative1'.format(c) for c in confound_vars]
        final_confounds = confound_vars  + deriv_vars
        confounds_mid_df = confounds_mid_df.fillna(0)

        # Add nuisance regressors for high motion TRs
        regressed_TR = set() #heheh lookups are o(1)
        num_TRs = len(confounds_mid_df) #get number of frames
        counter = 0
        for index in confounds_mid_df.index:
            # https://doi.org/10.1002/hbm.22307 for fd decision
            if confounds_mid_df['framewise_displacement'][index] > .5: #where fd is defined
                col_name = 'motion_' + str(counter)
                final_confounds.append(col_name)
                new_reg = [0] * num_TRs
                new_reg[counter] = 1 #the high motion TR
                regressed_TR.add(counter)
                confounds_mid_df[col_name] = new_reg  #add a new confound column for the high motion TR
            counter = counter + 1
        print(sub + " total: " + str(num_TRs))
        print(sub + " regressed: " + str(len(regressed_TR)))
        tr_list.append([sub, ses, str(num_TRs), len(regressed_TR)])

        ##### Temporal bandpass filtering + Nuisance regression
        mid_band = image.clean_img(mid_img, detrend=False, standardize=False, t_r=tr,
                                confounds=confounds_mid_df[final_confounds],
                                low_pass=0.08, high_pass=0.009)
        
        mid_band.to_filename(sesoutdir+'/'+sub+'_'+ses+'_task-MID_run-0' + str(i) + '_final.nii.gz')
        
        #### Define First Level Model 
        mid_model = FirstLevelModel(tr,
                            mask_img=mid_mask_img,
                            standardize=False, 
                            hrf_model='spm', # 
                            smoothing_fwhm=4) 
         
        #### Fit First Level Model with Given Participant and for each contrast
        print("Fitting a GLM")
        mid_model = mid_model.fit(mid_band, events)
        contrasts = []
        if(ANT_REW):
            contrasts = ["ant_win_5or15 - ant_win_0",
                            "ant_lose_5or15 - ant_lose_0",
                            "ant_win_5or15 - ant_lose_5or15"]
        else:
            contrasts = ["ant_win_5or15 - ant_win_0",
                         "ant_lose_5or15 - ant_lose_0",
                         "ant_win_5or15 - ant_lose_5or15"]
        #generate contrasts and save   
        for contrast in contrasts:
            mid_t_map = mid_model.compute_contrast((contrast), output_type="stat")
            contrast_name = contrast.replace(" - ", "_vs_").replace(".", "")
            mid_t_map.to_filename(sesoutdir + '/' + sub + '_'+ses+'_task-mid_run-0' + str(i) + '_' + contrast_name + '_tmap.nii.gz')
        
        # plot the contrasts as soon as they're generated
        # the display is overlaid on the mean fMRI image
        # a threshold of 3.0 is used, more sophisticated choices are possible
       
        '''
        mean_image = mean_img(mid_img)
        plotting.plot_stat_map(
            mid_t_map,
            bg_img=mean_image,
            threshold=2.0,
            display_mode="z", #this is the plane it is displayed on.
            cut_coords=3,
            black_bg=True,
            title="test",
        )
        plotting.show()
        ''' 
        i = i + 1
    return tr_list
        

def main():
    ses = "ses-1" #bids ses-1
    indir = '/projects/b1108/studies/transitions/data/preprocessed/neuroimaging/fmriprep_23_2_0_nofmap/'
    outdir = '/projects/b1108/studies/transitions/data/processed/neuroimaging/MID_processing_nofmap/'
    subject = os.scandir(indir)
    tr_counts = [["ID", "run", "original_shape", "cleaned_shape"]]
    
    for sub in subject:
        if("sub-" in sub.name and not(".html" in sub.name)):
            print(sub.name)
            funcindir = indir + sub.name + '/' + ses + '/func/' 
            sesoutdir = outdir + sub.name + '/' + ses + '/'
            #if they have a single MID run
            preproc_rest = os.path.join(funcindir, sub.name +'_'+ses+'_task-mid_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
            if(os.path.exists(preproc_rest)):
                os.makedirs(os.path.join(outdir, sub.name, ses), exist_ok=True)
                try:
                    sub_counts = mid_fl(sub.name, ses, funcindir, sesoutdir)
                    tr_counts.append(sub_counts[0])
                    tr_counts.append(sub_counts[1])
                except Exception as e:
                    print(e)
                    print(sub.name + " failed :( ")
    '''
    sub = "sub-t1040"
    funcindir = 'sub-t1040/ses-1/func/' 
    sesoutdir = outdir + sub + '/' + ses + '/'
    #sub-t1001_ses-1_task-mid_run-02_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
    #if(os.path.exists(os.path.join(funcindir, sub +'_'+ses+'_task-mid_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))):
    print("here")
    os.makedirs(os.path.join(outdir, sub, ses), exist_ok=True)
    sub_counts = mid_fl(sub, ses, funcindir, sesoutdir)
    tr_counts.append(sub_counts)
    '''
    with open('transitions_MID_TRs.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for row in tr_counts:
            wr.writerow(row)
    
            
main()