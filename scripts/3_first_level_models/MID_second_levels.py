import pandas as pd
import glob
from nilearn.glm.second_level import SecondLevelModel
from nilearn.image import threshold_img
from nilearn.glm import threshold_stats_img
### EXAMPLE SCRIPT/DOCUMENTATION
#https://nilearn.github.io/dev/auto_examples/05_glm_second_level/plot_thresholding.html

mid_dir = '/projects/b1108/studies/transitions2/data/processed/neuroimaging/MID_processing/'

def second_level(ses):
    contrasts = ["ant_win_5or15_vs_ant_win_0",
                "ant_lose_5or15_vs_ant_lose_0",
                "ant_win_5or15_vs_ant_lose_5or15"]
    
    for contrast in contrasts:
        print('working on second level for ' + contrast)
        #Get the set of individual statstical maps (contrast estimates)
        contrast_tmaps = glob.glob(mid_dir + '*/' + ses + "/*" + contrast + '*')
        # define trivial design matrix for model for one sample t-test, with all 1s
        n_samples = len(files)
        design_matrix = pd.DataFrame([1] * n_samples, columns=["intercept"])
        
        # Next, we specify and estimate the model.
        second_level_model = SecondLevelModel(n_jobs=2).fit(
            contrast_tmaps, design_matrix=design_matrix
        )
        # Compute the only possible contrast: the one-sample test            
        z_map = second_level_model.compute_contrast(output_type="z_score")
        
        # Threshold the resulting map without multiple comparisons correction, abs(z) > 3.29 
        # (equivalent to p < 0.001), cluster size > 10 voxels.
        threshold_img(
        z_map,
        threshold=3.29,
        cluster_threshold=10,
        two_sided=True,
        )
        
def main():
    ses = 'ses-1'
    second_level(ses)
    
if __name__ == "__main__":
    main()
    