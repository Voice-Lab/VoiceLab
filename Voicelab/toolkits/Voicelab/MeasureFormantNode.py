import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
from sklearn.impute import SimpleImputer
import sys
import os

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


###################################################################################################
# MEASURE FORMANTS NODE
# WARIO pipeline node for measuring the formants of a voice
###################################################################################################
# PIPELINE ARGUMENTS
# 'voice' :
# 'time step':
# 'max number of formants':
# 'window length(s):
# 'pre emphasis from'
# 'pitch floor'
# 'pitch ceiling'
# 'method': Option tuple for the praat algorithm to use, 0 = selected value, 1 = available options
# 'maximum formant': Maximum formant. Default is to dynamically calculate during runtime
###################################################################################################
# RETURNS
###################################################################################################


class MeasureFormantNode(VoicelabNode):
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            # Shared Settings
            "time step": 0.0025,  # a zero value is equal to 25% of the window length
            "max number of formants": 5.5, # Must be divisible by 0.5
            "window length(s)": 0.025,
            "pre emphasis from": 50,
            # Formant Burg-Specific Settings
            "max_formant (To Formant Burg...)": ('Auto', ['Auto', '5500']),
            # Formant Path-Specific Settings
            "Center Formant (Formant Path)": ('Auto', ['Auto', '5500']),
            "Ceiling Step Size (Formant Path)": 0.05,
            'Number of Steps (Formant Path)': 4,
            'method': ('To Formant Burg...', ['To Formant Burg...', 'Formant Path'],),
        }

        # check that max number of formants is divisible by 0.5
        if self.args['max number of formants'] % 0.5 != 0:
            # If it's not, round that to the nearest integer
            self.args['max number of formants'] = round(self.args['max number of formants'])

        self.state = {
            "f1 means": [],
            "f2 means": [],
            "f3 means": [],
            "f4 means": [],
            "f1 medians": [],
            "f2 medians": [],
            "f3 medians": [],
            "f4 medians": [],
        }

    def process(self):
        """:Returns the means and medians of the 1st 4 formants, and the Praat formant object for use in VTL
             estimates and plots.
            :param None
            :type: None
            ...
            :return: The max formant value
            :rtype: int
        """
        method = self.args['method'][0]
        try:
            # Load the sound
            sound = self.args["voice"]
<<<<<<< HEAD
            # Burg Method
            if method == 'To Formant Burg...':
                # Set Maximum Formant Value Automatically
                if self.args['max_formant (To Formant Burg...)'] == 'Auto':
                    try:
                        self.args['max_formant (To Formant Burg...)'] = self.formant_max(sound)
                    except:
                        # Otherwise default to 5500 Hz as max_formant value, Praat's default
                        self.args['max_formant (To Formant Burg...)'] == 5500
                # Set any user defined max formant values
                else:
                    try:
                        self.args['max_formant (To Formant Burg...)'] == int(self.args['max_formant (To Formant Burg...)'])
                    except:
                        # Otherwise default to 5500 Hz as max_formant value, Praat's default
                        self.args['max_formant (To Formant Burg...)'] = 5500

                # Create a Praat Formant Object
                formant_object = sound.to_formant_burg(
                    self.args["time step"],
                    self.args["max number of formants"],
                    self.args["max_formant (To Formant Burg...)"],
                    self.args["window length(s)"],
                    self.args["pre emphasis from"],
            )
=======
            # measure_PCA = self.args['Measure PCA']

            # Generate max_formant parameter
            self.args["max_formant"] = self.formant_max(sound)
            formant_path_object = call(sound, "To FormantPath (burg)", 0.005, 5, self.args["max_formant"], 0.025, 50.0, 0.025, 5)
            formant_object = call(formant_path_object, "Extract Formant")

            #formant_object = sound.to_formant_burg(
            #    self.args["time step"],
            #    self.args["max number of formants"],
            #    self.args["max_formant"],
            #    self.args["window length(s)"],
            #    self.args["pre emphasis from"],
            #)
