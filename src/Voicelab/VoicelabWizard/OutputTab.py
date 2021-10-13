from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import seaborn as sns

import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import parselmouth
from parselmouth.praat import call

from Voicelab.default_settings import display_whitelist
from Voicelab.VoicelabWizard.VoicelabTab import VoicelabTab


###################################################################################################
# OutputTab(VoicelabTab) : presentation widget for displaying and the results of our pipeline process
###################################################################################################


class OutputTab(VoicelabTab):
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

        self.test = {}
        self.results_tabs = {}
        self.results_tables = {}
        self.selected_tab = 0
        container_layout = QVBoxLayout(self)
        self.setLayout(container_layout)

        horizontal_splitter = QSplitter(Qt.Horizontal)
        vertical_splitter = QSplitter(Qt.Vertical)

        ## Set up files list section
        files_list_container = QFrame()
        files_list_container.setFrameShape(QFrame.StyledPanel)
        files_list_layout = QVBoxLayout()
        self.files_list = QListWidget()
        self.files_list.itemSelectionChanged.connect(self.on_selection_change)

        files_list_layout.addWidget(self.files_list)
        files_list_container.setLayout(files_list_layout)

        ## Set up spectrogram section
        spectrogram_display_container = QFrame()
        spectrogram_display_layout = QVBoxLayout()
        spectrogram_display_container.setFrameShape(QFrame.StyledPanel)
        spectrogram_display_container.setLayout(spectrogram_display_layout)
        self.spectrogram_display_stack = QStackedWidget()
        spectrogram_display_layout.addWidget(self.spectrogram_display_stack)
        self.spectrogram_map = {}
        self.btn_show_plt = QPushButton()
        self.btn_show_plt.clicked.connect(self.onshow_plot)
        self.btn_show_plt.setText("Expand Spectrogram")
        spectrogram_display_layout.addWidget(self.btn_show_plt)
        ## Set up results table section

        results_table_container = QFrame()
        results_table_layout = QVBoxLayout()
        results_table_container.setFrameShape(QFrame.StyledPanel)
        results_table_container.setLayout(results_table_layout)
        self.results_table_stack = QStackedWidget()
        results_table_layout.addWidget(self.results_table_stack)
        self.results_map = {}
        self.btn_save = QPushButton("Save Results")
        self.btn_save.clicked.connect(self.on_save)
        results_table_layout.addWidget(self.btn_save)

        ## Add the appropriate widgets to their respective layouts
        horizontal_splitter.addWidget(files_list_container)
        horizontal_splitter.addWidget(spectrogram_display_container)
        horizontal_splitter.setSizes([50, 50])

        vertical_splitter.addWidget(horizontal_splitter)
        vertical_splitter.addWidget(results_table_container)
        vertical_splitter.setSizes([60, 40])

        container_layout.addWidget(vertical_splitter)

        self.signals["on_processing_completed"].connect(self.on_processing_completed)

    ###############################################################################################
    # on_show_plot: callback for when the show plot button is pressed. opens the spectrogram in the
    # default matplotlib display.
    ###############################################################################################
    def onshow_plot(self):
        index = self.spectrogram_display_stack.currentIndex()
        if len(self.data_controller.figures) > 0:
            active_figure = self.data_controller.figures[index]

            # TODO: this is not a great way to handle this, the figure seems to be shared between the two...
            new_manager = plt.figure().canvas.manager
            new_manager.canvas.figure = active_figure
            new_manager.canvas.mpl_connect("close_event", self.refresh_figure_canvas)
            active_figure.set_canvas(new_manager.canvas)
            active_figure.show()

    ###############################################################################################
    # refresh_figure_canvas: redraws the currently displayed spectrogram canvas
    ###############################################################################################
    def refresh_figure_canvas(self, e):
        """
        Args:
            e:
        """
        self.spectrogram_display_stack.currentWidget().draw()

    ###############################################################################################
    # on_processing_completed: callback for when processing is completed. Triggers and update of
    # our results presentation
    ###############################################################################################
    def on_processing_completed(self, results):
        """
        Args:
            results:
        """
        self.update_results(results)

    ###############################################################################################
    # on_selection_change: callback for when an item in the list of filename is clicked
    ###############################################################################################
    def on_selection_change(self):
        if len(self.files_list.selectedItems()) > 0:
            selected_file_name = self.files_list.selectedItems()[0].text()
            # self.results_table_stack.setCurrentWidget(self.results_map[selected_file_name])
            index = self.results_table_stack.indexOf(
                self.results_map[selected_file_name]
            )
            self.results_table_stack.setCurrentIndex(index)
            self.results_table_stack.currentWidget().setCurrentIndex(self.selected_tab)
            if len(self.spectrogram_map) > 0:
                index = self.spectrogram_display_stack.indexOf(
                    self.spectrogram_map[selected_file_name]
                )
                self.spectrogram_display_stack.setCurrentIndex(index)

    def on_tab_select(self, selected_index):
        """
        Args:
            selected_index:
        """
        self.selected_tab = selected_index

    ###############################################################################################
    # update_results: clears the currently loaded results out and creates and adds the appropriate
    # widgets for a new set of results
    ###############################################################################################
    def update_results(self, results):

        # each file has a stack of tables containing the results of each function
        """
        Args:
            results:
        """
        self.files_list.clear()
        self.results_map = {}

        # We don't want the system to display things like voice files and pitch files. If
        # when creating the tab, if this flag is false then it wont be created

        for file_path in results:

            # create an entry in the list of files
            list_item = QListWidgetItem(parent=self.files_list)
            list_item.setText(file_path)

            # created a tabbed table for displaying the result values
            results_tabbed = QTabWidget()
            self.results_map[file_path] = results_tabbed
            for i, fn_name in enumerate(results[file_path]):
                if fn_name != "Load Voice":
                    display_tab = False
                    if fn_name == "Create Spectrograms":
                        spectrogram_figure = results[file_path][fn_name]["figure"]
                        spectrogram_display = FigureCanvas(spectrogram_figure)
                        self.spectrogram_display_stack.addWidget(spectrogram_display)
                        self.spectrogram_map[file_path] = spectrogram_display
                    else:
                        # create a table for the stack of tables
                        results_table = QTableWidget()
                        results_table.setColumnCount(1)
                        results_table.setRowCount(len(results[file_path][fn_name]))
                        results_table.setHorizontalHeaderLabels([fn_name])
                        results_table.setVerticalHeaderLabels(
                            results[file_path][fn_name].keys()
                        )
                        results_table.setEditTriggers(QTableWidget.NoEditTriggers)
                        results_table.horizontalHeader().setSectionResizeMode(
                            QHeaderView.Stretch
                        )
                        rows_to_delete = []

                        for j, result_name in enumerate(results[file_path][fn_name]):
                            result_value = results[file_path][fn_name][result_name]
                            display_value = type(result_value) in display_whitelist
                            display_tab = display_tab or display_value

                            if display_value:
                                if isinstance(display_value, np.generic):
                                    display_value = result_value.item()
                                results_table.setItem(
                                    j, 0, QTableWidgetItem(str(result_value))
                                )
                            # we dont want to delete the row yet since it will screw up the loop
                            else:
                                rows_to_delete.append(j)
                        # loop through the collection of which rows to delete
                        for row in rows_to_delete:
                            results_table.removeRow(row)
                        # if there is even one value to display we create the tab
                        if display_tab:
                            results_tabbed.addTab(results_table, fn_name)
            results_tabbed.currentChanged.connect(self.on_tab_select)
            self.results_table_stack.addWidget(results_tabbed)

    ###############################################################################################
    # on_list_change: callback function for when an item in the list of files is clicked.
    ###############################################################################################
    def on_list_change(self):
        selected = self.file_list.selectedItems()

        if len(selected) > 0:
            file_name = selected[0].text()
            # self.results_widget.show_result(file_name)

    ###############################################################################################
    # on_save: callback function for when the save button is pressed. saves the results to the filesystem
    ###############################################################################################
    def on_save(self):
        active_results = self.data_controller.active_results
        active_functions = self.data_controller.active_functions
        last_used_settings = self.data_controller.last_used_settings

        options = QFileDialog.Options()
        temp_loaded = QFileDialog.getExistingDirectory(self)

        self.data_controller.save_results(
            active_results, active_functions, last_used_settings, temp_loaded
        )

