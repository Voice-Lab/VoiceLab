from PyQt6.QtCore import QThread, pyqtSignal, QObject

class LoaderSignals(QObject):
    finished = pyqtSignal(list)  # Emitted when all files are loaded
    progress = pyqtSignal(int, str)  # Emitted to update progress and status messages


class VoiceLoaderThread(QThread):
    progress = pyqtSignal(int, str)  # Emitted for progress updates
    finished = pyqtSignal(list)  # Emitted when all files are loaded

    def __init__(self, file_paths, file_manager):
        super().__init__()
        self.file_paths = file_paths
        self.file_manager = file_manager

    def run(self):
        results = []
        total_files = len(self.file_paths)
        for index, path in enumerate(self.file_paths, 1):
            progress = int((index / total_files) * 100)
            self.progress.emit(progress, f"Loading: {path}")
            data = self.file_manager.load_file(path)
            results.append(data)
            self.progress.emit(progress + int(1 / total_files * 100), "Processing complete.")

        self.progress.emit(100, "All files loaded.")
        self.finished.emit(results)
        #return results