from __future__ import annotations

import numpy as np

from typing import Union
import parselmouth
from parselmouth.praat import call
from Voicelab.pipeline.Node import Node

from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class MeasureFormantNode(VoicelabNode):
    """Measure formant frequencies using Praat's Formant Path Function.

    Arguments:
    -----------
        self.args : dict
            Arguments for the node
            self.args['time step'] : Union[float, int], default=0.0025
                Time step in seconds
            self.args['max number of formants'] : Union[float, int], default=5.5
                Maximum number of formants is used to set the number of poles in the LPC filter.  The number of poles is 2x this number.
            self.args['window length'] : bool, default=True
                Normalize amplitude to 70 dB RMS
            self.args['pre-emphasis']: Union[float, int], default=50
                Pre-emphasis filter coefficient: the frequency F above which the spectral slope will increase by 6 dB/octave.
            self.args['max_formant (To Formant Burg...)']: Union[float, int], default=5500
                Maximum formant frequency in Hz. This is the nyquist frequency for resampling prior to LPC analysis. Sounds will be resampled to 2x this number. This is for the Formant Burg analysis, a fallback in-case Formant Path fails or is not selected.
            self.args["Center Formant (Formant Path)"]: Union[float, int], default=5500
                This is the centre frequency for the Formant Path analysis. This is the nyquist frequency for resampling prior to LPC analysis. Sounds will be resampled to 2x this number. Formant Path will measure formants using this value and several others, depending on the number of steps and ceiling step size.
            self.args["Ceiling Step Size (Formant Path)"]: Union[float, int], default=0.05
                This is the size of steps in the Formant Path analysis. This is the nyquist frequency for resampling prior to LPC analysis. Sounds will be resampled to 2x this number. Praat will measure formants at a number of steps up and down of this size.
            self.args["Number of Steps (Formant Path)"]: Union[float, int], default=4
                This is the number of steps in the Formant Path analysis. This is the nyquist frequency for resampling prior to LPC analysis. This is the number of formant analyses to perform.
            self.args['method']: str, default='Formant Path'
                Method to use for formant measurement. Options are: Formant Path or Formant Burg.
    """
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
            "max number of formants": 5.5,  # Must be divisible by 0.5
            "window length(s)": 0.025,
            "pre emphasis from": 50,
            # Formant Burg-Specific Settings
            "max_formant (To Formant Burg...)": 0.0,
            # Formant Path-Specific Settings
            "Center Formant (Formant Path)": 0.0,
            "Ceiling Step Size (Formant Path)": 0.05,
            'Number of Steps (Formant Path)': 4,
            'method': ('Formant Path', ['Formant Path', 'To Formant Burg...']),
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
        """Returns the means and medians of the 1st 4 formants, and the Praat formant object for use in VTL estimates and plots.

            :return: The max formant value
            :rtype: int
        """
        # Get the parameters for the analysis
        method = self.args['method'][0]
        self.method = method
        file_path = self.args["file_path"]
        time_step = self.args["time step"]
        max_number_of_formants = self.args["max number of formants"]
        max_formant = self.args["max_formant (To Formant Burg...)"]
        window_length = self.args["window length(s)"]
        pre_emphasis = self.args["pre emphasis from"]
        center_formant = self.args["Center Formant (Formant Path)"]
        ceiling_step_size = self.args["Ceiling Step Size (Formant Path)"]
        number_of_steps = self.args["Number of Steps (Formant Path)"]

        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)

        try:
            # Burg Method
            if max_formant == 0:
                max_formant = self.max_formant(file_path=file_path)
            if method == 'To Formant Burg...' or method == 'T':
                formant_object = self.measure_formants_burg(
                    file_path,
                    time_step,
                    max_number_of_formants,
                    max_formant,
                    window_length,
                    pre_emphasis
                )

            # Formant Path Method
            elif method == 'Formant Path' or method == 'F':
                # Find centre max formant
                if center_formant == 0:
                    f_center = self.max_formant(sound)
                # Set any user defined max formant values
                else:
                    f_center = center_formant

                formant_path_object = call(
                    sound,
                    "To FormantPath (burg)",
                    time_step,
                    max_number_of_formants,
                    f_center,
                    window_length,
                    pre_emphasis,
                    ceiling_step_size,
                    number_of_steps
                )
                formant_object = call(formant_path_object, "Extract Formant")
                self.args["method"]: str = 'Formant Path'


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

        except Exception as e:
            raise
            results = {
                "F1 Mean": str(e),
                "F2 Mean": str(e),
                "F3 Mean": str(e),
                "F4 Mean": str(e),
                "F1 Median": str(e),
                "F2 Median": str(e),
                "F3 Median": str(e),
                "F4 Median": str(e),
                "Formants": str(e),
            }
        return results

    def end(self, results):

        """This passes the data on to State for post-processing of VTL estimates

        :return: results: a dictionary of the results containing the output from process()
        :rtype: dict
        """
        return results

    def measure_formants_burg(self, filename, time_step, max_number_of_formants, max_formant, window_length, pre_emphasis):
        """This function measures the formants using the formant_burg method

        :param filename: the name of the file to measure
        :type: filename: str
        :param time_step: the time step to use for the analysis
        :type: time_step: float
        :param max_number_of_formants: the maximum number of formants to measure
        :type: max_number_of_formants: int
        :param max_formant: the maximum formant to measure
        :type: max_formant: float
        :param window_length: the window length to use for the analysis
        :type: window_length: float
        :param pre_emphasis: the pre-emphasis to use for the analysis
        :type: pre_emphasis: float
        :return formant_object: a praat formant object
        :rtype: parselmouth.Formant
        """
        # This is the function to call to measure the formants

        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        print(f'{max_formant=}')
        try:
            if max_formant == 'Auto':
                try:
                    max_formant = self.args['max_formant (To Formant Burg...)'] = self.formant_max(sound)
                except:
                    # Otherwise default to 5500 Hz as max_formant value, Praat's default
                    max_formant = self.args['max_formant (To Formant Burg...)'] = 5500
        except:
            # Otherwise default to 5500 Hz as max_formant value, Praat's default
            max_formant = self.args['max_formant (To Formant Burg...)'] = 5500
            raise

        print(f'{max_formant=}')
        formant_object = sound.to_formant_burg(
            time_step,
            max_number_of_formants,
            max_formant,
            window_length,
            pre_emphasis
        )
        return formant_object

def get_values_function(object, fn, command):
    """This function returns the values of a function from a praat formant object. This is used to make a vectorized NumPy function to reduce nested loops.

    :param object: the praat formant object
    :type: object: parselmouth.Formant
    :param fn: the function to return
    :type: fn: function
    :param command: the command to use to get the values
    :type: command: str
    :return: values: individual formant values
    :rtype: Union[float, int]
    """

    if command == 'Get mean':
        return call(object, command, fn, 0, 0, "hertz")
    elif command == 'Get quantile':
        return call(object, command, fn, 0, 0, "hertz", 0.5)

