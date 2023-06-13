from __future__ import annotations
import parselmouth
from parselmouth.praat import call
from typing import Union
from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode
import numpy as np

class MeasureAlphaRatioNode(VoicelabNode):
    """Measure Alpha Ratio of a sound file.

    Arguments:
    -----------
    self.args: dict
        Dictionary of arguments for the node.

            self.args["interpolation]": str, default="Parabolic"
                Interpolation method to use.
            self.args["Tilt line qeufrency lower bound"]: Union[float,str], default=0.001
                line qeufrency lower bound
            self.args["Tilt line qeufrency upper bound"]: Union[float, int], default=0.0
                line qeufrency upper bound; 0 means the entire range
            self.args["Line type"]: str,  default="Straight"
                Line type to use.
            self.args["Fit method"]: str, default="Robust"
                Fit method to use."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
            "Pre-Emphasis": 50.0,  # Set to zero to disable
            "Smoothing Bandwidth": 100.0,  # set to zero to disable
        }

    def process(self):
        """Measure Allpha Ratio of a sound file.
        Based on Leino, T. (2009). Long-Term Average Spectrum in Screening of Voice Quality in Speech:
        Untrained Male University Students. Journal of Voice, 23(6), 671–676.
        https://doi.org/10.1016/j.jvoice.2008.03.008

        :return: A dictionary containing the Alpha Ratio or an error message.
        :rtype: dict of str|union[float,str]]
        """
        try:
            signal, sampling_rate = self.args['voice']
            voice: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            sound = voice

            if self.args["Pre-Emphasis"] > 0:
                sound.pre_emphasize(self.args["Pre-Emphasis"])
            if self.args["Smoothing Bandwidth"]:
                sound = call(sound, "Filter (pass Hann band)", 500, 1000, self.args['Smoothing Bandwidth'])

            total_leq = get_leq(sound, sampling_rate)

            sound_below_1kHz = call(sound, "Filter (pass Hann band)", 50, 1000, 50)
            sound_above_1kHz = call(sound, "Filter (pass Hann band)", 1000, 5000, 50)

            leq_above_1kHz = get_leq(sound_above_1kHz, sampling_rate)
            leq_below_1kHz = get_leq(sound_below_1kHz, sampling_rate)

            # Calculate the alpha ratio
            alpha_ratio = leq_above_1kHz - leq_below_1kHz

            return {
                "Alpha (dB)": alpha_ratio.item(),
                "Leq above 1kHz (dB)": leq_above_1kHz.item(),
                "Leq below 1kHz (dB)": leq_below_1kHz.item(),
                "Total Leq (dB)": total_leq.item(),
                    }
        except Exception as e:
            return {"Error": str(e)}


def get_leq(signal, sampling_rate):
    n_samples = signal.get_number_of_samples()
    n_chunks = int(np.ceil(n_samples / (sampling_rate * signal.duration)))
    chunks = np.array_split(signal, n_chunks)
    rms = np.array([np.sqrt(np.mean(chunk ** 2)) for chunk in chunks])
    leq = 20 * np.log10(np.sqrt(np.nanmean(rms ** 2))/2e-5)
    return leq