>>>>>>> 92cbef5835595201bc2cf28062c8ee7f88bf6b1f

            # Formant Path Method
            elif self.args['method'] == 'Formant Path':
                try:  # Try formant path first
                    # Find centre max formant
                    if self.args['Center Formant (Formant Path)'] == 'Auto':
                        try:
                            self.args['Center Formant (Formant Path)'] = self.formant_max(sound)
                        except:
                            # Otherwise default to 5500 Hz as max_formant value, Praat's default
                            self.args['Center Formant (Formant Path)'] == 5500
                    # Set any user defined max formant values
                    else:
                        try:
                            self.args['Center Formant (Formant Path)'] == int(
                                self.args['Center Formant (Formant Path)'])
                        except:
                            # Otherwise default to 5500 Hz as max_formant value, Praat's default
                            self.args['Center Formant (Formant Path)'] = 5500

                    # Create A Praat Formant Path Object
                    formant_path_object = call(sound,
                                               "To FormantPath (burg)",
                                               self.args["time step"],
                                               self.args["max number of formants"],
                                               self.args["Center Formant (Formant Path)"],
                                               self.args["window length(s)"],
                                               self.args["pre emphasis from"],
                                               self.args["Ceiling Step Size (Formant Path)"],
                                               self.args['Number of Steps (Formant Path)'])
                    # Extract the Praat Formant Object from the Formant Path Object
                    formant_object = call(formant_path_object, "Extract Formant")
                    # Reset the method value in case previous voice failed at formant path and instead,
                    ## 'To Formant Burg...' was used
                    self.args["method"] = 'Formant Path'

                except :
                    # If formant path fails, get formant object formant_burg with max_formant from self.args
                    formant_object = sound.to_formant_burg(
                        self.args["time step"],
                        self.args["max number of formants"],
                        self.args["max_formant (To Formant Burg...)"],
                        self.args["window length(s)"],
                        self.args["pre emphasis from"],
                    )
                # Set the method to To formant burg to ensure we record the method change in the output data file.
                self.args["method"] = 'To formant burg...'

            # The following code is to vectorize gathering the formants in Numpy to prevent nested loops
            # Set up lists to apply the functions across, the list needs to be 8 items long
            # 4 Formants, mean and median ('Get quantile') = 8 items
            # 8 Formant objects
            objects = [formant_object]*8
            # 8 formant numbers
            formant_number = [1, 2, 3, 4]*2
            # 8 measures of central tendency
            command = ['Get mean']*4 + ['Get quantile']*4
            # This creates a vectorized function from our get_valus_function function
            get_values = np.frompyfunc(get_values_function, 3, 1)
            # This runs the vectorized function and returns a list of formant means and medias
            formant_means_and_medians = get_values(objects, formant_number, command)
            # This expands the list into the proper variable names to report the results
            f1_mean, f2_mean, f3_mean, f4_mean, f1_median, f2_median, f3_median, f4_median = formant_means_and_medians
            # This reports the results
            results = {
                "F1 Mean": f1_mean,
                "F2 Mean": f2_mean,
                "F3 Mean": f3_mean,
                "F4 Mean": f4_mean,
                "F1 Median": f1_median,
                "F2 Median": f2_median,
                "F3 Median": f3_median,
                "F4 Median": f4_median,
                "Formants": formant_object,
            }

        except:
            # If something went wrong beyond what's already been tested for, report nan values and move on
            results = {
                "F1 Mean":   np.nan,
                "F2 Mean":   np.nan,
                "F3 Mean":   np.nan,
                "F4 Mean":   np.nan,
                "F1 Median": np.nan,
                "F2 Median": np.nan,
                "F3 Median": np.nan,
                "F4 Median": np.nan,
                "Formants": "Formant Analysis Failed",
            }
        return results

    def end(self, results):

        """
        Args:
            results:
        """
        return results

    def formant_max(self, voice):
        """:Returns the max formant value based on the voice pitch for the `To Formant Burg...` function.
            :param voice: Parselmouth-Praat Sound object
            :type object:
            ...
            :return: The max formant value
            :rtype: int
        """
        try:
            pitch_floor, pitch_ceiling = self.pitch_bounds(voice)
            pitch = call(
                voice, "To Pitch", 0.0, pitch_floor, pitch_ceiling
            )  # check pitch to set formant settings
            mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")
            if 140 <= mean_f0 <= 300:
                max_formant = 5500

            elif mean_f0 < 140:
                max_formant = 5000

            else:
                max_formant = 8000
            return max_formant
        except:
            return 5500

def get_values_function(object, fn, command):
    if command == 'Get mean':
        return call(object, command, fn, 0, 0, "hertz")
    elif command == 'Get quantile':
        return call(object, command, fn, 0, 0, "hertz", 0.5)

