import pandas as pd
import numpy as np  
import glob
import csv
import itertools, os, glob

path_conn = ('/projects/b1108/studies/transitions/data/processed/neuroimaging/seitzman_networks_rest/') #or use below for same data
save_dir1 = ('/projects/b1108/studies/transitions/data/processed/neuroimaging/seitzman_networks_rest/final_data')
allFiles_conn = glob.glob(os.path.join(path_conn, '*/*/*corrmat.csv'))

#output lists
network_list_output = []
network_output = []

#loop through each file
for file in allFiles_conn:
    parts = file.split("/")[-1].split("_")
    subject = parts[0] #identify particiapnt
    run = parts[2] #identify network
    network = parts[3]
    print(subject, run, network)
    mattcor = pd.read_csv(file, header=None) #read the network matrix
    mattcor_z = mattcor.transform(lambda x: np.arctanh(x)) #fishers r to z transformation on r values
    mattcor_z.values[np.tril_indices_from(mattcor_z)] = np.nan #fill below the diagonal with nans
    average = mattcor_z.unstack().mean() #average across all z values that are not nans
    network_list_output.append([subject, run, network, average])
    network_output.append({'participant': subject, 'run': run, 'network': network, 'value': average}) #preferred format
    

Output = pd.DataFrame(network_output)
path_output_save1 = save_dir1 + os.path.sep + 'transitions_seitzman_rsfMRIConnectivity_long_062724.csv'
Output.to_csv(path_output_save1, index=False) #do no save the index column

#convert df to wide format (from long format)
#https://towardsdatascience.com/long-and-wide-formats-in-data-explained-e48d7c9a06cb
#Wide_Output = Output.pivot(index=['participant', 'run'], columns='network', values='value').reset_index()

#save data to both local and ACNL drives

#path_output_save1 = save_dir1 + os.path.sep + 'transitions_seitzman_rsfMRIConnectivity_wide_062724.csv'
#Wide_Output.to_csv(path_output_save1, index=False) #do no save the index column
