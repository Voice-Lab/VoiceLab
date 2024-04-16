from .sharedVoiceAttributes import VoiceAttributes, VoiceFile
from PyQt6.QtCore import QObject, pyqtSignal

from hashlib import sha256

class FileManager(QObject):
    # Define custom signals
    fileLoading = pyqtSignal(str)  # Signal with a string argument indicating the file name being loaded
    fileLoaded = pyqtSignal()  # Signal emitted when the file(s) are loaded successfully
    progressUpdated = pyqtSignal(int, str)  # Signal to update progress and status message

    def __init__(self):
        super().__init__() # Call the parent class constructor
        self.loaded_files = {}
        
    def load_file(self, file_path):
        """Load a file and store its data in the loaded_files dictionary."""
        #self.fileLoading.emit(file_path)  # Notify start of loading
        #self.progressUpdated.emit(10, f"Starting to load {file_path}")  # Initial progress update

        self.voice_attributes = VoiceAttributes(file_path)
        #self.progressUpdated.emit(50, f"Analyzing data for {file_path}")  # Midway progress update

        self.praat_data = self.voice_attributes.load_sound_praat()
        self.sound_file_data = self.voice_attributes.get_unscaled_signal()
        file_data = self.sound_file_data | self.praat_data
        print(f"{file_data=}")
        self.loaded_files[file_path] = file_data
        return file_data

    def get_file_data(self, file_path):
        """Return the data for a loaded file."""
        return self.loaded_files.get(file_path)
    
    def unload_file(self, file_path):
        if file_path in self.loaded_files:
            del self.loaded_files[file_path]
            return True
        return False

    def list_files(self):
        """Return a list of all loaded file paths."""
        return list(self.loaded_files.keys())
    
    def unload_all_files(self):
        self.loaded_files.clear()
        # Emit a signal or directly clear UI elements related to the files

    def get_loaded_voice_files(self):
        """Return a dictionary of all loaded files."""
        return self.loaded_files