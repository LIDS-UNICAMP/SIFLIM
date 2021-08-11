# importing Qt widgets
from PyQt5.QtWidgets import *

# importing system
import sys

# importing pyqtgraph as pg
import pyqtgraph as pg
from PyQt5.QtGui import *

import warnings
ift = None

try:
    import pyift.pyift as ift
except:
    warnings.warn("PyIFT is not installed.", ImportWarning)

def load_opf_dataset(path):
    assert ift is not None, "PyIFT is not available"

    opf_dataset = ift.ReadDataSet(path)

    return opf_dataset


class Window(QMainWindow):

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


		Z = load_opf_dataset('../datasets/corel.zip')

		tsne = ift.DimReductionByTSNE(Z, 2, 20, 1000).GetData()
		
		# creating a plot window      
		plot = pg.plot()
  
     
  
        # creating a scatter plot item
        # of size = 10
        # using brush to enlarge the of green color
		scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(30, 255, 35, 255))

  		# Convert data array into a list of dictionaries with the x,y-coordinates
		# pos = [{'pos': tsne[:, i]} for i in range(len(tsne))]
		# adding spots to the scatter plot
	
		scatter.setData(pos=tsne)
  
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


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
