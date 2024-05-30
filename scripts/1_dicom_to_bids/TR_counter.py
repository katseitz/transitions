import glob
import os
import nibabel as nib
import csv


PATH = '/projects/b1108/studies/transitions2/data/processed/neuroimaging/AIB_RestOnly_Networks/*/ses-1/*_fd-1_final.nii.gz'


files = glob.glob(PATH)

tr_counts = [["ID", "ses", "run", "cleaned_shape"]]


for file in files:     
    #sub-t1133_ses-1_task-rest_run-02_fd-1_final.nii.gz
    short_name = os.path.basename(file)
    print(short_name)
    ID = short_name[0:9]
    ses = short_name[10:15]
    run = short_name[26:32]
    img = nib.load(file)
    tr_counts.append([ID, ses, run, img.shape])
    print(img.shape)
    

with open('transitions_REST_fd-1_TRs.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    for row in tr_counts:
        wr.writerow(row)