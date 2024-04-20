from nilearn import signal
import math
import nibabel as nib #3.2.1
import numpy as np #1.19.1
from scipy.interpolate import interp1d
import pandas as pd


def calc_ffd(confounds_df, tr):
    confounds_df['trans_x_filt'] = signal.butterworth(confounds_df['trans_x'], tr, low_pass=0.1)
    confounds_df['trans_y_filt'] = signal.butterworth(confounds_df['trans_y'], tr, low_pass=0.1)
    confounds_df['trans_z_filt'] = signal.butterworth(confounds_df['trans_z'], tr, low_pass=0.1)
    confounds_df['rot2_x_filt'] = signal.butterworth((confounds_df['rot_x']*50*math.pi)/360, tr, low_pass=0.1)
    confounds_df['rot2_y_filt'] = signal.butterworth((confounds_df['rot_x']*50*math.pi)/360, tr, low_pass=0.1)
    confounds_df['rot2_z_filt'] = signal.butterworth((confounds_df['rot_x']*50*math.pi)/360, tr, low_pass=0.1)
    confounds_df['ffd'] = 0
    for i, row in confounds_df.iterrows():
        if i == 0:
            curr_trans_x_filt = confounds_df.loc[i, 'trans_x_filt']
            curr_trans_y_filt = confounds_df.loc[i, 'trans_y_filt']
            curr_trans_z_filt = confounds_df.loc[i, 'trans_z_filt']
            curr_rot2_x_filt = confounds_df.loc[i, 'rot2_x_filt']
            curr_rot2_y_filt = confounds_df.loc[i, 'rot2_y_filt']
            curr_rot2_z_filt = confounds_df.loc[i, 'rot2_z_filt']
        else:
            prev_trans_x_filt = curr_trans_x_filt
            prev_trans_y_filt = curr_trans_y_filt
            prev_trans_z_filt = curr_trans_z_filt
            prev_rot2_x_filt = curr_rot2_x_filt
            prev_rot2_y_filt = curr_rot2_y_filt
            prev_rot2_z_filt = curr_rot2_z_filt
            curr_trans_x_filt = confounds_df.loc[i, 'trans_x_filt']
            curr_trans_y_filt = confounds_df.loc[i, 'trans_y_filt']
            curr_trans_z_filt = confounds_df.loc[i, 'trans_z_filt']
            curr_rot2_x_filt = confounds_df.loc[i, 'rot2_x_filt']
            curr_rot2_y_filt = confounds_df.loc[i, 'rot2_y_filt']
            curr_rot2_z_filt = confounds_df.loc[i, 'rot2_z_filt']
            confounds_df.loc[i, 'ffd'] = abs(prev_trans_x_filt - curr_trans_x_filt) \
                        + abs(prev_trans_y_filt - curr_trans_y_filt) \
                        + abs(prev_trans_z_filt - curr_trans_z_filt) \
                        + abs(prev_rot2_x_filt - curr_rot2_x_filt) \
                        + abs(prev_rot2_y_filt - curr_rot2_y_filt) \
                        + abs(prev_rot2_z_filt - curr_rot2_z_filt)
    return confounds_df

def remove_trs(img, confounds_df, replace=True):
    img_array = img.get_fdata()
    if 'keep_ffd' not in confounds_df.columns:
        keep_array = np.full((img_array.shape[3]), True)
        for index, row in confounds_df.iterrows():
            keep = confounds_df.loc[index, 'ffd_good']
            if keep == False:
                np.put(keep_array, index, False)
                # Is there a False within the subsequent 6?
                nextsix = confounds_df.loc[(index+1):(index+6), 'ffd_good'].to_list()
                if len(nextsix) > 0:
                    if nextsix[0] == True:
                        # If so, replace all the intervening Trues with False
                        if False in nextsix:
                            index_firstfalse = index + nextsix.index(False) + 1
                            np.put(keep_array, range(index, index_firstfalse), False)
                        elif len(nextsix) < 6:
                            index_firstfalse = len(keep_array)
                            np.put(keep_array, range(index, index_firstfalse), False)
        confounds_df['keep_ffd'] = keep_array
    else:
        keep_array = confounds_df['keep_ffd'].to_list()
    # NA out bad TRs
    if replace == True:
        for i in range(0, img.shape[3]):
            if keep_array[i] == False:
                img_array[:,:,:,i] = float('nan')
    else:
        img_array = img_array[:,:,:,keep_array]
    img_cen = nib.Nifti1Image(img_array, affine=img.affine)
    return img_cen, confounds_df

