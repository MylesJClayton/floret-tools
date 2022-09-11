# floret-tools
Computer vision tools for preprocessing images of wheat florets from 3D-μCT scans. 
Scanco CT scanners create images in the ISQ format which can be hard to work with.
This repository allows the user to convert and crop large batches of such 3D images. 
Cropping the volumes massively reduces required stroage space to about 1/20 of the original. 
The smaller images can also be processed by 3D-CNNs, in which case it is recommened to use the cropping tools normalization functionality.  

## Dependencies:

Use the FT-env.yml file to create a suitable environment with the required packages with command
conda env create -f FT-env.yml
Read the file to view the required packages. 
Package Version numbers specified may not be strict requirements but other versions and combinations are untested


## Instructions for use:  
From virtual environment (such as anaconda) call the script from the command line with python. 
Windows example : >python RunWorkflow.py -t -n -i C:/path/to/input/directory -o D:/path/to/output/directory 

You can use the ISQ2nii, and FloretCropper scripts separately. 

Note: When using -i and -o, A backslash is used to denote subdirectories on both Linux and Windows. 

### Semicolons in filenames
Sometimes the scanner will save CT scans with the extension .ISQ;1. 
ISQ filetype can be opened by the itk library but the reader fails when given an ISQ;1 file. 
The ISQsemicolonremover.py script can either remove ;1 from the filenames or make a copy, saving the original. 
The latter is recommended and is the default, but the -r or --rename argumant can be given and the process is much faster and easier on storage.
 
The semicolon remover script must be run seperately (before RunWorkflow.py) if your files have extension .ISQ;1


## Arguments 
 
### Runworkflow.py
```
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        Input directory absolute path
  -o OUTPATH, --outpath OUTPATH
                        Output directory absolute path
  -t, --troubleshoot    Save images of intermediate steps threshold, components, and mask
  -n, --normalize       Normalize cropped images to have zero mean and unit variance across all voxels
```
### ISQ2nii.py
```
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        Input directory absolute path
  -o OUTPATH, --outpath OUTPATH
                        Output directory absolute path
```
### FloretCropper.py
```
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        Input directory absolute path
  -o OUTPATH, --outpath OUTPATH
                        Output directory absolute path
  -t, --troubleshoot    Save images of intermediate steps threshold, components, and mask
  -n, --normalize       Normalize cropped images to have zero mean and unit variance across all voxels
```
### ISQsemicolonremover.py
```
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        Input directory absolute path
  -o OUTPATH, --outpath OUTPATH
                        Output directory absolute path
  -r, --rename          Rename ISQ;1 to ISQ in same directory Much faster for bulk processing but WILL NOT keep
                        originals
```

## Cropper Methodology  
The script makes a note of each nii.gz file in the input directory and the following process is applied for each one: 
- Image is read 
- Otsu filter determines threshold based on intensity histogram, this seperates dense objects from background (scan tube and grain) 
- A binary mask of forground/background is made * 
- Objects not connected to each other are labelled from 1 to n according to size (largest is 1) * 
- 2nd largest object is assumed to be ROI (scan tube is always largest object in the image) and mask is made * 
- A bounding box of the grain is obtained and expanded to include surroundings (other floral organs) 
- Bounding box volume is extracted/cropped out and saved 
- Voxel size of plantmatter and bounding box dimensions are recorded in a .csv 
- Cropped image of wheat grain is placed in the output folder 
- If --troubleshoot -t is specified, images of (potentially error prone) intermediate steps (*) are saved
- If --normalize -n is specified, cropped images will also be normalized to have zero mean and unit variance across all inputs
	(recommended for preprocessing images for machine learning algorithms)






