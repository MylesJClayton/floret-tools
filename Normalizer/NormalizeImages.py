
"""
Created on Thu Jun 25 13:47:35 2020
Normalize nifti files to zero mean and unit variance
yields better performance from CNNs
@author: Myles Clayton
"""

import SimpleITK as sitk
import os


MainDirectory = "D:/Work/NPPC/Pyscripts/ZMUV/"
InputDirectory = MainDirectory + "/RawImagesInput"
OutputDirectory = MainDirectory + "/ZMUVImagesOutput"

os.chdir(InputDirectory)
RawImageFileList = []

for file in os.listdir(InputDirectory):
    if file.endswith(".nii.gz"):
        file = file[:-7]
        RawImageFileList.append(file)
        print(file)
        
        
print(str(len(RawImageFileList)) + " Raw images were found")

reader = sitk.ImageFileReader()
reader.SetImageIO("NiftiImageIO")
sitkwriter = sitk.ImageFileWriter()
getstats = sitk.StatisticsImageFilter()
Normalize = sitk.NormalizeImageFilter()

for RawImageFilename in RawImageFileList:
    os.chdir(InputDirectory)
    print("Normalizing " + str(RawImageFilename))
    
    reader.SetFileName(str(RawImageFilename) + ".nii.gz")
    RawImage = reader.Execute()
    
    NormalizedImage = Normalize.Execute(RawImage)
    getstats.Execute(NormalizedImage)
    print("Zero mean test for " + str(RawImageFilename) + ", mean is: " + str(getstats.GetMean()))
    print("Unit variance test, variance is: " + str(getstats.GetVariance()))
    
    os.chdir(OutputDirectory)
    sitkwriter.SetFileName(str(RawImageFilename) + ".nii.gz")
    sitkwriter.Execute(NormalizedImage)










