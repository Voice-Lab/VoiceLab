from __future__ import annotations

from typing import Union

import parselmouth
from parselmouth.praat import call

from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode


class MeasureLTASNode(VoicelabNode):
    """Measure frequency characteristics of a Long-Term Average Spectrum of a voice

    Attributes:
    -----------
    self.args: dict
        A dictionary of settings for the LTAS measurements

        self.args['Pitch corrected']: bool, default=False
             It tries to compute an Ltas of the spectral envelope of the voiced parts, correcting away the influence of F0 in a way that does not sacrifice frequency selectivity. The resulting Ltas is meant to reflect only the resonances (formants) in the vocal tract and the envelope of the glottal source spectrum. `<https://www.fon.hum.uva.nl/praat/manual/Sound__To_Ltas__pitch-corrected____.html>`_

        self.args['Bandwidth']: Union[float, int], default=100.0
            Frequency bandwidth of LTAS

        self.args['Maximum frequency']: Union[float, int], default=5000.0
            Sound will be resampled to 2x this value for LTAS analysis
        self.args['Shortest period (s)']: Union[float, int], default=0.0001
            The shortest period considered
        self.args['Longest period (s)']: Union[float, int], default=0.02
            The longest period considered
        self.args['Maximum period factor']: Union[float, int], default=1.3
            The longest difference between periods to be considered

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
            "Minimum Pitch": 0.0,
            "Maximum Pitch": 0.0,
            "Pitch corrected": False,
            "Bandwidth": 100.0,
            "Maximum frequency": 5000.0,
            "Shortest period": 0.0001,
            "Longest period": 0.02,
            "Maximum period factor": 1.3,
        }

    def process(self):
        """Run LTAS node on a sound

        Returns:
        --------

        dict[str | Union[float, int, str]
            Dictionary of following results or dict of error message

            - "LTAS Mean (dB)": mean_dB,
            - "LTAS slope (dB)": slope_dB,
            - "LTAS local peak height (dB)": local_peak_height_dB,
            - "LTAS standard deviation (dB)": standard_deviation_dB,
            - "LTAS spectral tilt slope ({slope_unit})": slope_value,
            - "LTAS spectral tilt intercept ({intercept_unit})": intercept_value,

        """
        file_path = self.args['file_path']
        sound = parselmouth.Sound(file_path)

        try:
            f0min, f0max = self.pitch_bounds(file_path)
            bandwidth = self.args["Bandwidth"]
            # todo grey these out when Pitch Corrected is False
            max_frequency = self.args["Maximum frequency"]
            shortest_period = self.args["Shortest period"]
            longest_period = self.args["Longest period"]
            max_period_factor = self.args["Maximum period factor"]

            if not self.args["Pitch corrected"]:
                method = "To Ltas"
                ltas = call(
                    sound,
                    method,
                    bandwidth,
                )
            elif self.args["Pitch corrected"]:
                method =  "To Ltas (pitch-corrected)"
                ltas = call(
                    sound,
                    method,
                    bandwidth,
                    max_frequency,
                    shortest_period,
                    longest_period,
                    max_period_factor
                )

            mean_dB = call(ltas, "Get mean", 0, 0, "dB")
            slope_dB = call(ltas, "Get slope", 0, 1000, 1000, 4000, "dB")
            local_peak_height_dB = call(
                ltas, "Get local peak height", 1700, 4200, 2400, 3200, "dB"
            )
            standard_deviation_dB = call(ltas, "Get standard deviation", 0, 0, "dB")
            ltas_spectral_tilt = call(
                ltas, "Report spectral tilt", 100, 5000, "Linear", "Robust"
            )
            formula, slope, intercept = ltas_spectral_tilt.splitlines()
            slope_name, slope_value, slope_unit = slope.split()
            intercept_name, intercept_value, intercept_unit = intercept.split()
            return {
                "LTAS Mean (dB)": mean_dB,
                "LTAS slope (dB)": slope_dB,
                "LTAS local peak height (dB)": local_peak_height_dB,
                "LTAS standard deviation (dB)": standard_deviation_dB,
                "LTAS spectral tilt slope ({slope_unit})": slope_value,
                "LTAS spectral tilt intercept ({intercept_unit})": intercept_value,
            }
        except Exception as e:
            return {
                "LTAS Mean (dB)": str(e),
                "LTAS slope (dB)": str(e),
                "LTAS local peak height (dB)": str(e),
                "LTAS standard deviation (dB)": str(e),
                "LTAS spectral tilt slope ": str(e),
                "LTAS spectral tilt intercept": str(e),
            }
