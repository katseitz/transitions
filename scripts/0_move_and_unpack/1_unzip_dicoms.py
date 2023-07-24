import os
import glob
import json
import shutil
import sys

ses = sys.argv[1]

##Deal with that we're in an infinite loop
compressed_path = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/compressed/" + ses + "/"
compressed_files = glob.glob(compressed_path + "*" )
uncompressed_path = "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/uncompressed/" + ses + "/"
uncompressed_files = glob.glob(uncompressed_path + "*" )
problem_subs = ["t1135", "t1120", "t1123", "t1140"]
#print(uncompressed_files)

for compressed in compressed_files:
    if(not(compressed == "/projects/b1108/studies/transitions2/data/raw/neuroimaging/dicoms/compressed/complete")):
        
        #print(compressed)
        #grabs subject id from compressed file name
        subject = compressed.split("/")[-1][0:5].lower()
        if(not(uncompressed_path + subject in uncompressed_files) and not(subject in problem_subs)):
            #print(uncompressed_path + subject)
            print(subject)
        #unzip/untar into participant dir
            shutil.unpack_archive(compressed, uncompressed_path + subject)

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

    

