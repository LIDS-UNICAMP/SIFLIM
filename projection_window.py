from image_view_window import ImageViewWindow
from random import sample
from numpy import dtype
from numpy.core.fromnumeric import reshape
import utils
import numpy as np
# from image_view_window import *
# importing Qt widgets
from PyQt5.QtWidgets import *

from draw_window_test import *

# importing system
import sys

from pyift.pyift import Sample

import utils


from PyQt5.QtGui import *

import warnings
ift = None

try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)


class SamplePoint():
    def __init__(self, id, x, y, img, true_label):
        self.id = id
        self.x = x
        self.y = y
        self.img = img
        self.true_label = true_label

    def print_info(self):
        print("{")
        print("    id: ", self.id)
        print("    x: ", self.x)
        print("    y: ", self.y)
        print("    img: ", self.img)
        print("}")


class ProjectionPoint(QGraphicsEllipseItem):
    def setAssociatedSamplePoint(self, point):
        self.sample_point = point
        return

    def mousePressEvent(self, event):
        # Do your stuff here.
        self.sample_point.print_info()
        return QGraphicsEllipseItem.mousePressEvent(self, event)

    def hoverMoveEvent(self, event):
        # Do your stuff here.
        pass


class ProjectionWindow(QWidget):

    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("PyQt Test")

        # setting geometry
        self.setGeometry(100, 100, 2000, 800)

        # icon
        icon = QIcon("skin.png")

        # setting icon to the window
        self.setWindowIcon(icon)

        mainLayout = QHBoxLayout()

        self.createProjectionView()
        self.createProjectionConfig()

        mainLayout.addWidget(self.projectionConfig)
        mainLayout.addWidget(self.projectionView)

        self.setLayout(mainLayout)
        # showing all the widgets
        self.show()

    def createProjectionConfig(self):
        self.projectionConfig = QGroupBox("Group 1")

        radioButton1 = QRadioButton("Radio button 1")
        radioButton2 = QRadioButton("Radio button 2")
        radioButton3 = QRadioButton("Radio button 3")
        radioButton1.setChecked(True)

        checkBox = QCheckBox("Tri-state check box")
        checkBox.setTristate(True)
        checkBox.setCheckState(Qt.PartiallyChecked)

        layout = QVBoxLayout()
        layout.addWidget(radioButton1)
        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addWidget(checkBox)
        layout.addStretch(1)

        self.projectionConfig.setLayout(layout)

    def setProjectionPoints(self, data):
        X = data[:, 0]
        X_ = np.array([x.flatten() for x in X], dtype=np.float32)
        # print(X_)
        Y = np.array(data[:, 1], dtype=np.int32)
        paths = list(data[:, 2])
        ids = np.array(data[:, 3], dtype=np.int32)
        # y = np.ndarray([y_[0] for y_ in Y], dtype=np.int32)
        Z = ift.CreateDataSetFromNumPy(X_, Y)
        Z.SetId(ids)
        Z.SetRefData(paths)

        print(Z.nsamples, " amostras")
        reduced_ds = ift.DimReductionByTSNE(Z, 2, 30, 1000)

        proj_data = Z.GetProjection()
        orig_data = Z.GetData()
        ref_data = Z.GetRefData()
        true_labels = Z.GetTrueLabels()
        ids = Z.GetIds()

        self.sample_points = {}
        for i in range(Z.nsamples):
            img = orig_data[i]
            sample_x = proj_data[i][0]
            sample_y = proj_data[i][1]
            p = SamplePoint(ids[i], sample_x, sample_y,
                            ref_data[i], true_labels[i])
            self.sample_points[str(sample_x)+" "+str(sample_y)] = p

    # method for components
    def createProjectionView(self):

        training_data = utils.get_training_data()[:1000]
        self.setProjectionPoints(training_data)

        # Defining a scene rect of 500x500, with it's origin at 0,0.
        # If we don't set this on creation, we can set it later with .setSceneRect
        scene = QGraphicsScene(0, 0, 500, 500)

        self.projectionView = QGraphicsView(scene, parent=self)

        # Convert data array into a list of dictionaries with the x,y-coordinates
        # pos = [{'pos': tsne[:, i]} for i in range(len(tsne))]
        # adding spots to the scatter plot

        for key in self.sample_points:
            sample = self.sample_points[key]
            # Draw a ellipse item, setting the dimensions.
            point = ProjectionPoint(0, 0, 10, 10)
            point.setPos(sample.x * 400, sample.y*400)

            # Define the brush (fill).
            brush = QBrush(Qt.red)
            point.setBrush(brush)

            # Define the pen (line)
            pen = QPen(Qt.black)
            pen.setWidth(1)
            point.setPen(pen)

            scene.addItem(point)
            point.setAssociatedSamplePoint(sample)