def cubic_interp(img_cen, mask, tr, confounds_df):
    # Get the times that all of the TRs were collected
    all_sample_times = np.arange(confounds_df.shape[0])*tr
    keep_ffd = confounds_df['keep_ffd'].tolist()
    retained_sample_times = all_sample_times[keep_ffd]
    ditch_ffd = [not elem for elem in keep_ffd]
    excluded_sample_times = all_sample_times[ditch_ffd]
    # Turn the nifti into an array object
    img_array = img_cen.get_fdata()
    # Get the voxels that are brain tissue
    mask_array = mask.get_fdata()
    # Make an empty numpy array to put the interpolated data into
    nout = confounds_df.shape[0]
    int_array = np.zeros((img_array.shape[0], img_array.shape[1], img_array.shape[2], nout))
    ditch_beg = 0
    # Check for leading TRs to ditch
    if ditch_ffd[0] == True:
        # Get the number of TRs that need to be ditched at the end
        for i in range(0, ditch_ffd):
            if ditch_ffd[i] == True:
                ditch_beg = ditch_beg + 1
            else:
                break
    # Check for trailing TRs to ditch
    ditch_end = 0
    if ditch_ffd[-1] == True:
        # Get the number of TRs that need to be ditched at the end
        ditch_ffd_reversed = list(reversed(ditch_ffd))
        for i in range(0, len(ditch_ffd_reversed)):
            if ditch_ffd_reversed[i] == True:
                ditch_end = ditch_end + 1
            else:
                break
    # Loop over the voxels to pull out single times series
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(img_array.shape[2]):
                if mask_array[i, j, k]:
                    vals = img_array[i, j, k, :]
                    # Fit the cubic model
                    fit = interp1d(retained_sample_times, vals, kind='cubic')
                    # Get the predicted values for the censored times
                    if ditch_ffd[0] == True and ditch_ffd[-1] == True:
                        interp_vals = fit(excluded_sample_times[ditch_beg:-ditch_end])
                        int_array[i, j, k, ditch_ffd] = np.append(np.repeat(0, ditch_beg), interp_vals, np.repeat(0, ditch_end))
                    elif ditch_ffd[0] == True:
                        interp_vals = fit(excluded_sample_times[ditch_beg:])
                        int_array[i, j, k, ditch_ffd] = np.append(np.repeat(0, ditch_beg), interp_vals)
                    elif ditch_ffd[-1] == True:
                        interp_vals = fit(excluded_sample_times[0:-ditch_end])
                        int_array[i, j, k, ditch_ffd] = np.append(interp_vals, np.repeat(0, ditch_end))
                    else:
                        interp_vals = fit(excluded_sample_times)
                        # Put predicted values in the correct TRs
                        int_array[i, j, k, ditch_ffd] = interp_vals
                    # Put in the retained values
                    int_array[i, j, k, keep_ffd] = vals
    img_int = nib.Nifti1Image(int_array, affine=img_cen.affine)
    return img_int

def get_qual_metrics(confounds_df, task, subid, sesid):
    qual_dict = {
        'subid':[],
        'sesid':[],
        'task':[],
        'mean_fd':[],
        'mean_ffd':[],
        'num_trs':[],
        'num_trs_kept':[]
    }
    qual_dict['subid'].append(subid)
    qual_dict['sesid'].append(sesid)
    qual_dict['task'].append(task)
    qual_dict['mean_fd'].append(confounds_df['framewise_displacement'].mean())
    qual_dict['mean_ffd'].append(confounds_df['ffd'].mean())
    qual_dict['num_trs'].append(confounds_df.shape[0])
    qual_dict['num_trs_kept'].append(confounds_df['keep_ffd'].sum())
    qual_df = pd.DataFrame.from_dict(qual_dict)
    return qual_df