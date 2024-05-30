SUB=$1 #check if $ needed. 
echo $SUB
SES=$2 #check if $ needed. 
echo $SES


pydeface --verbose /Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/${SES}/anat/sub-${SUB}_${SES}_run-1_T1w.nii.gz 
mv /Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/${SES}/anat/sub-${SUB}_${SES}_run-1_T1w_defaced.nii.gz \
/Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/${SES}/anat/sub-${SUB}_${SES}_run-1_T1w.nii.gz
rm /Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/${SES}/${SUB}-*