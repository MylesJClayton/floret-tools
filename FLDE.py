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

#Choose a suitable filepath and file names (filenames must end in seg.nii.gz)
os.chdir("/data/DATA/NPPC/FTcavitytest/Untitled Folder")
FloretFileNamesList = []

#Search for all files in directory that end with seg.nii.gz
for file in os.listdir("/data/DATA/NPPC/FTcavitytest/Untitled Folder"):
    if file.endswith("seg.nii.gz"):
        file = file[:-10]
        FloretFileNamesList.append(file)
        print(file)
        
print(str(len(FloretFileNamesList)) + " floret labels were found")


fieldnames = [ "FloretName", "Elongation", "Flatness", "LeastAxisLength", "MajorAxisLength", "Maximum2DDiameterColumn", "Maximum2DDiameterRow", "Maximum2DDiameterSlice", "Maximum3DDiameter", "MeshVolume", "MinorAxisLength", "Sphericity", "SurfaceArea", "SurfaceVolumeRatio", "VoxelVolume"]
with open('GrainData.csv', mode='w', newline='') as GrainData_csv:
    writer = csv.DictWriter(GrainData_csv, fieldnames=fieldnames)
    writer.writeheader()
with open('CavityData.csv', mode='w', newline='') as CavityData_csv:
    writer = csv.DictWriter(CavityData_csv, fieldnames=fieldnames)
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
   
reader = sitk.ImageFileReader()
reader.SetImageIO("NiftiImageIO")
sitkwriter = sitk.ImageFileWriter()
getstats = sitk.StatisticsImageFilter()
DilateImage = sitk.BinaryDilateImageFilter()
ErodeImage = sitk.BinaryErodeImageFilter()
    
CompleteCounter = 0
#For each listed floret label, create a cavity label and extract statistics for each part
for FloretFilename in FloretFileNamesList:
    print("Finding Cavity for " + str(FloretFilename))
    #read segmentation file
    reader.SetFileName(str(FloretFilename) + "seg.nii.gz")
    FloretLabel = reader.Execute();
    FloretLabel.SetSpacing((0.034, 0.034, 0.034)) #resolution of CT scanner in milimeters
    
    #obtain shell mask by thresholding labels 4 and 5 which are the palea and lemma respectively 
    GrainMask = sitk.BinaryThreshold( FloretLabel, 1, 1, 1, 0 )
    PaleaMask = sitk.BinaryThreshold( FloretLabel, 2, 2, 1, 0 )
    LemmaMask = sitk.BinaryThreshold( FloretLabel, 3, 3, 1, 0 )
    ShellMask = PaleaMask + LemmaMask #Shell mask obtained by elementwise addition of the masks
    ShellMaskNoCap = PaleaMask + LemmaMask
    
    #save result
    sitkwriter.SetFileName(str(FloretFilename) + "ShellMask.nii.gz")
    sitkwriter.Execute(ShellMask)
        
    #perform dilation on shell mask to form enclosed region
    #Dilation number (number of iterations of dilaion) is manually chosen
    #based on the size of the gap between the lemma and palea which needs to be filled

    """ Use this when doing grain growth
    dilationnumber = 12
    dilationcounter1 = 0
    print("dilating shell")
    
    while dilationcounter1 < dilationnumber:
        ShellMaskDilated = DilateImage.Execute(ShellMaskDilated)
        dilationcounter1 = dilationcounter1 + 1
    """
    
    "This section is for using pyradiomics to extract sphericity; length, width and height values; "
    #Define Dictionaries in which the first the first entry is the name of the floret
    GrainFeatures = {
            "FloretName" : FloretFilename
            }
    CavityFeatures = {
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
    
    print('Calculating shape features for ' + str(FloretFilename) + ' Cavity...',)
    shapeFeatures = shape.RadiomicsShape(FloretLabel, CavityLabel)
    
    # Set the features to be calculated
    # shapeFeatures.enableFeatureByName('Volume', True)
    shapeFeatures.enableAllFeatures()

    # Calculate the features, print result and append to the dictionary
    result = shapeFeatures.execute()
    print('done')
    
    print('Calculated shape features for ' + str(FloretFilename) + ' Cavity: ')
    for (key, val) in six.iteritems(result):
        CavityFeatures[key] = np.round(val, 4)
        print('  ', key, ':', np.round(val, 4))
    
    with open('CavityData.csv', mode='a', newline='') as CavityData_csv:
        writer = csv.DictWriter(CavityData_csv, fieldnames=fieldnames)
        writer.writerow(CavityFeatures)
    

    # Calculate the features, print result and append to the dictionary
    print('Calculating shape features for ' + str(FloretFilename) + ' Grain...',)
    shapeFeatures = shape.RadiomicsShape(FloretLabel, GrainMask)
    
    result = shapeFeatures.execute()
    print('done')
    
    print('Calculated shape features for ' + str(FloretFilename) + ' Grain: ')
    for (key, val) in six.iteritems(result):
        GrainFeatures[key] = np.round(val, 4)
        print('  ', key, ':', np.round(val, 4))
    
    with open('GrainData.csv', mode='a', newline='') as GrainData_csv:
        writer = csv.DictWriter(GrainData_csv, fieldnames=fieldnames)
        writer.writerow(GrainFeatures)
    
    
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
    print(str(CompleteCounter) + "/" + str(len(FloretFileNamesList)) + " Completed")
    

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
    parser.add_argument('-g', '--troubleshoot', action='store_true',
                        help='Save images  of intermediate steps threshold, components, and mask')

    args = parser.parse_args()
    print(args, flush=True)
    main(args.inpath,args.outpath,troubleshoot=args.troubleshoot,normalize=args.normalize)
    
    
