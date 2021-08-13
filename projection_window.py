from random import sample
from numpy import dtype
from numpy.core.fromnumeric import reshape
import utils
import numpy as np
# importing Qt widgets
from PyQt5.QtWidgets import *

# importing system
import sys

from pyift.pyift import Sample

import utils

# importing pyqtgraph as pg
import pyqtgraph as pg
from PyQt5.QtGui import *

import warnings
ift = None

try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

class SamplePoint(pg.SpotItem):
	def __init__(self, id, x, y, img, true_label):
		self.id=id
		self.x=x
		self.y=y
		self.img=img
		self.true_label=true_label
	
	def print_info(self):
		print("{")
		print("    id: ", self.id)
		print("    x: ", self.x)
		print("    y: ", self.y)
		print("    img: ", self.img)
		print("}")

class ProjectionWindow(QMainWindow):

	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("PyQtGraph")

		# setting geometry
		self.setGeometry(100, 100, 600, 500)

		# icon
		icon = QIcon("skin.png")

		# setting icon to the window
		self.setWindowIcon(icon)

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()


	# method for components
	def UiComponents(self):

		# creating a widget object
		widget = QWidget()

		# creating a label
		label = QLabel("t-SNE projection")

		# making label do word wrap
		label.setWordWrap(True)

		training_data = utils.get_training_data()[:1000]

		X = training_data[:,0]
		X_ = np.array([x.flatten() for x in X], dtype=np.float32)
		# print(X_)
		Y = np.array(training_data[:,1], dtype=np.int32)
		paths = list(training_data[:,2])
		ids = np.array(training_data[:,3], dtype=np.int32)
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
			p = SamplePoint(ids[i], sample_x, sample_y, ref_data[i], true_labels[i])
			self.sample_points[str(sample_x)+" "+str(sample_y)] = p
		
		# for key in sample_points:
		# 	sample_points[key].print_info()
		
		# creating a plot window      
		plot = pg.plot()

     
  
        # creating a scatter plot item
        # of size = 10
        # using brush to enlarge the of green color
		scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(30, 255, 35, 255))


  		# Convert data array into a list of dictionaries with the x,y-coordinates
		# pos = [{'pos': tsne[:, i]} for i in range(len(tsne))]
		# adding spots to the scatter plot
		
		for key in self.sample_points:
			sample = self.sample_points[key]
			if np.asscalar(sample.true_label)== 0:
				scatter.addPoints([{'pos': (sample.x,sample.y), 'brush':'r'}])
			else:
				scatter.addPoints(x=[sample.x], y=[sample.y])
  
        # add item to plot window
        # adding scatter plot item to the plot window
		plot.addItem(scatter)


		# Creating a grid layout
		layout = QGridLayout()

		# minimum width value of the label
		label.setMinimumWidth(130)

		# setting this layout to the widget
		widget.setLayout(layout)

		# adding label in the layout
		layout.addWidget(label, 1, 0)

		# plot window goes on right side, spanning 3 rows
		layout.addWidget(plot, 0, 1, 3, 1)

		# setting this widget as central widget of the main widow
		self.setCentralWidget(widget)

		scatter.sigClicked.connect(self.clicaste)
	
	def clicaste(self, obj, points):
		key = str(points[0]._data['x']) + " " + str(points[0]._data['y'])
		print("clicaste no ponto da imagem: ", self.sample_points[key].img)
