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

#Choose a suitable filepath and file names (filenames must end in seg.nii.gz)
os.chdir("E:\work\pyscript test")
FloretFileNamesList = []

#Search for all files in directory that end with seg.nii.gz
for file in os.listdir("E:\work\pyscript test"):
    if file.endswith("seg.nii.gz"):
        file = file[:-9]
        FloretFileNamesList.append(file)
        print(file)
        
print(str(len(FloretFileNamesList)) + " floret labels were found")


fieldnames = [ "FloretName", "Elongation", "Flatness", "LeastAxisLength", "MajorAxisLength", "Maximum2DDiameterColumn", "Maximum2DDiameterRow", "Maximum2DDiameterSlice", "Maximum3DDiameter", "MeshVolume", "MinorAxisLength", "Sphericity", "SurfaceArea", "SurfaceVolumeRatio", "VoxelVolume"]
GrainFieldnames = [ "FloretName", "Elongation", "Flatness", "LeastAxisLength", "MajorAxisLength", "Maximum2DDiameterColumn", "Maximum2DDiameterRow", "Maximum2DDiameterSlice", "Maximum3DDiameter", "MeshVolume", "MinorAxisLength", "Sphericity", "SurfaceArea", "SurfaceVolumeRatio", "VoxelVolume", "PercentageOfCavityFilled", "BranPercentage"]
with open('GrainData.csv', mode='w', newline='') as GrainData_csv:
    writer = csv.DictWriter(GrainData_csv, fieldnames=GrainFieldnames)
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
   
