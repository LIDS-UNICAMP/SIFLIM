import numpy as np
import pyift.pyift as ift
from sklearn.cluster import MiniBatchKMeans
from sklearn.manifold import TSNE

Z:ift.DataSet = ift.ReadDataSet("corel_integral2.zip")

class_truelabels = Z.GetTrueLabels()
ref_data = Z.GetRefData()
patch_ids = Z.GetIds()
patches_feats = Z.GetData()

# dict of sets of patches from same image (=key)
img_dict = dict()

img_as_labels = []
for i in range(len(ref_data)):
    img_path = ref_data[i]
    img_number = int(ref_data[i].split('_')[1].split('.')[0])
    img_class = class_truelabels[i]

    if img_path not in img_dict.keys():
        img_dict[img_path] = []

    img_dict[img_path].append({
        "patch_index": i,
        "patch_features": patches_feats[i]
    })

selected_patches = []
for key in img_dict.keys():
    patches = img_dict[key]
    array_for_kmeans = []
    for patch in patches:
        array_for_kmeans.append(patch['patch_features'])
    X = np.array(array_for_kmeans)

    kmeans = MiniBatchKMeans(n_clusters=10, random_state=0, batch_size=1)
    kmeans.fit(X)
    for j in range(10):
        d = kmeans.transform(X)[:, j]
        ind = np.argsort(d)[::-1][:1]
        selected_patches.append(patches[ind[0]]['patch_index'])

print(len(selected_patches))



