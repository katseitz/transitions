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
from nilearn.glm.first_level import FirstLevelModel
from nilearn.input_data import NiftiLabelsMasker
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.image import concat_imgs, mean_img, resample_img
from nilearn import image
from nilearn.image import resample_to_img
from nilearn.interfaces.bids import save_glm_to_bids
import scipy.signal as sgnl #1.5.4
#from get_qual_metrics import get_qual_metrics


affine = [[2.5, 0. , 0. , -76. ],
        [0. , 2.5, 0. , -112. ],
        [0. , 0. , 2.5, -75.5],
        [0. , 0. , 0. , 1. ]]

def finish_preproc(sub, ses, run, funcindir, sesoutdir):
    """
    Finishes preprocessing, by managing affine differences, 
    accounting for motion and other nuisance regressors, 
    detrending and band pass filtering. 
    
    Also saves preprocessed MID image in output dir. 
    ----------
    sub : str
        Subject ID starting with sub-t*
    ses : str
        ses-1 or ses-2
    run : str
        "1" or "2"
    funcindir : str
        Path to subject's fmriprep/ses/func output directory
    sesoutdir : str
        Path to processed MID folder with sub/ses appended. 
    Returns
    -------
    A list with the subject ID, session, number of TRs in MID run, 
    and number of TRs regressed for motion
    """
    #### READ IN FILES
    flist = os.listdir(funcindir)
    #Load in MID file, and mask
    file_mid = os.path.join(funcindir, [x for x in flist if ('_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz' in x and 'task-mid_run-0' + run in x)][0])
    mid_img = nib.load(file_mid)
    
    #resample MID image so that the affines are the same for all images.
    if(not(mid_img.affine == affine).all()):
        mid_img = resample_img(mid_img, target_affine = affine)
    
    # Load parameters for MID #TODO change out ses
    param_mid_file = open(os.path.join(funcindir, sub+'_ses-1_task-mid_run-0' + run + '_space-MNI152NLin2009cAsym_desc-preproc_bold.json'),)
    param_mid_df = json.load(param_mid_file)
    # Get TRs
    tr = param_mid_df['RepetitionTime']

    
    ##### Temporal bandpass filtering + Nuisance regression
    mid_band = image.clean_img(mid_img, detrend=True, standardize=False, t_r=tr,
                            confounds=None,
                            low_pass=0.08, high_pass=0.009)
    ### Save Output
    mid_band.to_filename(sesoutdir+'/'+sub+'_'+ses+'_task-mid_run-0' + run + '_final.nii.gz')
    return 

def define_confounds(sub, ses, run, funcindir, sesoutdir):
    flist = os.listdir(funcindir)
    
    # Load confounds for MID and read in as pandas df
    confounds_mid_path = os.path.join(funcindir, [x for x in flist if ('task-mid_run-0' + run + '_desc-confounds_timeseries.tsv' in x)][0])
    confounds_mid_df = pd.read_csv(confounds_mid_path, sep='\t')

    #### MANAGE CONFOUNDS AND MOTION
    # https://www.sciencedirect.com/science/article/pii/S1053811919306822
    confound_vars = ['trans_x','trans_y','trans_z', 'rot_x','rot_y','rot_z', 'global_signal']
    deriv_vars = ['{}_derivative1'.format(c) for c in confound_vars]
    final_confounds = confound_vars  + deriv_vars
    confounds_mid_df = confounds_mid_df.fillna(0)

    # Add nuisance regressors for high motion TRs
    regressed_TR = set() 
    num_TRs = len(confounds_mid_df) #get number of volumes
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
    confounds = confounds_mid_df[final_confounds]
    return [[sub, run, str(num_TRs), len(regressed_TR)], confounds]


