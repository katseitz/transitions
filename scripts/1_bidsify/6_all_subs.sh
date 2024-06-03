SES=$1 #check if $ needed. 
echo $SES

python 0_unzip_dicoms.py

for DIR in /Users/katharinaseitz/Documents/dicom_conversions/dicoms/uncompressed/*; do
    BASE_DIR=$(basename $DIR)
    #[ -d "$dirs" ] && [ -n "$(ls -A $dirs)" ]
    if [ ! -d "/Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$BASE_DIR/ses-1/anat" ]; then
        echo $BASE_DIR
        source /Users/katharinaseitz/Documents/dicom_conversions/scripts/5_single_sub.sh $BASE_DIR $SES
    fi 
done