# -*- coding: utf-8 -*-
"""

WARNING: THIS CAN OVERWRITE DATA IF BOTH FILENAME.ISQ;1 AND FILENAME.ISQ ARE BOTH IN THE TARGET DIRECTORY.
            ISQ;1 FILE WILL NOT BE KEPT, MAKE SURE YOU HAVE BACKUPS 


Scanco's proprietary 3D image format is .ISQ
Sometimes, however the scanner will save CT scans with the extension .ISQ;1 
ISQ filetype can be opened by the itk library but the reader fails when given an ISQ;1 file 
This script simply saves a copy of the files without ";1" 
It essentially renames the file, but saves the original 

"""


import os
import argparse

def RemoveSemicolon(inpath,outpath): #Function can be used by other scripts by specifying paths

    if not os.path.exists(outpath):
            os.makedirs(outpath)
            
    InDir = inpath
    OutDir = outpath
    RenameListFileList = []
    
    for file in os.listdir(InDir):
        if file.endswith(".ISQ;1"):
            
            file = file[:-6]
            RenameListFileList.append(file)
 
    print(str(len(RenameListFileList)) + " files found ending with .ISQ;1" , flush=True)
    
    for InputFilename in RenameListFileList:
        os.rename( str(InDir) + "/" + str(InputFilename) + '.ISQ;1', str(OutDir) + "/" + str(InputFilename) +  '.ISQ')


def rename(args): #performs function with given argumensts
    
    if not os.path.exists(args.outpath):
            os.makedirs(args.outpath)
     
    RenameListFileList = []
    
    for file in os.listdir(args.inpath):
        if file.endswith(".ISQ;1"):
            
            file = file[:-6]
            RenameListFileList.append(file)
 
    print(str(len(RenameListFileList)) + " files found ending with .ISQ;1" , flush=True)
    
    for InputFilename in RenameListFileList:
        os.rename( str(args.inpath) + "/" + str(InputFilename) + '.ISQ;1', str(args.inpath) + "/" + str(InputFilename) +  '.ISQ')
     
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description=(
        "Find all .ISQs in --inpath directory and converts to .nii.gz "
        "as a new image "
    ))
    
    parser.add_argument('-i', '--inpath',
                        type=str, default=None,
                        help='Input directory absolute path')
    parser.add_argument('-o', '--outpath',
                        type=str, default=None,
                        help='Output directory absolute path')
    parser.add_argument('-r', '--rename', action='store_true',
                        help='Save images  of intermediate steps threshold, components, and mask')
    
    args = parser.parse_args()
    print(args, flush=True)
    rename(args)
