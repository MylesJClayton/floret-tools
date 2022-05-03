# -*- coding: utf-8 -*-
"""

WARNING: THIS CAN OVERWRITE DATA IF BOTH FILENAME.ISQ;1 AND FILENAME.ISQ ARE BOTH IN THE TARGET DIRECTORY.
            ISQ;1 FILE WILL NOT BE KEPT, MAKE SURE YOU HAVE BACKUPS 

"""


import os

Directory = "D:/Work/NPPC/Pyscripts/ISQ2nii/InputISQ"

RenameListFileList = []

for file in os.listdir(Directory):
    if file.endswith(".ISQ;1"):

        file = file[:-6]
        RenameListFileList.append(file)
        
 
print(str(len(RenameListFileList)) + " files found ending with .ISQ;1" , flush=True)

for InputFilename in RenameListFileList:
    
    print("removing ;1 for " + str(InputFilename) , flush=True)

    os.rename( str(Directory) + "/" + str(InputFilename) + '.ISQ;1', str(Directory) + "/" + str(InputFilename) +  '.ISQ')
    