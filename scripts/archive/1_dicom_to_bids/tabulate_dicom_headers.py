### This script creates a csv of the various key parameters in the dicom headers
### for all of the sequences, subjects and sessions
### Python version 3.8.4
###
### kat seitz and Ellyn Butler
### Feb 16, 2023

import pydicom #https://github.com/pydicom/pydicom
# https://pydicom.github.io/pydicom/stable/old/getting_started.html
import os
import pandas as pd
from datetime import datetime
import glob

param_dict = {
    'subid':[],
    'sesid':[],
    'PatientID':[],
    'SeriesDescription':[],
    'Modality':[],
    'AcquisitionDate':[],
    'SeriesNumber':[],
    'EchoNumbers':[],
    'EchoTime':[],
    'FlipAngle':[],
    'InPlanePhaseEncodingDirection':[],
    'ProtocolName':[],
    'RepetitionTime':[],
    'SequenceName':[],
    'SliceThickness':[],
    'NDicoms':[]}
'''
    Iterates through the uncompressed dicom folders and tabulates 
    depending on whether they are in the old or new format.
            Parameters:
                    a) The list of participant subdirs:
                        ex: ["/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/t1080"]
            Returns:
                    none, but calls tabulate depending on method. 

'''

def find_dicom_dir(subdirs):
    for subdir in subdirs: #for participant dir
        subject = subdir.split("/")[-1][0:5].lower()
        print(subject + "!!!")
        #print("subdir is : " + subdir)
        sub_folder = glob.glob(subdir + "/*") #previously sessions
        #print("sub folders:")
        #print(sub_folder)
        e_folder = glob.glob(subdir + "/e*")
        print("length of e " + str(len(e_folder)))
        if((subdir + "/" + subject in sub_folder)):
            sequences = glob.glob(subdir + "/" + subject + "/*")
            print(sequences)
            for seq in sequences:
                print("call tab old method")
                tabulate(subject, seq + "/MR")
        elif(len(e_folder) > 0):
            print(sequences)
            sequences = os.listdir(e_folder[0])
            for seq in sequences:
                if(os.path.exists(seq + "/MR")):
                    print("call tab new method")
                    tabulate(subject, seq + "/MR")
        else:
            print("Unable to unpack subject " + subject)


def tabulate(subject, dicomdir):
    print(subject)
    print(dicomdir)
    sub = subject
    session = "ses-1" #will need to modify when there are multiple sessions
    dicoms = glob.glob(dicomdir + "/*")
    #print(dicoms)
    if len(dicoms) > 0:
        dcm_path = dicoms[0] ## search for MRDC??
        #if len(dcm_path) == 0:
        #    dcm_path = os.popen('find '+dicomdir+' -regex ".*/[0-9]+"').read().split("\n")[0]
        #    dicoms = os.popen('find '+dicomdir+' -regex ".*/[0-9]+"').read().split("\n")[:-1]
        if len(dcm_path) > 0:  #check if folder is non-empty
            dcm = pydicom.dcmread(dcm_path, force = True)  #going to have to add force = True
            param_dict['subid'].append(sub)
            param_dict['sesid'].append(session)
            if hasattr(dcm, 'AcquisitionDate'):
                param_dict['AcquisitionDate'].append(dcm.AcquisitionDate)
            else:
                param_dict['AcquisitionDate'].append('NA')
            if hasattr(dcm, 'PatientID'):
                param_dict['PatientID'].append(dcm.PatientID)  #(0010, 0020)
            else:
                param_dict['PatientID'].append('NA')
            if hasattr(dcm, 'SeriesDescription'):
                param_dict['SeriesDescription'].append(dcm.SeriesDescription)
            else:
                param_dict['SeriesDescription'].append('NA')
            if hasattr(dcm, 'SeriesNumber'):
                param_dict['SeriesNumber'].append(dcm.SeriesNumber)
            else:
                param_dict['SeriesNumber'].append('NA')
            if hasattr(dcm, 'EchoNumbers'):
                param_dict['EchoNumbers'].append(dcm.EchoNumbers)
            else:
                param_dict['EchoNumbers'].append('NA')
            if hasattr(dcm, 'EchoTime'):
                param_dict['EchoTime'].append(dcm.EchoTime)
            else:
                param_dict['EchoTime'].append('NA')
            if hasattr(dcm, 'FlipAngle'):
                param_dict['FlipAngle'].append(dcm.FlipAngle)
            else:
                param_dict['FlipAngle'].append('NA')
            #param_dict['ImageType'].append(dcm.ImageType)
            if hasattr(dcm, 'InPlanePhaseEncodingDirection'):
                param_dict['InPlanePhaseEncodingDirection'].append(dcm.InPlanePhaseEncodingDirection)
            else:
                param_dict['InPlanePhaseEncodingDirection'].append('NA')
            param_dict['Modality'].append(dcm.Modality)
            param_dict['ProtocolName'].append(dcm.ProtocolName)
            if hasattr(dcm, 'RepetitionTime'):
                param_dict['RepetitionTime'].append(dcm.RepetitionTime)
            else:
                param_dict['RepetitionTime'].append('NA')
            if hasattr(dcm, 'SequenceName'):
                param_dict['SequenceName'].append(dcm.SequenceName)
            else:
                param_dict['SequenceName'].append('NA')
            if hasattr(dcm, 'SliceThickness'):
                param_dict['SliceThickness'].append(dcm.SliceThickness)
            else:
                param_dict['SliceThickness'].append('NA')
            # Count the number of dicoms in the dicom directory
            ndicoms = len(dicoms)
            param_dict['NDicoms'].append(ndicoms)

def main():
    indir = '/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed'
    subdirs = os.popen('find '+indir+' -maxdepth 1 -name "t1*"').read().split("\n")[:-1] ## participant directories. 
    print(subdirs)
    find_dicom_dir(subdirs)
    param_df = pd.DataFrame.from_dict(param_dict)
    param_df.to_csv('/projects/b1108/studies/transitions2/data/raw/neuroimaging/meta/params_'+datetime.today().strftime('%Y-%m-%d')+'.csv', index=False)


if __name__ == '__main__':
    main()