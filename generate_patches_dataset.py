import warnings
import sys
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import shutil
import pyift.pyift as ift
from PIL import Image
import os
from ctypes import *
from typing import List
from os.path import isfile, join

def getBaseNameFromFile(file_path):
    return file_path.split('/')[-1].split('.')[0]

def getLabelFromFile(file_path):
    return int(file_path.split('/')[-1].split('_')[0])

def patches_from_superpixels(orig_path, output_filename, nsuperpixels, patch_size):
    fs = [join(orig_path, f) for f in os.listdir(orig_path) if isfile(join(orig_path, f))]
    input: List[ift.MImage] = []
    input_orig: List[ift.Image] = []
    label_set = set()
    for file in fs:
        label_set.add(getLabelFromFile(file))
        input.append(ift.ImageToMImage(ift.ReadImageByExt(file), ift.RGB_CSPACE))
        input_orig.append(ift.ReadImageByExt(file))
    
    nclasses = len(label_set)
    nimages = len(fs)

    Q:ift.AdjRel = ift.Rectangular(patch_size, patch_size)

    samples = []
    ids = []
    truelabels = []
    ref_data = []
    s = 0


    patches_csv_file = open("{}.csv".format(output_filename), mode='w')

    for i in range(nimages):
        truelabel = getLabelFromFile(fs[i])
        img_basename = getBaseNameFromFile(fs[i])
    
        ift.RandomSeed(1)

        A_ = ift.Circular(1.0)

        mask1 = ift.SelectImageDomain(input[i].xsize, input[i].ysize, input[i].zsize)

        # minima of a basins manifold in that domain */
        igraph: ift.IGraph = ift.ImplicitIGraph(input[i], mask1, A_)

        # seed sampling for ISF */
        seeds = ift.GridSampling(input[i], mask1, nsuperpixels)

        nseeds = ift.NumberOfElements(seeds)

        finalniters = ift.IGraphISF_Root(igraph, seeds, 0.1, 12, 2)

        S: ift.Set = ift.SuperpixelCenterSetFromIGraph(igraph)
        
        # S_np: np.ndarray = S.AsNumPy(input[i])
        S_va: ift.VoxelArray = S.AsVoxelArray(input_orig[i]).AsList()

        invalid_voxel = 0

        img_np:np.ndarray = input_orig[i].AsNumPy().reshape((input[i].n, input[i].m))


        for j in range(len(S_va)):
            u = ift.Voxel()
            u.x = S_va[j][0]
            u.y = S_va[j][1]
            u.z = S_va[j][2]
            # u: ift.Voxel = ift.MGetVoxelCoord(input[i], p)

            invalid_voxel = 0
            f = 0

            sample_feats=[]

            # for each pixel in square patch around u
            for k in range(Q.n):
                v:ift.Voxel = ift.GetAdjacentVoxel(Q, u, k)
                if ift.MValidVoxel(input[i], v) == '\x01':
                    q = ift.MGetVoxelIndex_pyift(input[i], v)
                    sample_feats.extend(img_np[q].tolist())
                else:
                    invalid_voxel = 1
                    break
            
            if invalid_voxel == 0:
                patches_csv_file.write("{}-{:03d}-{:03d}-{:03d}-{:03d}-{:010d}\n".format(img_basename, u.x, u.y, u.z, patch_size, s))
                ids.append(s)
                truelabels.append(truelabel)
                ref_data.append([os.path.abspath(fs[i])])
                samples.append(sample_feats)
                s += 1

    patches_csv_file.close()
    
    y = np.array(truelabels, dtype=np.int32)
    
    X = np.array(samples, dtype=np.float32)


    Z: ift.DataSet = ift.CreateDataSetFromNumPy(X, y)

    Z.SetId(np.array(ids, dtype=np.int32))
    Z.SetRefData(ref_data)
    Z.SetNClasses(nclasses)

    ift.SetStatus(Z, ift.IFT_TRAIN)

    return Z

