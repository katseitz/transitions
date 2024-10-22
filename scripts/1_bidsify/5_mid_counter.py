import glob 
import csv
import pandas as pd

def tsv_reader(path):
    sub = path.split("/")[-4]
    ses = path.split("/")[-3]
    run = path.split("/")[-1][-17:-11]

    
    events = pd.read_csv(path, sep='\t')
    sorted_val_counts = events['trial_type'].value_counts().sort_index()
    sorted_types = sorted_val_counts.index.tolist()
    sorted_counts = sorted_val_counts.tolist()
    
    return [sub, run, sorted_types, sorted_counts]



def main():
    dirs = glob.glob("/projects/b1108/studies/transitions/data/raw/neuroimaging/bids/sub-t*/ses-1/func/*tsv") 
    df = pd.DataFrame()
    for i, path in enumerate(dirs):
        try:
            sub, run, sorted_types, sorted_counts = tsv_reader(path)
            df.at[i, 'sub'] = sub
            for j, type in enumerate(sorted_types):
                df.at[i, type] = sorted_counts[j]
            #df['total_count'] = df.sum(axis=1, numeric_only=True)
            #getting totals not working for some reason
        except Exception as e:
            print("FAILURE: " + path)
            print(traceback.format_exc())
    grouped_df = df.groupby('sub').sum().reset_index()
    grouped_df.to_csv("MID_trial_types_counts_akash_test_summed.csv")

if __name__ == "__main__":
    main()