from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QPainter, QPen, QPixmap, QPolygonF


class ImageViewWindow(QGraphicsView):
	def __init__(self, image_path):
		super().__init__()


		# Defining a scene rect of 400x200, with it's origin at 0,0.
		# If we don't set this on creation, we can set it later with .setSceneRect
		scene = QGraphicsScene(0, 0, 400, 200)

		# Draw a rectangle item, setting the dimensions.
		rect = QGraphicsRectItem(0, 0, 200, 50)

		# Set the origin (position) of the rectangle in the scene.
		rect.setPos(50, 20)

		# Define the brush (fill).
		brush = QBrush(Qt.red)
		rect.setBrush(brush)

		# Define the pen (line)
		pen = QPen(Qt.cyan)
		pen.setWidth(10)
		rect.setPen(pen)

		scene.addItem(rect)

		self.setScene(scene)



