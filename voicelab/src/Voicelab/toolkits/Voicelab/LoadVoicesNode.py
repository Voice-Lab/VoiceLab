import parselmouth
from ...pipeline.Node import Node
from parselmouth.praat import call
from ...pipeline.FileWidget import FileWidget


"""
LOAD VOICES NODE
WARIO pipeline node for loading voice files.
###################################################################################################
ARGUMENTS
'file_locations'   : list of filesystem locations for where to find the voice files
###################################################################################################
RETURNS
'voice' [batch]   : return a parselmouth voice object for each file loaded
###################################################################################################
"""


class LoadVoicesNode(Node):
    def __init__(self, name):
        """
        Args:
            name:
        """
        super().__init__(name)
        self.done = False


    def process(self):
        """
        process: Retrieve the next file location and return it
        """
        #item, file_path = self.get_next(self.state["voices"])
        #return {"voice": item, "file_path": file_path}
        (signal, sampling_rate), file_path = self.get_next(self.state["voices"])
        return {"voice": (signal, sampling_rate), "file_path": file_path}


    def start(self):
        """
        start: WARIO hook, run before any data is processed to load the data in
        """
        self.state["voices"] = []

        # If a collection of file locations are present use those, otherwise prompt for them
        if len(self.args["file_locations"]) == 0:
            ex = FileWidget()
            self.state["files"] = ex.openFileNamesDialog()
        else:
            self.state["files"] = self.args["file_locations"]

        for file_path in self.state["files"]:
            #  This is where we load files
            #  Select Load None if we want to load nothing
            #  Append the parselmouth.Sound object if you don't need multiprocessing
            #  We are going to try passing the data and sampling rate through nodes instead of sound objects.
            sound = parselmouth.Sound(file_path)
            signal = sound.values
            sampling_rate = sound.sampling_frequency
            voice = (signal, sampling_rate)
            self.state["voices"].append((voice, file_path))
            #self.state["voices"].append((None, file_path))

        # return how many files have been loaded
        return len(self.state["voices"])

    """
    get_next: Retrieve the next file location by simply popping off the stack
    """
    def get_next(self, collection):
        """
        Args:
            collection:
        """
        item = collection.pop()
        if len(collection) <= 0:
            self.done = True
        return item
