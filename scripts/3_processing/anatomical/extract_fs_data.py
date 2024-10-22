import pandas as pd
import numpy as np  
import glob
import csv
import itertools, os, glob

fs_dir = ('/projects/b1108/studies/transitions/data/preprocessed/neuroimaging/freesurfer_23_2') #or use below for same data
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

def getMeasures(asegRaw,measure):
    ind = asegRaw[0][asegRaw[0] == '# Measure '+measure].index[0]
    val = asegRaw[3][ind]
    return val

def getMeasures_rhlh(aparcRaw,measure):
    ind = aparcRaw[1][aparcRaw[1] == ' '+measure].index[0]
    val = aparcRaw[3][ind]
    return val

values = []
patient_id = []
def main():
    for i,participant_path in enumerate(fs_participants):
        cortex_file = os.path.join(participant_path, 'stats/aseg.stats')
        subject = cortex_file.split("/")[9] #identify participant
        print(subject,i)
        if(subject != "fsaverage" and subject != "sub-t1142_orig"):
            asegRaw = fsStat2pd(cortex_file)
            
            # get lhSurfaceHoles, rhSurfaceHoles, SurfaceHoles
            lhSurfaceHoles = getMeasures(asegRaw,'lhSurfaceHoles')
            rhSurfaceHoles = getMeasures(asegRaw,'rhSurfaceHoles')
            SurfaceHoles = getMeasures(asegRaw,'SurfaceHoles')
            TotalGrayVol = getMeasures(asegRaw,'TotalGray')
            CortGrayVol = getMeasures(asegRaw,'Cortex')

            
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
            icvVol = asegRaw.iloc[icv_ind, 3].strip() 
            icvVol_df = pd.DataFrame([icvVol], columns = ['icvVol'])
            icvVol_df.index = [subject]

            # right half cortical regions
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
            # get NumVert, WhiteSurfArea, and MeanThickness
            rhNumVert = getMeasures_rhlh(aparcrhRaw,'NumVert')
            rhWhiteSurfArea = getMeasures_rhlh(aparcrhRaw,'WhiteSurfArea')
            rhMeanThickness = getMeasures_rhlh(aparcrhRaw,'MeanThickness')

            #left half cortical regions
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
            # get NumVert, WhiteSurfArea, and MeanThickness
            lhNumVert = getMeasures_rhlh(aparclhRaw,'NumVert')
            lhWhiteSurfArea = getMeasures_rhlh(aparclhRaw,'WhiteSurfArea')
            lhMeanThickness = getMeasures_rhlh(aparclhRaw,'MeanThickness')
            
            # defining dataset and dataframe
            measures_data = {'TotalGrayVol':[TotalGrayVol], 'CorticalGrayVol':[CortGrayVol],'lhSurfaceHoles':[lhSurfaceHoles],'rhSurfaceHoles':[rhSurfaceHoles], 'SurfaceHoles':[SurfaceHoles],
                            'rhNumVert':[rhNumVert],'rhWhiteSurfArea':[rhWhiteSurfArea],'rhMeanThickness':rhMeanThickness,
                            'lhNumVert':[lhNumVert],'lhWhiteSurfArea':[lhWhiteSurfArea],'lhMeanThickness':[lhMeanThickness]}
            measures_df = pd.DataFrame(measures_data)
            measures_df.index = [subject]

            #create mega line
            final_df = pd.concat([icvVol_df, aseg_df, aparcrh_df, aparclh_df, measures_df], axis = 1)
            final_df_columns = final_df.columns
            final_df_values = final_df.values
            values.append(final_df_values[0])
            patient_id.append(subject)


    
    all_subs_df = pd.DataFrame(values, columns=final_df_columns)
    all_subs_df.index = patient_id
    #print(all_subs_df.shape)
    all_subs_df.to_csv("transitions_t1_sMRI_10102024.csv")

        
        
main()