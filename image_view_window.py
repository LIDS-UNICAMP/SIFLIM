from PyQt5.QtCore import QPointF, Qt, QRect
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainterPath, QWindow
from PyQt5.QtGui import QBrush, QPainter, QColor, QPen, QPixmap, QPolygonF
import numpy as np

from utils import *


class ImageViewWindow(QWidget):
	def __init__(self, points):
		super().__init__()
		self.images_tab_bar = ImagesTabs(points)
		self.setWindowTitle("Selected Images")

		# setting geometry
		self.setGeometry(100, 100, 1000, 800)
		hbox = QHBoxLayout()
		hbox.addWidget(self.images_tab_bar)
		self.setLayout(hbox)

class ImageCanvas(QLabel):
	def __init__(self, point, patch_set):
		super().__init__()
		self.sample = point.sample_point
		self.last_x, self.last_y = None, None
		if (self.sample.label == 0):
			self.label = self.sample.true_label
		else:
			self.label = self.sample.label
		
		self.pen_color = index_to_Qcolor(self.label)
		self.patch_set = patch_set
		
		self.pixmap_img = QPixmap(self.sample.img)
		self.setFixedHeight(self.pixmap_img.height())
		self.setFixedWidth(self.pixmap_img.width())

		# create painter instance with pixmap
		self.painter = QPainter(self.pixmap_img)

		# set rectangle color and thickness
		self.penRectangle = QPen(Qt.red)
		self.penRectangle.setWidth(3)

		# draw rectangle on painter
		self.painter.setPen(self.penRectangle)

		for patch in self.patch_set:
			l = (int(np.sqrt(patch.sample_point.size)))
			bb = (patch.sample_point.voxel_coords[0] - l//2,
				patch.sample_point.voxel_coords[1] - l//2, l)
			self.painter.drawRect(bb[0], bb[1], bb[2], bb[2])

		# self.painter.drawRect(50, 50, 50, 50)


		# draw previous markers, if any
		p = self.painter.pen()
		p.setWidth(4)
		p.setColor(self.pen_color)
		self.painter.setPen(p)
		key = self.sample.img
		if key in MARKERS.keys():
			for xy in MARKERS[key]:
				self.painter.drawPoint(QPointF(xy[0], xy[1]))


		self.painter.end()

		self.setPixmap(self.pixmap_img)

	def setLabel(self,l):
		self.label = l
		self.pen_color = index_to_Qcolor(l)
		self.sample.label = l

	def reset(self):
		self.last_x, self.last_y = None, None
		
		self.pixmap_img = QPixmap(self.sample.img)
		self.setFixedHeight(self.pixmap_img.height())
		self.setFixedWidth(self.pixmap_img.width())

		# create painter instance with pixmap
		self.painter = QPainter(self.pixmap_img)

		# set rectangle color and thickness
		self.penRectangle = QPen(Qt.red)
		self.penRectangle.setWidth(3)

		# draw rectangles on painter
		self.painter.setPen(self.penRectangle)
		for patch in self.patch_set:
			l = (int(np.sqrt(patch.sample_point.size)))
			bb = (patch.sample_point.voxel_coords[0] - l//2,
				patch.sample_point.voxel_coords[1] - l//2, l)
			self.painter.drawRect(bb[0], bb[1], bb[2], bb[2])
		# self.painter.drawRect(50, 50, 50, 50)

		self.painter.end()

		self.setPixmap(self.pixmap_img)

		# reset markers
		key = self.sample.img
		MARKERS[key] = set()
		

	def mouseMoveEvent(self, e):
		x = e.x()
		y = e.y()
	
		if self.last_x is None: # First event.
			self.last_x = x
			self.last_y = y
			return # Ignore the first time.

		painter = QPainter(self.pixmap())
		p = painter.pen()
		p.setWidth(4)
		p.setColor(self.pen_color)
		painter.setPen(p)
		painter.drawLine(self.last_x, self.last_y, x, y)
		painter.end()
		self.update()

		# add points from line to markers set
		key = self.sample.img

		step_x = 1
		if (self.last_x > x):
			step_x = -1
		for x_ in range(self.last_x,x, step_x):
			a = (y - self.last_y) / (x - self.last_x)
			y_ = self.last_y + a*(x_ - self.last_x)
			if key in MARKERS.keys():
				MARKERS[key].add((x_, round(y_), self.pixmap_img.width(), self.pixmap_img.height(), self.label))
			else:
				MARKERS[key] = set()

		step_y = 1
		if (self.last_y > y):
			step_y = -1

		for y_ in range(self.last_y,y, step_y):
			if not (abs(x - self.last_x) < 1):
				a = (y - self.last_y) / (x - self.last_x)
				x_ = self.last_x + (1/a)*(y_ - self.last_y)
			else:
				x_ = self.last_x

			if key in MARKERS.keys():
				MARKERS[key].add((round(x_), y_, self.pixmap_img.width(), self.pixmap_img.height(), self.label))
			else:
				MARKERS[key] = set()

		# Update the origin for next time.
		self.last_x = x
		self.last_y = y

	def mouseReleaseEvent(self, e):
		self.last_x = None
		self.last_y = None

class ImagesTabs(QTabWidget):
	def __init__(self, points):
		super().__init__()
		self.tabs = []
		i = 0
		bb_imgs = dict()
		for point in points:
			if point.sample_point.img in bb_imgs.keys():
				bb_imgs[point.sample_point.img].add(point)
			else:
				bb_imgs[point.sample_point.img] = set([point])

		for sample_img in bb_imgs.keys():
			point = tuple(bb_imgs[sample_img])[0]

			tab = QWidget()
			vbox_layout = QVBoxLayout()

			sample_canvas = ImageCanvas(point, bb_imgs[sample_img])

			cb = QComboBox()
			for color in LabelColor:
				cb.addItem("Class "+ str(color.value))
			cb.currentIndexChanged.connect(lambda index: sample_canvas.setLabel(index+1))
			cb.setCurrentIndex(sample_canvas.label - 1)

			reset_markers_button = QPushButton("Clear Markers")
			reset_markers_button.setFixedHeight(20)
			reset_markers_button.setFixedWidth(100)
			reset_markers_button.clicked.connect(sample_canvas.reset)

			vbox_layout.addWidget(cb)
			vbox_layout.addWidget(reset_markers_button)
			vbox_layout.addWidget(sample_canvas)
			tab.setLayout(vbox_layout)
			self.tabs.append(tab)

			self.addTab(tab, "Image " +str(i))
			self.setTabText(i, sample_img)
			i += 1

