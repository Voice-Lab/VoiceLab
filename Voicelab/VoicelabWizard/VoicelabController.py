from Voicelab.VoicelabWizard.VoicelabDataModel import VoicelabDataModel
from Voicelab.pipeline.Pipeline import Pipeline
import Voicelab.toolkits.Voicelab as Voicelab

import copy
from Voicelab.VoicelabWizard.InputTab import InputTab
import parselmouth
from parselmouth.praat import call

from Voicelab.default_settings import visualize_list, function_requirements, display_whitelist
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

"""
# Voicelab Controller: coordinates the interaction between the presentation of the data and its storage
# The data controller does not need to know how the data gets in from the user, nor how the data
# is stored. This could in the future let us change the front end and backend more flexibly.
"""


class VoicelabController:
    """
    # init: setup the base state of a controller, including a data model
    """

    def __init__(self):

        self.data_model = VoicelabDataModel()
        self.active_settings_cache = {}
        self.active_functions_cache = {}
        self.last_used_settings = {}
        self.progress = 0
        # Lambdas are not allowed in multiprocessing.  I made a function below instead.
        #self.progress_callback = lambda node, start, current, end: print(
        #    node.node_id, start, current, end
        #)
        self.figures = []
        self.spectra = []
        self.displayable_results = {}

    """
    # load_figure: load a single figure into the list of figures. This lets us keep track of and
    # close the figures when they are not needed. This is important especially given matplotlib's statefulness
    """

    def progress_callback(self, node, start, current, end):
        print(
            node.node_id, start, current, end
        )

    def load_figure(self, figure):
        self.figures.append(figure)

    """
    # load_spectrum: load a single spectrum into the list of spectrums. This lets us keep track of and
    # close the spectrums when they are not needed. This is important especially given matplotlib's statefulness
    """

    def load_spectrum(self, spectrum):
        self.spectra.append(spectrum)

    """
    
    # reset_figures: clear all of the figures that we have saved and empty the figures variable
    """

    def reset_figures(self):
        for figure in self.figures:
            figure.clear()
            plt.close(figure)
        self.figures = []

    """
    # load voices: from a list of file paths, create voice objects and save them in the model
    """
    def load_voices(self, file_paths):
        for file_path in file_paths:
            #self.data_model.load_voice(parselmouth.Sound(file_path), file_path)
            sound = parselmouth.Sound(file_path)
            signal = sound.values
            sampling_rate = sound.sampling_frequency
            voice = (signal, sampling_rate)
            self.data_model.load_voice(file_path, signal, sampling_rate)
        return self.data_model.loaded_voices

    """
    # unload voices: from a list of file paths, remove the associated voice file from the model
    """

    def unload_voices(self, file_paths):
        for file_path in file_paths:
            self.data_model.unload_voice(file_path)
        return self.data_model.loaded_voices

    """
    # activate_voices: from a list of file paths, set the associated voice files for processing
    """

    def activate_voices(self, file_paths):
        self.data_model.activate_voices(file_paths)
        print(self.data_model.active_voices)
        return self.data_model.active_voices

    """
    # deactivate voices: from a list of file paths, remove the associated files from processing
    """

    def deactivate_voices(self, file_paths):
        for file_path in file_paths:
            self.data_model.deactivate_voice(file_path)
        return self.data_model.active_voices

    """
    # load function: load a single function into the data model
    """

    def load_function(self, fn_name, fn_node, default=False) -> object:
        self.data_model.load_function(fn_name, fn_node, default)
        return self.data_model.loaded_functions

    """
    # activate function: set a single function to run during processing
    # TODO: this behaviour could probably be handled only by the controller rather than by the model
    """

    def activate_function(self, fn_name):
        self.data_model.activate_function(fn_name)
        return self.data_model.active_functions

    """
    # deactivate function: set a single function to not run during processing
    # todo: this behaviour could probably be handled only by the controller rather than by the model
    """

    def deactivate_function(self, fn_name):
        self.data_model.deactivate_function(fn_name)
        return self.data_model.active_functions

    """
    # set setting: set a value for a given setting
    """

    def set_settings(self, fn, settings, values):
        for i, setting in enumerate(settings):
            self.data_model.set_setting(fn, settings[i], values[i])
        return self.data_model.active_settings

    """
    # activate setting: indicate that a setting is non-default
    # TODO: this behaviour could probably be handled only by the controller rather than by the model
    """

    def activate_settings(self, settings):
        for i, setting in enumerate(settings):
            self.data_model.activate_setting(setting)
        return self.data_model.active_settings

    """
    # reset setting: take a setting id and reset it to it's default value
    """

    def reset_setting(self, fn_name, setting_name):
        self.data_model.reset_setting(fn_name, setting_name)

    """
    # save_state: caches the setting values so that they can be retrieved later. Used currently for
    # toggling between default and non-default settings
    """

    def save_state(self):
        self.active_settings_cache = copy.copy(self.active_settings)
        self.active_functions_cache = copy.copy(self.active_functions)

    """
    # load state : swap whatever is currently loaded with what is cached.
    """

    def load_state(self):
        self.data_model.swap_active_settings(self.active_settings_cache)
        self.data_model.swap_active_functions(self.active_functions_cache)

    """
    # reset active settings : swap all active settings with the default values. convenience function
    # so that we don't have to loop through all of the settings each time we want to do this action
    """

    def reset_active_settings(self):
        self.data_model.swap_active_settings(self.default_settings)

    """
    # reset active functions : swap all active functions with the default functions. convenience
    # so that we don't have to loop through all of the settings each time we want to do this action
    """

    def reset_active_functions(self):
        self.data_model.swap_active_functions(self.default_functions)

    """
    # reset results : Empty the results in preperation for another run
    """

    def reset_results(self):
        self.data_model.reset_results()

    """
    # start processing: Start processing the loaded voice files using the set of active functions
    # and active settings.
    """

    def start_processing(self, active_voices, active_functions, active_settings):

        # we want to deep copy the active settings otherwise they may be unintentionally
        # modifed with values during processing
        # self.last_used_settings = copy.deepcopy(active_settings)

        # DRF - I guess we don't really need to do that after all since it's commented out

        # save the settings so we can put them in the excel file later
        self.last_used_settings = active_settings

        # reset the results in case this isn't our first run since the program opened
        self.reset_results()

        # Create an empty WARIO pipeline
        pipeline = Pipeline()

        # Create a node that will load all of the voices
        load_voices = Voicelab.LoadVoicesNode("Load Voice")

        # Set up the load node with the appropriate file locations
        load_voices.args["file_locations"] = active_voices
        # Add the node to the pipeline
        pipeline.add(load_voices)

        # We want to specially configure the visualize voice node because later on we will be attaching things to it later
        if "Create Spectrograms" in active_functions:
            # Create a node that will draw the default spectrogram for the loaded voices, we always want to plot the spectrogram
            visualize_voices = Voicelab.VisualizeVoiceNode("Create Spectrograms")

            # if there are settings the user has configured, we want to attach them to the node

            visualize_voices.args = active_settings["Create Spectrograms"]

            # visualize_voices.args[value] = self.model['settings']['Visualize Voice']['value'][value]

            # Connect the loaded voice to the visualize node so it has access to it
            pipeline.connect((load_voices, "voice"), (visualize_voices, "voice"))

            # Add the node to the pipeline
            pipeline.add(visualize_voices)

        # todo Fix this
        if "Visualize Spectrum" in active_functions:
            # Create a node that will draw the default spectrogram for the loaded voices, we always want to plot the spectrogram
            visualize_spectrum = Voicelab.VisualizeSpectrumNode("Visualize Spectrum")

            # if there are settings the user has configured, we want to attach them to the node

            visualize_spectrum.args = active_settings["Visualize Spectrum"]

            # Connect the loaded voice to the visualize node so it has access to it
            pipeline.connect((load_voices, "voice"), (visualize_spectrum, "voice"))

            # Add the node to the pipeline
            pipeline.add(visualize_spectrum)

        # For each checked operation we create the appropriate node, assign its associated
        # parameters, and add it to the pipeline connecting it to the load voice node and
        # visualize node. those two functions are always performed

        for fn in active_functions:
            # Visualize is handled outside of this
            # if fn != "Create Spectrograms":
            active_functions[fn].args = active_settings[fn]
            pipeline.add(active_functions[fn])
            pipeline.connect(
                (load_voices, "voice"), (active_functions[fn], "voice")
            )
            pipeline.connect(
                (load_voices, "file_path"), (active_functions[fn], "file_path")
            )
            # if "Create Spectrograms" in active_functions and fn in visualize_list:
            #    pipeline.connect(
            #        (active_functions[fn], visualize_list[fn]),
            #        (visualize_voices, visualize_list[fn]),
            #    )

        # Some nodes may require specific values from upstream nodes (as specified in the default settings file)
        # Resolve these dependancies and create the relevant connections
        for fn_name in function_requirements:
            if fn_name in active_functions:
                child_node = active_functions[fn_name]
                # function requirements are a defined as a tuple of parent_name followed by the name of the shared argument
                for parent_name, argument in function_requirements[fn_name]:
                    parent_node = active_functions[parent_name]
                    pipeline.connect((parent_node, argument), (child_node, argument))

        pipeline.listen(self.progress_callback)
        pipeline_results = pipeline.start()

        finished_window = QMessageBox()
        finished_window.setWindowTitle("Finished")
        finished_window.setText("Finished processing.\nCheck your data, then save.")
        finished_window.setIcon(QMessageBox.Information)
        finished_window.exec_()


        # Collect the results of the pipeline running
        for i, result_file in enumerate(pipeline_results):
            for result_fn in pipeline_results[i]:
                if result_fn.node_id == "Create Spectrograms":
                    # "figure" is the maptlotlib figure returned from VisualizeVoiceNode.py
                    #  it is a dictionary key, the dictionary value is the actual figure `fig`  from fig = plt.figure()
                    figure: object = pipeline_results[i][result_fn]["figure"]
                    self.load_figure(figure)
                elif result_fn.node_id == "Visualize Spectrum":
                    # "spectrum" is the matplotlib figure from VisualizeSpectrum.py
                    #  it is a dictionary key, the dictionary value is the actual figure `fig`  from fig = plt.figure()
                    spectrum: object = pipeline_results[i][result_fn]["spectrum"]
                    self.load_spectrum(spectrum)
                self.data_model.load_result(
                    active_voices[i], result_fn.node_id, pipeline_results[i][result_fn]
                )
                for arg_setting in result_fn.args:
                    self.data_model.set_computed_setting(result_fn.node_id, arg_setting, result_fn.args[arg_setting])
        return self.data_model.active_results

    """
    # save_results: save the results of processing to the files system
    """

    def save_results(
            self, active_results, active_functions, last_used_settings, save_location
    ):

        append_file_to_results = False
        append_file_to_settings = False

        if save_location != "":

            # Prepare the data for saving as an excel workbook
            results_sheets = {
                fn_name: {"Input File": []} for fn_name in active_functions
            }
            settings_sheets = {
                fn_name: {"Input File": []} for fn_name in active_functions
            }

            # Create a new sheet for each function, and fill with the results for each file
            for i, file_path in enumerate(active_results):

                file_name = file_path.split("/")[-1].split(".wav")[0]

                for fn_name in active_results[file_path]:

                    if fn_name != "Load Voice":
                        # We want to exclude saving the unmodified voice
                        for result_name in active_results[file_path][fn_name]:

                            result_value = active_results[file_path][fn_name][
                                result_name
                            ]
                            header_value = ""
                            output_value = ""

                            if isinstance(result_value, np.generic):
                                result_value = result_value.item()

                            # if the result is a modified sound file, we want to save that as a wav file
                            if isinstance(result_value, parselmouth.Sound):
                                voice_name = result_value.name
                                modified_path = (
                                        save_location + "/" + voice_name + ".wav"
                                )
                                self.save_voice(result_value, modified_path)
                                header_value = result_name + " Output File"
                                output_value = voice_name

                            # if the result is some sort of matlab figure, we want to save it as a png
                            # assign filenames based on results dictionary key
                            elif isinstance(result_value, Figure):
                                spectrogram_path = ''.join([save_location, "/", file_name, "_spectrogram.png"])
                                spectrum_path = ''.join([save_location, "/", file_name, "_spectrum.png"])
                                if result_name == "figure":
                                    self.save_spectrogram(result_value, spectrogram_path)
                                    output_value = spectrogram_path
                                elif result_name == "spectrum":
                                    self.save_spectrum(result_value, spectrum_path)
                                    output_value = spectrogram_path
                                header_value = "Output File"

                            # if the result is any other type that we know how to save, save it as part of the work book
                            elif type(result_value) in display_whitelist:
                                header_value = result_name
                                output_value = result_value

                            # create a column in the sheet for this type of result if it hasnt already been created
                            if header_value not in results_sheets[fn_name]:
                                results_sheets[fn_name][header_value] = []

                            # append the result to this column
                            results_sheets[fn_name][header_value].append(
                                str(output_value)
                            )
                            append_file_to_results = True

                        # fill the settings sheets with values
                        for j, param_name in enumerate(last_used_settings[fn_name]):
                            if param_name not in settings_sheets[fn_name]:
                                settings_sheets[fn_name][param_name] = []

                            # if there are options, save the first one
                            if isinstance(
                                    last_used_settings[fn_name][param_name], tuple
                            ):
                                param_value = last_used_settings[fn_name][param_name][0]

                            else:
                                param_value = last_used_settings[fn_name][param_name]

                            settings_sheets[fn_name][param_name].append(
                                str(param_value)
                            )

                        # Check to see if we have already written the file name to the sheet
                        results_sheets[fn_name]["Input File"].insert(0, file_name)
                        settings_sheets[fn_name]["Input File"].insert(0, file_name)

            results_writer = ExcelWriter(save_location + "/voicelab_results.xlsx")
            settings_writer = ExcelWriter(save_location + "/voicelab_settings.xlsx")

            summary_data = {
                "files loaded": [file_name for file_name in self.active_voices],
                "functions loaded": [fn_name for fn_name in self.active_functions],
            }
            # these need to be the same size, so we pad the one that needs it with blanks spaces
            difference = len(summary_data["files loaded"]) - len(
                summary_data["functions loaded"]
            )
            if difference > 0:
                summary_data["functions loaded"] = summary_data["functions loaded"] + [
                    "" for i in range(abs(difference))
                ]
            else:
                summary_data["files loaded"] = summary_data["files loaded"] + [
                    "" for i in range(abs(difference))
                ]

            # results_summary_sheet = pd.DataFrame(summary_data)

            # results_summary_sheet.to_excel(results_writer, "Summary", index=False)
            summary_result_sheets = []
            test = copy.deepcopy(list(results_sheets.keys()))
            for sheet_name in results_sheets:
                sheet_data = results_sheets[sheet_name]
                if len(sheet_name) > 31:  # Excel column label lengths can't be longer than 31 characters
                    sheet_name = sheet_name[:31]

                # Delete Praat pitch object from results dictionary
                # We need it for other algos, but we dont' want it in the excel file
                if 'Pitch' in sheet_data.keys():
                    del sheet_data['Pitch']

                # Same as the above with any empty sheets
                if '' in sheet_data.keys():
                    del sheet_data['']

                # ...and again for  Formant Objects
                if 'Formants' in sheet_data.keys():
                    del sheet_data['Formants']

                sheet = pd.DataFrame(sheet_data)
                summary_result_sheets.append(sheet)
                sheet.to_excel(results_writer, sheet_name, index=False)
                print(f"Data from {sheet_name} saved.")


            results_summary_sheet = pd.concat(summary_result_sheets, axis=1)
            results_summary_sheet.to_excel(results_writer, "Summary", index=False)

            for sheet_name in settings_sheets:
                if len(settings_sheets[sheet_name]) > 0:
                    sheet_data = settings_sheets[sheet_name]
                    if len(sheet_name) > 31:
                        sheet_name = sheet_name[:31]
                    sheet_df = pd.DataFrame(sheet_data)
                    sheet_df.to_excel(settings_writer, sheet_name, index=False)

            try:
                results_writer.save()
                print('Results file saved successfully.')
                message_text = 'Results saved successfully.'
            except:
                print("Error saving results.")
                message_text = 'Error saving results.'

            saved_window = QMessageBox()
            saved_window.setWindowTitle("Save Results")
            saved_window.setText(message_text)
            saved_window.setIcon(QMessageBox.Information)
            saved_window.exec_()

            try:
                settings_writer.save()
            except:
                print("error saving settings")


    def save_voice(self, voice: object, file_name: str) -> object:
        """saves a single parselmouth Sound object to the file system as a .wav file
        :param: voice: A parselmouth Sound object:
        :return: file_name: The name of the file to save
        :rtype: object
        """
        voice.save(file_name, "WAV")
        return file_name

    """
    # save_spectrogsave_spectrumram: save a figure generated by matplotlib to the file system as a .png file
    # TODO: have the dpi and quality settings be configurable
    """

    def save_spectrogram(self, figure, file_name):
        figure.set_size_inches(10, 5)
        figure.savefig(file_name, dpi=250, quality=95)
        plt.close(figure)
        return file_name

    def save_spectrum(self, figure, file_name):
        figure.set_size_inches(10, 5)
        figure.savefig(file_name, dpi=250, quality=95)
        plt.close(figure)
        return file_name

    """
    # Accessor/getter properties for interfacing transparently with the data model
    """

    @property
    def loaded_voices(self):
        return self.data_model.loaded_voices

    @property
    def loaded_functions(self):
        return self.data_model.loaded_functions

    @property
    def loaded_settings(self):
        return self.data_model.loaded_settings

    @property
    def active_voices(self):
        return self.data_model.active_voices

    @property
    def active_functions(self):
        return self.data_model.active_functions

    @property
    def active_settings(self):
        return self.data_model.active_settings

    @property
    def active_results(self):
        return self.data_model.active_results

    @property
    def default_functions(self):
        return self.data_model.default_functions

    @property
    def default_settings(self):
        return self.data_model.default_settings
