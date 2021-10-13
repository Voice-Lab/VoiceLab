from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Voicelab.VoicelabWizard.VoicelabTab import VoicelabTab


###################################################################################################
# OutputTab(VoicelabTab) : presentation widget for displaying and the results of our pipeline process
###################################################################################################
class F1F2PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 F2 Plot")
        self.setMinimumSize(400, 400)
        self.label = QLabel(self)
        self.pixmap = QPixmap('f1f2.png')
        #self.selected_tab = 0
        self.container_layout = QVBoxLayout(self)
        self.setLayout(self.container_layout)
        # Display image
        print("label size: ", self.label.size())
        self.label.setPixmap(self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.label.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(400, 400)

        self.container_layout.addWidget(self.label)
        self.show()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        pixmap1 = QPixmap("f1f2.png")
        self.pixmap = pixmap1.scaled(self.width(), self.height(),
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation
                                     )
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width(), self.height())

    #def resizeEvent(self, event):
    #    scaledSize = self.label.size()
    #    scaledSize.scale(self.label.size(), Qt.KeepAspectRatio)
    #    if not self.label.pixmap() or scaledSize != self.label.pixmap().size():
    #        self.updateLabel()
#
    #def updateLabel(self):
    #    self.label.setPixmap(self.pixmap.scaled(
    #        self.label.size(), Qt.KeepAspectRatio,
    #        Qt.SmoothTransformation))


class ExperimentalTab(VoicelabTab):
    def __init__(self, data_controller, signals, tabs, *args, **kwargs):
        """
        Args:
            data_controller:
            signals:
            tabs:
            *args:
            **kwargs:
        """
        super().__init__(data_controller, signals, tabs, *args, **kwargs)

        self.f1f2button = QPushButton("Click to View F1 F2 Plot.")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.f1f2button)
        self.setLayout(self.layout)
        self.f1f2button.clicked.connect(self.on_click)
        #self.tabs = tabs

    @pyqtSlot()
    def on_click(self):
        self.f1f2button.clicked.connect(self.popupwindow)

    def popupwindow(self):
        self.plotwindow = F1F2PlotWindow()
        self.plotwindow.show()
        self.hide()

