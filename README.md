# SIFLIM
Software for image selection and marker labeling for FLIM using feature space projections

## Requirements
Create virtual environment with Python 3.8 (ex. anaconda or miniconda)
- ```pip install -r requirements.txt```

## Generanting Dataset of Patches from Input Images
  SIFLIM can recieve as input an OPFDataset with each sample being an NxNx3 patch extracted from a given image's superpixel segmentation. 
<br>
To create such dataset you can run <br>
```python generate_patches_dataset.py <INPUT> <OUTPUT.zip> <PATCHSIZE> <MAX-SAMPLES-PER-CLASS>``` <br>
on your virtual environment, where <br> 
- ```<INPUT>``` is the path to the fileset of original .png images
- ```<OUTPUT.zip>``` is the desired output file path/name
- ```<PATCHSIZE>``` is the patch size (e.g. <PATCHSIZE> = 75 generates 75x75x3 patches)
- ```<MAX-SAMPLES-PER-CLASS>``` is the max number of generates sample points per image

