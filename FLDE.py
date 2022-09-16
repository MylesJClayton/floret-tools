"""
4 csv files with column headings are written to contain the measurements for the grain, cavity, lemma and palea
The for loop takes all named input floret labels with awn=1, grain=2, bran layer=3, palea=4, lemma=5 and embryo=6
NOTE: Awn is not currently used for any calculations.
A mask of the shell is created, saved and then dilated
volume is filled and dilated shell mask subtracted to create a shrunken cavity.
Cavity is then dilated to fill most of the shell with a few gaps, most notably, the inside corners. 
    This is a heavily smoothed version
Cavity then goes through a process which dilates it and then subtracts the shell from it over multiple iterations.
    This makes it fill the aforementioned gaps and corners, but it can 'leak' through the gaps in the shell because these gaps aren't being subtracted.
These 'leaks' are removed by a final process of erosion (because they are thin enough to be removed by this method) and then dilation to refil the cavity
Shell mask is then subtracted again to remove any pixels that may have overstepped the boundary of the shell. 
Afterwards stats are calculated using pyradiomics and they are placed into a dictionary and printed
Finally a line into each CSV file is created from the dictionary of the respecive floret part's stats 

Change folder path on line 27 to something suitable

"""
import SimpleITK as sitk
import os 
from radiomics import shape
import six
import csv
import numpy as np
import argparse 

def MkDirDict(InDirectory,OutDirectory,growingspace):
    "builds dictionary of filepaths to use later"
    
    if growingspace > 0:
        DirDict = {
            'in': InDirectory,
            'out': OutDirectory,
            'shellmask': OutDirectory + "/ShellMasks",
            'GrainSpace': OutDirectory + "/GrainGrowingSpace",
            }
    else:
        DirDict = {
            'in': InDirectory,
            'out': OutDirectory,
            'shellmask': OutDirectory + "/ShellMasks"
            }

    for path in DirDict:
        if not os.path.exists(DirDict[path]):
            os.makedirs(DirDict[path])
    
    return(DirDict)


def MkInputList(directory):
    "finds all files in folder ending with seg.nii.gz and adds them to a list"
    
    ImageFileList = []
    
    for file in os.listdir(directory):
        if file.endswith("seg.nii.gz"):
            file = file[:-10]
            ImageFileList.append(file)
    
    print(str(len(ImageFileList)) + " Input images were found" , flush=True)
    return(ImageFileList)
     
def GrainGrowingSpace(GrainMask,ShellMask,grownumber):
    DilateImage = sitk.BinaryDilateImageFilter()
    ErodeImage = sitk.BinaryErodeImageFilter()
    getstats = sitk.StatisticsImageFilter()
    if grownumber == 0:
        EmptyLabel = GrainMask - GrainMask
        return(EmptyLabel) #This is an image the same size as the image but contains only zeroes.  
    else:
        dilationnumber = grownumber
        dilationcounter = 0
        print("dilating grain")

        Space = GrainMask
        while dilationcounter < dilationnumber:
            Space = DilateImage.Execute(Space)
            Space = Space - ShellMask + 1
            Space = sitk.BinaryThreshold( Space, 2, 2, 1, 0 )
            dilationcounter += 1
        Space = Space - GrainMask

        getstats.Execute(Space)
        volume = getstats.GetSum() * 0.034**3 #voxel count multiplied by milimeters per voxel
        return(Space,volume)
    

