from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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

class ImageCanvas(QGraphicsScene):
	def __init__(self, point, patch_set):
		super().__init__()
		self.setSceneRect(0,0,500,500)

		self.sample = point.sample_point
		self.last_x, self.last_y = None, None
		if (self.sample.label == 0):
			self.label = self.sample.true_label
		else:
			self.label = self.sample.label
		
		self.pen_color = index_to_Qcolor(self.label)
		self.patch_set = patch_set
		self.penWidth = 4
		self.scribbling = False

		loadedImage: QImage = QImage(self.sample.img)

		self.pix = QPixmap.fromImage(loadedImage)
		self.pixmap_item = self.addPixmap(self.pix)
		painter = QPainter(self.pix)

		# set rectangle color and thickness
		self.penRectangle = QPen(Qt.red)
		self.penRectangle.setWidth(3)

		# draw rectangle on painter
		painter.setPen(self.penRectangle)

		for patch in self.patch_set:
			l = (int(np.sqrt(patch.sample_point.size)))
			bb = (patch.sample_point.voxel_coords[0] - l//2,
				patch.sample_point.voxel_coords[1] - l//2, l)
			painter.drawRect(bb[0], bb[1], bb[2], bb[2])

		# self.painter.drawRect(50, 50, 50, 50)
		self.pixmap_item.setPixmap(self.pix)
		self.update()

		# draw previous markers, if any
		p = painter.pen()
		p.setWidth(4)
		p.setColor(self.pen_color)
		
		key = self.sample.img
		if key in MARKERS.keys():
			for xy in MARKERS[key]:
				self.addEllipse(xy[0], xy[1], 1, 1, pen=p)
		
		painter.end()


	def setLabel(self,l):
		self.label = l
		self.pen_color = index_to_Qcolor(l)
		self.sample.label = l

	def reset(self):
		self.lastPoint = QPointF()
		
		loadedImage: QImage = QImage(self.sample.img)
		
		self.pix = QPixmap.fromImage(loadedImage)
		self.pixmap_item = self.addPixmap(self.pix)
		self.pixmap_item.setPixmap(self.pix)

		
		# self.pixmap_item_img = QPixmap(self.sample.img)
		# self.setFixedHeight(self.pixmap_item_img.height())
		# self.setFixedWidth(self.pixmap_item_img.width())

		# create painter instance with pixmap
		painter = QPainter(self.pix)

		# set rectangle color and thickness
		self.penRectangle = QPen(Qt.red)
		self.penRectangle.setWidth(3)

		# draw rectangle on painter
		painter.setPen(self.penRectangle)

		for patch in self.patch_set:
			l = (int(np.sqrt(patch.sample_point.size)))
			bb = (patch.sample_point.voxel_coords[0] - l//2,
				patch.sample_point.voxel_coords[1] - l//2, l)
			painter.drawRect(bb[0], bb[1], bb[2], bb[2])

		# self.painter.drawRect(50, 50, 50, 50)
		self.pixmap_item.setPixmap(self.pix)
		self.update()

		# reset markers
		key = self.sample.img
		MARKERS[key] = set()
		
	
	def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
		if event.button() == Qt.LeftButton:
			self.lastPoint = event.scenePos()
			print((self.lastPoint.x(), self.lastPoint.y()))
			self.scribbling = True


	def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
		if (event.buttons() == Qt.LeftButton) and self.scribbling:
			x = int(event.scenePos().x())
			y = int(event.scenePos().y())

			# add points from line to markers set
			key = self.sample.img

			last_x = int(self.lastPoint.x())
			last_y = int(self.lastPoint.y())
			
			step_x = 1
			if (last_x > x):
				step_x = -1
			for x_ in range(last_x,x, step_x):
				a = (y - last_y) / (x - last_x)
				y_ = last_y + a*(x_ - last_x)
				if key in MARKERS.keys():
					MARKERS[key].add((x_, round(y_), self.pixmap_item.pixmap().width(), self.pixmap_item.pixmap().height(), self.label))
				else:
					MARKERS[key] = set()

			step_y = 1
			if (last_y > y):
				step_y = -1

			for y_ in range(last_y,y, step_y):
				if not (abs(x - last_x) < 1):
					a = (y - last_y) / (x - last_x)
					x_ = last_x + (1/a)*(y_ - last_y)
				else:
					x_ = last_x

				if key in MARKERS.keys():
					MARKERS[key].add((round(x_), y_, self.pixmap_item.pixmap().width(), self.pixmap_item.pixmap().height(), self.label))
				else:
					MARKERS[key] = set()

				self.drawLineTo(event.scenePos())


	def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
		if (event.button() == Qt.LeftButton and self.scribbling):
			self.drawLineTo(event.scenePos())
			self.scribbling = False
		
	

	def drawLineTo(self, endPoint: QPointF):
	
		# painter = QPainter(self.pix)
		# painter.setPen(QPen(self.pen_color, self.penWidth, Qt.SolidLine, Qt.RoundCap,
		# 					Qt.RoundJoin))
		# painter.drawLine(self.lastPoint, endPoint)
		pen = QPen(self.pen_color, self.penWidth, Qt.SolidLine, Qt.RoundCap,
		 					Qt.RoundJoin)
		self.addLine(self.lastPoint.x(), self.lastPoint.y(), endPoint.x(), endPoint.y(), pen=pen)
		# painter.end()
		self.update()
		self.lastPoint = endPoint

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

			sample_canvas: QGraphicsScene = ImageCanvas(point, bb_imgs[sample_img])
			sample_view = QGraphicsView(parent=tab)
			sample_view.setScene(sample_canvas)

			scale: float = 500/sample_canvas.pixmap_item.pixmap().width()
			sample_view.scale(scale,scale)

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
			vbox_layout.addWidget(sample_view)
			tab.setLayout(vbox_layout)
			self.tabs.append(tab)

			self.addTab(tab, "Image " +str(i))
			self.setTabText(i, sample_img)
			i += 1

