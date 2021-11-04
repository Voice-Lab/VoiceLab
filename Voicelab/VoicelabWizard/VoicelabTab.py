from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class VoicelabTab(QWidget):
    def __init__(self, data_controller, signals, tabs, *args, **kwargs):
        """
        Args:
            data_controller:
            signals:
            tabs:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self.data_controller = data_controller
        self.signals = signals
        self.tabs = tabs

    ###############################################################################################
    # start_process: start processing the data through the pipeline
    ###############################################################################################
    def start_process(self):
        """start_process -tells the data controller to start processing"""
        pipeline_results = self.data_controller.start_processing(
            self.data_controller.active_voices,
            self.data_controller.active_functions,
            self.data_controller.active_settings,

        )

        # todo figure out where pipeline_results ends up
        # notify all those listening that the processing has completed
        self.signals["on_processing_completed"].emit(
            self.data_controller.active_results
        )

    ###############################################################################################
    # on_completed: default callback function for when data processing is complete
    ###############################################################################################
    def on_completed(self, pipeline_results):
        """
        Args:
            pipeline_results:
        """
        print("test", pipeline_results)
