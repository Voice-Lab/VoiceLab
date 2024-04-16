from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget
from .custom_dialogs import PraatInfoDialog
from PyQt6.QtCore import Qt

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
        
        # Connect the itemDoubleClicked signal
        self.voiceList.itemDoubleClicked.connect(self.on_item_double_clicked)


    def loadVoice(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Sound files (*.wav *.mp3)")
        if dialog.exec():
            self.file_names = dialog.selectedFiles()
            for file_name in self.file_names:
                # Try to load the file using FileManager
                #try:
                self.fileManager.load_file(file_name)
                self.voiceList.addItem(file_name)
                #except Exception as e:
                #    # Failure: Report error (file already loaded or other reasons)
                #    print(e)


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
                if items := self.voiceList.findItems(
                    file_path, Qt.MatchFlag.MatchExactly
                ):
                    for item in items:
                        self.voiceList.takeItem(self.voiceList.row(item))

    def on_item_double_clicked(self, item):
        file_name = item.text()
        voice_file = self.fileManager.get_file_data(file_name)
        
        # Assuming voice_file.praat_sound_object contains the information to display
        # You might need to convert or extract the information from praat_sound_object differently
        info_text = str(voice_file.praat_sound_object)
        
        dialog = PraatInfoDialog(info_text, self)
        dialog.exec()
