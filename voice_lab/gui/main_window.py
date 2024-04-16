import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from dataclasses import fields
from voice_lab.gui.file_manager import FileManager
from voice_lab.gui.custom_widgets import VoiceLoadingWidget
from voice_lab.gui.figure_display import MplCanvas
from voice_lab.gui.custom_dialogs import PraatInfoDialog
from voice_lab.Algorithms.VisualizeSpectrogramNode import VisualizeSpectrogramNode
from voice_lab.gui.threading_utils import VoiceLoaderThread, LoaderSignals
from voice_lab.gui.sharedVoiceAttributes import VoiceFile

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fileManager = FileManager()
        self.connectSignals()
        self.setWindowTitle("VoiceLab 3.0")
        self.resize(800, 600)
        self.initUI()
        self.initProgressDialog()

    def connectSignals(self):
        self.fileManager.fileLoading.connect(self.updateStatusLabelLoading)
        self.fileManager.fileLoaded.connect(self.updateStatusLabelLoaded)
        self.fileManager.progressUpdated.connect(self.update_progress)
        self.fileManager.fileLoaded.connect(self.on_file_loaded)

    def initUI(self):
        layout = QVBoxLayout()
        self.setupVoiceLoadingWidget(layout)
        self.createMenuBar()
        self.setupDataDisplayWidget(layout)
        self.setupAdditionalUI(layout)
        self.setCentralWidgetWithLayout(layout)

    def initProgressDialog(self):
        self.progressDialog = QProgressDialog("Loading files...", "Cancel", 0, 100, self)
        self.progressDialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.setAutoClose(True)
        self.progressDialog.hide()

    def setupVoiceLoadingWidget(self, layout):
        self.voiceLoadingWidget = VoiceLoadingWidget(self.fileManager)
        layout.addWidget(self.voiceLoadingWidget)
        self.voiceLoadingWidget.voiceList.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.voiceLoadingWidget.voiceList.itemSelectionChanged.connect(self.on_selection_changed)

    def setupDataDisplayWidget(self, layout):
        self.dataDisplayWidget = QWidget()
        dataLayout = QVBoxLayout(self.dataDisplayWidget)
        dataLabel = QLabel("Data Display Widget")
        dataLayout.addWidget(dataLabel)
        self.table = QTableWidget()
        self.table.setRowCount(10)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(VoiceFile.__dataclass_fields__.keys())
        dataLayout.addWidget(self.table)
        layout.addWidget(self.dataDisplayWidget)

    def setupAdditionalUI(self, layout):
        self.plotCanvas = MplCanvas(width=5, height=4, dpi=100)
        layout.addWidget(self.plotCanvas)
        self.statusLabel = QLabel("Ready")
        layout.addWidget(self.statusLabel)

    def setCentralWidgetWithLayout(self, layout):
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        openAction = QAction('Open', self)
        openAction.triggered.connect(self.open_file_dialog)
        fileMenu.addAction(openAction)

    def on_selection_changed(self):
        selected_items = self.voiceLoadingWidget.voiceList.selectedItems()
        if not selected_items:
            return
        file_paths = [item.text() for item in selected_items]
        self.load_files(file_paths)

    def load_files(self, files):
        self.prepareProgressDialog(len(files))
        self.manageFileLoadingThread(files)

    def prepareProgressDialog(self, fileCount):
        self.progressDialog.setMaximum(100)
        self.progressDialog.setValue(0)
        self.progressDialog.show()

    def manageFileLoadingThread(self, files):
        if hasattr(self, 'fileLoaderThread') and self.fileLoaderThread.isRunning():
            self.fileLoaderThread.terminate()
            self.fileLoaderThread.wait()
        self.fileLoaderThread = VoiceLoaderThread(files, self.fileManager)
        self.fileLoaderThread.progress.connect(self.update_progress, Qt.ConnectionType.UniqueConnection)
        self.fileLoaderThread.finished.connect(self.files_loaded, Qt.ConnectionType.UniqueConnection)
        self.fileLoaderThread.start()

    def update_progress(self, value, message):
        self.progressDialog.setValue(value)
        self.progressDialog.setLabelText(message)
        if value >= 100:
            QTimer.singleShot(500, self.progressDialog.accept)

    def updateStatusLabelLoading(self, file_name):
        self.statusLabel.setText(f"Loading {file_name}")

    def updateStatusLabelLoaded(self):
        self.statusLabel.setText("File(s) loaded successfully")

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Select one or more files to open", "", 
                                                "All Files (*);;wav Files (*.wav)", options=options)
        if files:
            self.load_files(files)

    def files_loaded(self, results):
        self.results = results  # Store the results
        self.update_ui()


    def on_file_loaded(self):
        # get the file data
        self.update_ui()

    def set_data_to_table(self):
        self.table.setRowCount(len(self.results))
        for row, result in enumerate(self.results):
            for col, field in enumerate(fields(VoiceFile)):
                self.table.setItem(row, col, QTableWidgetItem(str(getattr(result, field.name))))
    
    def update_ui(self):
        # Refresh the table to show new data
        self.set_data_to_table()
        self.table.viewport().update()
        self.update_spectrogram()

    def update_spectrogram(self):
        if self.results and len(self.results) > 0:
            signal = self.results[0].signal  # Ensure your VoiceFile class or equivalent has this attribute
            sampling_rate = self.results[0].sampling_rate  # Ensure your VoiceFile class or equivalent has this attribute
            self.plotCanvas.display_spectrogram(signal, sampling_rate)
