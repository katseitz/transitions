### This script conducts the processing steps after fmriprep for rest
### And extracts AIB Networks
###
### Katharina Seitz
### March 2024

# Python version: 3.8.4
import os
import glob
import json
import csv
import pandas as pd #1.0.5
import nibabel as nib #3.2.1
import numpy as np #1.19.1
#from bids.layout import BIDSLayout #may not be needed
from nilearn.input_data import NiftiLabelsMasker #0.8.1
from nilearn import plotting
from nilearn import signal
from nilearn import image
import scipy.signal as sgnl #1.5.4
import sys, getopt
from calc_ffd import calc_ffd
from remove_trs import remove_trs
from cubic_interp import cubic_interp
#from get_qual_metrics import get_qual_metrics

def postproc_rest(sub, ses, funcindir, sesoutdir):
    tr_list = []
    #if(True or not(os.path.exists(sesoutdir+'/'+sub+'_'+ses+'_task-rest_final.nii.gz'))):   
    print("here!!!!")
    flist = os.listdir(funcindir)
    print(funcindir)
    i = 1
    while(i <= len(glob.glob(funcindir+"*ses-1_task-rest_run-0*_space-MNI152NLin6Asym_desc-preproc_bold.json"))):
        file_rest = os.path.join(funcindir, [x for x in flist if ('_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz' in x and 'task-rest_run-0' + str(i) in x)][0])
        file_rest_mask = os.path.join(funcindir, [x for x in flist if ('_space-MNI152NLin6Asym_desc-brain_mask.nii.gz' in x and 'task-rest_run-0' + str(i) in x)][0])
        rest_mask_img = nib.load(file_rest_mask)
        
        # Load confounds for rest
        #sub-20572_ses-2_task-rest_run-1_desc-confounds_timeseries.tsv
        confounds_rest_path = os.path.join(funcindir, [x for x in flist if ('task-rest_run-0' + str(i) + '_desc-confounds_timeseries.tsv' in x)][0])
        confounds_rest_df = pd.read_csv(confounds_rest_path, sep='\t')

        # Load parameters for rest
        #TODO change out ses
        param_rest_file = open(os.path.join(funcindir, sub+'_ses-1_task-rest_run-0' + str(i) + '_space-MNI152NLin6Asym_desc-preproc_bold.json'),)
        param_rest_df = json.load(param_rest_file)

        # Get TRs
        rest_tr = param_rest_df['RepetitionTime']
        
        #### Select confound columns
        # https://www.sciencedirect.com/science/article/pii/S1053811917302288
        # Removed csf and white_matter because too collinear with global_signal
        confound_vars = ['trans_x','trans_y','trans_z',
                        'rot_x','rot_y','rot_z', 'global_signal'] #, 'csf', 'white_matter'
        deriv_vars = ['{}_derivative1'.format(c) for c in confound_vars]
        power_vars = ['{}_power2'.format(c) for c in confound_vars]
        power_deriv_vars = ['{}_derivative1_power2'.format(c) for c in confound_vars]
        final_confounds = confound_vars + deriv_vars + power_vars + power_deriv_vars

        confounds_rest_df = confounds_rest_df.fillna(0)
        
        rest_img = nib.load(file_rest)

        ##### Demean and detrend
        rest_de = image.clean_img(rest_img, detrend=True, standardize=False, t_r=rest_tr)

        ##### Nuisance regression
        rest_reg = image.clean_img(rest_de, detrend=False, standardize=False,
                                confounds=confounds_rest_df[final_confounds], t_r=rest_tr)

        ###### Identify TRs to censor
        confounds_rest_df = calc_ffd(confounds_rest_df, rest_tr)
        confounds_rest_df['ffd_good'] = confounds_rest_df['ffd'] < 0.1
        print("run 0" + str(i))
        print("total volumes: " )
        print(len(confounds_rest_df.index)) 
        print("num censored: ") 
        print((~confounds_rest_df['ffd_good']).values.sum())
        #i = i + 1 #COMMENT OUT LATER JUST FOR TESTING
        
        ##### Censor the TRs where fFD > .1
        rest_cen, confounds_rest_df = remove_trs(rest_reg, confounds_rest_df, replace=False)
        print("after censoring 1")
        print(rest_cen.shape)

        ##### Interpolate over these Volumess
        rest_int = cubic_interp(rest_cen, rest_mask_img, rest_tr, confounds_rest_df)
        print("after interpolation 1")
        print(rest_int.shape)
        ##### Temporal bandpass filtering + Nuisance regression again
        rest_band = image.clean_img(rest_int, detrend=False, standardize=False, t_r=rest_tr,
                                confounds=confounds_rest_df[final_confounds],
                                low_pass=0.08, high_pass=0.009)
        print("after bandpass")
        print(rest_band.shape)
        
        
        ##### Censor volumes identified as having fFD > .1
        rest_cen2, confounds_rest_df = remove_trs(rest_band, confounds_rest_df, replace=False)
        print("after censoring 2")
        print(rest_cen2.shape)
        rest_cen2.to_filename(sesoutdir+'/'+sub+'_'+ses+'_task-rest_run-0' + str(i) + '_fd-1_final.nii.gz')
        #i = i + 1
        
        rest_cen2 = nib.load(sesoutdir+'/'+sub+'_'+ses+'_task-rest_run-0' + str(i) + '_fd-1_final.nii.gz')
        ##### Run masker for each network in the loop
        networks = ['CEN', 'AS', 'ATTC', 'ER', 'DMN', 'PS', 'FS']
        for network in networks:
            # Get the labeled image and labels
            #TODO fill 
            labels_img = nib.load('/projects/b1108/studies/transitions/scripts/3_processing/AIB_rest/AIB_networks/' + network + '_merged_image.nii.gz')
            labels_path = '/projects/b1108/studies/transitions/scripts/3_processing/AIB_rest/AIB_networks/' + network + '_label.txt'
            labels_df = pd.read_csv(labels_path, sep='\t')
            new_header = labels_df.iloc[0] #grab the first row for the header
            labels_df = labels_df[1:] #take the data less the header row
            labels_df.columns = new_header #set the header row as the df header   
            labels_list = labels_df.iloc[:, 0] 


            masker_rest = NiftiLabelsMasker(labels_img=labels_img,
                                        labels=labels_list,
                                        mask_img=rest_mask_img,
                                        smoothing_fwhm=0,
                                        standardize=True,
                                        detrend=False,
                                        low_pass=None,
                                        high_pass=None,
                                        verbose=5,
                                        t_r=rest_tr
                                    )

            rest_time_series = masker_rest.fit_transform(rest_cen2)
            ##### Connectivity
            #save timeseries data
            np.savetxt(sesoutdir+sub+'_'+ses+'_task-rest_run-0' + str(i) + '_' + network + '_network_timeseries.csv',
            rest_time_series, delimiter=',')

            # Correlate every column with every other column
            corr_matrix = np.corrcoef(rest_time_series, rowvar=False)

            # Get the number of non-nan values for each corr matrix
            num_nonnan = np.isnan(corr_matrix)

            # Write out number of non-nan matrices
            np.savetxt(sesoutdir+'/'+sub+'_'+ses+'_run-0' + str(i) + '_' + network + '_network_nonnan.csv',
                num_nonnan, delimiter=',')

            # Write out correlation matrix
            np.savetxt(sesoutdir+'/'+sub+'_'+ses+'_run-0' + str(i) + '_' + network + '_network_corrmat.csv',
                corr_matrix, delimiter=',')
            tr_list.append([sub, ses, i, rest_cen2.shape])
        i = i+1
        print("updated i " + str(i))
    return tr_list
        

