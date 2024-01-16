import pandas as pd
import numpy as np
import glob
import os 

basedir = '/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural/'
basedir2 = '/projects/b1108/studies/transitions2/data/raw/neuroimaging/bids/'

mid = 1
make_plot = 0
save_output = 0


fnames = glob.glob(basedir+'sub-*/ses-1/beh/3_MID*2.txt')

dirs = glob.glob(basedir + '*')


#TO-DO: Do file testing here 

test_file = '/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural/sub-t1018/ses-1/beh/3_MID_Scanner_HARP_11-1018-2.txt'


def sus_out_files(path = dirs[10]):
    #print(path)
    files =  glob.glob(path +'/ses-1/beh/3_MID*.txt')
    #print("here are the files")
    #print(files)
    midshared_files = []
    mid1_files = []
    mid2_files = []
    for file in files: 
        df = file_to_df(file)
        #print(df.head(40))
        #print(('Run1Cue.OnsetTime' in df[0].unique()))
        if('Run1Cue.OnsetTime' in df[0].unique() and 'Run2Cue.OnsetTime' in df[0].unique()):
            midshared_files.append([file, len(df)])
        elif('Run1Cue.OnsetTime' in df[0].unique()):
            mid1_files.append([file, len(df)])
        elif('Run2Cue.OnsetTime' in df[0].unique()):
            mid2_files.append([file, len(df)])
        else:
            print("No sutable MID file for " + path)
            break
        
        #best case 
        if(len(midshared_files) == 1 and len(mid1_files) == 0 and len(mid1_files) == 0): 
            happy_mid(midshared_files[0][0])
        else:
            print("this path has confusing mid files " + path)


def remove_unicode(string):
    """
    Removes unicode characters in string.
    Parameters
    ----------
    string : str
        String from which to remove unicode characters.
    Returns
    -------
    str
        Input string, minus unicode characters.
    """
    return ''.join([val for val in string if 31 < ord(val) < 127])

def file_to_df(text_file):
    # Load the text file as a list.
    print(text_file)
    with open(text_file, 'rb') as fo:
        text_data = list(fo)

    # Remove unicode characters.
    filtered_data = [remove_unicode(row.decode('utf-8', 'ignore')) for row in text_data]
    list_data = []
    for row in filtered_data: 
        if ":" in row:
            row_as_list = row.split(": ")
            list_data.append(row_as_list)
            
        else:
            list_data.append([row])
    df = pd.DataFrame(list_data)
    #print(df.head(40))
    return df
    
