
"""
Takes 3D Nifti images of grains within a cylinder and outputs cropped image of just the plant matter.
Change MainDirctory string on line 13 to a suitable filepath

@author: Myles Clayton
"""
import itk
import SimpleITK as sitk
import os
import numpy as np
import csv
MainDirectory = "D:/Work/NPPC/Pyscripts/FloretCropper"
InputDirectory = MainDirectory + "/CropperInput"
#InputDirectory = "D:/Work/NPPC/MAIN IMAGES/UncroppedFlorets"  #This line allows the script to get input files from elsewhere (outside main directory)
OutputDirectory = MainDirectory + "/CropperOutput"
OutputMaskDirectory = OutputDirectory + "/PlantMatter"
ThresholdDirectory = OutputDirectory + "/Thresholded"
ComponentsDirectory = OutputDirectory + "/Components"

Dirs = (InputDirectory, OutputDirectory, OutputMaskDirectory, ThresholdDirectory, ComponentsDirectory)

Testdir = OutputDirectory + "/Test"
for dirpath in Dirs:
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    

RawImageFileList = []

for file in os.listdir(InputDirectory):
    if file.endswith(".nii.gz"):
        file = file[:-7]
        RawImageFileList.append(file)
        print(file)
        
        
print(str(len(RawImageFileList)) + " Input images were found" , flush=True)


PixelType = itk.UC
Dimension = 3


ImageType = itk.Image[PixelType, Dimension]

reader = sitk.ImageFileReader()
reader.SetImageIO("NiftiImageIO")
#reader = itk.ImageFileReader[ImageType].New()


sitkwriter = sitk.ImageFileWriter()
getstats = sitk.StatisticsImageFilter()
Normalize = sitk.NormalizeImageFilter()

#thresholdFilter = itk.OtsuMultipleThresholdsImageFilter[ImageType, ImageType].New()
#thresholdFilter.SetNumberOfHistogramBins(100)
#thresholdFilter.SetNumberOfThresholds(2)
#.SetLabelOffset(1)

otsu_filter = sitk.OtsuThresholdImageFilter()
otsu_filter.SetInsideValue(0)
otsu_filter.SetOutsideValue(1)

Componentsfilter = sitk.ConnectedComponentImageFilter()
Relabel = sitk.RelabelComponentImageFilter()
DilateImage = sitk.BinaryDilateImageFilter()
ErodeImage = sitk.BinaryErodeImageFilter()
#CropFloret = sitk.RegionOfInterestImageFilter()
#CropFloret.SetRegionOfInterest(VectorUInt32)

LabelShapestats = sitk.LabelShapeStatisticsImageFilter()
LabelStats = sitk.LabelStatisticsImageFilter()

Crop = sitk.ExtractImageFilter()
ROIF = sitk.RegionOfInterestImageFilter()

#rescaler = itk.RescaleIntensityImageFilter[ImageType, ImageType].New()
#rescaler.SetOutputMinimum(0)
#rescaler.SetOutputMaximum(2)

writer = itk.ImageFileWriter[ImageType].New()
Getminmax = sitk.MinimumMaximumImageFilter()


os.chdir(MainDirectory)
imagedata = open("ImageData.txt", "w" )
imagedata.write( "Image Name," + "Image Xsize," + "Image Ysize," + "ImageZsize," + "MaskVoxels")
imagedata.close()

for InputFilename in RawImageFileList:
    os.chdir(InputDirectory)
    print("Reading " + str(InputFilename) , flush=True)
    
    reader.SetFileName(str(InputFilename) + ".nii.gz")
    reader.SetFileName(InputFilename)
    Input = reader.Execute()
    #thresholdFilter.SetInput(reader.GetOutput())
    #rescaler.SetInput(thresholdFilter.GetOutput())
    
    print("Thresholding " + str(InputFilename) , flush=True)
    Output = otsu_filter.Execute(Input) #Gives binary mask of grain and cylinder
    Thresholded = Output
    
    os.chdir(ThresholdDirectory)
    sitkwriter.SetFileName(str(InputFilename) + "threshold.nii.gz")
    sitkwriter.Execute(Thresholded)
    
    
    
    print("Obtaining plant mask for  " + str(InputFilename) , flush=True)
    Output = Componentsfilter.Execute(Output)
    Output = Relabel.Execute(Output)
    Components = Output
    
    os.chdir(ComponentsDirectory)
    sitkwriter.SetFileName(str(InputFilename) + "components.nii.gz")
    sitkwriter.Execute(Components)
    
    PlantMatter = sitk.BinaryThreshold( Components, 2, 2, 1, 0 )
    
    os.chdir(OutputMaskDirectory)
    sitkwriter.SetFileName(str(InputFilename) + "PlantMatter" + ".nii.gz")
    sitkwriter.Execute(PlantMatter)
    
    
    Output = sitk.Cast(PlantMatter, sitk.sitkFloat32)
    
    LabelStats.Execute(Output,PlantMatter)
    LabelStats.GetBoundingBox(1) #Returns  xmin, xmax, ymin, ymax, zmin, zmax
    ROIF.SetRegionOfInterest(LabelStats.GetBoundingBox(1)) 
    
    a = LabelStats.GetBoundingBox(1)
    bignumpy = sitk.GetArrayFromImage(Input)
    
    if a[4] > 21:
        b = a[4] - 20
    else:
        b=0
            
        
    if a[5] + 21 < bignumpy.shape[0]:
        c = a[5] + 20
    else:
        c = bignumpy.shape[0] -1 
    
    
    #croppednumpy = bignumpy[ a[4]-100 : a[5]+30, a[2]-20 : a[3]+20, a[0]-30 : a[1]+20] # zmin:zmax,ymin:ymax,xmin:xmax
    croppednumpy = bignumpy[ b : c, a[2]-20 : a[3]+20, a[0]-20 : a[1]+20]
    
    Cropped = sitk.GetImageFromArray(croppednumpy)
    Cropped.SetSpacing(Input.GetSpacing())
    
    CroppedSize = [a[1]-a[0] , a[3]-a[2] , a[5]-a[4] ]
    print(CroppedSize)
    getstats.Execute(PlantMatter)
    
    
    os.chdir(MainDirectory)
    imagedata = open("ImageData.txt", "a")
    imagedata.write( "\n" + str(InputFilename) +"," + str(CroppedSize[0]) +"," + str(CroppedSize[1]) +"," + str(CroppedSize[2]) +"," + str(getstats.GetSum()))
    imagedata.close()
    
    print("Saving image and mask of   " + str(InputFilename) , flush=True)
    os.chdir(OutputDirectory)
    sitkwriter.SetFileName(str(InputFilename) + "crop.nii.gz")
    sitkwriter.Execute(Cropped)
    
    #writer.SetFileName(str(InputFilename) + ".nii.gz")
    #writer.SetInput(rescaler.GetOutput())
    #writer.Update()

print("done")









