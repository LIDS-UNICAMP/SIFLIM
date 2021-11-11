# importing Qt widgets
from PyQt5.QtWidgets import *

# importing system
import sys

from projection_window import *


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of the projection window
projection_window = ProjectionWindow()

# start the app
sys.exit(App.exec())
