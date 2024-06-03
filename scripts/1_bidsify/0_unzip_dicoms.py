import glob
import shutil
import pydicom


#load paths and files.
compressed_path = "/Users/katharinaseitz/Documents/dicom_conversions/dicoms/compressed/" 
compressed_files = glob.glob(compressed_path + "*" )
uncompressed_path = "/Users/katharinaseitz/Documents/dicom_conversions/dicoms/uncompressed/" 
uncompressed_files = glob.glob(uncompressed_path + "*" )
compressed_files = compressed_files

print(compressed_files)
for compressed in compressed_files:    
    print(compressed)
    if(compressed.split("/")[-1][0] == 'T' or compressed.split("/")[-1][0] == 't'):
        subject = compressed.split("/")[-1][0:5].lower()
    elif(compressed.split("/")[-1][0] == 'F' or compressed.split("/")[-1][0] == 'f'):
        subject = compressed.split("/")[-1][0:6].lower()
    else:
        print(compressed + " is not a valid subject path")
        break
    #if file hasn't already been unzipped, proceed
    if(not(uncompressed_path + subject in uncompressed_files)):
        print(subject)
        #unzip/untar into participant dir
        shutil.unpack_archive(compressed, uncompressed_path + subject + '_TEMP')
        #check to make sure file name and participant ID match
        dicoms = glob.glob(uncompressed_path  + subject + '_TEMP' + "/*/*/*")
        dcm_path = dicoms[0]
        dcm = pydicom.dcmread(dcm_path, force = True)
        if hasattr(dcm, 'PatientID'):
                if dcm.PatientID.lower() == subject:
                    #if they are the same, remove the _TEMP ending to file
                    shutil.move(uncompressed_path + subject + '_TEMP', uncompressed_path + subject)
                else:
                    print("ERROR: .zip participant ID does not match ID in dicom header")
        else:
            print("PatientID field missing from dicom header") 

    