def first_levels(sub, ses, run, funcindir, sesoutdir, confounds, anticipation=1): 
    """
    Runs first levels for a single subject, session, and run and generates
    MID contrasts for either anticipation or reward. Contrasts are saved to
    output directory. 
    
    Also saves preprocessed MID image in output dir. 
    ----------
    sub : str
        Subject ID starting with sub-t*
    ses : str
        ses-1 or ses-2
    run : str
        "1" or "2"
    funcindir : str
        Path to subject's fmriprep/ses/func output directory
    sesoutdir : str
        Path to processed MID folder with sub/ses appended.
    anticipation : int
        Either be 0 or 1, default is 1 to run anticipation. If any non-zero 
        number is passed in, reward contrasts are run. 
    Returns
    -------
    Nothing
    """
    
    
    #load pre-proc MID image
    mid_final = nib.load(sesoutdir+'/'+sub+'_'+ses+'_task-mid_run-0' + run + '_final.nii.gz')
    
    #load MNI mask
    mni_mask_img = load_mni152_brain_mask(resolution=None, threshold=0.2)
    resampled_mni_mask = resample_to_img(mni_mask_img, mid_final, interpolation="nearest")
    
    # Load parameters for MID #TODO change out ses
    param_mid_file = open(os.path.join(funcindir, sub+'_ses-1_task-mid_run-0' + run + '_space-MNI152NLin2009cAsym_desc-preproc_bold.json'),)
    param_mid_df = json.load(param_mid_file)
    # Get TRs
    tr = param_mid_df['RepetitionTime']
    
    #Load events file
    events_base = '/projects/b1108/studies/transitions/data/raw/neuroimaging/bids/'
    events = pd.read_csv(events_base + sub + '/ses-1/func/' + sub + '_ses-1_task-mid_run-0'+ run + '_events.tsv', sep='\t')
    
    #collapse trials into win/lose groups
    if(anticipation):
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
        events.replace("rew_win_5_Hit", "rew_win_5or15_Hit", inplace=True) #merge 1.5 5 groups
        events.replace("rew_win_1.5_Hit", "rew_win_5or15_Hit", inplace=True)
        events.replace("rew_win_5_Miss", "rew_win_5or15_Miss", inplace=True)
        events.replace("rew_win_1.5_Miss", "rew_win_5or15_Miss", inplace=True)
        events.replace("rew_lose_5_Miss", "rew_lose_5or15_Miss", inplace=True) 
        events.replace("rew_lose_1.5_Miss", "rew_lose_5or15_Miss", inplace=True)
        events.replace("rew_lose_5_Hit", "rew_lose_5or15_Hit", inplace=True) 
        events.replace("rew_lose_1.5_Hit", "rew_lose_5or15_Hit", inplace=True)

    #mid_band = nib.load(sesoutdir+'/'+sub+'_'+ses+'_task-MID_run-0' + run + '_final.nii.gz')
    #### Define First Level Model     
    mid_model = FirstLevelModel(tr,
                        mask_img=resampled_mni_mask,
                        standardize=False, 
                        #signal_scaling=False,
                        hrf_model='spm', # 
                        smoothing_fwhm=4) 
         
    #### Fit First Level Model with Given Participant and for each contrast
    mid_model = mid_model.fit(mid_final, events= events, confounds = confounds)
    contrasts = []
    if(anticipation):
        contrasts = ["ant_win_5or15 - ant_win_0",
                        "ant_lose_5or15 - ant_lose_0",
                        "ant_win_5or15 - ant_lose_5or15"]
    else:
        contrasts = ["rew_win_5or15_Hit - rew_win_5or15_Miss",
                        "rew_lose_5or15_Miss - rew_lose_5or15_Hit"]
    #generate contrasts and save    
    for contrast in contrasts:
        mid_t_map = mid_model.compute_contrast((contrast), output_type="stat")
        contrast_name = contrast.replace(" - ", "_vs_").replace(".", "")
        mid_t_map.to_filename(sesoutdir + sub + '_'+ses+'_task-mid_run-0' + run + '_' + contrast_name + '_tmap.nii.gz')
        
        
