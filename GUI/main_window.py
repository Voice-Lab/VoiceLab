import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTabWidget, QTextEdit, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from file_manager import FileManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fileManager = FileManager()  # Instantiate FileManager
        
        # Correctly instantiate VoiceLoadingWidget with FileManager
        self.voiceLoadingWidget = VoiceLoadingWidget(self.fileManager)

        self.setWindowTitle("Voice Analysis Application")
        self.resize(800, 600)

        # Menu Bar
        self.createMenuBar()

        # Main layout
        layout = QVBoxLayout()

        # Add the voice loading widget to the layout
        layout.addWidget(self.voiceLoadingWidget)

        # Initialize the table attribute
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # allow selection of multiple files
        # Access voiceList through voiceLoadingWidget
        self.voiceLoadingWidget.voiceList.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        
        # Connect the itemSelectionChanged signal to the on_selection_changed slot
        self.voiceLoadingWidget.voiceList.itemSelectionChanged.connect(self.on_selection_changed)

        # Create a data display widget underneath all the other widgets
        self.dataDisplayWidget = QWidget()
        dataLayout = QVBoxLayout()
        dataLayout.addWidget(QLabel("Data Display Widget"))
        self.dataDisplayWidget.setLayout(dataLayout)
        layout.addWidget(self.dataDisplayWidget)


        # add a table to the data display widget
        self.table = QTableWidget()
        dataLayout.addWidget(self.table)

        # Central Widget
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def createMenuBar(self):
        menuBar = self.menuBar()  # Correct way to access the menu bar
        fileMenu = menuBar.addMenu('File')
        self.openAction = QAction('Open', self)
        self.openAction.triggered.connect(self.voiceLoadingWidget.loadVoice)
        fileMenu.addAction(self.openAction)
        editMenu = menuBar.addMenu('Edit')
        helpMenu = menuBar.addMenu('Help')

    def on_selection_changed(self):
        selected_items = self.voiceLoadingWidget.voiceList.selectedItems()
        self.table.setRowCount(0)  # Clear the table
        self.table.setColumnCount(0)  # Clear the columns

        all_headers = set()  # Use a set to collect unique headers
        all_values = []

        for item in selected_items:
            file_name = item.text()
            headers, values = self.get_data(self.fileManager.loaded_files[file_name])
            all_headers.update(headers)
            all_values.append(values)

        self.set_data_to_table(list(all_headers), all_values)

    def get_data(self, voice_file):
        data = vars(voice_file)  # Get a dictionary of the VoiceFile's attributes
        extra_attributes = data.pop('extra_attributes', {})  # Remove and get the extra_attributes dictionary

        headers = list(data.keys()) + list(extra_attributes.keys())
        values = list(data.values()) + list(extra_attributes.values())

        return headers, values

    def set_data_to_table(self, headers, all_values):
        self.table.setRowCount(len(all_values) + 1)  # One row for headers and one row for each file's values
        self.table.setColumnCount(len(headers))  # One column for each header

        for i, header in enumerate(headers):
            self.table.setItem(0, i, QTableWidgetItem(str(header)))

        for i, values in enumerate(all_values, start=1):
            for j, value in enumerate(values):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        # Make the table cell widths draggable
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)


class VoiceLoadingWidget(QWidget):
    def __init__(self, fileManager):
        super().__init__()
        self.fileManager = fileManager
        self.voiceList = QListWidget()
        self.loadVoiceBtn = QPushButton("Load Voice")
        self.loadVoiceBtn.clicked.connect(self.loadVoice)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Loaded Voices:"))
        layout.addWidget(self.voiceList)
        layout.addWidget(self.loadVoiceBtn)

        self.unloadVoiceBtn = QPushButton("Unload Voice")
        self.unloadVoiceBtn.clicked.connect(self.unloadVoice)
        layout.addWidget(self.unloadVoiceBtn)

        self.setLayout(layout)
        self.voiceList.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

    def loadVoice(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Sound files (*.wav *.mp3)")
        if dialog.exec():
            self.file_names = dialog.selectedFiles()
            for file_name in self.file_names:
                # Try to load the file using FileManager
                try:
                    self.fileManager.load_file(file_name)
                    self.voiceList.addItem(file_name)
                except Exception as e:
                    # Failure: Report error (file already loaded or other reasons)
                    print(f"Error loading: {file_name}\n{e}")
    

    def unloadVoice(self):
        selected_items = self.voiceList.selectedItems()
        unloaded_files = []

        # Iterate over selected items and attempt to unload each
        for item in selected_items:
            file_path = item.text()  # Assuming the item text is the file path or a unique identifier
            if self.fileManager.unload_file(file_path):
                unloaded_files.append(file_path)

        # Update the QListWidget to reflect the unloaded files
        if unloaded_files:
            for file_path in unloaded_files:
                # Find and remove the item from the list
                items = self.voiceList.findItems(file_path, Qt.MatchFlag.MatchExactly)  # Corrected for PyQt6
                if items:
                    for item in items:
                        self.voiceList.takeItem(self.voiceList.row(item))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
