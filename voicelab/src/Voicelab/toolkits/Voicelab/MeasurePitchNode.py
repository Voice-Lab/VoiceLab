from ...pipeline.Node import Node
from parselmouth import Sound
from parselmouth.praat import call
import parselmouth
import numpy as np
from .VoicelabNode import VoicelabNode
# Importing the necessary libraries for the program to run.
from typing import Union, List, Tuple, Dict, Any
from .MeasurePitchYinNode import MeasurePitchYinNode
from .MeasureSHRPNode import MeasureSHRPNode


class MeasurePitchNode(VoicelabNode):
    """Measure Pitch with Praat
       -------------------------

        Arguments:
        -----------
        self.args: dict
            Dictionary of arguments for the node.

            self.args{'Time Step'} (float):
                Hop length in seconds. 0 is praat's default, 0.75 / (pitch floor)
            self.args{'Max Number of Candidates'} (float)
                The maximum number of pitch candidates to be considered
            self.args{"Silence Threshold"} (float)
                frames that do not contain amplitudes above this threshold (relative to the global maximum amplitude), are probably silent.
            self.args{'Voicing Threshold'} (float)
                the strength of the unvoiced candidate, relative to the maximum possible autocorrelation. To increase the number of unvoiced decisions, increase this value.
            self.args{'Octave Cost'} (float)
                degree of favouring of high-frequency candidates, relative to the maximum possible autocorrelation. This is necessary because even (or: especially) in the case of a perfectly periodic signal, all undertones of F0 are equally strong candidates as F0 itself. To more strongly favour recruitment of high-frequency candidates, increase this value.
            self.args{"Octave Jump Cost"} (float)
                degree of disfavouring of pitch changes, relative to the maximum possible autocorrelation. To decrease the number of large frequency jumps, increase this value. In contrast with what is described in the article, this value will be corrected for the time step: multiply by 0.01 s / TimeStep to get the value in the way it is used in the formulas in the article.
            self.args{'Vocied Unvoiced Cost'} (float)
                degree of disfavouring of voiced/unvoiced transitions, relative to the maximum possible autocorrelation. To decrease the number of voiced/unvoiced transitions, increase this value. In contrast with what is described in the article, this value will be corrected for the time step: multiply by 0.01 s / TimeStep to get the value in the way it is used in the formulas in the article.
            self.args{'Unit'} (str)
                The unit for pitch. Choices are "Hertz","Hertz (Logarithmic)", "mel", "logHertz", "semitones re 1 Hz", "semitones re 100 Hz", "semitones re 200 Hz", "semitones re 440 Hz", "ERB"
            self.args{'Algorithm} (str)
                Either Autocorrelation or Cross Correlation
            self.args{"Very Accurate"} (str)
                No uses 3 pitch periods. Yes uses 6 pitch periods.

        Measure Pitch with Yin:
        -----------------------
        Use minF0 and maxF0 to set the range of frequencies to search for. Values supplied above. None of the other arguments are used.
    """
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        # Default settings for measuring pitch with Praat

        self.args = {
            "Praat To Pitch (ac)": True,
            "Praat To Pitch (cc)": True,
            "Pitch Floor": 0.0,
            "Pitch Ceiling": 0.0,
            "Time Step": 0.0,  # Time step in seconds. 0 is praat's default, 0.75 / (pitch floor)
            "Max Number of Candidates": 15,  # Positive integers
            "Silence Threshold": 0.03,  # Positive number
            "Voicing Threshold": 0.45,  # Positive number
            "Octave Cost": 0.01,  # Positive number
            "Octave Jump Cost": 0.35,  # Positive number
            "Voiced Unvoiced Cost": 0.14,  # Positive number
            "Very Accurate": True,
            "Unit": ("Hertz", ["Hertz",
                               "Hertz (Logarithmic)",
                               "mel",
                               "logHertz",
                               "semitones re 1 Hz",
                               "semitones re 100 Hz",
                               "semitones re 200 Hz",
                               "semitones re 440 Hz",
                               "ERB",
                               ]
                     ),
            "Yin": True,
            "Subharmonic Pitch": True,
        }

    def process(self):
        """
        The process function is the heart of VoiceLab. It is where all the processing
        is done. The process function takes in a single argument, which is an object that contains
        all the input data for this process (the input object). This function should return a dictionary, if it works,
        or a string with an error message if it does not.

        :param self: Used to Access the attributes and methods of the class in python.

        Returns:
        -------
        :returns: A dictionary with the following keys:


                'Pitches' (list of floats)
                    List of pitch values.
                'Mean Pitch (F0)' (float)
                    Mean pitch value in Hz.
                'Standard Deviation (F0)' (float)
                    Standard deviation of pitch values in Hz.
                'Minimum Pitch (F0)' (float)
                    Minimum pitch value in Hz.
                'Maximum Pitch (F0)' (float)
                    Maximum pitch value in Hz.
                'Pitch Floor' (float)
                    Pitch floor used in manipulation.
                'Pitch Ceiling' (float)
                    Pitch ceiling used in manipulation.

        """
        file_path: str = self.args["file_path"]
        voice: parselmouth.Sound = parselmouth.Sound(file_path)
        time_step: float = self.args["Time Step"]
        max_number_of_candidates: int = self.args["Max Number of Candidates"]
        silence_threshold: float = self.args["Silence Threshold"]
        voicing_threshold: float = self.args["Voicing Threshold"]
        octave_cost: float = self.args["Octave Cost"]
        octave_jump_cost: float = self.args["Octave Jump Cost"]
        voiced_unvoiced_cost: float = self.args["Voiced Unvoiced Cost"]
        unit: str = self.args["Unit"][0]
        very_accurate: str = self.args["Very Accurate"]
        pitch_algorithms: dict = {
            "praat_ac": self.args["Praat To Pitch (ac)"],
            "praat_cc": self.args["Praat To Pitch (cc)"],
            "yin": self.args["Yin"],
            "subharmonic_pitch": self.args['Subharmonic Pitch']
        }
        pitch_results_list_of_dictionaries: list = []
        pitch_floor: Union[float, int] = self.args['Pitch Floor']
        pitch_ceiling: Union[float, int] = self.args['Pitch Ceiling']
        try:
            # If user does not specify floor or ceiling use automatic settings
            if pitch_floor == 0.0:
                pitch_floor = self.pitch_floor(file_path)
            if pitch_ceiling == 0.0:
                pitch_ceiling = self.pitch_ceiling(file_path)


            if pitch_algorithms["praat_ac"]:
                method = 'To Pitch (ac)'
                pitch, praat_ac_pitch_values, praat_ac_mean_f0, praat_ac_median_f0, praat_ac_stdev_f0, praat_ac_min_f0, praat_ac_max_f0 = measure_pitch_praat(
                    file_path,
                    floor=pitch_floor,
                    ceiling=pitch_ceiling,
                    method=method,
                    time_step=time_step,
                    max_number_of_candidates=max_number_of_candidates,
                    silence_threshold=silence_threshold,
                    voicing_threshold=voicing_threshold,
                    octave_cost=octave_cost,
                    octave_jump_cost=octave_jump_cost,
                    voiced_unvoiced_cost=voiced_unvoiced_cost,
                    unit=unit,
                    very_accurate=very_accurate,
                )
                praat_ac_results = {
                    "Pitch": pitch,
                    "Pitch Praat To Pitch (ac)": pitch,
                    "Pitch Values (Praat To Pitch (ac))": praat_ac_pitch_values,
                    "Mean Pitch (F0) (Praat To Pitch (ac))": praat_ac_mean_f0,
                    "Median Pitch (F0) (Praat To Pitch (ac))": praat_ac_median_f0,
                    "Standard Deviation Pitch (F0) (Praat To Pitch (ac))": praat_ac_stdev_f0,
                    "Pitch Min (F0) (Praat To Pitch (ac))": praat_ac_min_f0,
                    "Pitch Max (F0) (Praat To Pitch (ac))": praat_ac_max_f0,
                    "Pitch Floor": pitch_floor,
                    "Pitch Ceiling": pitch_ceiling,
                }
                pitch_results_list_of_dictionaries.append(praat_ac_results)

                if pitch_algorithms["praat_cc"]:
                    method = 'To Pitch (cc)'
                    pitch, praat_cc_pitch_values, praat_cc_mean_f0, praat_cc_median_f0, praat_cc_stdev_f0, praat_cc_min_f0, praat_cc_max_f0\
                        = measure_pitch_praat(
                        file_path,
                        floor=pitch_floor,
                        ceiling=pitch_ceiling,
                        method=method,
                        time_step=time_step,
                        max_number_of_candidates=max_number_of_candidates,
                        silence_threshold=silence_threshold,
                        voicing_threshold=voicing_threshold,
                        octave_cost=octave_cost,
                        octave_jump_cost=octave_jump_cost,
                        voiced_unvoiced_cost=voiced_unvoiced_cost,
                        unit=unit,
                        very_accurate=very_accurate,
                    )
                    praat_cc_results = {
                        "Pitch": pitch,
                        "Pitch To Pitch (cc)": pitch,
                        "Pitch Values (Praat To Pitch (cc))": praat_cc_pitch_values,
                        "Mean Pitch (F0) ( To Pitch (cc))": praat_cc_mean_f0,
                        "Median Pitch (F0) (Praat To Pitch (cc))": praat_cc_median_f0,
                        "Standard Deviation Pitch (F0) (Praat To Pitch (cc))": praat_cc_stdev_f0,
                        "Pitch Min (F0) (Praat To Pitch (cc))": praat_cc_min_f0,
                        "Pitch Max (F0) (Praat To Pitch (cc))": praat_cc_max_f0,
                        "Pitch (Praat To Pitch (cc))": pitch,
                        "Pitch Floor": pitch_floor,
                        "Pitch Ceiling": pitch_ceiling,
                    }
                    pitch_results_list_of_dictionaries.append(praat_cc_results)

            if pitch_algorithms["yin"]:
                yin = MeasurePitchYinNode()
                yin_results = yin.process(audioFilePath=file_path)
                pitch_results_list_of_dictionaries.append(yin_results)

            if pitch_algorithms["subharmonic_pitch"]:
                shrp = MeasureSHRPNode()
                shrp_results = shrp.process(filename=file_path)
                pitch_results_list_of_dictionaries.append(shrp_results)

            if all(value is False for value in pitch_algorithms.values()):
                method = 'To Pitch (ac)'
                pitch, praat_ac_pitch_values, praat_ac_mean_f0, praat_ac_median_f0, praat_ac_stdev_f0, praat_ac_min_f0, praat_ac_max_f0 = measure_pitch_praat(
                    file_path,
                    floor=pitch_floor,
                    ceiling=pitch_ceiling,
                    method=method,
                    time_step=time_step,
                    max_number_of_candidates=max_number_of_candidates,
                    silence_threshold=silence_threshold,
                    voicing_threshold=voicing_threshold,
                    octave_cost=octave_cost,
                    octave_jump_cost=octave_jump_cost,
                    voiced_unvoiced_cost=voiced_unvoiced_cost,
                    unit=unit,
                    very_accurate=very_accurate,
                )
                praat_ac_results = {
                    "Pitch": pitch,
                    "Pitch Values (Praat To Pitch (ac))": praat_ac_pitch_values,
                    "Mean Pitch (F0) (Praat To Pitch (ac))": praat_ac_mean_f0,
                    "Median Pitch (F0) (Praat To Pitch (ac))": praat_ac_median_f0,
                    "Standard Deviation Pitch (F0) (Praat To Pitch (ac)": praat_ac_stdev_f0,
                    "Pitch Min (F0) (Praat To Pitch (ac))": praat_ac_min_f0,
                    "Pitch Max (F0) (Praat To Pitch (ac))": praat_ac_max_f0,
                    "Pitch (Praat To Pitch (ac))": pitch,
                    "Pitch Floor": pitch_floor,
                    "Pitch Ceiling": pitch_ceiling,
                }
                pitch_results_list_of_dictionaries.append(praat_ac_results)

            # combine all the results dictionaries together
            current_results = {k:v for x in pitch_results_list_of_dictionaries for k,v in x.items()}
            return current_results

        except Exception as e:
            return {
                "Pitch": str(e),
                "Pitch Values (Praat To Pitch (ac))":  str(e),
                "Mean Pitch (F0) (Praat To Pitch (ac))": str(e),
                "Median Pitch (F0) (Praat To Pitch (ac))":str(e),
                "Standard Deviation Pitch (F0) (Praat To Pitch (ac)": str(e),
                "Pitch Min (F0) (Praat To Pitch (ac))": str(e),
                "Pitch Max (F0) (Praat To Pitch (ac))": str(e),
                "Pitch (Praat To Pitch (ac))": str(e),
                "Pitch Floor": str(e),
                "Pitch Ceiling": str(e),
            }


