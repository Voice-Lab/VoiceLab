from sharedVoiceAttributes import VoiceAttributes, VoiceFile
from hashlib import sha256

class FileManager:
    def __init__(self):
        self.loaded_files = {}
        
    def load_file(self, file_path):
        if file_path in self.loaded_files:
            return False  # File already loaded
        else:
            voice_attributes = VoiceAttributes(file_path)
            praat_data = voice_attributes.load_sound_praat()
            sound_file_data = voice_attributes.get_unscaled_signal()
            file_data = praat_data | sound_file_data
            self.loaded_files[file_path] = file_data
            return True

    def unload_file(self, file_path):
        if file_path in self.loaded_files:
            del self.loaded_files[file_path]
            return True
        return False

    # Add other methods as needed, e.g., updating file data, listing files, etc.


    def list_files(self):
        """Return a list of all loaded file paths."""
        return list(self.loaded_files.keys())
