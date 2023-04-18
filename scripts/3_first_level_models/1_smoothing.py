from nilearn import image, plotting
import glob
import os

fmriprepped = glob.glob("/projects/b1108/studies/RADAR/data/processed/neuroimaging/fmriprep/sub-*")
for participant in fmriprepped:
    #get functional files that match the right pattern...
    if(not(".html" in participant)):
        funcs = glob.glob(participant + "/ses-1/func/sub*preproc_bold.nii.gz")
        for file in funcs:
            smoothed_img = image.smooth_img(file, 25)
            parts = os.path.split(file) #2-item list with path up-to filename and filename
            smoothed_img.to_filename(parts[0] + "/s" + parts[1])