def main(inpath,outpath,growingspace=0,troubleshoot=False):
    """Extract measurements from each label """

    #Initialize functions and filters
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    sitkwriter = sitk.ImageFileWriter()
    getstats = sitk.StatisticsImageFilter()

    DirDict = MkDirDict(inpath,outpath,growingspace)
    InputLabelList = MkInputList(inpath)

    print(str(len(InputLabelList)) + " floret labels were found")

    os.chdir(DirDict['out'])
    fieldnames = [ "FloretName", "Elongation", "Flatness", "LeastAxisLength", "MajorAxisLength", "Maximum2DDiameterColumn", "Maximum2DDiameterRow", "Maximum2DDiameterSlice", "Maximum3DDiameter", "MeshVolume", "MinorAxisLength", "Sphericity", "SurfaceArea", "SurfaceVolumeRatio", "VoxelVolume"]
    Grainfieldnames = [ "FloretName", "Elongation", "Flatness", "LeastAxisLength", "MajorAxisLength", "Maximum2DDiameterColumn", "Maximum2DDiameterRow", "Maximum2DDiameterSlice", "Maximum3DDiameter", "MeshVolume", "MinorAxisLength", "Sphericity", "SurfaceArea", "SurfaceVolumeRatio", "VoxelVolume", "EmptySurroundingSpace","SpaceToGrainSurfaceRatio"]
    with open('GrainData.csv', mode='w', newline='') as GrainData_csv:
        writer = csv.DictWriter(GrainData_csv, fieldnames=Grainfieldnames)
        writer.writeheader()
    with open('GrowingSpaceData.csv', mode='w', newline='') as GrowingSpaceData_csv:
        writer = csv.DictWriter(GrowingSpaceData_csv, fieldnames=fieldnames)
        writer.writeheader()
    with open('PaleaData.csv', mode='w', newline='') as PaleaData_csv:
        writer = csv.DictWriter(PaleaData_csv, fieldnames=fieldnames)
        writer.writeheader()
    with open('LemmaData.csv', mode='w', newline='') as LemmaData_csv:
        writer = csv.DictWriter(LemmaData_csv, fieldnames=fieldnames)
        writer.writeheader()
    with open('ShellData.csv', mode='w', newline='') as ShellData_csv:
        writer = csv.DictWriter(ShellData_csv, fieldnames=fieldnames)
        writer.writeheader()
   
   
    CompleteCounter = 0
    #For each listed floret label, create a cavity label and extract statistics for each part
    for FloretFilename in InputLabelList:
        
        #read segmentation/label file
        os.chdir(DirDict['in'])
        reader.SetFileName(str(FloretFilename) + "seg.nii.gz")
        FloretLabel = reader.Execute()
        FloretLabel.SetSpacing((0.034, 0.034, 0.034)) #resolution of CT scanner in milimeters
        
        #obtain shell mask by thresholding labels 2 and 3 which are the palea and lemma respectively 
        GrainMask = sitk.BinaryThreshold( FloretLabel, 1, 1, 1, 0 )
        PaleaMask = sitk.BinaryThreshold( FloretLabel, 2, 2, 1, 0 )
        LemmaMask = sitk.BinaryThreshold( FloretLabel, 3, 3, 1, 0 )
        ShellMask = PaleaMask + LemmaMask #Shell mask obtained by elementwise addition of the masks
        
        #save result
        os.chdir(DirDict['shellmask'])
        sitkwriter.SetFileName(str(FloretFilename) + "ShellMask.nii.gz")
        sitkwriter.Execute(ShellMask)
        
        "This section is for using pyradiomics to extract sphericity; length, width and height values; "
        #Define Dictionaries in which the first entry is the name of the floret
        GrainFeatures = {
                "FloretName" : FloretFilename
                }
        SpaceFeatures = {
                "FloretName" : FloretFilename
                }
        PaleaFeatures = {
                "FloretName" : FloretFilename
                }
        LemmaFeatures = {
                "FloretName" : FloretFilename
                }
        ShellFeatures = {
                "FloretName" : FloretFilename
                }
        
        os.chdir(DirDict['out'])
        
        # Calculate the features, print result and append to the dictionary
        print('Calculating shape features for ' + str(FloretFilename) + ' Grain...',)
        shapeFeatures = shape.RadiomicsShape(FloretLabel, GrainMask)
        
        # Set the features to be calculated
        # shapeFeatures.enableFeatureByName('Volume', True)
        shapeFeatures.enableAllFeatures()

        result = shapeFeatures.execute()
        print('done')
        
        print('Calculated shape features for ' + str(FloretFilename) + ' Grain: ')
        for (key, val) in six.iteritems(result):
            GrainFeatures[key] = np.round(val, 4)
            print('  ', key, ':', np.round(val, 4))
        
        #This is where we calculate raio of growingspace to surface area of grain and insert it into the csv (if growinspace argument is used)
        if growingspace>0:
            #perform dilation on grain mask to obtain available growing space for the grain
            Space,SpaceVolume = GrainGrowingSpace(GrainMask,ShellMask,growingspace) #Dilation number (number of iterations of dilaion) is manually chosen with the growingspace argument
            GrainFeatures["EmptySurroundingSpace"] = SpaceVolume
            GrainFeatures["SpaceToGrainSurfaceRatio"] =  SpaceVolume / GrainFeatures["SurfaceArea"]

            #Save Spacemask
            os.chdir(DirDict['GrainSpace'])
            sitkwriter.SetFileName(str(FloretFilename) + "GrainGrowingSpace_seg.nii.gz")
            sitkwriter.Execute(Space)
            os.chdir(DirDict['out'])

        

        with open('GrainData.csv', mode='a', newline='') as GrainData_csv:
            writer = csv.DictWriter(GrainData_csv, fieldnames=Grainfieldnames)
            writer.writerow(GrainFeatures)
        
        
        # Calculate the features, print result and append to the dictionary
        print('Calculating shape features for ' + str(FloretFilename) + 'GrowingSpace...',)
        shapeFeatures = shape.RadiomicsShape(FloretLabel, Space)
        result = shapeFeatures.execute()
        print('done')
        
        print('Calculated shape features for ' + str(FloretFilename) + ' GrowingSpace: ')
        for (key, val) in six.iteritems(result):
                SpaceFeatures[key] = np.round(val, 4)
                print('  ', key, ':', np.round(val, 4))
        
        with open('GrowingSpaceData.csv', mode='a', newline='') as GrowingSpaceData_csv:
            writer = csv.DictWriter(GrowingSpaceData_csv, fieldnames=fieldnames)
            writer.writerow(SpaceFeatures)
        

        # Calculate the features, print result and append to the dictionary
        print('Calculating shape features for ' + str(FloretFilename) + ' Palea...',)
        shapeFeatures = shape.RadiomicsShape(FloretLabel, PaleaMask)
        result = shapeFeatures.execute()
        print('done')
        
        print('Calculated shape features for ' + str(FloretFilename) + ' Palea: ')
        for (key, val) in six.iteritems(result):
                PaleaFeatures[key] = np.round(val, 4)
                print('  ', key, ':', np.round(val, 4))
        
        with open('PaleaData.csv', mode='a', newline='') as PaleaData_csv:
            writer = csv.DictWriter(PaleaData_csv, fieldnames=fieldnames)
            writer.writerow(PaleaFeatures)
        

        # Calculate the features, print result and append to the dictionary
        print('Calculating shape features ' + str(FloretFilename) + ' for Lemma...',)
        shapeFeatures = shape.RadiomicsShape(FloretLabel, LemmaMask)
        result = shapeFeatures.execute()
        print('done')

        print('Calculated shape features for ' + str(FloretFilename) + ' Lemma: ')
        for (key, val) in six.iteritems(result):
            LemmaFeatures[key] = np.round(val, 4)
            print('  ', key, ':', np.round(val, 4))
        
        with open('LemmaData.csv', mode='a', newline='') as LemmaData_csv:
            writer = csv.DictWriter(LemmaData_csv, fieldnames=fieldnames)
            writer.writerow(LemmaFeatures)


        # Calculate the features, print result and append to the dictionary
        print('Calculating shape features ' + str(FloretFilename) + ' for Shell...',)
        shapeFeatures = shape.RadiomicsShape(FloretLabel, ShellMask)
        result = shapeFeatures.execute()
        print('done')

        print('Calculated shape features for ' + str(FloretFilename) + ' Shell: ')
        for (key, val) in six.iteritems(result):
            ShellFeatures[key] = np.round(val, 4)
            print('  ', key, ':', np.round(val, 4))
        
        with open('ShellData.csv', mode='a', newline='') as ShellData_csv:
            writer = csv.DictWriter(ShellData_csv, fieldnames=fieldnames)
            writer.writerow(ShellFeatures)
        
        print("Process complete for " + str(FloretFilename))
        CompleteCounter = CompleteCounter + 1
        print(str(CompleteCounter) + "/" + str(len(InputLabelList)) + " Completed")
        

    print("Data extraction completed for all listed floret labels")
    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description=(
        "Analyse the shape of labels in the *seg.nii.gz files in the specified folder."
        "Save extracted shape statistics in .csv files."
    ))
    
    parser.add_argument('-i', '--inpath',
                        type=str, default=None,
                        help='Input directory absolute path')
    parser.add_argument('-o', '--outpath',
                        type=str, default=None,
                        help='Output directory absolute path')
    parser.add_argument('-t', '--troubleshoot', action='store_true',
                        help='Save images  of intermediate steps threshold, components, and mask')
    parser.add_argument('-g', '--growingspace',
                        type=int, default=0,
                        help='Number of dilaions of the space around the grain. <10 is recommended')

    args = parser.parse_args()
    print(args, flush=True)
    main(args.inpath,args.outpath,growingspace=args.growingspace,troubleshoot=args.troubleshoot)
    
    
