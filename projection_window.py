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

class SamplePoint():
	def __init__(self, id, x, y, img):
		self.id=id
		self.x=x
		self.y=y
		self.img=img
	
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


		Z = utils.load_opf_dataset('../datasets/corel.zip')

		ds = Z.GetData()
		sample_features = ds[5]
		reduced_ds = ift.DimReductionByTSNE(Z, 2, 20, 1000)
		print(Z.GetData()[10].shape)
		
		proj_data = Z.GetProjection()
		orig_data = Z.GetData()
		ids = Z.GetIds()

		sample_points = {}
		for i in range(Z.nsamples):
			img = orig_data[i]
			p = SamplePoint(ids[i], proj_data[i][0], proj_data[i][1], None)
			sample_points[str(ids[i])] = p
		
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
		
		for sample in proj_data:
			scatter.addPoints(x=[sample[0]], y=[sample[1]])
  
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