def extract_rois(sub, ses, funcindir, sesoutdir):
    """
    Extract Oldham ROIs from contrasts.
    
    Also saves preprocessed MID image in output dir. 
    ----------
    sub : str
        Subject ID starting with sub-t*
    ses : str
        ses-1 or ses-2
    funcindir : str
        Path to subject's fmriprep/ses/func output directory
    sesoutdir : str
        Path to processed MID folder with sub/ses appended.
    Returns
    -------
    Nothing
    """
    extracted_list = []
    roi_path = "/projects/b1108/projects/MID_FSL_contrasts/MID_T4_data/rois/"
    
    #load tr
    param_mid_file = open(os.path.join(funcindir, sub+'_ses-1_task-mid_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json'),)
    param_mid_df = json.load(param_mid_file)
    # Get TRs
    tr = param_mid_df['RepetitionTime']
    '''
    ###ROI 1: VS_Oldham_Rew_AntGain_v_AntNoGain_avg
    #load t-maps
    antgain_vs_antnogain_1 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-01_ant_win_5or15_vs_ant_win_0_tmap.nii.gz')
    antgain_vs_antnogain_2 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-02_ant_win_5or15_vs_ant_win_0_tmap.nii.gz')
    
    #load roi
    VS_Oldham_rew_img = nib.load(roi_path + "anticipation/VS_8mmsphere_Oldham_Rew.nii.gz")
    
    masker = NiftiLabelsMasker(labels_img=VS_Oldham_rew_img,
                        smoothing_fwhm=None,
                        standardize=False,
                        detrend=False,
                        low_pass=None,
                        high_pass=None,
                        verbose=5,
                        t_r=tr
                    )
    
    series_1 = masker.fit_transform(antgain_vs_antnogain_1)
    series_2 = masker.fit_transform(antgain_vs_antnogain_2)
    VS_Oldham_Rew_AntGain_v_AntNoGain_avg = (series_1[0][0] + series_2[0][0])/2
    
    #VS_Oldham_Rew_AntGain5_v_AntNoGain_avg - current not possible
    
    ### ROI 2: VS_Oldham_Rew_AntLoss_v_AntNoLoss_avg
    #load t-maps
    antloss_vs_antnogain_1 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-01_ant_lose_5or15_vs_ant_lose_0_tmap.nii.gz')
    antloss_vs_antnogain_2 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-02_ant_lose_5or15_vs_ant_lose_0_tmap.nii.gz')
    
    #load roi
    VS_Oldham_loss_img = nib.load(roi_path + "anticipation/VS_8mmsphere_Oldham_Loss.nii.gz")
    
    masker = NiftiLabelsMasker(labels_img=VS_Oldham_loss_img,
                        smoothing_fwhm=None,
                        standardize=False,
                        detrend=False,
                        low_pass=None,
                        high_pass=None,
                        verbose=5,
                        t_r=tr
                    )
    series_1 = masker.fit_transform(antloss_vs_antnogain_1)
    series_2 = masker.fit_transform(antloss_vs_antnogain_2)
    VS_Oldham_Rew_AntGain_v_AntNoGain_avg = (series_1[0][0] + series_2[0][0])/2
    
    ###ROI 3: OFC_Oldham_ConGainHit_v_ConGainMiss_avg
        #load t-maps
    rewgainhit_vs_rewgainmiss_1 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-01_rew_win_5or15_Hit_vs_rew_win_5or15_Miss_tmap.nii.gz')
    rewgainhit_vs_rewgainmiss_2 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-02_rew_win_5or15_Hit_vs_rew_win_5or15_Miss_tmap.nii.gz')
    
    #load roi
    OFC_Oldham_img = nib.load(roi_path + "consumption/OFC_8mmsphere_Oldham.nii.gz")
    
    masker = NiftiLabelsMasker(labels_img=OFC_Oldham_img,
                        smoothing_fwhm=None,
                        standardize=False,
                        detrend=False,
                        low_pass=None,
                        high_pass=None,
                        verbose=5,
                        t_r=tr
                    )
    series_1 = masker.fit_transform(rewgainhit_vs_rewgainmiss_1)
    series_2 = masker.fit_transform(rewgainhit_vs_rewgainmiss_2)
    OFC_Oldham_ConGainHit_v_ConGainMiss_avg = (series_1[0][0] + series_2[0][0])/2
    
    ### ROI4: VS_Oldham_Con_ConGainHit_v_ConGainMiss_avg
    #load roi, uses same t-maps as ROI 3
    VS_Oldham_Con_img = nib.load(roi_path + "consumption/VS_8mmsphere_Oldham_Con.nii.gz")
    
    masker = NiftiLabelsMasker(labels_img=VS_Oldham_Con_img,
                        smoothing_fwhm=None,
                        t_r=tr
                    )
    series_1 = masker.fit_transform(rewgainhit_vs_rewgainmiss_1)
    series_2 = masker.fit_transform(rewgainhit_vs_rewgainmiss_2)
    VS_Oldham_Con_ConGainHit_v_ConGainMiss_avg = (series_1[0][0] + series_2[0][0])/2
    '''
    
    ###ROI 5: AMYG_HO_Rew_AntGain_v_AntNoGain_avg
    #TODO:
    #AntGain_v_AntNoGain_avg -- DONE
    #AntLoss_v_AntNoLoss_avg
    #ConGainHit_v_ConGainMiss_avg
    #ConLossMiss_v_ConLossHit_avg
    #load t-maps
    antgain_vs_antnogain_1 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-01_ant_win_5or15_vs_ant_win_0_tmap.nii.gz')
    antgain_vs_antnogain_2 = nib.load(sesoutdir + sub + '_'+ses+'_task-mid_run-02_ant_win_5or15_vs_ant_win_0_tmap.nii.gz')
    
    #load roi
    amyg_HO = nib.load(roi_path + "anticipation/HO_Amygdala_50prob.nii.gz")
    
    masker = NiftiLabelsMasker(labels_img=amyg_HO,
                        smoothing_fwhm=None,
                        standardize=False,
                        detrend=False,
                        low_pass=None,
                        high_pass=None,
                        verbose=5,
                        t_r=tr
                    )
    
    series_1 = masker.fit_transform(antgain_vs_antnogain_1)
    series_2 = masker.fit_transform(antgain_vs_antnogain_2)
    Amyg_HO_Rew_AntGain_v_AntNoGain_avg = (series_1[0][0] + series_2[0][0])/2
    
    
    #TODO ADD ON HERE 
     
    
    #This is the return for all non AMYG ROIs
    #return [sub, VS_Oldham_Rew_AntGain_v_AntNoGain_avg, VS_Oldham_Rew_AntGain_v_AntNoGain_avg,  
    #        OFC_Oldham_ConGainHit_v_ConGainMiss_avg, VS_Oldham_Con_ConGainHit_v_ConGainMiss_avg]
    
    return [sub, Amyg_HO_Rew_AntGain_v_AntNoGain_avg,]



