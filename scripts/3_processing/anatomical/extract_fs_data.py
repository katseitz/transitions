import pandas as pd
import numpy as np  
import glob
import csv
import itertools, os, glob

fs_dir = ('/projects/b1108/studies/transitions/data/preprocessed/neuroimaging/freesurfer') #or use below for same data
fs_participants = glob.glob(os.path.join(fs_dir, '*'))


def fsStat2pd(input):
    f = open(input, 'rt')
    reader = csv.reader(f)
    csv_list = []
    for l in reader:
        csv_list.append(l)
    f.close()
    df = pd.DataFrame(csv_list)
    return df

def fsValExt(data):
    res = []
    for i in range(data.shape[0]):
        tmp = data.iloc[i].str.split(' ')
        tmp_value = ' '.join(tmp[0]).split()
        df = res.append(tmp_value)
    res_df = pd.DataFrame(res)
    return res_df

def main():
    for participant_path in fs_participants:
        cortex_file = os.path.join(participant_path, 'stats/aseg.stats')
        subject = cortex_file.split("/")[9] #identify participant
        print(subject)
        asegRaw = fsStat2pd(cortex_file)
        #print(df)
        
        # confirm starting index
        asegInd = asegRaw[0][asegRaw[0] == '# NRows 45 '].index[0]
        asegData = asegRaw.iloc[asegInd+3:]
        aseg_df = fsValExt(asegData) #TODO at some point at column headers
        aseg_df.columns = ["Index", "SegId", "NVoxels", "Volume_mm3", "StructName",
                           "normMean", "normStdDev", "normMin", "normMax", "normRange"]
        aseg_df.drop(["Index", "SegId", "NVoxels", "normMean", "normStdDev", "normMin", "normMax", "normRange"], axis = 1, inplace = True)
        aseg_df["PID"] = subject
        aseg_df = aseg_df.pivot(index='PID', columns='StructName', values='Volume_mm3')
        #TODO: think about adding Vol_ to front variable 

        
        #Here's where we get intercranial volume
        icv_ind = asegRaw[1][asegRaw[1] == ' BrainSegVol'].index[0]
        icvVol = asegRaw.iloc[icv_ind, 3].strip() #TODO add this to mega spreadsheet
       
        rh_file = os.path.join(participant_path, 'stats/rh.aparc.stats')
        aparcrhRaw = fsStat2pd(rh_file)
        aparcInd = aparcrhRaw[0][aparcrhRaw[0] == '# ColHeaders StructName NumVert SurfArea GrayVol ThickAvg ThickStd MeanCurv GausCurv FoldInd CurvInd'].index[0]
        aparcrhData = aparcrhRaw.iloc[aparcInd+1:]
        aparcrh_df = fsValExt(aparcrhData)
        aparcrh_df[0] = 'right_' + aparcrh_df[0].astype(str)
        aparcrh_df.columns = ["StructName", "NumVert", "SurfArea", "GrayVol", "ThickAvg", "ThickStd", 
                              "MeanCurv", "GausCurv", "FoldIn", "CurvInd"]
        aparcrh_df.drop(["NumVert","MeanCurv", "GausCurv", "FoldIn", "CurvInd"], axis = 1, inplace = True)
        aparcrh_df["PID"] = subject
        aparcrh_df = aparcrh_df.pivot(index='PID', columns='StructName', values=["SurfArea", "GrayVol", "ThickAvg"])
        aparcrh_df.columns = aparcrh_df.columns.map('_'.join).str.strip('|')
         
        
        lh_file = os.path.join(participant_path, 'stats/lh.aparc.stats')
        aparclhRaw = fsStat2pd(lh_file)
        aparcInd = aparclhRaw[0][aparclhRaw[0] == '# ColHeaders StructName NumVert SurfArea GrayVol ThickAvg ThickStd MeanCurv GausCurv FoldInd CurvInd'].index[0]
        aparclhData =aparclhRaw.iloc[aparcInd+1:]
        aparclh_df = fsValExt(aparclhData)
        aparclh_df[0] = 'left_' + aparclh_df[0].astype(str)
        aparclh_df.columns = ["StructName", "NumVert", "SurfArea", "GrayVol", "ThickAvg", "ThickStd", 
                              "MeanCurv", "GausCurv", "FoldIn", "CurvInd"]
        aparclh_df.drop(["NumVert","MeanCurv", "GausCurv", "FoldIn", "CurvInd"], axis = 1, inplace = True)
        aparclh_df["PID"] = subject
        aparclh_df = aparclh_df.pivot(index='PID', columns='StructName', values=["SurfArea", "GrayVol", "ThickAvg"])
        aparclh_df.columns = aparclh_df.columns.map('_'.join).str.strip('|')
        #print(aparclh_df)
        
        
        #create mega line
        final_df = pd.concat([aseg_df, aparcrh_df, aparclh_df], axis = 1)
        #TODO figure out how to make this global....
    final_df.to_csv("test.csv")

        
        
main()