def df_to_timing_txt(df, subject, mid2=0):
    #MID RUN 1
    tgt_on = df.loc[df[0] == 'Run1Tgt.OnsetTime'][1].reset_index() #     txt.Var2(find(contains(txt.Var1,'Run1Tgt.OnsetTime'))); 
    tgt_dur = df.loc[df[0] == 'TgtDur'][1].reset_index()  #txt.Var2(find(contains(txt.Var1,'TgtDur')));
    #cue onset and duration
    cue_on1 = df.loc[df[0] == 'Run1Cue.OnsetTime'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run1Cue.OnsetTime')));
    cue_on1 = (cue_on1 - int(df.loc[df[0] == 'Run1Fix.OnsetTime'].iloc[0][1])) / 1000  #'cue_on1 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
    
    #After some Zach logic that I haven't added here where we compate onset times
    cue_rt_time = df.loc[df[0] == 'Run1Cue.RTTime'][1].reset_index()#txt.Var2(find(contains(txt.Var1,'Run1Cue.RTTime')));
    cue_dur = df.loc[df[0] == 'Run1Cue.Duration'][1].reset_index()#txt.Var2(find(contains(txt.Var1,'Run1Cue.Duration')));
    # ITI onset
    cue_iti1 = df.loc[df[0] == 'Run1Dly3.OnsetTime'][1].astype(int).reset_index()#txt.Var2(find(contains(txt.Var1,'Run1Dly3.OnsetTime')));
    cue_iti1 = (cue_iti1 -  int(df.loc[df[0] == 'Run1Fix.OnsetTime'].iloc[0][1])) / 1000   #(cue_iti1 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
    trial_duration1 = cue_iti1 - cue_on1
    #response times of participant responses
    rt1 = df.loc[df[0] == 'Run1Tgt.RT'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run1Tgt.RT')));
    rt1 = rt1.replace(0, np.nan) #rt1(rt1 == 0) = NaN; #TODO
    #feedback onset and duration
    
    #TODO: adjust fbk onset??
    fbk_on1 = df.loc[df[0] == 'Run1Fbk.OnsetTime'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run1Fbk.OnsetTime')));
    fbk_on1 = (fbk_on1 -  int(df.loc[df[0] == 'Run1Fix.OnsetTime'].iloc[0][1])) / 1000 #(fbk_on1 - txt.Var2(strcmp(txt.Var1,'Run1Fix.OnsetTime'))) ./ 1000;
    fbk_dur = df.loc[df[0] == 'Run1Fbk.Duration'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run1Fbk.Duration')));
    
    #Was the participant accurate?
    #print(type(rt1))
    acc1 = ~(rt1.isna())  #~isnan(rt1);
    print(type(acc1))
    acc1 = acc1.replace({True: 'Hit', False: 'Miss'})

    rwd = df.loc[df[0] == 'Rwd'][1].reset_index() #txt.Var2(find(contains(txt.Var1,'Rwd'))); 
    
    # what was the target rt?
    target_RT1 =  df.loc[df[0] == 'Run1Tgt.Duration'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run1Tgt.Duration')));
    #target_RT1(target_RT1 < 0) = []; TODO
    
    trial_type1 = df.loc[df[0] == 'RunList1'][1]+ "-" #strcat(string(txt.Var2(find(contains(txt.Var1,'RunList1')))),'-');
    trial_type1 = trial_type1.replace('1-','win_5') #replace(trial_type1,'1-','Run1 Win $5.00');
    trial_type1 = trial_type1.replace('2-','win_1.5')#replace(trial_type1,'2-','Run1 Win $1.50');
    trial_type1 = trial_type1.replace('3-','win_0')#replace(trial_type1,'3-','Run1 Win $0.00');
    trial_type1 = trial_type1.replace('4-','lose_5')#replace(trial_type1,'4-','Run1 Lose $5.00');
    trial_type1 = trial_type1.replace('5-','lose_1.5')#replace(trial_type1,'5-','Run1 Lose $1.50');
    trial_type1 = trial_type1.replace('6-','lose_0')#replace(trial_type1,'6-','Run1 Lose $0.00');
    trial_type1 = trial_type1.reset_index()
    
    #final_MID=pd.concat([cue_on1[1],[trial_duration1[1]],rt1[1],acc1[1],fbk_on1[1], trial_type1[1]],axis=1)
    num_trials = len(cue_on1[1])
    #Anticipation Phase
    final_MID_ant=pd.concat([cue_on1[1], "ant_" + trial_type1[1]], axis = 1)
    final_MID_ant["duration"] = 2
    final_MID_ant.columns =['onset', 'trial_type', 'duration']

    #Reward Phase
    #TODO: all showing up as either hit or miss, not reflecting actual values
    #T1040 has a miss on the 9th trial 
    final_MID_rew=pd.concat([fbk_on1[1]],axis=1)
    final_MID_rew['trial_type'] = "rew_"+trial_type1[1]+ "_" + acc1[1]
    final_MID_rew["duration"] = 2
    final_MID_rew.columns =['onset', 'trial_type', 'duration']
    print(final_MID_rew)

    #Merge the two
    final_MID = final_MID_ant.append(final_MID_rew, ignore_index=True)
    final_MID.columns =['onset', 'trial_type', 'duration']
    #print(final_MID)
    
    #print(trial_type1)
     #MID RUN 2
    if(mid2):
        #TODO: figure out timing of cue onset and fbk onset. 
        #Right now it is relative to the start of R2
        cue_on2 = df.loc[df[0] == 'Run2Cue.OnsetTime'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run2Cue.OnsetTime')));
        cue_on2 = (cue_on2 - int(df.loc[df[0] == 'Run2Fix.OnsetTime'].iloc[0][1])) / 1000   
        cue_iti2 = df.loc[df[0] == 'Run2Dly3.OnsetTime'][1].astype(int).reset_index() #txt.Var2(find(contains(txt.Var1,'Run2Dly3.OnsetTime')));
        cue_iti2 = (cue_iti2 -  int(df.loc[df[0] == 'Run2Fix.OnsetTime'].iloc[0][1])) / 1000
        trial_duration2 = cue_iti2 - cue_on2
        
        rt2 = df.loc[df[0] == 'Run2Tgt.RT'][1].astype(int).reset_index()
        rt2 = rt2.replace(0, np.nan)
        
        fbk_on2 = df.loc[df[0] == 'Run2Fbk.OnsetTime'][1].astype(int).reset_index()
        fbk_on2 = (fbk_on2 -  int(df.loc[df[0] == 'Run2Fix.OnsetTime'].iloc[0][1])) / 1000  
        acc2 = ~(rt2.isna())
        acc2 = acc2.replace({True: 'Hit', False: 'Miss'})
        #target rt
        target_RT2 = df.loc[df[0] == 'Run2Tgt.Duration'][1].astype(int).reset_index() 
        #TODO target_RT2(target_RT2 < 0) = [];
        
        #trial types
        trial_type2 = df.loc[df[0] == 'RunList1'][1]+ "-" #strcat(string(txt.Var2(find(contains(txt.Var1,'RunList1')))),'-');
        trial_type2 = trial_type2.replace('1-','win_5') #replace(trial_type2,'1-','Run1 Win $5.00');
        trial_type2 = trial_type2.replace('2-','win_1.5')#replace(trial_type2,'2-','Run1 Win $1.50');
        trial_type2 = trial_type2.replace('3-','win_0')#replace(trial_type2,'3-','Run1 Win $0.00');
        trial_type2 = trial_type2.replace('4-','lose_5')#replace(trial_type2,'4-','Run1 Lose $5.00');
        trial_type2 = trial_type2.replace('5-','lose_1.5')#replace(trial_type2,'5-','Run1 Lose $1.50');
        trial_type2 = trial_type2.replace('6-','lose_0')#replace(trial_type2,'6-','Run1 Lose $0.00');
        trial_type2 = trial_type2.reset_index()
        
        num_trials = len(cue_on2[1])
        #Anticipation Phase
        final_MID2_ant=pd.concat([cue_on2[1] + 1000, "ant_" + trial_type2[1]], axis = 1)
        final_MID2_ant["duration"] = 2
        final_MID2_ant.columns =['onset', 'trial_type', 'duration']

        #Reward Phase
        #TODO: fix acc here too... same issue. 
        final_MID2_rew=pd.concat([fbk_on2[1] + 1000],axis=1)
        final_MID2_rew['trial_type'] = "rew_"+trial_type2[1]+ "_" + acc2[1]
        final_MID2_rew["duration"] = 2
        final_MID2_rew.columns =['onset', 'trial_type', 'duration']
        
        #Merge the two
        final_MID = final_MID.append(final_MID2_ant, ignore_index=True)
        final_MID = final_MID.append(final_MID2_rew, ignore_index=True)
        final_MID.columns =['onset', 'trial_type', 'duration']
        final_MID = final_MID.iloc[:,[0,2,1]]
        final_MID = final_MID.sort_values(by = 'onset') 
        
        
        final_MID.to_csv(basedir2 + subject + '/ses-1/func/' + subject + '_task-MID_events.tsv', sep="\t", index=False) 
        #print(final_MID)
        
        #final_MID2=pd.concat([cue_on2[1],trial_duration2[1],rt2[1],acc2[1],fbk_on2[1], trial_type2[1]],axis=1)
        #final_MID2.columns =['onset','duration','response_time','correct','feedback_onset', 'trial_type']
        #print(final_MID2)

        
def happy_mid(path):
    subject = path.split("/")[-4]
    df = file_to_df(path)
    df_to_timing_txt(df, subject, 1)

#for i in range(40): 
#    print(formated[i])    

dirs = ["/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural/sub-t1093",
        "/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural/sub-t1040"]
#MAIN
for path in dirs :
    dirs = ["/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural/sub-t1093",
            "/projects/b1108/studies/transitions2/data/raw/neuroimaging/behavioural/sub-t1040"]
    print(path)
    sus_out_files(path)
    
#formated = file_to_df(test_file)
#df_to_timing_txt(formated)

#for i in range(40): 
#    print(formated[i])