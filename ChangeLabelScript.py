
"""
Created on Fri Jun 26 14:13:28 2020
Changes labels in segmentation files. Not for use with main images.
if -f 2 -t 3 given as arguments, label 2 in the image will be changed to label 3
"""

import SimpleITK as sitk
import os
import argparse

def MkInputList(directory):
    "finds all files in folder ending with nii.gz and adds them to a list"
    
    ImageFileList = []
    
    for file in os.listdir(directory):
        if file.endswith(".nii.gz"):
            file = file[:-7]
            ImageFileList.append(file)
    
    print(str(len(ImageFileList)) + " Input images were found" , flush=True)
    return(ImageFileList)

def main(args):
    
    InputFileList = MkInputList(args.inpath)
    
    if not os.path.exists(args.outpath):
        os.makedirs(args.outpath)
    
    #Initialize functions
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    sitkwriter = sitk.ImageFileWriter()
    
    #loop through each suitable file that was found
    for InputFilename in InputFileList:
        os.chdir(args.inpath)
        print("Reading " + str(InputFilename))
        #read file
        reader.SetFileName(str(InputFilename) + ".nii.gz")
        FloretLabelInput = reader.Execute()
        print("changing labels")
        #Threshhold function takes all voxels with value in between first two arguments and gives them new voxel value equal to 3rd argument
        #If outside of range set voxel value equal to 4th argument
        
        #FOR MERGING LEMMA AND PALEA LABELS INTO ONE CLASS
        mask = sitk.BinaryThreshold(FloretLabelInput, args.labelfrom, args.labelfrom, 1, 0)
        Out = (mask * (args.to - args.labelfrom) + FloretLabelInput)
        
        print('saving')
        if args.replace:
            os.chdir(args.inpath)
            sitkwriter.SetFileName(str(InputFilename) + ".nii.gz")
            sitkwriter.Execute(Out)
        else:
            #Save result in output folder
            os.chdir(args.outpath)
            sitkwriter.SetFileName(str(InputFilename) + ".nii.gz")
            sitkwriter.Execute(Out)
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description=(
        "Changes labels in segmentation files. Not for use with main images."
        "if -f 2 -t 3 given as arguments, label 2 in the image will be changed to label 3"
    ))
    
    parser.add_argument('-i', '--inpath',
                        type=str, default=None,
                        help='Input directory absolute path')
    parser.add_argument('-o', '--outpath',
                        type=str, default=None,
                        help='Output directory absolute path')
    parser.add_argument('-f', '--labelfrom',
                        type=int, default=None,
                        help='turn label f into label t')
    parser.add_argument('-t', '--labelto', action='store_true',
                        help='turn label f into label t')
    parser.add_argument('-r', '--replace', action='store_true',
                        help='If specified, this OVERWRITES the inputs, no outputs needed. SAVING BACKUPS RECOMMENDED' +
                        'Allows you to run this script multiple times in quick succession without changing -i or -o parameters')
    args = parser.parse_args()
    print(args, flush=True)
    main(args.inpath,args.outpath,troubleshoot=args.troubleshoot,normalize=args.normalize)







  
