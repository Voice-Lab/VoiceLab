from __future__ import annotations
from typing import Union

import parselmouth

from ...pipeline.Node import Node
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode


class MeasureIntensityNode(VoicelabNode):
    """Measure Intensity (dB) of sound
    Arguments:
        self.args: dict of arguments
            These are the Intensity options from Praat:
            minimum_pitch Union[float, int], default 100.0
                The minimum pitch for the analysis. This sets the analysis window to 0.8 / minimum pitch
            time step: float, default 0.0 (Automatic)
                The time step (hop length) for the analysis
            Subtract Mean: bool, default True
                Subtract the mean intensity from the intensity
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "minimum_pitch": 100.0,
            "time step": 0.0,
            "Subtract Mean": True
        }

    def process(self):
        """Run the intensity analysis

        :argument self.args['file_path']: the path to the file to be analysed
        :type self.args['file_path']: str

        :return: dict of results
        :rtype: dict[str, Union[int, float, str, list]]
        """
        file_path = self.args['file_path']
        voice = parselmouth.Sound(file_path)
        try:
            minimum_pitch = self.args["minimum_pitch"]
            intensity = voice.to_intensity(minimum_pitch)
            mean_intensity = intensity.get_average()
            return {
                "Intensity": intensity,
                "Mean Intensity (dB)": mean_intensity
            }
        except Exception as e:
            return {
                "Intensity": str(e),
                "Mean Intensity (dB)": str(e)
            }
