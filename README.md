# SIFLIM
Software for image selection and marker labeling for FLIM using feature space projections

## Requirements
Create virtual environment with Python 3.8 (ex. anaconda or miniconda)
- PyIFT: ```pip install pyift-0.1-cp39-cp39-linux_x86_64.whl```
- PyQt5: ```pip install PyQt5```
- Numpy: ```conda install numpy```

## Generanting Dataset of Patches from Input Images
  SIFLIM can recieve as input an OPFDataset with each sample being an NxNx3 patch extracted from a given image's superpixel segmentation. 
<br>
To create such dataset you can run <br>
```python generate_patches_dataset.py <INPUT> <OUTPUT.zip> <NUM_SUPERPIXELS> <PATCHSIZE>``` <br>
on your virtual environment, where <br> 
- ```<INPUT>``` is the path to the fileset of original .png images
- ```<OUTPUT.zip>``` is the desired output file path/name
- ```<NUM_SUPERPIXELS>``` is the number of superpixels per image
- ```<PATCHSIZE>``` is the patch size (e.g. <PATCHSIZE> = 75 generates 75x75x3 patches)

