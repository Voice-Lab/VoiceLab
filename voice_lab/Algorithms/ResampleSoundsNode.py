from __future__ import annotations

import parselmouth
from parselmouth.praat import call

from typing import Union

from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode



class ResampleSoundsNode(VoicelabNode):
    """
    Attributes
    ----------
    self.args: dict
        Dictionary of parameters to pass into the node.

    self.args['Sampling Rate']: Union[float, int], default = 44100.0
        The target sampling rate.
    self.args['Precision']: Union[float, int], default=50
        - If Precision is 1, the method is linear interpolation, which is inaccurate but fast.
        - If Precision is greater than 1, the method is sin(x)/x ("sinc") interpolation, with a depth equal to Precision. For higher Precision, the algorithm is slower but more accurate.
        - If Sampling frequency is less than the sampling frequency of the selected sound, an anti-aliasing low-pass filtering is performed prior to resampling.
        - `<https://www.fon.hum.uva.nl/praat/manual/Sound__Resample___.html>`_

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {"Sampling Rate": 44100.0,  # Positive number
                     "Precision": 50    # Positive integer
                     }
        # process: WARIO hook called once for each voice file.

    def process(self):
        """Resample sounds. This returns a parselmouth.Sound object which is saved later by the Voicelab interface.

        :return : dictionary with note of success and the resampled parselmouth.Sound object
        :rtype: dict{
            str|str,
            str|Union[parselmouth.Sound, str]
            }

        """
        try:
            # Load arguments
            file_path = self.args['file_path']
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            sampling_rate = self.args["Sampling Rate"]
            precision = self.args["Precision"]
            file_path = self.args["file_path"]

            # resample sound
            sound = sound.resample(sampling_rate, precision)

            # set up file name
            output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
            output_file_name = f"{output_file_name}_resampled_to_{sampling_rate}_Hz"
            sound.name = output_file_name
            success = "Sound resampled successfully"

        except Exception as e:
            sound = str(e)
            success = "Sound not resampled"

        return {
            "result": success,
            "voice": sound
        }
