import os
import glob
import json
import sys

#takes in a participant ID in format tXXXX
participant = sys.argv[1]

subjectPath = "/projects/b1108/studies/transitions/data/raw/neuroimaging/bids/sub-"+participant
print(subjectPath)
#finds all fmaps 
fmapsPath = os.path.join(subjectPath, 'ses-1', 'fmap', '*.json')
fmaps = glob.glob(fmapsPath)
#finds all functional files 
funcsPath = os.path.join(subjectPath, 'ses-1', 'func', '*.nii.gz')
funcs = glob.glob(funcsPath)

#adds short path of functional files to intended for field in FMAP
pathToRemove = subjectPath + '/'
funcs = list(map(lambda x: x.replace(pathToRemove, ''), funcs))
for fmap in fmaps:
	with open(fmap, 'r') as data_file:
		fmap_json = json.load(data_file)
	fmap_json['IntendedFor'] = funcs
	with open(fmap, 'w') as data_file:
		fmap_json = json.dump(fmap_json, data_file)

#TO-DO Figure out who/what scans are missing FMAPS and hard code special cases
#t1017 t1040 t1023 t1071 t1081 t1083 t1089 t1122 t1135 t1134 <-- intial hunch 
			
