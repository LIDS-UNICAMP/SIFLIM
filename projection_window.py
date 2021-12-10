from projector import Projector
from image_view_window import ImageViewWindow
from random import sample
from numpy import dtype
from numpy.core.fromnumeric import reshape
import utils
import numpy as np
# from image_view_window import *
# importing Qt widgets
from PyQt5.QtWidgets import *

import os
from datetime import datetime
from pyift.pyift import Sample

import utils
from projector import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
import warnings
ift = None

try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)



class ProjectionPoint(QGraphicsEllipseItem):
    def setAssociatedSamplePoint(self, point):
        self.sample_point = point
        return

    # def mousePressEvent(self, event):
    #     # Do your stuff here.
    #     self.sample_point.print_info()
    #     event.accept()
    #     return QGraphicsEllipseItem.mousePressEvent(self, event)

    def hoverMoveEvent(self, event):
        # Do your stuff here.
        pass

class ProjectionScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(ProjectionScene, self).__init__(parent)
        self.setSceneRect(0,0,500,500)

    def mousePressEvent(self, event):
        items = self.items(event.scenePos())
        # for item in items:
        #     item.sample_point.print_info()
        if len(items) > 0:
            self.image_view = ImageViewWindow(points=items)
            self.image_view.show()
        super(ProjectionScene, self).mousePressEvent(event)

class ProjectionWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.ngroups = 10
        self.inputDataSet = None
        self.OPFDataset = None
        self.patchCSV = None
        self.patches = True
        # setting title
        self.setWindowTitle("Select Flim")

        # setting geometry
        self.setGeometry(100, 100, 2000, 800)


        self.createActions()
        # self.createMenuBar()


        self.createProjectionView()
        self.createProjectionConfig()
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.projectionConfig)
        hbox.addWidget(self.projectionView)
        self.setLayout(hbox)

        # showing all the widgets
        self.show()

    def createMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        helpMenu = menuBar.addMenu("&Help")

        fileMenu.addAction(self.importAction)
        fileMenu.addAction(self.saveAction)
    
    def createActions(self):
        self.importAction = QAction("&Import Dataset...", self)
        self.importAction.triggered.connect(self.importDataset)
        self.saveAction = QAction("&Save", self)

    def onInputDatasetButtonClicked(self):
        filename, filter = QFileDialog.getOpenFileName(parent=self, caption='Open file', dir='.', filter='*.zip')
        if filename:
            self.inputFileLineEdit.setText(filename)

    def saveMarkers(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
        markers_dir = os.path.abspath("markers")
        project_dir = os.path.join(markers_dir, dt_string)
        os.mkdir(project_dir)
        for img in MARKERS.keys():
            img_name = os.path.basename(img)
            file_name = img_name.split(".")[0] + str("-seeds.txt")
            file_path = os.path.join(project_dir, file_name)
            with open(file_path, 'a') as f:
                w, h = tuple(MARKERS[img])[0][2], tuple(MARKERS[img])[0][3]
                n_marker_pixels = len(MARKERS[img])
                f.write("{} {} {}\n".format(n_marker_pixels, w, h))
                for marker_pixel in MARKERS[img]:
                    x = marker_pixel[0]
                    y = marker_pixel[1]
                    label = marker_pixel[4]
                    f.write("{} {} -1 {}\n".format(x, y, label))
                f.close()

    def getOPFDataset(self):
        if self.projector == None:
            return None
        
        return self.projector.dataset

    def importDataset(self):
        fname = QFileDialog.getOpenFileName(self, 'Import Dataset', 
         '.',"OPFDataset Files (*.zip)")
        self.inputDataSet = fname[0]
        self.importedDatasetLabel.setText("Selected: " + str(self.inputDataSet))
    
    def importPatchCSV(self):
        fname = QFileDialog.getOpenFileName(self, 'Import Patch CSV file', 
         '.',"CSV Files (*.csv)")
        self.patchCSV = fname[0]
        self.importedCSVLabel.setText("Selected: " + str(self.patchCSV))

        

    def createProjectionConfig(self):
        self.projectionConfig = QGroupBox("Projection Settings")
        self.projectionConfig.setMaximumWidth(400)

        #  ============== INPUT FILES ===================  
        inputFilesGroupBox = QGroupBox("Input Files")
        inputFilesGroupBoxLayout = QVBoxLayout()
        inputFilesGroupBox.setLayout(inputFilesGroupBoxLayout)

        self.patchVisualization = QRadioButton("Patch Visualization")
        self.patchVisualization.setChecked(True)
        self.patchVisualization.toggled.connect(lambda:self.btnstate(self.patchVisualization))
        inputFilesGroupBoxLayout.addWidget(self.patchVisualization)

        button1 = QPushButton(self)
        button1.setText("Import Dataset")
        button1.clicked.connect(self.importDataset)
        self.importedDatasetLabel = QLabel("Selected: " + str(self.inputDataSet))
        inputFilesGroupBoxLayout.addWidget(button1)
        inputFilesGroupBoxLayout.addWidget(self.importedDatasetLabel)

        self.button2 = QPushButton(self)
        self.button2.setText("Import CSV")
        self.button2.clicked.connect(self.importPatchCSV)
        self.importedCSVLabel = QLabel("Selected: " + str(self.patchCSV))
        inputFilesGroupBoxLayout.addWidget(self.button2)
        inputFilesGroupBoxLayout.addWidget(self.importedCSVLabel)


        # ============= HYPERPARAMETERS ============= 
        # self.hyperparameters = QGroupBox("Groups per Image")
        # ngroups_input = QLineEdit("10")
        # ngroups_input.textChanged.connect(self.changedNGroups)
        # hyperparametersLayout = QVBoxLayout()
        # hyperparametersLayout.addWidget(QLabel("Groups per Image"))
        # hyperparametersLayout.addWidget(ngroups_input)
        # self.hyperparameters.setLayout(hyperparametersLayout)

        # ============== GENERATE PROJECTION ===============
        generateProjectionButton = QPushButton(self)
        generateProjectionButton.setText("Generate Projection")
        generateProjectionButton.clicked.connect(self.createProjectionView)

        # ============== SAVE MARKERS ==================
        saveMarkersButton = QPushButton(self)
        saveMarkersButton.setText("Save Markers")
        saveMarkersButton.clicked.connect(self.saveMarkers)

        layout = QVBoxLayout()

        layout.addWidget(inputFilesGroupBox)

        layout.addWidget(self.hyperparameters)

        layout.addWidget(generateProjectionButton)
        layout.addWidget(saveMarkersButton)

        layout.addStretch(1)

        self.projectionConfig.setLayout(layout)

    def changedNGroups(self, text):
        if len(text) > 0:
            self.ngroups = int(text)

    def btnstate(self,b):
	
        if b.isChecked() == True:
            self.usePatches = True
            self.button2.setEnabled(True)
        else:
            self.usePatches = False
            self.button2.setEnabled(False)

    def setProjectionPoints(self):

        if self.patches == True:
            self.projector = Projector(self.inputDataSet, self.patchCSV, self.ngroups)
        else:
            self.projector = Projector(self.inputDataSet, None, None)
        # self.projector = DummyProjector()

        self.projector.generate_reduced(method='tsne', hyperparameters=(30,0))

        self.projection = self.projector.get_projection()


    # method for components
    def createProjectionView(self):
        if self.inputDataSet != None:
            self.setProjectionPoints()

            scene = ProjectionScene()

            self.drawProjectionPoints(scene)
            
            self.layout().removeWidget(self.projectionView)
            self.projectionView = QGraphicsView(scene, parent=self)
            self.layout().addWidget(self.projectionView)
            self.update()
        else:
            label = QLabel("Please select an input dataset.")
            self.projectionView = label

    def drawProjectionPoints(self, scene):
    
        for key in self.projection.sample_points:
            sample = self.projection.sample_points[key]
            # Draw a ellipse item, setting the dimensions.
            point = ProjectionPoint(0, 0, 10, 10)
            point.setPos(sample.x * self.projection.scale, sample.y*self.projection.scale)

            # Define the brush (fill).
            color = index_to_Qcolor(sample.true_label)
            color = QColor(color)
            color.setAlphaF( 1.0 )
            brush = QBrush(color)
            point.setBrush(brush)

            # Define the pen (line)
            pen = QPen(Qt.black)
            pen.setWidth(1)
            point.setPen(pen)

            scene.addItem(point)
            point.setAssociatedSamplePoint(sample)
