DIR=$1 #check if $ needed. 
echo $DIR
SES=$2 #check if $ needed. 
echo $SES


#Pipeline calls, one after another. 
source 1_dic_to_nifti.sh $DIR $SES
python 2_nifti_to_bids_naming.py $DIR
source 3_deface.sh $DIR $SES





