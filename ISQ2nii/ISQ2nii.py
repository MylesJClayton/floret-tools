# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 15:39:25 2020

Convert .ISQ to .nii.gz

INSTRUCTIONS FOR USE
1)  Make a folder to contain this file, and within it, folders named InputISQ and Output
2)  Change MainDirectory string on line 21 as appropriate
3)  Place ISQs in inputISQ folder, all files within will be found automatically. 
4)  If necessary, run semicolonremover.py, ScancoImageIO will not load files with extension .ISQ;1 (directory string in semicolonremover.py will also need to be changed)
5)  run this file, compressed nifti files will be saved in output folder

@author: myles
"""

import os
import itk
import SimpleITK as sitk

MainDirectory = "D:/Work/NPPC/Pyscripts/ISQ2nii"
InputDirectory = MainDirectory + "/InputISQ"
OutputDirectory = MainDirectory + "/Output"


os.chdir("D:/Work/NPPC/Pyscripts/ISQ2nii")
InputFileList = []

#Find suitable files in given directory
for file in os.listdir(InputDirectory):
    if file.endswith(".ISQ"):
        file = file[:-4]
        InputFileList.append(file)
        print(file)
        
print(str(len(InputFileList)) + "Input ISQs were found")

PixelType = itk.ctype('unsigned char')
PixelType = itk.RGBPixel[PixelType]
ImageType = itk.Image[itk.F, 3]
WriterType = itk.ImageFileWriter[ImageType]


for InputFilename in InputFileList:
    os.chdir(InputDirectory)
    print("Loading ISQ for  " + str(InputFilename))
    
    file_name = str(str(InputFilename) + '.ISQ')
    ImageType = itk.Image[itk.F, 3]
    reader = itk.ImageFileReader[ImageType].New()
    imageio = itk.ScancoImageIO.New()
    reader.SetImageIO(imageio)
    reader.SetFileName(file_name)
    reader.Update()
    
    os.chdir(OutputDirectory)
    print("Saving image as Nifti")
    #Save result in output folder
    writer = WriterType.New()
    writer.SetFileName(str(InputFilename) + ".nii.gz")
    writer.SetInput(reader.GetOutput())
    writer.Update()

