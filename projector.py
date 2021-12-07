import utils
import warnings
# from PIL import Image
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from image_view_window import *
ift = None
try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

CSV_PATH = "../ift/demo/IterativeOPF/output.csv"

def is_valid_voxel(img, voxel):
    return ((voxel.x >= 0) and (voxel.x <= (img.xsize - 1)) and (voxel.y >= 0) and (voxel.y <= (img.ysize - 1)) and (voxel.z >= 0) and (voxel.z <= (img.zsize - 1)))

def fit_bounding_box_on_image_domain(bb, img):
    bb_fit = bb
    
    upper_left_voxel = bb.begin;
    bottom_right_voxel = bb.end;
    
    if not is_valid_voxel(img, upper_left_voxel):

        bb_fit.begin.x = upper_left_voxel.x if (upper_left_voxel.x >= 0) else 0
        bb_fit.begin.y = upper_left_voxel.y if (upper_left_voxel.y >= 0) else 0
        bb_fit.begin.z = upper_left_voxel.z if (upper_left_voxel.z >= 0) else 0
    
    
    if not is_valid_voxel(img, bottom_right_voxel):
        
        bb_fit.end.x = img.xsize - 1 if (bottom_right_voxel.x >= img.xsize) else bottom_right_voxel.x
        bb_fit.end.y = img.ysize - 1 if (bottom_right_voxel.y >= img.ysize) else bottom_right_voxel.y
        bb_fit.end.z = img.zsize - 1 if (bottom_right_voxel.z >= img.zsize) else bottom_right_voxel.z
    
    
    return bb_fit


class Projector():
    def __init__(self, path_to_dataset, inputCSV, ngroups) -> None:
        self.dataset = utils.load_opf_dataset(path_to_dataset)
        self.patchCSV = inputCSV
        self.ngroups = ngroups
        self.projection = None
        print("Projector created with ", self.dataset.nsamples, " samples of size ", self.dataset.nfeats, " from ", self.dataset.nclasses, " different classes")
    
    def generate_reduced(self, method, hyperparameters):
        Z = self.dataset
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

        selected_patches = []
        for key in img_dict.keys():
            patches = img_dict[key]
            array_for_kmeans = []
            for patch in patches:
                array_for_kmeans.append(patch['patch_features'])
            X = np.array(array_for_kmeans)

            kmeans = MiniBatchKMeans(n_clusters=self.ngroups, random_state=0, batch_size=1)
            kmeans.fit(X)
            for j in range(self.ngroups):
                d = kmeans.transform(X)[:, j]
                ind = np.argsort(d)[::-1][:1]
                selected_patches.append(patches[ind[0]]['patch_index'])
        
        X_for_dim_redux = []
        Xlabels = []
        small_refdata = []
        small_patch_ids = []
        
        for i in selected_patches:
            X_for_dim_redux.append(patches_feats[i].tolist())
            Xlabels.append(class_truelabels[i])
            small_refdata.append([ref_data[i]])
            small_patch_ids.append(patch_ids[i])

        X_for_dim_redux = np.array(X_for_dim_redux, dtype=np.float32)
        Xlabels = np.array(Xlabels, dtype=np.int32)
        small_patch_ids = np.array(small_patch_ids)
        small_dataset:ift.DataSet = ift.CreateDataSetFromNumPy(X_for_dim_redux, Xlabels)
        small_dataset.SetRefData(small_refdata)
        small_dataset.SetId(small_patch_ids)

        self.dataset = small_dataset

        if method == 'tsne':
            perplexity = hyperparameters[0]
            ift.DimReductionByTSNE(self.dataset, 2, perplexity, 1000)
            self.projection = Projection(self.dataset, self.patchCSV)

    def get_projection(self):
        return self.projection

class DummyProjection():
    def __init__(self):
        self.scale = 500
        self.index_buffer = [[-1 for _ in range(self.scale)] for _ in range(self.scale)]
        pontos_fake = [(0,0), (1,1), (0,1), (0,1), (0.5, 0.4)]
        self.sample_points = {}
        for i in range(len(pontos_fake)):
            sample_x = pontos_fake[i][0]
            sample_y = pontos_fake[i][1]

      
            n = 5625 // 3
            center_voxel = (int(np.sqrt(n) // 2), int(np.sqrt(n) // 2))
            p = SamplePoint(i, sample_x, sample_y,
                            "/home/gabrielseabra/datasets/exper/orig_mini/0002_0009.png", 
                            2, feats=[], size=n, voxel_coords=center_voxel)
            self.sample_points[str(i)] = p


class Projection():
    def __init__(self, reduced_ds, csv_path):
        self.feat_space_2d = reduced_ds.GetProjection()
        self.feat_space_nd = reduced_ds.GetData()
        self.scale = 500
        ref_data = reduced_ds.GetRefData()
        true_labels = reduced_ds.GetTrueLabels()
        ids = reduced_ds.GetIds()

        self.sample_points = {}
        self.index_buffer = [[-1 for _ in range(self.scale)] for _ in range(self.scale)]
        for i in range(reduced_ds.nsamples):
            sample_x = self.feat_space_2d[i][0]
            sample_y = self.feat_space_2d[i][1]

            if csv_path != None:
                superpixel_x, superpixel_y, l = utils.get_voxel_from_csv(csv_path, int(ids[i]))
                center_voxel = (superpixel_x, superpixel_y)
                n = l*l // 3
            else:
                n = reduced_ds.nfeats // 3
                center_voxel = (int(np.sqrt(n) // 2), int(np.sqrt(n) // 2))
            p = SamplePoint(ids[i], sample_x, sample_y,
                            ref_data[i], true_labels[i], feats=self.feat_space_nd[i], size=n, voxel_coords=center_voxel)
            self.sample_points[str(ids[i])] = p

            # self.set_index_buffer_point(p.x, p.y, p.true_label)
    
    def get_index_buffer_coords(self, x, y):
        x_, y_ = int(round(x * self.scale)), int(round(y * self.scale))
        return x_, y_
    
    def set_index_buffer_label(self, x, y, label):
        r = 5
        center_x, center_y = self.get_index_buffer_coords(x,y)
        for x_ in range(center_x - 5, center_x + 5):
            for y_ in range(center_y - 5, center_y + 5):
                distance_to_center = np.sqrt((center_x - x_)**2 + (center_y - y_)**2)
                if distance_to_center <= 5:
                    self.index_buffer[x_][y_] = label

class DummyProjector():
    def __init__(self) -> None:
        self.projection = None
    
    def generate_reduced(self, method, hyperparameters):
        if method == 'tsne':
            self.projection = DummyProjection()

    def get_projection(self):
        return self.projection

class SamplePoint():
    def __init__(self, id, x, y, ref_img, true_label, feats, size, voxel_coords):
        self.id = id
        self.x = x
        self.y = y
        self.img = ref_img
        self.true_label = true_label
        self.label = 0
        self.feats = feats
        self.size = size
        self.voxel_coords = voxel_coords


    def print_info(self):
        # print("patch {")
        # print("    id: ", self.id)
        # print("    x: ", self.voxel_coords[0])
        # print("    y: ", self.voxel_coords[1])
        # print("    img: ", self.img)
        # print("}")

        print(self.true_label)
        print(self.img)

        l = (int(np.sqrt(self.size)))
        w, h = l , l

        bb = (self.voxel_coords[0] - l//2, self.voxel_coords[1] - l//2, l) 
        
        
        self.image_view = ImageViewWindow(self.img, bb)
        
