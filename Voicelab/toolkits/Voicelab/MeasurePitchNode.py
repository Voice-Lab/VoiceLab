from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
import parselmouth
import numpy as np
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from typing import Union, List, Tuple, Dict, Any


class MeasurePitchNode(VoicelabNode):
    """
            Attributes:
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

    """
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        # Default settings for measuring pitch.
        self.args = {
            "Time Step": 0.0, # Time step in seconds. 0 is praat's default, 0.75 / (pitch floor)
            "Max Number of Candidates": 15,  # Positive integers
            "Silence Threshold": 0.03,  # Positive number
            "Voicing Threshold": 0.45,  # Positive number
            "Octave Cost": 0.01,  # Positive number
            "Octave Jump Cost": 0.35,  # Positive number
            "Voiced Unvoiced Cost": 0.14,  # Positive number
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
            # Tuple defines a discrete set of options, 0 = selected value, 1 = a list of all options
            "Algorithm": ("To Pitch (ac)", ["To Pitch (ac)", "To Pitch (cc)"]),
            "Very Accurate": ("yes", ["yes", "no"]),
        }

    def process(self) -> dict[str, any]:
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

        voice: parselmouth.Sound = self.args["voice"]
        """The voice object is a parselmouth.Sound object.
        :type: parselmouth.Sound
        """

        time_step: float = self.args["Time Step"]
        """The time step is the amount of time between each frame.
        :type: float
        """

        max_number_of_candidates: int = self.args["Max Number of Candidates"]
        """max_number_of_candidates is the maximum number of pitch candidates that will be returned. 
        :type: int
        """

        silence_threshold: float = self.args["Silence Threshold"]
        """silence_threshold is the threshold for determining if a frame is silent.
        :type: float
        """

        voicing_threshold: float = self.args["Voicing Threshold"]
        """voicing_threshold is the threshold for determining if a frame is voiced.
        :type: float
        """

        octave_cost: float = self.args["Octave Cost"]
        """octave_cost is the cost of a jump in octave.
        :type: float
        """

        octave_jump_cost: float = self.args["Octave Jump Cost"]
        """octave_jump_cost is the cost of a jump in octave.
        :type: float
        """

        voiced_unvoiced_cost: float = self.args["Voiced Unvoiced Cost"]
        """voiced_unvoiced_cost is the degree of disfavouring of voiced/unvoiced transitions
        :type: float
        """

        unit = self.args["Unit"][0]
        """unit is the unit of the pitch.  The choices are:\n
        - Hertz\n
        - Hertz (Logarithmic)\n
        - mel\n
        - logHertz\n
        - semitones re 1 Hz\n
        - semitones re 100 Hz\n
        - semitones re 200 Hz\n
        - semitones re 440 Hz\n
        - ERB\n
        :type: str
        """

        method: str = self.args["Algorithm"][0]
        """method is the algorithm used to find the pitch.  The choices are:\n
        - To Pitch (ac)\n
        - To Pitch (cc)\n
        :type: str
        """

        very_accurate: str = self.args["Very Accurate"][0]
        """very_accurate is a boolean value that determines if the algorithm used 3 pitch periods or 6. 6 are used if the value is yes.
        :type: bool
        """

        try:
            pitch_floor, pitch_ceiling = self.pitch_bounds(voice)
            pitch, pitch_values, mean_f0, stdev_f0, min_f0, max_f0 = measure_pitch(
                voice,
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

            return {
                "Pitches": pitch_values,
                "Mean Pitch (F0)": mean_f0,
                "Standard Deviation Pitch (F0)": stdev_f0,
                "Pitch Min (F0)": min_f0,
                "Pitch Max (F0)": max_f0,
                "Pitch": pitch,
                "Pitch Floor": pitch_floor,
                "Pitch Ceiling": pitch_ceiling,
            }
        except:
            return {
                "Pitches": "Pitch Measurement Failed",
                "Mean Pitch (F0)": "Pitch Measurement Failed",
                "Standard Deviation Pitch (F0)": "Pitch Measurement Failed",
                "Pitch Min (F0)": "Pitch Measurement Failed",
                "Pitch Max (F0)": "Pitch Measurement Failed",
                "Pitch": "Pitch Measurement Failed",
                "Pitch Floor": "Pitch Measurement Failed",
                "Pitch Ceiling": "Pitch Measurement Failed",
            }


def measure_pitch(
    voice,
    floor=50,
    ceiling=500,
    method="ac",
    time_step=0,
    max_number_of_candidates=15,
    silence_threshold=0.03,
    voicing_threshold=0.45,
    octave_cost=0.01,
    octave_jump_cost=0.35,
    voiced_unvoiced_cost=0.14,
    unit="Hertz",
    very_accurate="no",
) -> Tuple[float, List[float], float, float, float, float]:
    """
        :param voice: The audio file to be analyzed.
        :type voice: str
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
    pitch: parselmouth.Data = call(
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
    """ The mean pitch of the audio file. 
    
    :type mean_f0: float
    """
    stdev_f0: float = call(pitch, "Get standard deviation", 0, 0, unit)  # get standard deviation
    """
    The standard deviation of the pitch of the audio file.
    
    :type stdev_f0: float
    """
    min_f0: float = call(pitch, "Get minimum", 0, 0, unit, "Parabolic")
    max_f0: float = call(pitch, "Get maximum", 0, 0, unit, "Parabolic")
    pitch_values = pitch.selected_array['frequency']
    pitch_values[pitch_values == 0] = np.nan
    pitch_values = pitch_values.tolist()
    return pitch, pitch_values, mean_f0, stdev_f0, min_f0, max_f0