if len(sys.argv) != 5:
    print('usage: {} <original images diectory> <output file name> <patch size> <max patches per class>'.format(sys.argv[0]))
    exit()

original_imgs_path = sys.argv[1]
output_dir = sys.argv[2]
patch_size = int(sys.argv[3])
max_patches_per_class = int(sys.argv[4])

# for debugging:
# python generate_patches_dataset.py ../classification-with-FLIM/data/cats-vs-dogs/images_mini cats_mini 25 600
# original_imgs_path = "../classification-with-FLIM/data/cats-vs-dogs/images_mini"
# output_dir = "cats_mini"
# patch_size = 25
# max_patches_per_class = 600

ngroups = 50

first_img =  os.path.join(original_imgs_path, os.listdir(original_imgs_path)[0])
im = Image.open(first_img)
w, h = im.size

nsuperpixels = 12*int((w/patch_size)**2)

print("Creating patches dataset from superpixels...")
# Z:ift.DataSet = ift.PatchesFromSuperpixels(original_imgs_path,output_dir, nsuperpixels, patch_size)
Z:ift.DataSet = patches_from_superpixels(original_imgs_path, output_dir, nsuperpixels, patch_size)

print("Created dataset with {} samples and {} features.".format(Z.nsamples, Z.nfeats))
class_truelabels = Z.GetTrueLabels()
ref_data = Z.GetRefData()
patch_ids = Z.GetIds()
patches_feats = Z.GetData()

# dict of sets of patches from same image (=key)
img_dict = dict()

img_as_labels = []
for i in range(len(ref_data)):
    img_path = ref_data[i]

    if img_path not in img_dict.keys():
        img_dict[img_path] = []

    img_dict[img_path].append({
        "patch_index": i,
        "patch_features": patches_feats[i]
        }
    )
print("Running kmeans clustering...")
selected_patches = [[] for _ in range(Z.nclasses)]
for key in img_dict.keys():
    patches = img_dict[key]
    array_for_kmeans = []
    for patch in patches:
        array_for_kmeans.append(patch['patch_features'])
    if len(patches) < 10:
        ngroups = len(patches)
    X = np.array(array_for_kmeans)

    kmeans = MiniBatchKMeans(n_clusters=ngroups, random_state=0, batch_size=1)
    kmeans.fit(X)
    for j in range(ngroups):
        d = kmeans.transform(X)[:, j]
        ind = np.argsort(d)[::-1][:1]
        cl_i = int(class_truelabels[i]) - 1
        selected_patches[cl_i].append(patches[ind[0]]['patch_index'])

further_selected_patches = []
for c in selected_patches:
    if len(c) > max_patches_per_class:
        further_selected_patches.extend(np.random.choice(a=c, size=max_patches_per_class).tolist())
    else:
        further_selected_patches.extend(c)



X_for_dim_redux = []
Xlabels = []
small_refdata = []
small_patch_ids = []

for i in further_selected_patches:
    X_for_dim_redux.append(patches_feats[i].tolist())
    Xlabels.append(class_truelabels[i])
    small_refdata.append([ref_data[i]])
    small_patch_ids.append(patch_ids[i])

X_for_dim_redux = np.array(X_for_dim_redux, dtype=np.float32)
Xlabels = np.array(Xlabels, dtype=np.int32)
small_patch_ids = np.array(small_patch_ids)

print("Creating reduced dataset of  samples per class".format(len(further_selected_patches)))
small_dataset:ift.DataSet = ift.CreateDataSetFromNumPy(X_for_dim_redux, Xlabels)
small_dataset.SetRefData(small_refdata)
small_dataset.SetId(small_patch_ids)

if os.path.exists(output_dir):
    os.remove(output_dir)
output_dir = output_dir + ".zip"
print("Writing reduced dataset...")
ift.WriteDataSet(small_dataset, output_dir)

