from __future__ import annotations

from typing import Union
from ...pipeline.Node import Node
import parselmouth
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode


class MeasureHarmonicityNode(VoicelabNode):
    """Measure the harmonics-to-noise ratio of a sound. This is effetively the Signal-to-Noise Ratio (SNR) of a periodic sound.

    Arguments:
    ---------
        self.args: dict
            Dictionary of arguments for the node.
            self.args['Algorithm'] : str, default=To Harmonicity (cc)'
                Which pitch algorithm to use. Default is Cross Correlation, alternate is Auto Correlation.
            self.args['Timestep'] : float, default 0.01
                The timestep (hop length/time between windows) to use for the analysis.
            self.args["Silence Threshold"]: float, default=0.1,
                The threshold below which a frame is considered silent.
            self.args["Periods per Window"]: float, default=4.5,
                The number of periods per window.
    """
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "Algorithm": (
                "To Harmonicity (cc)",
                ["To Harmonicity (cc)", "To Harmonicity (ac)"],
            ),
            "Timestep": 0.01,
            "Silence Threshold": 0.1,
            "Periods per Window": 4.5,  # This is a new change from 1.0
        }

    def process(self):
        """This function measures Harmonics to Noise Ratio

        :return: A dictionary of the results or an error message.
        :rtype: dict[str, Union[str, float]]
        """

        try:
            file_path: str = self.args["file_path"]
            sound: parselmouth.Sound = parselmouth.Sound(file_path)
            algorithm: str = self.args["Algorithm"][0]
            timestep: float = self.args["Timestep"]
            silence_threshold: float = self.args["Silence Threshold"]
            periods_per_window: float = self.args["Periods per Window"]
            pitch_floor: float = self.pitch_floor(sound)
            harmonicity: float = call(sound, algorithm, timestep, pitch_floor, silence_threshold, periods_per_window,)
            hnr: float = call(harmonicity, "Get mean", 0, 0)
            return {"Harmonics to Noise Ratio": hnr}
        except Exception as e:
            return {"Harmonics to Noise Ratio": str(e)}
