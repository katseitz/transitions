# -*- coding: utf-8 -*-
import glob
import os
import sys
import json


participant = sys.argv[1]
ses = 'ses-2'

'''
    Removes participant name from file names. 
            Parameters:
                    a) participant in f1XXXX format
                    b) directory up to and inclduding ses-XX
            Returns:
                    none
'''
def remove_name(participant, directory):
    for file in os.listdir(directory):
        print(file)
        parts = file.split("--", 1)
        new_name = participant + "--" + parts[-1]
        os.rename(directory + "/" + file, directory + "/" + new_name) 
'''
    Checks for func, beh, anat, and fmap directories
    Creates them, if they do not exist.
            Parameters:
                    a) participant in f1XXXX format
                    b) directory up to and inclduding ses-XX
            Returns:
                    none
'''
def makedir(participant, directory):
    #check if directories exist, if not, create them
    if(not os.path.exists(directory + "/func/")):
        os.mkdir(directory + "/func/")
    if(not os.path.exists(directory + "/anat/")):
        os.mkdir(directory + "/anat/")
    if(not os.path.exists(directory + "/fmap/")):
        os.mkdir(directory + "/fmap/")

'''
    Renames files all per the file renaming document from Nina
            Parameters:
                    a) participant in f1XXXX format
                    b) directory up to and inclduding ses-XX
            Returns:
                    none
'''
def rename_partic(participant, directory): 
    #search using glob on the pattern that Nina in the doc 
    print(participant + " " + directory)
    print("in rename partic")
    files = glob.glob(directory + "/" + participant + "--FMAP1--GR--?_ph*")+ glob.glob(directory + "/" + participant + "--FMAP1*ph*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        new_name = "sub-" + participant + "_" + ses + "_phase1." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    files = glob.glob(directory + "/" + participant + "--FMAP2--GR--?_ph*") + glob.glob(directory + "/" + participant + "--FMAP2*ph*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        new_name = "sub-" + participant + "_" + ses + "_phase2." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    files = glob.glob(directory + "/" + participant + "--FMAP1--GR--*") + glob.glob(directory + "/" + participant + "--FMAP1*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        new_name = "sub-" + participant + "_" + ses + "_magnitude1." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    files = glob.glob(directory + "/" + participant + "--FMAP2--GR--*") + glob.glob(directory + "/" + participant + "--FMAP2*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        new_name = "sub-" + participant + "_" + ses + "_magnitude2." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    #MID 1
    files = glob.glob(directory + "/" + participant + "--MID1--EP_RM--*") + glob.glob(directory + "/" + participant + "--MID1*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        if(parts[1] == "json"):
            json_obj = json.load(open(file, 'r'))
            json_obj['TaskName'] = 'mid'
            with open(file, 'w') as f:
                json.dump(json_obj, f)
        if("_ph" in file):
            new_name = "sub-" + participant + "_" + ses + "_task-mid_run-01_phase." + parts[1]
        else:
            new_name = "sub-" + participant + "_" + ses + "_task-mid_run-01_bold." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    #MID2
    files = glob.glob(directory + "/" + participant + "--MID2--EP_RM--*") + glob.glob(directory + "/" + participant + "--MID2*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        if(parts[1] == "json"):
            json_obj = json.load(open(file, 'r'))
            json_obj['TaskName'] = 'mid'
            with open(file, 'w') as f:
                json.dump(json_obj, f)
        if("_ph" in file):
            new_name = "sub-" + participant + "_" + ses + "_task-mid_run-02_phase." + parts[1]
        else:
            new_name = "sub-" + participant + "_" + ses + "_task-mid_run-02_bold." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name)  

    #REST1
    files = glob.glob(directory + "/" + participant + "--REST1--EP_RM--*") + glob.glob(directory + "/" + participant + "--REST1*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        if(parts[1] == "json"):
            json_obj = json.load(open(file, 'r'))
            json_obj['TaskName'] = 'rest'
            with open(file, 'w') as f:
                json.dump(json_obj, f)
        if("_ph" in file):
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-01_phase." + parts[1]
        else:
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-01_bold." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    #REST2
    files = glob.glob(directory + "/" + participant + "--REST2--EP_RM--*") + glob.glob(directory + "/" + participant + "--REST2*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        if(parts[1] == "json"):
            json_obj = json.load(open(file, 'r'))
            json_obj['TaskName'] = 'rest'
            with open(file, 'w') as f:
                json.dump(json_obj, f)
        if("_ph" in file):
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-02_phase." + parts[1]
        else:
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-02_bold." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name)  
    #REST3
    files = glob.glob(directory + "/" + participant + "--REST3--EP_RM--*") + glob.glob(directory + "/" + participant + "--REST3*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        if(parts[1] == "json"):
            json_obj = json.load(open(file, 'r'))
            json_obj['TaskName'] = 'rest'
            with open(file, 'w') as f:
                json.dump(json_obj, f)
        if("_ph" in file):
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-03_phase." + parts[1]
        else:
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-03_bold." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    #REST4
    files = glob.glob(directory + "/" + participant + "--REST4--EP_RM--*") + glob.glob(directory + "/" + participant + "--REST4*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        if(parts[1] == "json"):
            json_obj = json.load(open(file, 'r'))
            json_obj['TaskName'] = 'rest'
            with open(file, 'w') as f:
                json.dump(json_obj, f)
        if("_ph" in file):
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-04_phase." + parts[1]
        else:
            new_name = "sub-" + participant + "_" + ses + "_task-rest_run-04_bold." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 
    #T1W
    files = glob.glob(directory + "/" + participant + "--T1w--GR--*") + glob.glob(directory + "/" + participant + "--T1w*")
    for file in files:
        print(file)
        parts = file.split(".", 1)
        new_name = "sub-" + participant + "_" + ses + "_run-1_T1w." + parts[1]
        print(directory + "/" + new_name)
        os.rename(file, directory + "/" + new_name) 

'''
    Moves files to their respective sub folders
            Parameters:
                    a) participant in f1XXXX format
                    b) directory up to and inclduding ses-XX
            Returns:
                    none
'''   
def move_to_folders(participant, directory):
    #move functional files
    print("in move to folders")
    func_pattern = "sub-"+ participant + "_" + ses+ "_task*"
    func_files = glob.glob(directory + "/" + func_pattern)
    for file in func_files:
        print(file)
        parts = file.split("/")
        os.rename(file, directory + "/func/" + parts[-1])
    #move anatomical files
    anat_pattern = "sub-"+ participant + "_"+ ses + "_run-1_T1w*"
    anat_files = glob.glob(directory + "/" + anat_pattern)
    for file in anat_files:
        print(file)
        parts = file.split("/")
        os.rename(file, directory + "/anat/" + parts[-1])
    #move fmap files
    fmap_files = glob.glob(directory + "/sub*")
    for file in fmap_files:
        print(file)
        parts = file.split("/")
        os.rename(file, directory + "/fmap/" + parts[-1])



def main():
    key = participant
    value = "/Users/katharinaseitz/Documents/dicom_conversions/bids/sub-" + participant + "/" + ses 
    remove_name(key, value)
    makedir(key, value)
    rename_partic(key, value)
    move_to_folders(key, value)



if __name__ == "__main__":
    main()