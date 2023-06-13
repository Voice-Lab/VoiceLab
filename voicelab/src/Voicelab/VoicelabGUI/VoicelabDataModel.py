import copy

###################################################################################################
# VoicelabDataModel: Abstracts the data management for the system from control and view logic.
# currently this data is stored only temporarily in a set of dictionaries (making it almost the same
# as the data controller), but this can be changed to more persistent storage without needing to
# change the front end.
# TODO: This can be simplified down to basic CRUD (create, remove, update, delete) operations with
# everything else being handled by the controller
###################################################################################################
class VoicelabDataModel:
    def __init__(self):

        # a set of default values for each of the configurable settings
        self.default_settings = {}
        # a set of default functions that are automatically checked when you start the program
        self.default_functions = {}
        # the set of functions that are available
        self.loaded_functions = {}
        # the set of voices that are available
        self.loaded_voices = {}
        # the set of voices that will be worked on
        self.active_voices = {}
        # the set of functions that will be run on the active voices
        self.active_functions = {}
        # the settings as they will be passed to each of the functions
        self.active_settings = {}
        # the settings as they have been changed within the functions
        self.active_computed_settings = {}
        # the set of results for the last run set of functions
        self.active_results = {}
        #
        self.active_results_output = {}
        self.active_settings_output = {}

    ###############################################################################################
    # load_function:
    # + fn_name: name of the function we are loading
    # + fn_node: WARIO compatable node containing the functionality
    # + default: boolean value whether this is a default function or not
    ###############################################################################################
    def load_function(self, fn_name, fn_node, default=False):
        """
        Args:
            fn_name:
            fn_node:
            default:
        """
        self.loaded_functions[fn_name] = fn_node
        self.default_settings[fn_name] = {}
        self.active_settings[fn_name] = {}

        for setting in fn_node.args:
            self.default_settings[fn_name][setting] = fn_node.args[setting]
            self.active_settings[fn_name][setting] = fn_node.args[setting]

        if default:
            self.default_functions[fn_name] = self.loaded_functions[fn_name]
            self.active_functions[fn_name] = self.loaded_functions[fn_name]

        return self.loaded_functions

    ###############################################################################################
    # activate_function: activated functions will run when processing
    # + fn_name: Name of the function to activate
    ###############################################################################################
    def activate_function(self, fn_name):
        """
        Args:
            fn_name:
        """
        self.active_functions[fn_name] = self.loaded_functions[fn_name]

    ###############################################################################################
    # deactivate_function: deactivated functions will not run when processing
    # + fn_name: Name of the function to deactivate
    ###############################################################################################
    def deactivate_function(self, fn_name):
        """
        Args:
            fn_name:
        """
        if fn_name in self.active_functions:
            del self.active_functions[fn_name]

    ###############################################################################################
    # load_voice: makes the voice available to the system
    # + voice: parselmouth Sound object
    # + file_path: path to the file in the filesystem. Used for indexing
    ###############################################################################################
    #def load_voice(self, voice, file_path):
    def load_voice(self, file_path, signal, sampling_rate):
        """
        Args:
            voice:
            file_path:
        """
        voice = (signal, sampling_rate)
        self.loaded_voices[file_path] = voice
        return self.loaded_voices

    ###############################################################################################
    # unload_voice: removes a voice from the system
    # + file_path: path to the file in the filesystem. Used for indexing
    ###############################################################################################
    def unload_voice(self, file_path):
        """
        Args:
            file_path:
        """
        if file_path in self.loaded_voices:
            del self.loaded_voices[file_path]
        return self.loaded_voices

    ###############################################################################################
    # activate_voices: activated voices will be processed using active functions
    # + file_path: path to the file in the filesystem. Used for indexing
    ###############################################################################################
    def activate_voices(self, file_paths):
        """
        Args:
            file_paths:
        """
        self.active_voices = file_paths
        return self.active_voices

    ###############################################################################################
    # deactivate_voice: inactive voices will not be processed
    # + file_path: path to the file in the filesystem. Used for indexing
    ###############################################################################################
    def deactivate_voice(self, file_path):
        """
        Args:
            file_path:
        """
        if file_path in self.active_voices:
            del self.active_voices[voice]
        return self.active_voices

    ###############################################################################################
    # set_setting: configure a setting to a value
    # + fn_name: name of the function this setting is a part of
    # setting_name: name of the setting to configure
    # value: name of the value to set the setting to
    ###############################################################################################
    def set_setting(self, fn_name, setting_name, value):
        # if the setting hasnt been loaded yet, then we store this as a default value
        """
        Args:
            fn_name:
            setting_name:
            value:
        """
        self.active_settings[fn_name][setting_name] = value
        return self.active_settings

    def set_computed_setting(self, fn_name, setting_name, value):
        """
        Args:
            fn_name:
            setting_name:
            value:
        """
        if fn_name not in self.active_computed_settings:
            self.active_computed_settings[fn_name] = {}
        self.active_computed_settings[fn_name][setting_name] = value

    ###############################################################################################
    # swap_active_settings: used to avoid iterating over all settings when changing many
    # + settings: replaces all settings with those contained in this dictionary
    ###############################################################################################
    def swap_active_settings(self, settings):
        """
        Args:
            settings:
        """
        self.active_settings = settings
        return self.active_settings

    ###############################################################################################
    # swap_active_functions: used to avoid iterating over all functions when changing many
    # + functions: replaces all functions with those contained in this dictionary
    ###############################################################################################
    def swap_active_functions(self, functions):
        """
        Args:
            functions:
        """
        self.active_functions = functions
        return self.active_functions

    ###############################################################################################
    # reset_setting: resets the specified setting to its default value
    # + fn_name: name of the function this setting is a part of
    # + setting_name: name of the setting to configure
    ###############################################################################################
    def reset_setting(self, fn_name, setting_name):
        """
        Args:
            fn_name:
            setting_name:
        """
        self.active_settings[fn_name][setting_name] = self.default_settings[fn_name][
            setting_name
        ]
        return self.active_settings[fn_name][setting_name]

    ###############################################################################################
    # reset_setting: remove the specified setting
    # + fn_name: name of the function this setting is a part of
    # + setting_name: name of the setting to configure
    ###############################################################################################
    def remove_setting(self, fn_name, setting):
        """
        Args:
            fn_name:
            setting:
        """
        del self.default_settings[fn_name][setting]
        del self.active_settings[fn_name][setting]
        return self.default_settings

    ###############################################################################################
    # load_result: store the results of running the processing pipeline
    # + file_path: path to the voice file that was processed
    # + fn: name of  the function that was processe
    # + results: values for the results from this function
    # TODO: + settings: values for the settings used with this function
    ###############################################################################################
    def load_result(self, file_path, fn, results):
        """
        Args:
            file_path:
            fn:
            results:
        """
        if file_path not in self.active_results:
            self.active_results[file_path] = {}

        self.active_results[file_path][fn] = results
        return self.active_results

    ###############################################################################################
    # reset_results: empty the results and makes it ready for the next run
    ###############################################################################################
    def reset_results(self):
        self.active_results = {}

    ###############################################################################################
    # Resets all functions and settings to their default values
    ###############################################################################################
    def reset_all_defaults(self):
        self.active_functions = copy.copy(self.default_functions)
        self.active_settings = copy.copy(self.default_settings)
