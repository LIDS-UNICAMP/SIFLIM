import warnings
import os
import struct
import csv
import numpy as np
from random import shuffle
from PyQt5.QtCore import *
from enum import Enum
ift = None
try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

MARKERS = dict()

class LabelColor(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    CYAN = 4
    MAGENTA = 5
    GRAY = 6
    WHITE = 7

def index_to_Qcolor(i):
    if i == LabelColor.RED.value:
        color = Qt.red
    elif i == LabelColor.GREEN.value:
        color = Qt.green
    elif i == LabelColor.BLUE.value:
        color = Qt.blue
    elif i == LabelColor.CYAN.value:
        color = Qt.cyan
    elif i == LabelColor.MAGENTA.value:
        color = Qt.magenta
    elif i == LabelColor.GRAY.value:
        color = Qt.gray
    else:
        color = Qt.black
    return color

def load_opf_dataset(path):
    assert ift is not None, "PyIFT is not available"

    opf_dataset = ift.ReadDataSet(path)

    return opf_dataset

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

def get_voxel_from_csv(path_to_csv, id):
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if int(row[0][-5:]) == int(id):
                cols = row[0].split('-')
                return int(cols[1]), int(cols[2]), int(cols[3])
    return None

#-------------------------------------------------------------------------------
# Name:        get_image_size
# Purpose:     extract image dimensions given a file path using just
#              core modules
#
# Author:      Paulo Scardine (based on code from Emmanuel VAÏSSE)
#
# Created:     26/09/2013
# Copyright:   (c) Paulo Scardine 2013
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python

class UnknownImageFormat(Exception):
    pass

def get_image_size(file_path):
    """
    Return (width, height) for a given img file content - no external
    dependencies except the os and struct modules from core
    """
    size = os.path.getsize(file_path)

    with open(file_path) as input:
        height = -1
        width = -1
        data = input.read(25)

        if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
            # GIFs
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
              and (data[12:16] == 'IHDR')):
            # PNGs
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
            # older PNGs?
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        elif (size >= 2) and data.startswith('\377\330'):
            # JPEG
            msg = " raised while trying to decode as JPEG."
            input.seek(0)
            input.read(2)
            b = input.read(1)
            try:
                while (b and ord(b) != 0xDA):
                    while (ord(b) != 0xFF): b = input.read(1)
                    while (ord(b) == 0xFF): b = input.read(1)
                    if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                        input.read(3)
                        h, w = struct.unpack(">HH", input.read(4))
                        break
                    else:
                        input.read(int(struct.unpack(">H", input.read(2))[0])-2)
                    b = input.read(1)
                width = int(w)
                height = int(h)
            except struct.error:
                raise UnknownImageFormat("StructError" + msg)
            except ValueError:
                raise UnknownImageFormat("ValueError" + msg)
            except Exception as e:
                raise UnknownImageFormat(e.__class__.__name__ + msg)
        else:
            raise UnknownImageFormat(
                "Sorry, don't know how to get information from this file."
            )

    return width, height