from __future__ import annotations
import parselmouth
from parselmouth.praat import call
from typing import Union
from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode


class MeasureCPPNode(VoicelabNode):
    """Measure Cepstral Peak Prominance (CPP) of a sound file.

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
            "Measure only voiced segments": True,
            "interpolation": "Parabolic",  # todo add user options for 'None', 'Cubic', and 'Sinc70'
            "Tilt line qeufrency lower bound": 0.001,
            "Tilt line qeufrency upper bound": 0.0,  # 0 = entire range
            "Line type": "Straight",  # todo add user option 'Exponential decay'
            "Fit method": "Robust",  # todo add user option 'Least Squares',
        }

    def process(self):
        """Measure Cepstral Peak Prominance (CPP) of a sound file.


        :return: A dictionary containing the CPP value or an error message.
        :rtype: dict of str|union[float,str]]
        """
        try:
            file_path: str = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            voice: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            sound = voice
            spectrum: parselmouth.Spectrum = voice.to_spectrum()
            cepstrum: parselmouth.Data = call(spectrum, "To PowerCepstrum")

            interpolation: str = self.args["interpolation"]
            tilt_line_qeufrency_lower_bound: Union[float, int] = self.args["Tilt line qeufrency lower bound"]
            tilt_line_qeufrency_upper_bound: Union[float, int] = self.args["Tilt line qeufrency upper bound"]
            linetype: str = self.args["Line type"]
            fitmethod: str = self.args["Fit method"]

            pitch_floor: Union[float, int]
            pitch_ceiling: Union[float, int]
            pitch_floor, pitch_ceiling = self.pitch_bounds(voice)

            maximum_period = 0.02
            mean_period = 0.01

            if self.args["Measure only voiced segments"]:
                pitch = voice.to_pitch_cc(
                    pitch_floor=pitch_floor,
                    pitch_ceiling=pitch_ceiling)
                PointProcess = call([sound, pitch], "To PointProcess (cc)")
                textgrid: parselmouth.Data = call(PointProcess, "To TextGrid (vuv)", maximum_period, mean_period)
                newsounds: list = call([sound, textgrid], "Extract all intervals", 1, False)
                concatenated_sound: parselmouth.Sound = call(newsounds, "Concatenate")
                spectrum: parselmouth.Spectrum = concatenated_sound.to_spectrum()
                cepstrum: parselmouth.Data = call(spectrum, "To PowerCepstrum")


            cpp: Union[int, str] = call(
                cepstrum,
                "Get peak prominence",
                pitch_floor,
                pitch_ceiling,
                interpolation,
                tilt_line_qeufrency_lower_bound,
                tilt_line_qeufrency_upper_bound,
                linetype,
                fitmethod,
            )
            return {"cpp": cpp}
        except Exception as e:
            return {"cpp": str(e)}
