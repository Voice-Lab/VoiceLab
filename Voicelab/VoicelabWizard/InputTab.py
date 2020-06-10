from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QSound

from Voicelab.pipeline.Pipeline import Pipeline
import Voicelab.toolkits.Voicelab as Voicelab

import sklearn.utils._cython_blas
import sklearn.neighbors.typedefs
import sklearn.neighbors.quad_tree
import sklearn.tree
import sklearn.tree._utils
import webbrowser

from Voicelab.VoicelabWizard.VoicelabTab import VoicelabTab


class InputTab(VoicelabTab):
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
        self.signals = signals
        self.signals["on_files_changed"].connect(self.on_files_changed)
        self.initUI()

    def initUI(self):

        # FilesTab
        self.layout = QVBoxLayout()

        # List of loaded voice files
        self.list_loaded_voices = QListWidget()
        self.list_loaded_voices.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_loaded_voices.itemSelectionChanged.connect(self.onselection_change)

        # Create and connect add button
        btn_add_voices = QPushButton("Load Sound File(s)")
        btn_add_voices.clicked.connect(self.onclick_add)

        # Create and connect remove button
        btn_remove_voices = QPushButton("Remove Sound File(s)")
        btn_remove_voices.clicked.connect(self.onclick_remove)

        # Create and connect start button
        self.btn_start = QPushButton("Start Queue")
        self.btn_start.clicked.connect(self.onclick_start)
        self.btn_start.setDisabled(True)

        # Create and connect help button
        btn_help = QPushButton("Help")
        btn_help.clicked.connect(self.onclick_help)

        # Create and connect play button
        btn_play = QPushButton("Play Sound File(s)")
        btn_play.clicked.connect(self.onclick_play)

        # Create and connect stop button
        btn_stop = QPushButton("Stop Playing Sound File(s)")
        btn_stop.clicked.connect(self.onclick_stop)

        # Create the progress bar
        self.progress = QProgressBar()

        # Display the widgets in the correct order
        self.layout.addWidget(btn_add_voices)
        self.layout.addWidget(btn_remove_voices)
        self.layout.addWidget(btn_play)
        self.layout.addWidget(btn_stop)
        self.layout.addWidget(btn_help)
        self.layout.addWidget(self.list_loaded_voices)
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.progress)

        # Loaded Voice List
        self.setLayout(self.layout)

    #onclick_help
    def onclick_help(self):
        try:
            url = 'Voicelab/help/index.html'
            webbrowser.open(url, new=2)  # open in new tab
        except:
            pass

    # onclick_play
    def onclick_play(self):
        try:
            for self.soundfile in self.playlist:
                self.sound = QSound(self.soundfile)
                self.sound.play()
        except:
            pass

    # onclick_stop
    def onclick_stop(self):
        try:
            self.sound.stop()
        except:
            pass

    ###############################################################################################
    # on_selection_change: callback for when the selection of files has changed.
    ###############################################################################################
    def onselection_change(self):
        active_widgets = self.list_loaded_voices.selectedItems()
        active_files = [i.text() for i in active_widgets]

        # simply pass the selected files on to the controller
        self.data_controller.activate_voices(active_files)
        self.signals["on_files_changed"].emit(self.data_controller.active_voices)
        self.playlist = active_files
    ###############################################################################################
    # onclick_add: callback for when the add file button is pressed. adds a list of files to the model
    ###############################################################################################
    def onclick_add(self):

        # Select a collection of voice files using the systems default dialog
        options = QFileDialog.Options()
        file_locations = QFileDialog.getOpenFileNames(
            self,
            "QFileDialog.getOpenFileNames()",
            "",
            "Sound Files (*.wav *.mp3 *.aiff *.ogg *.aifc *.au *.nist *.flac)",
            options=options,
        )[0]

        # Display the loaded files in a list. Only add if the file is not already loaded
        for file_location in file_locations:
            if file_location is not self.data_controller.loaded_voices:
                widget = QListWidgetItem(parent=self.list_loaded_voices)
                widget.setText(file_location)
                widget.setSelected(True)
            self.data_controller.load_voices([file_location])

        if len(file_locations) > 0:
            self.signals["on_files_changed"].emit(self.data_controller.active_voices)

    ###############################################################################################
    # on_files_changed: callback for when the list of files are changes to update the displayed list.
    ###############################################################################################
    def on_files_changed(self, file_locations):

        """
        Args:
            file_locations:
        """
        if len(file_locations) > 0:
            self.btn_start.setDisabled(False)
        else:
            self.btn_start.setDisabled(True)

    ###############################################################################################
    # onclick_remove()
    # Remove all of the selected voice files from the list gui and the data model
    ###############################################################################################
    def onclick_remove(self):
        try:
            active_files = self.list_loaded_voices.selectedItems()

            for list_item in active_files:
                file_path = list_item.text()
                self.data_controller.unload_voices([file_path])
                self.list_loaded_voices.takeItem(self.list_loaded_voices.row(list_item))

            self.signals["on_files_changed"].emit(self.data_controller.active_voices)
        except:
            pass

    ###############################################################################################
    # onclick_start()
    # Constructs and starts a WARIO pipeline to process loaded voices according to the settings
    ###############################################################################################
    def onclick_start(self):

        self.data_controller.reset_figures()

        n_voices = len(self.data_controller.active_voices)
        n_functions = len(self.data_controller.active_functions) + 1
        self.progress.setMinimum(0)
        self.progress.setMaximum(n_voices * n_functions)
        self.signals["on_progress_update"].connect(self.on_progress_updated)

        self.start_process()

        self.tabs.setCurrentIndex(2)

    ###############################################################################################
    # on_progress_updated: callback function for when progress is made during pipeline processing
    # + node: the name of the node that finished running
    # + start: the progress number this started with (most often 0)
    # + current: the current progress as an integer of how many nodes have finished processing
    # + end: the total number of nodes that will be processed as reported at the start of processing
    ###############################################################################################
    def on_progress_updated(self, node, start, current, end):
        """
        Args:
            node:
            start:
            current:
            end:
        """
        self.progress.setValue(current)
        print(node, start, current, end)
