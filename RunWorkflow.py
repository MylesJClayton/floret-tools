# -*- coding: utf-8 -*-
"""
Takes a directory containing ISQ files as inputs -i
Converts and crops the images
Places outputs in specified folder -o
"""

import argparse
import ISQ2nii
import os
import FloretCropper 

def MkDirDict(InDirectory,OutDirectory):
    "builds dictionary of filepaths to use later"
    
    
    DirDict = {
        'in': InDirectory,
        'out': OutDirectory,
        'bignifti': OutDirectory + "/NiftiUncropped",
        'cropped': OutDirectory + "/CroppedImages",
        'normcropped': OutDirectory + "/CroppedNormalized",
        'mask': OutDirectory + "/ImageMasks",
        'threshold': OutDirectory + "/Thresholded",
        'components': OutDirectory + "/Components"
        }
    for path in DirDict:
        if not os.path.exists(DirDict[path]):
            os.makedirs(DirDict[path])
    
    return(DirDict)



def main(args):
    
    DirDict = MkDirDict(args.inpath,args.outpath) #use this to manage filepaths
    ISQ2nii.main(DirDict['in'],DirDict['bignifti']) #tell ISQ2nii where to save converted files to
    FloretCropper.main(DirDict['bignifti'],DirDict['out']) #floretcropper saves outputs to subdirectories of outpath
    
    
    
    
    

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
    parser.add_argument('-t', '--troubleshoot', action='store_true',
                        help='Save images  of intermediate steps threshold, components, and mask')
    parser.add_argument('-n', '--normalize', action='store_true',
                        help='Normalize cropped images to have zero mean and unit variance across all voxels')
    args = parser.parse_args()
    print(args, flush=True)
    main(args)



