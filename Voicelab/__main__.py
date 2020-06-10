import qdarkstyle
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Voicelab.VoicelabWizard.InputTab import InputTab
from Voicelab.VoicelabWizard.OutputTab import OutputTab
from Voicelab.VoicelabWizard.SettingsTab import SettingsTab
from Voicelab.VoicelabWizard.VoicelabController import VoicelabController

from Voicelab.default_settings import available_functions, default_functions


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
        self.setWindowIcon(QIcon('favicon.ico'))
        # signals are created once and passed into each tab
        # TODO: this may be possible using a singleton class or some other OOP way
        self.voicelab_signals = {
            "on_files_changed": self.on_files_changed,
            "on_settings_changed": self.on_settings_changed,
            "on_functions_changed": self.on_functions_changed,
            "on_processing_completed": self.on_processing_completed,
            "on_progress_update": self.on_progress_updated,
        }

        # Specifies the default size of the window, this should be long enough to have all the settings without a slider
        self.setMinimumSize(QSize(800, 680))
        # Specifies the default title, simply change the string to change this
        self.setWindowTitle("Voice Lab: Reproducible Automated Voice Analysis")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_layout = QGridLayout(self)
        central_widget.setLayout(central_layout)

        self.tabs = QTabWidget()
        central_layout.addWidget(self.tabs)

        self.data_controller = VoicelabController()
        # links the progress updating on the data controller side to a pyqt signal that can be listend to anywhere
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

        self.tabs.addTab(
            InputTab(
                self.data_controller, self.voicelab_signals, self.tabs, parent=self
            ),
            "Load Voices",
        )
        self.tabs.addTab(
            SettingsTab(
                self.data_controller, self.voicelab_signals, self.tabs, parent=self
            ),
            "Settings",
        )
        self.tabs.addTab(
            OutputTab(
                self.data_controller, self.voicelab_signals, self.tabs, parent=self
            ),
            "Results",
        )


if __name__ == "__main__":
    # boilerplate pyqt window creation
    app = QApplication(sys.argv)
    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    w = VoicelabWizard()
    w.show()
    sys.exit(app.exec_())
