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
import shutil
import argparse

def RemoveSemicolon(inpath,outpath,rename=True): #Function can be used by other scripts by specifying paths

    if not os.path.exists(outpath):
            os.makedirs(outpath)
            
    RenameListFileList = []
    
    for file in os.listdir(inpath):
        if file.endswith(".ISQ;1"):
            
            file = file[:-6]
            RenameListFileList.append(file)
 
    print(str(len(RenameListFileList)) + " files found ending with .ISQ;1" , flush=True)
    
    if rename:
        for InputFilename in RenameListFileList:
            os.rename( str(inpath) + "/" + str(InputFilename) + '.ISQ;1', str(inpath) + "/" + str(InputFilename) +  '.ISQ')
    else:
        for InputFilename in RenameListFileList:
            shutil.copy( str(inpath) + "/" + str(InputFilename) + '.ISQ;1', str(outpath) + "/" + str(InputFilename) +  '.ISQ')
 


def main(args): #performs function with given argumensts
    
    if not os.path.exists(args.outpath):
            os.makedirs(args.outpath)
     
    RenameListFileList = []
    
    for file in os.listdir(args.inpath):
        if file.endswith(".ISQ;1"):
            
            file = file[:-6]
            RenameListFileList.append(file)
 
    print(str(len(RenameListFileList)) + " files found ending with .ISQ;1" , flush=True)
    
    if args.rename:
        for InputFilename in RenameListFileList:
            os.rename( str(args.inpath) + "/" + str(InputFilename) + '.ISQ;1', str(args.inpath) + "/" + str(InputFilename) +  '.ISQ')
    else:
        for InputFilename in RenameListFileList:
            shutil.copy( str(args.inpath) + "/" + str(InputFilename) + '.ISQ;1', str(args.outpath) + "/" + str(InputFilename) +  '.ISQ')
 
    
    
    
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
                        help='Rename ISQ;1 to ISQ in same directory '
                        'Much faster for bulk processing but WILL NOT keep originals')
    
    args = parser.parse_args()
    print(args, flush=True)
    
    rename(args)
    
