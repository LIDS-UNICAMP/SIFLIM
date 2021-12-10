import warnings
import sys
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import shutil
import pyift.pyift as ift
from PIL import Image
from os import listdir
from os.path import isfile, join

original_imgs_path = sys.argv[1]
output_dir = sys.argv[2]
patch_size = int(sys.argv[3])
max_patches_per_class = int(sys.argv[4])
ngroups = 10

first_img =  join(original_imgs_path, listdir(original_imgs_path)[0])
im = Image.open(first_img)
w, h = im.size

nsuperpixels = 4*int((w/patch_size)**2)

print("Creating patches dataset from superpixels...")
Z:ift.DataSet = ift.PatchesFromSuperpixels(original_imgs_path, "temp.zip", nsuperpixels, patch_size)
# Z:ift.DataSet = ift.ReadDataSet("temp.zip")
print("Created dataset with {} samples".format(Z.nsamples))
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
    })
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

print("Creating reduced dataset of {} samples per class".format(len(further_selected_patches)))
small_dataset:ift.DataSet = ift.CreateDataSetFromNumPy(X_for_dim_redux, Xlabels)
small_dataset.SetRefData(small_refdata)
small_dataset.SetId(small_patch_ids)

print("Writing reduced dataset...")
ift.WriteDataSet(small_dataset, output_dir)

