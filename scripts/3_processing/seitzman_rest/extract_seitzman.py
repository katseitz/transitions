### This script extracts the Seitzman networks
###
### Katharina Seitz
### June 2024

# Python version: 3.8.4
import os
import json
import pandas as pd #1.0.5
import nibabel as nib #3.2.1
import numpy as np #1.19.1
from nilearn.input_data import NiftiLabelsMasker #0.8.1

def extract_seitzman_nodes(sub, ses, funcindir, procindir, sesoutdir):   
    flist = os.listdir(funcindir)
    # Location of the fMRIprep & mask image
    file_rest_mask = os.path.join(funcindir, [x for x in flist if ('brain_mask.nii.gz' in x and 'task-rest' in x)][0])
    rest_mask_img = nib.load(file_rest_mask)

    # Load parameters to get TR
    param_rest_file = open(os.path.join(funcindir, sub+'_ses-1_task-rest_space-MNI152NLin6Asym_desc-preproc_bold.json'),)
    param_rest_df = json.load(param_rest_file)
    rest_tr = param_rest_df['RepetitionTime']
    
    # Load processed resting state scan
    rest_cen2 = nib.load(procindir+'/'+sub+'_'+ses+'_task-rest_final_nr6.nii.gz')
    
    # Load the atlas image and labels
    labels_img = nib.load('/projects/b1108/templates/Seitzman300/Seitzman300_MNI_res02_allROIs.nii.gz')
    labels_path = '/projects/b1108/templates/Seitzman300/ROIs_anatomicalLabels.txt'
    labels_df = pd.read_csv(labels_path, sep='\t')  
    labels_list = labels_df.iloc[:, 0]
    
    
    ####Begin network extraction
    masker_rest = NiftiLabelsMasker(labels_img=labels_img,
                                labels=labels_list,
                                mask_img=rest_mask_img,
                                smoothing_fwhm=None,
                                standardize=True,
                                detrend=False,
                                low_pass=None,
                                high_pass=None,
                                verbose=5,
                                t_r=rest_tr
                            )
    rest_time_series = masker_rest.fit_transform(rest_cen2)
    
    ##### Save Output
    #save timeseries data
    np.savetxt(sesoutdir+sub+'_'+ses+'_task-rest_seitzman_timeseries_nr6.csv',
    rest_time_series, delimiter=',')

    return
    
def get_network_timeseries(sub,ses, sesoutdir):
    # Load file with node's network affiliations
    all_info = '/projects/b1108/templates/Seitzman300/ROIs_300inVol_MNI_allInfo.txt'
    network_affiliations = pd.read_csv(all_info, sep=" ")
    timeseries = pd.read_csv(sesoutdir+sub+'_'+ses+'_task-rest_seitzman_timeseries_nr6.csv',
                             header=None)
    
    # Get a list of the networks
    networks = network_affiliations['netName'].unique()
    
    #Iterate through each network and create timeseries for just that network
    for network in networks:
        network_indeces = network_affiliations[network_affiliations['netName'] == network].index
        network_timeseries = timeseries.iloc[:, network_indeces]
        np.savetxt(sesoutdir+'/'+sub+'_'+ses+'_seitzman_' +network + '_timeseries_nr6.csv',
            network_timeseries, delimiter=',')
        # Correlate every column with every other column
        corr_matrix = np.corrcoef(network_timeseries, rowvar=False)
        np.savetxt(sesoutdir+'/'+sub+'_'+ses+'_' + network + '_network_corrmat_nr6.csv',
                corr_matrix, delimiter=',')


def main():
    ses = "ses-1" #bids ses-1
    fmriprepdir = '/projects/b1108/studies/TEAM/data/preprocessed/neuroimaging/fmriprep_23_2/'
    procdir = '/projects/b1108/studies/TEAM/data/processed/neuroimaging/aib_networks_rest/'
    outdir = '/projects/b1108/studies/TEAM/data/processed/neuroimaging/seitzman_networks_rest/'
    subjects = os.scandir(fmriprepdir)
    for sub in subjects:
        if("sub-" in sub.name and not(".html" in sub.name)):
            #define subject specific file paths
            funcindir = fmriprepdir + sub.name + '/' + ses + '/func/' 
            sesoutdir = outdir + sub.name + '/' + ses + '/'
            procindir = procdir + sub.name + '/' + ses + '/'
            preproc_rest = os.path.join(funcindir, sub.name +'_'+ses+'_task-rest_space-MNI152NLin6Asym_desc-preproc_bold.json')
            if(os.path.exists(preproc_rest)):
                os.makedirs(os.path.join(outdir, sub.name, ses), exist_ok=True)
                extract_seitzman_nodes(sub.name, ses, funcindir, procindir, sesoutdir)
                get_network_timeseries(sub.name,ses, sesoutdir)
                try:
                    extract_seitzman_nodes(sub.name, ses, funcindir, procindir, sesoutdir)
                    get_network_timeseries(sub.name,ses, sesoutdir)
                except Exception as e:
                    print(e)

if __name__ == "__main__":            
    main()