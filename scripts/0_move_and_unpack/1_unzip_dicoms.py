import os
import glob
import json
import shutil

##Deal with that we're in an infinite loop
compressed_path = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/compressed/"
compressed_files = glob.glob(compressed_path + "*" )


for compressed in compressed_files:
    if(not(compressed == "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/compressed/complete")):
        print(compressed)
        #grabs subject id from compressed file name
        subject = compressed.split("/")[-1][0:5].lower()
        print(subject)
        #unzip/untar into participant dir
        uncom_path = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/"
        shutil.unpack_archive(compressed, uncom_path + subject)
        #shutil.move(compressed, "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/compressed/complete")

        '''
        if(subject = "t1040"):
            #MOVE MID1  MID2  REST3  REST4 to ses-1a, move everything to normal dir structure, 
            #remove ses folders
            source = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/t1040/t1040/ses-1b/*"
            dest = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/t1040/t1040/ses-1a"
            shutil.move(source, dest)
        elif(subject = "t1023"):
            #FMAP  REST3  REST4, move everything to normal dir structure, 
            #rename FMAPS so I know which to use when....
            #will need to script for this in the dicom to bids script
            #remove ses folders
            source = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/t1040/t1040/ses-1b/*"
            dest = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/t1040/t1040/ses-1a"
            shutil.move(source, dest)
            '''


            #TO-DO Figure out who/what scans are missing FMAPS and hard code special cases
            #t1017 t1040 t1023 t1071 t1081 t1083 t1089 t1122 t1135 t1134 <-- intial hunch 

    

