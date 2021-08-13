import warnings
import os
import numpy as np
import cv2
from tqdm import tqdm
from random import shuffle
ift = None

try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

TRAIN_DIR = 'train/'
TEST_DIR = './test1/'
IMG_SIZE = 50

def load_opf_dataset(path):
    assert ift is not None, "PyIFT is not available"

    opf_dataset = ift.ReadDataSet(path)

    return opf_dataset

def get_training_data():
    '''
        Return training data
    '''
    training_data = []
    if os.path.isfile('training_data_{}.npy'.format(IMG_SIZE)):
        return np.load('training_data_{}.npy'.format(IMG_SIZE), allow_pickle=True)
    else:
        for img in tqdm(os.listdir(TRAIN_DIR)):
            label = get_label(img)
            id = get_id(img)
            path = os.path.join(TRAIN_DIR,img)
            img = cv2.resize(cv2.imread(path,cv2.IMREAD_GRAYSCALE), (IMG_SIZE,IMG_SIZE))
            img = img/255
            training_data.append([np.array(img),np.array(label), [path], np.array(id)])
        shuffle(training_data)
        np.save('training_data_{}.npy'.format(IMG_SIZE),training_data)
        return np.array(training_data)

def get_label(img):
    '''
        Return the label for images
    '''
    word = img.split('.')[0]
    if word == 'cat':
        return [0]
    else:
        return [1]

def get_id(img):
    '''
        Return unique id for sample image
    '''
    num = int(img.split('.')[1]) + 1
    label = get_label(img)

    return num*(label[0] + 1)