def main():
    ses = "ses-1" #bids ses-1
    indir = '/projects/b1108/studies/transitions/data/preprocessed/neuroimaging/fmriprep_23_2_0_nofmap/'
    outdir = '/projects/b1108/studies/transitions/data/processed/neuroimaging/aib_networks_rest/'
    subjects = os.scandir(indir)
    tr_counts = [["ID", "ses", "run", "cleaned_shape"]]
    #subjects = glob.glob('/projects/b1108/studies/transitions2/data/processed/neuroimaging/ses-1_v23_2_0_nofmap/sub-t102*')
    for sub in subjects:
        if("sub-t125" in sub.name and not(".html" in sub.name)):
            #print(sub.name)
            funcindir = indir + sub.name + '/' + ses + '/func/' 
            sesoutdir = outdir + sub.name + '/' + ses + '/'
            preproc_rest = os.path.join(funcindir, sub.name +'_'+ses+'_task-rest_run-01_space-MNI152NLin6Asym_desc-preproc_bold.json')
            if(os.path.exists(preproc_rest)):
                os.makedirs(os.path.join(outdir, sub.name, ses), exist_ok=True)
                try:
                    sub_counts = postproc_rest(sub.name, ses, funcindir, sesoutdir)
                    for val in sub_counts:
                        tr_counts.append(val)
                except Exception as e:
                    print(e)
        with open('transitions_REST_fd-1_TRs.csv', 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            for row in tr_counts:
                wr.writerow(row)
        '''
        elif(not '.html' in sub):
            print("here")
            funcindir = indir + sub.split('/')[-1] + '/' + ses + '/func/' 
            sesoutdir = outdir + sub.split('/')[-1] + '/' + ses + '/'
            preproc_rest = os.path.join(funcindir, sub.split('/')[-1] +'_'+ses+'_task-rest_run-01_space-MNI152NLin6Asym_desc-preproc_bold.json')
            print(preproc_rest)
            if(os.path.exists(preproc_rest)):
                print("here")
                os.makedirs(os.path.join(outdir, sub, ses), exist_ok=True)
                postproc_rest(sub, ses, funcindir, sesoutdir)
        '''
main()