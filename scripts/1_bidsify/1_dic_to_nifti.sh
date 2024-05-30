
SUB=$1
echo $SUB
SES=$2
echo $SES

scan_folders=/Users/katharinaseitz/Documents/dicom_conversions/dicoms/uncompressed/$SUB/*/*
echo $scan_folders

if [ ! -d "/Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB" ]; then
    mkdir /Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB
fi
if [ ! -d "/Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/$SES" ]; then
    mkdir /Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/$SES     
fi

for SCAN in $scan_folders; do # Whitespace-safe but not recursive.
    echo $SCAN
    OUTPUT=/Users/katharinaseitz/Documents/dicom_conversions/bids/sub-$SUB/$SES
    echo $OUTPUT
    dcm2niix -b y -z o -w 1 -f %n--%d--s%s--e%e -o $OUTPUT $SCAN
done