reader = sitk.ImageFileReader()
reader.SetImageIO("NiftiImageIO")
sitkwriter = sitk.ImageFileWriter()
getstats = sitk.StatisticsImageFilter()
CompleteCounter = 0
#For each listed floret label, create a cavity label and extract statistics for each part
for FloretFilename in FloretFileNamesList:
    print("Finding Cavity for " + str(FloretFilename))
    #read segmentation file
    reader.SetFileName(str(FloretFilename) + "seg.nii.gz")
    FloretLabel = reader.Execute();
    FloretLabel.SetSpacing((0.034, 0.034, 0.034)) #resolution of CT scanner in milimeters
    
    #obtain shell mask by thresholding labels 4 and 5 which are the palea and lemma respectively 
    PaleaMask = sitk.BinaryThreshold( FloretLabel, 4, 4, 1, 0 )
    LemmaMask = sitk.BinaryThreshold( FloretLabel, 5, 5, 1, 0 )
    CapMask = sitk.BinaryThreshold( FloretLabel, 6, 6, 1, 0 )
    ShellMask = PaleaMask + LemmaMask + CapMask #Shell mask obtained by elementwise addition of the masks
    ShellMaskNoCap = PaleaMask + LemmaMask
    
    #save result
    sitkwriter.SetFileName(str(FloretFilename) + "ShellMask.nii.gz")
    sitkwriter.Execute(ShellMask)
    #Create masks of grain, bran layer and embryo
    GrainMask = sitk.BinaryThreshold( FloretLabel, 2, 2, 1, 0 )
    BranMask = sitk.BinaryThreshold( FloretLabel, 3, 3, 1, 0 )
    
    #Merge masks
    TotalGrainMask = GrainMask + BranMask
    
    #perform dilation on shell mask to form enclosed region
    #Dilation number (number of iterations of dilaion) is manually chosen
    #based on the size of the gap between the lemma and palea which needs to be filled
    ShellMaskDilated = ShellMask
    DilateImage = sitk.BinaryDilateImageFilter()
    ErodeImage = sitk.BinaryErodeImageFilter()
    
    dilationnumber = 12
    dilationcounter1 = 0
    print("dilating shell")
    
    while dilationcounter1 < dilationnumber:
        ShellMaskDilated = DilateImage.Execute(ShellMaskDilated)
        dilationcounter1 = dilationcounter1 + 1
    
    print("done")
    #Fill dilated shell to get dilated shell + cavity 
    #cavity has been shrunk due to shell dilation
    FillCavity = sitk.BinaryFillholeImageFilter()
    ShellandCavity = FillCavity.Execute(ShellMaskDilated)
    
    #subtract dilated shell from the sum , leaving shrunk cavity
    CavityShrunk = ShellandCavity - ShellMaskDilated
    
    #Dilate cavity equal number of times to dilation counter
    CavityDilation = CavityShrunk
    dilationcounter2 = 0
    print("dilating cavity")
    while dilationcounter2 < dilationcounter1:
        CavityDilation = DilateImage.Execute(CavityDilation)
        dilationcounter2 = dilationcounter2 + 1
        #Creates a smoothed cavity with quite a bit of unlabelled empty space near inside corners
    
    ShellMask3Dilations = DilateImage.Execute(DilateImage.Execute(DilateImage.Execute(ShellMask)))
    DilateErodeLeakIterations = 0
    while DilateErodeLeakIterations < 3:
        print("done")
        #Expand to fill area, subtract shellmask from cavity, remove parts that overstepped the shell
        FillIterations = 5
        Iterationcounter = 0 
        print("performing 4 iterations of dilation and shell subtraction")
        while Iterationcounter < FillIterations:
            CavityDilation = DilateImage.Execute(CavityDilation)
            CavityDilation = CavityDilation - ShellMask3Dilations + 1
            CavityDilation = sitk.BinaryThreshold( CavityDilation, 2, 2, 1, 0 ) #possible outcomes: 0-0+1=1 1-0+1=2 0-1+1=0 1-1+1=1
            Iterationcounter = Iterationcounter + 1
            #This causes a small amount of the label to leak through the gaps in the shell 
            #They are thin and can be eroded away
            
        print("done")
         
        #Erode 3 times and dilate 4 times (+1 to regain accuracy) and subtract shell again
        ErodeIterations = 3
        ErodeCounter = 0
        dilationcounter3 = 0
        print("eroding to remove leak")
        while ErodeCounter < ErodeIterations:
            CavityDilation = ErodeImage.Execute(CavityDilation)
            ErodeCounter = ErodeCounter + 1
            
            print("dilating to refill cavity")
            while dilationcounter3 < ErodeIterations + 3:
                CavityDilation = DilateImage.Execute(CavityDilation)
                dilationcounter3 = dilationcounter3 + 1
                
        DilateErodeLeakIterations = DilateErodeLeakIterations +1
          
    
    CavityDilation = DilateImage.Execute(CavityDilation)
    CavityDilation = CavityDilation - ShellMaskNoCap + 1
    CavityDilation = sitk.BinaryThreshold( CavityDilation, 2, 2, 1, 0 )
    CavityDilation = DilateImage.Execute(CavityDilation)
    CavityDilation = CavityDilation - ShellMaskNoCap + 1
    CavityDilation = sitk.BinaryThreshold( CavityDilation, 2, 2, 1, 0 )
    CavityLabel = CavityDilation
    
    
    print("done")
   
    #save result cavity label
    sitkwriter.SetFileName(str(FloretFilename) + "CavityLabel.nii.gz")
    sitkwriter.Execute(CavityLabel)
    
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
    
    print('Calculating shape features for ' + str(FloretFilename) + ' Grain...',)
    shapeFeatures = shape.RadiomicsShape(FloretLabel, TotalGrainMask)
    
    # Calculate the features, print result and append to the dictionary
    result = shapeFeatures.execute()
    print('done')
    
    print('Calculated shape features for ' + str(FloretFilename) + ' Grain: ')
    for (key, val) in six.iteritems(result):
        GrainFeatures[key] = np.round(val, 4)
        print('  ', key, ':', np.round(val, 4))
    
    Branstats = getstats.Execute(BranMask)
    BranVoxelSum = getstats.GetSum()
    BranVolume = BranVoxelSum * 0.034**3
    GrainFeatures
    print(GrainFeatures)
    GrainFeatures["PercentageOfCavityFilled"] = GrainFeatures["VoxelVolume"] / CavityFeatures["VoxelVolume"]
    GrainFeatures["BranPercentage"] =  BranVolume / GrainFeatures["VoxelVolume"]

    with open('GrainData.csv', mode='a', newline='') as GrainData_csv:
        writer = csv.DictWriter(GrainData_csv, fieldnames=GrainFieldnames)
        writer.writerow(GrainFeatures)

    
        
    print('Calculating shape features for ' + str(FloretFilename) + ' Palea...',)
    shapeFeatures = shape.RadiomicsShape(FloretLabel, PaleaMask)
        
    # Calculate the features, print result and append to the dictionary
    result = shapeFeatures.execute()
    print('done')
    
    print('Calculated shape features for ' + str(FloretFilename) + ' Palea: ')
    for (key, val) in six.iteritems(result):
            PaleaFeatures[key] = np.round(val, 4)
            print('  ', key, ':', np.round(val, 4))
    
    with open('PaleaData.csv', mode='a', newline='') as PaleaData_csv:
        writer = csv.DictWriter(PaleaData_csv, fieldnames=fieldnames)
        writer.writerow(PaleaFeatures)
    
    print('Calculating shape features ' + str(FloretFilename) + ' for Lemma...',)
    shapeFeatures = shape.RadiomicsShape(FloretLabel, LemmaMask)

    # Calculate the features, print result and append to the dictionary
    result = shapeFeatures.execute()
    print('done')

    print('Calculated shape features for ' + str(FloretFilename) + ' Lemma: ')
    for (key, val) in six.iteritems(result):
        LemmaFeatures[key] = np.round(val, 4)
        print('  ', key, ':', np.round(val, 4))
    
    with open('LemmaData.csv', mode='a', newline='') as LemmaData_csv:
        writer = csv.DictWriter(LemmaData_csv, fieldnames=fieldnames)
        writer.writerow(LemmaFeatures)
    
    print("Process complete for " + str(FloretFilename))
    CompleteCounter = CompleteCounter + 1
    print(str(CompleteCounter) + "/" + str(len(FloretFileNamesList)) + " Completed")
    

print("Data extraction completed for all listed floret labels")
print("Have a good day :)")
    
    
    
    
    
    
    
