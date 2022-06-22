from __future__ import annotations

import parselmouth
from parselmouth.praat import call

from typing import Union

from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class ScaleIntensityNode(VoicelabNode):
    """Scale intensity.

    Options include RMS or peak method, and a value to scale to

    self.args: dict
        dictionary of values to be passed into the node

        self.args['value']: Union[float, int], default=70.0
            The value to scale intensity to.  For RMS, this is a positive number between 1 and 90.9691. For Peak (-1, 1), pick a number between -1 and 1.
        self.args['method']: str, default='RMS (dB)'
            Choose between RMS and peak.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
            "value": 70.0, # positive float
            "method": ("RMS (dB)", ["RMS (dB)", "Peak (-1, 1)"])
        }
        # process: WARIO hook called once for each voice file.

    def process(self):
        """Process the Scale Intensity Node

        :return {"voice": sound} : Dictionary with the manipulated praat sound object
        :rtype parselmouth.Sound:
        """
        value = self.args["value"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        file_path = self.args['file_path']
        #sound = parselmouth.Sound(file_path)
        method = self.args["method"]
        if method == "RMS":
            sound.scale_intensity(value)
        elif method == "Peak":
            call(sound, "Scale peak", value)
        else:
            sound.scale_intensity(value)
        output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
        output_file_name = f"{output_file_name}_intensity_{value}_{method[0]}"
        sound.name = output_file_name

        return {"voice": sound}
