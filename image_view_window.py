from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap


class ImageViewWindow(QWidget):
	def __init__(self, image_path):
		super().__init__()

		self.acceptDrops()
		# set the title
		self.setWindowTitle("Image")

		# setting the geometry of window
		self.setGeometry(0, 0, 400, 300)

		# creating label
		self.label = QLabel(self)
		
		# loading image
		self.pixmap = QPixmap(image_path)

		# adding image to label
		self.label.setPixmap(self.pixmap)

		# Optional, resize label to image size
		self.label.resize(self.pixmap.width(),
						self.pixmap.height())



