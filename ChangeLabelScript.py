
"""
Created on Fri Jun 26 14:13:28 2020
Changes labels for grain, palea, and lemma from 2, 4 and 5 respectively to 1, 2, and 3 respectively
@author: myles
"""

import SimpleITK as sitk
import os
import argparse

os.chdir("E:\WORK\pyscript test\ChangeLabels\Input")
InputFileList = []

#Find suitable files in given directory
for file in os.listdir("E:\WORK\Pyscripts\ChangeLabels\Input"):
    if file.endswith(".nii.gz"):
        file = file[:-7]
        InputFileList.append(file)
        print(file)
        
print(str(len(InputFileList)) + "Input Labels were found")


def main(args):
    #Prepare functions for use
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    sitkwriter = sitk.ImageFileWriter()
    getstats = sitk.StatisticsImageFilter()
    Normalize = sitk.NormalizeImageFilter()
    
    #loop through each suitable file that was found
    for InputFilename in InputFileList:
        os.chdir("E:\WORK\Pyscripts\ChangeLabels\Input")
        print("Processing " + str(InputFilename))
        print("reading")
        #read file
        reader.SetFileName(str(InputFilename) + ".nii.gz")
        FloretLabelInput = reader.Execute()
        print("changing labels")
        #Threshhold function takes all voxels with value in between first two arguments and gives them new voxel value equal to 3rd argument
        #If outside of range set voxel value equal to 4th argument
        
        #FOR MERGING LEMMA AND PALEA LABELS INTO ONE CLASS
        GrainLabel = sitk.BinaryThreshold( FloretLabelInput, 1, 1, 1, 0)
        ShellLabel = sitk.BinaryThreshold( FloretLabelInput, 2, 3, 2, 0)
        
        OutputFloretLabel = GrainLabel + ShellLabel
        
        """
        #FOR 2->1, 4->2, 5->3
        GrainLabel = sitk.BinaryThreshold( FloretLabelInput, 2, 2, 1, 0 )
        PaleaLabel = sitk.BinaryThreshold( FloretLabelInput, 4, 4, 2, 0 )
        LemmaLabel = sitk.BinaryThreshold( FloretLabelInput, 5, 5, 3, 0 )
        
        #Merge each label that we have made into a single image
        OutputFloretLabel = GrainLabel + PaleaLabel + LemmaLabel
        """
        print("saving")
        #Save result in output folder
        os.chdir("E:\WORK\Pyscripts\ChangeLabels\Output")
        sitkwriter.SetFileName(str(InputFilename) + ".nii.gz")
        sitkwriter.Execute(OutputFloretLabel)
        
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description=(
        "Identify grain in image, crop and save surrounding area "
        "as a new image "
    ))
    
    parser.add_argument('-i', '--inpath',
                        type=str, default=None,
                        help='Input directory absolute path')
    parser.add_argument('-o', '--outpath',
                        type=str, default=None,
                        help='Output directory absolute path')
    parser.add_argument('-f', '--from',
                        type=int, default=None,
                        help='turn label f into label t')
    parser.add_argument('-t', 'to', action='store_true',
                        help='turn label f into label t')
    parser.add_argument('-r', '--replace', action='store_true',
                        help='If specified, this OVERWRITES the inputs, no outputs needed. SAVING BACKUPS RECOMMENDED' +
                        'Allows you to run this script multiple times in quick succession without changing -i or -o parameters')
    args = parser.parse_args()
    print(args, flush=True)
    main(args.inpath,args.outpath,troubleshoot=args.troubleshoot,normalize=args.normalize)






  