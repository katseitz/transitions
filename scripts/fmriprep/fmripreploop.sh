#!/usr/bin/bash

#SBATCH -A p31833
#SBATCH -p normal
#SBATCH -t 48:00:00
#SBATCH --mem=64G
#SBATCH -J fmriprep_single_sub


#!/usr/bin/bash

Usage() {
        echo ‘Usage: WIN_dsi_trk_loop <subject list>’
        exit 0
}

[ ‘$1’ = ‘’ ] && Usage

# Subject list for loop
subs=`cat ${1}`          # make sure txt file is full fib file names

for sub in ${subs}
do
echo $sub	
sbatch ./fmriprepsinglepartic.sh ${sub}

echo ‘done for subject: ‘ ${sub}
done