def caller(sub, ses, funcindir, sesoutdir):
    """
    Coordinates the process for a single participant

    ----------
    sub : str
        Subject ID starting with sub-t*
    ses : str
        ses-1 or ses-2
    funcindir : str
        Path to subject's fmriprep/ses/func output directory
    sesoutdir : str
        Path to processed MID folder with sub/ses appended.
    Returns
    -------
    tr_list : a nested list describing how many unregressed TRs remain
    per participant
    extracted : a list of average t-values per ROI
    """
    i = 1
    tr_list = []
    '''
    while(i <= len(glob.glob(funcindir + "*_ses-1_task-mid_run-*_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"))):
        print("########\nworking on run 0" + str(i) + " for participant " + sub + "\n########", flush=True)
        sub_counts = finish_preproc(sub, ses, str(i), funcindir, sesoutdir)
        counts_confounds = define_confounds(sub, ses, str(i), funcindir, sesoutdir)
        tr_list.append(counts_confounds[0])
        confounds = counts_confounds[1]
        first_levels(sub, ses, str(i), funcindir, sesoutdir, confounds, 1)
        first_levels(sub, ses, str(i), funcindir, sesoutdir, confounds, 0)
        i = i+1
    '''
    extract = extract_rois(sub, ses, funcindir, sesoutdir)
    #use this when running whole process
    #return tr_list, extract
    return [], extract

def main():
    ses = "ses-1" #bids ses-1
    indir = '/projects/b1108/studies/transitions/data/preprocessed/neuroimaging/fmriprep_23_2_0_nofmap/'
    outdir = '/projects/b1108/studies/transitions/data/processed/neuroimaging/mid_processing_nofmap/'
    subject = os.scandir(indir)
    tr_counts = [["ID", "run", "original_shape", "regressed_TRs"]]
    
    #extracted = [["ID", "VS_Oldham_Rew_AntGain_v_AntNoGain_avg", "VS_Oldham_Rew_AntGain_v_AntNoGain_avg",  
    #            "OFC_Oldham_ConGainHit_v_ConGainMiss_avg", "VS_Oldham_Con_ConGainHit_v_ConGainMiss_avg"]]
    
    #TODO define new extracted
    extracted = [['ID','NEW ROI NAMES...']]
    for sub in subject:
        #TODO pick a test subjec that we have good MID data for at T1
        if(("sub-t1001" in sub.name) and not(".html" in sub.name)):
            funcindir = indir + sub.name + '/' + ses + '/func/' 
            sesoutdir = outdir + sub.name + '/' + ses + '/'
            #if they have a single MID run
            print(sub.name)
            preproc_rest = os.path.join(funcindir, sub.name +'_'+ses+'_task-mid_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
            if(os.path.exists(preproc_rest)):
                os.makedirs(os.path.join(outdir, sub.name, ses), exist_ok=True)
                try:
                    sub_counts, rois_extracted = caller(sub.name, ses, funcindir, sesoutdir)
                    #tr_counts.append(sub_counts[0])
                    #tr_counts.append(sub_counts[1])
                    extracted.append(rois_extracted)
                except Exception as e:
                    print(sub.name + " failed :( ")
                    print(e)
    #with open('transitions_MID_all_TRs_09102024.csv', 'a') as myfile:
    #    wr = csv.writer(myfile)
    #    for row in tr_counts:
    #        wr.writerow(row) 
    
    with open('transitions_MID_amyg_ROIs_10012024s.csv', 'a') as myfile:
        wr = csv.writer(myfile)
        for row in extracted:
            wr.writerow(row)

main()