def measure_pitch_praat(
    file_path: str,
    floor: Union[float, int] = 50,
    ceiling: Union[float, int] = 500,
    method: str = "ac",
    time_step: Union[float, int] = 0.0,
    max_number_of_candidates: int = 15,
    silence_threshold: Union[float, int] = 0.03,
    voicing_threshold: Union[float, int] = 0.45,
    octave_cost: Union[float, int] = 0.01,
    octave_jump_cost: Union[float, int] = 0.35,
    voiced_unvoiced_cost: Union[float, int] = 0.14,
    unit: str = "Hertz",
    very_accurate: str = "no",
) -> Tuple[float, List[float], float, float, float, float, float]:
    """
        :param file_path:The path to the audio file to be analyzed.
        :type file_path: str
        :param floor: The lowest pitch to be considered.
        :type floor: int, float
        :param ceiling: The highest pitch to be considered.
        :type ceiling: int, float
        :param method: The algorithm used to find the pitch (autocorrelation or cross correlation).
        :type method: str
        :param time_step:  The time step used to find the pitch.
        :type time_step: float
        :param max_number_of_candidates: The maximum number of pitch candidates to be considered.
        :type max_number_of_candidates: int
        :param silence_threshold:  The threshold used to determine if a frame is silent.
        :type silence_threshold: float
        :param voicing_threshold: The threshold used to determine if a frame is voiced.
        :type voicing_threshold: float
        :param octave_cost: degree of favouring of high-frequency candidates, relative to the maximum possible autocorrelation
        :type octave_cost: float
        :param octave_jump_cost: degree of disfavouring of pitch changes, relative to the maximum possible autocorrelation
        :type octave_jump_cost: float
        :param voiced_unvoiced_cost: degree of disfavouring of unvoiced frames
        :type voiced_unvoiced_cost: float
        :param unit: The unit of the pitch. The choices are:\n
                        - Hertz\n
                        - Hertz (Logarithmic)\n
                        - mel\n
                        - logHertz\n
                        - semitones re 1 Hz\n
                        - semitones re 100 Hz\n
                        - semitones re 200 Hz\n
                        - semitones re 440 Hz\n
                        - ERB\n
        :type unit: str
        :param very_accurate: very_accurate is a boolean value that determines if the algorithm used 3 pitch periods or 6. 6 are used if the value is yes.
        :type very_accurate: str


        :returns:
            - **pitch**: *(parselmouth.Data)* - parselmouth pitch object
            - **mean_f0**: *(float)* - The mean pitch
            - **std_f0**: *(float)* - The standard deviation of the pitch
            - **min_f0**: *(float)* - The minimum pitch
            - **max_f0**: *(float)* - The maximum pitch
    """
    voice: Sound = parselmouth.Sound(file_path)
    pitch: parselmouth.Pitch = call(
        voice,
        method,
        time_step,
        floor,
        max_number_of_candidates,
        very_accurate,
        silence_threshold,
        voicing_threshold,
        octave_cost,
        octave_jump_cost,
        voiced_unvoiced_cost,
        ceiling,
    )
    mean_f0: float = call(pitch, "Get mean", 0, 0, unit)
    median_f0: float = call(pitch, "Get quantile", 0, 0, 0.5, "Hertz")
    stdev_f0: float = call(pitch, "Get standard deviation", 0, 0, unit)
    min_f0: Union[float, int] = call(pitch, "Get minimum", 0, 0, unit, "Parabolic")
    max_f0: Union[float, int] = call(pitch, "Get maximum", 0, 0, unit, "Parabolic")
    pitch_values: np.array = pitch.selected_array['frequency']
    pitch_values[pitch_values == 0]: np.array = np.nan
    pitch_values: list[Union[int, float]] = pitch_values.tolist()
    return pitch, pitch_values, mean_f0, median_f0, stdev_f0, min_f0, max_f0
