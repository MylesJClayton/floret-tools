
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
import argparse


def MkDirDict(InDirectory,OutDirectory):
    "builds dictionary of filepaths to use later"
    
    
    DirDict = {
        'in': InDirectory,
        'out': OutDirectory,
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



def MkInputList(directory):
    "finds all files in folder ending with nii.gz and adds them to a list"
    
    ImageFileList = []
    
    for file in os.listdir(directory):
        if file.endswith(".nii.gz"):
            file = file[:-7]
            ImageFileList.append(file)
    
    print(str(len(ImageFileList)) + " Input images were found" , flush=True)
    return(ImageFileList)
     
    
    
    

def main(inpath,outpath,troubleshoot=False,normalize=False):
    """initialize filters then crop for image in input directory"""
    
    DirDict = MkDirDict(inpath,outpath)                 #MAKE THIS WORK FOR SAVING THE DIFFERENT STAGES
    
    ImageFileList = MkInputList(inpath)
    
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
    
    os.chdir(DirDict['out'])
    imagedata = open("ImageData.txt", "w" )
    imagedata.write( "Image Name," + "Image Xsize," + "Image Ysize," + "ImageZsize," + "MaskVoxels")
    imagedata.close()
    
    for InputFilename in ImageFileList:
        os.chdir(DirDict['in'])
        print("Reading " + str(InputFilename) , flush=True)
        
        reader.SetFileName(str(InputFilename) + ".nii.gz")
        reader.SetFileName(InputFilename)
        Input = reader.Execute()
        #thresholdFilter.SetInput(reader.GetOutput())
        #rescaler.SetInput(thresholdFilter.GetOutput())
        
        print("Thresholding " + str(InputFilename) , flush=True)
        Output = otsu_filter.Execute(Input) #Gives binary mask of grain and cylinder
        Thresholded = Output
        
        
        print("Obtaining plant mask for  " + str(InputFilename) , flush=True)
        Output = Componentsfilter.Execute(Output)
        Output = Relabel.Execute(Output)
        Components = Output
        
        
        PlantMatter = sitk.BinaryThreshold( Components, 2, 2, 1, 0 )
        
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
        
        
        os.chdir(DirDict['out'])
        imagedata = open("ImageData.txt", "a")
        imagedata.write( "\n" + str(InputFilename) +"," + str(CroppedSize[0]) +"," + str(CroppedSize[1]) +"," + str(CroppedSize[2]) +"," + str(getstats.GetSum()))
        imagedata.close()
        
        if normalize:
            NormCropped = Normalize.Execute(Cropped)
            print("Saving image and mask of   " + str(InputFilename) , flush=True)
            os.chdir(DirDict['normcropped'])
            sitkwriter.SetFileName(str(InputFilename) + "crop.nii.gz")
            sitkwriter.Execute(NormCropped)
        else:    
            print("Saving image and mask of   " + str(InputFilename) , flush=True)
            os.chdir(DirDict['cropped'])
            sitkwriter.SetFileName(str(InputFilename) + "crop.nii.gz")
            sitkwriter.Execute(Cropped)
        
        if troubleshoot: #save intermediate steps if troubleshoot is true or -t is specified
            print('saving intermediate steps (troubleshoot mode)', flush=True)
            
            if normalize:
                os.chdir(DirDict['cropped'])
                sitkwriter.SetFileName(str(InputFilename) + "crop.nii.gz")
                sitkwriter.Execute(Cropped)
            
            os.chdir(DirDict['threshold'])
            sitkwriter.SetFileName(str(InputFilename) + "threshold.nii.gz")
            sitkwriter.Execute(Thresholded)
            
            os.chdir(DirDict['components'])
            sitkwriter.SetFileName(str(InputFilename) + "components.nii.gz")
            sitkwriter.Execute(Components)
            
            os.chdir(DirDict['mask'])
            sitkwriter.SetFileName(str(InputFilename) + "PlantMatter" + ".nii.gz")
            sitkwriter.Execute(PlantMatter)
        
            
            
            
            
        
        #writer.SetFileName(str(InputFilename) + ".nii.gz")
        #writer.SetInput(rescaler.GetOutput())
        #writer.Update()


    
    
    

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
    main(args.inpath,args.outpath,troubleshoot=args.troubleshoot,normalize=args.normalize)






