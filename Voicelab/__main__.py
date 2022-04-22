import qdarkstyle
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Voicelab.VoicelabWizard.InputTab import InputTab
from Voicelab.VoicelabWizard.OutputTab import OutputTab
from Voicelab.VoicelabWizard.SettingsTab import SettingsTab
#from Voicelab.VoicelabWizard.ExperimentalTab import ExperimentalTab
from Voicelab.VoicelabWizard.VoicelabController import VoicelabController
#from Voicelab.VoicelabWizard.ManipulationWindow import ManipulationWindow
from Voicelab.default_settings import available_functions, default_functions

# import logging


sys.setrecursionlimit(10000)


class VoicelabWizard(QMainWindow):
    # triggers when the list of loaded files has changed with the active list of files
    on_files_changed = pyqtSignal(list)

    # triggers when a setting is changed with the list of active settings for the respective function
    on_settings_changed = pyqtSignal(dict)

    # triggers when the list of active functions is changed with the list of active functions
    on_functions_changed = pyqtSignal(dict)

    # triggers when the pipeline is done processing all of the files with the results
    on_processing_completed = pyqtSignal(dict)

    # triggers on each node finishing with the node name, the start, current, and end count of processed nodes
    on_progress_updated = pyqtSignal(str, int, int, int)

    def __init__(self):
        super().__init__()

        # set the icon in the corner of the window
        self.setWindowIcon(QIcon('Voicelab/favicon.ico'))

        # signals are created once and passed into each tab
        # TODO: this may be possible using a singleton class or some other OOP way

        # Puts all signals into a dictionary that's loaded into each tab
        self.voicelab_signals = {
            "on_files_changed": self.on_files_changed,
            "on_settings_changed": self.on_settings_changed,
            "on_functions_changed": self.on_functions_changed,
            "on_processing_completed": self.on_processing_completed,
            "on_progress_update": self.on_progress_updated,
        }

        # Specifies the default size of the window,
        # this should be long enough to have all the settings without a slider
        self.setMinimumSize(QSize(800, 880))
        # Specifies the default title, simply change the string to change this
        self.setWindowTitle("Voice Lab: Reproducible Automated Voice Analysis")

        # This is the main widget in the main window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        # This set's up a grid layout for the central_widget
        central_layout = QGridLayout(self)
        central_widget.setLayout(central_layout)

        # This sets up the tab layout for the central_layout
        self.tabs = QTabWidget()
        central_layout.addWidget(self.tabs)

        # init: setup the base state of a controller, including a data model
        self.data_controller = VoicelabController()
        # links the progress updating on the data controller side to a pyqt signal that can be listened to anywhere
        self.data_controller.progress_callback = lambda node, start, current, end: self.voicelab_signals[
            "on_progress_update"
        ].emit(
            node.node_id, start, current, end
        )

        # load all of the functions specified in the default settings file
        for fn in available_functions:
            self.data_controller.load_function(
                fn, available_functions[fn], default=fn in default_functions
            )

        # add the Input Tab
        self.tabs.addTab(
            InputTab(
                self.data_controller, self.voicelab_signals, self.tabs, parent=self
            ),
            "Load Voices",
        )
        # add the Settings Tab
        self.tabs.addTab(
            SettingsTab(
                self.data_controller, self.voicelab_signals, self.tabs, parent=self
            ),
            "Settings",
        )
        # add the Output Tab
        self.tabs.addTab(
            OutputTab(
                self.data_controller, self.voicelab_signals, self.tabs, parent=self
            ),
            "Results",
        )

        # add the Voice Spectrum Tab
        #self.tabs.addTab(
        #    ExperimentalTab(
        #        self.data_controller, self.voicelab_signals, self.tabs, parent=self
        #    ),
        #    "Results (Spectrum)",
        #)

        # add the Manipulation Tab
        #self.tabs.addTab(
        #    ManipulationWindow(
        #        self.data_controller, self.voicelab_signals, self.tabs, parent=self
        #    ),
        #    "Voice Manipulations",
        #)

        # Experimental tab
        #self.tabs.addTab(
        #    ExperimentalTab(
        #        self.data_controller, self.voicelab_signals, self.tabs, parent=self
        #    ),
        #    "Experimental",  # Specify the Tab title here
        #)


if __name__ == "__main__":

    # boilerplate pyqt window creation
    app = QApplication(sys.argv)
    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # Create an instance of VoiceLab
    w = VoicelabWizard()
    # Show the GUI
    w.show()
    # Exit gracefully
    sys.exit(app.exec_())




