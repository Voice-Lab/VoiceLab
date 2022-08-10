from __future__ import annotations

import parselmouth
from parselmouth.praat import call

from typing import Union

from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class MeasureSpectralShapeNode(VoicelabNode):
    """Measure characteristics of the spectral shape

    Arguments
    =========

    self.args: dict
        A dictionary of options for the node

            self.args["Low band floor (Hz)"]: Union[float, int], default=0.0

            self.args["Low band ceiling (Hz)"]: Union[float, int], default=500.0

            self.args["High band floor (Hz)"]: Union[float, int], default=500.0

            self.args["High band ceiling (Hz)"]: Union[float, int], default=4000.0

            self.args["Power"]: 2 int, default=2
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "Low band floor (Hz)": 0.0,  # positive number or 0
            "Low band ceiling (Hz)": 500.0,  # positive number greater than "Low band floor (Hz)"
            "High band floor (Hz)": 500.0,  # positive number or 0
            "High band ceiling (Hz)": 4000.0,  # positive number greater than "High band floor (Hz)"
            "Power": 2,  # Positive integer
        }
        # process: WARIO hook called once for each voice file.

    def process(self):
        """Run the Spectral Shape Node

        Returns:
        --------
        dict of str | Union[float, str]
            dictionary with the following keys:
                - "Centre of Gravity": centre_of_gravity,
                - "Standard Deviation": standard_deviation,
                - "Kurtosis": kurtosis,
                - "Skewness": skewness,
                - "Band Energy Difference": band_energy_difference,
                - "Band Density Difference": band_density_difference,

        """
        try:
            # Gather parameters
            file_path: str = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            #sound = parselmouth.Sound(file_path)
            spectrum = sound.to_spectrum()
            power = self.args["Power"]
            low_band_floor = self.args["Low band floor (Hz)"]
            low_band_ceiling = self.args["Low band ceiling (Hz)"]
            high_band_floor = self.args["High band floor (Hz)"]
            high_band_ceiling = self.args["High band ceiling (Hz)"]

            # Measure voices
            centre_of_gravity = spectrum.get_centre_of_gravity(power)
            standard_deviation = spectrum.get_standard_deviation(power)
            kurtosis = spectrum.get_kurtosis(power)
            skewness = spectrum.get_skewness(power)
            band_energy_difference = spectrum.get_band_energy_difference(
                low_band_floor, low_band_ceiling, high_band_floor, high_band_ceiling
            )
            band_density_difference = spectrum.get_band_density_difference(
                low_band_floor, low_band_ceiling, high_band_floor, high_band_ceiling
            )

            return {
                "Centre of Gravity": centre_of_gravity,
                "Standard Deviation": standard_deviation,
                "Kurtosis": kurtosis,
                "Skewness": skewness,
                "Band Energy Difference": band_energy_difference,
                "Band Density Difference": band_density_difference,
            }
        except Exception as e:
            return {
                "Centre of Gravity": str(e),
                "Standard Deviation": str(e),
                "Kurtosis": str(e),
                "Skewness": str(e),
                "Band Energy Difference": str(e),
                "Band Density Difference": str(e),
            }
