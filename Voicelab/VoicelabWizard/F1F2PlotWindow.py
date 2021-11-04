from PyQt5.QtGui import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


###################################################################################################
# Displays the F1F2 Plot in a new window
###################################################################################################
class F1F2PlotWindow(QMainWindow):
    """This class creates a new window to display F1 F2 Plot.  It is to be called from F1F2PlotNode."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("View F1 F2 Plot") 
        # self.setMinimumSize() has to match self.label.setMinimumSize()
        self.setMinimumSize(600, 600)
        # create a label object inside the new window
        self.label = QLabel(self)
        # set the image file
        self.pixmap = QPixmap('f1f2.png')

        # TODO fix this so we don't get the warning anymore
        # set the central widget
        #self.central_widget = QWidget(self)
        #self.setCentralWidget(self.central_widget)


        # Create a container in the label to put image
        self.container_layout = QVBoxLayout(self)
        # set the layout of the container
        self.setLayout(self.container_layout)
        # resize the image
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(600, 600)
        # add the image widget to the window
        self.container_layout.addWidget(self.label)
        # display the widget
        self.show()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        """Resizes the image when you resize the window"""
        newpixmap: QPixmap = QPixmap("f1f2.png")
        self.pixmap = newpixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width(), self.height())
