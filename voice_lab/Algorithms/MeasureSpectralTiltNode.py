import math
import parselmouth

from ...pipeline.Node import Node
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode


class MeasureSpectralTiltNode(VoicelabNode):
    """Measure Spectral Tilt by returning the slope of zero-intercept linear regression of the power spectrum.

    :argument window_length_in_millisecs: Window length in milliseconds
    :type window_length_in_millisecs: str
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "window_length_in_millisecs": ("32", ["32", "64", "128", "256"]),
        }

    def process(self):
        """run the Spectral tilt measurement

            :return {"Spectral Tilt": spectral_tilt}
            :rtype dict[str|Union[float, str]]
            """
        try:
            "Measure spectral tilt"
            file_path: str = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            window_length_in_millisecs = int(self.args["window_length_in_millisecs"][0])
            print(f'{window_length_in_millisecs=}')
            window_length = window_length_in_millisecs / 1000
            # Compute begin and end times, set window
            end = sound.duration
            midpoint = end / 2

            begintime = midpoint - (window_length / 2)
            endtime = midpoint + (window_length / 2)
            part_to_measure = sound.extract_part(begintime, endtime)
            spectrum = part_to_measure.to_spectrum()
            total_bins = spectrum.get_number_of_bins()
            dBValue = []
            bins = []

            # convert spectral values to dB
            for bin in range(total_bins):
                bin_number = bin + 1
                realValue = spectrum.get_real_value_in_bin(bin_number)
                imagValue = spectrum.get_imaginary_value_in_bin(bin_number)
                rmsPower = math.sqrt((realValue ** 2) + (imagValue ** 2))
                db = 20 * (math.log10(rmsPower / 0.0002))
                dBValue.append(db)
                bin_number += 1
                bins.append(bin)

            # find maximum dB value, for rescaling purposes
            maxdB = max(dBValue)
            mindB = min(dBValue)  # this is wrong in Owren's script, where mindB = 0
            rangedB = maxdB - mindB

            # stretch the spectrum to a normalized range that matches the number of frequency values
            scalingConstant = (total_bins - 1) / rangedB
            scaled_dB_values = []
            for value in dBValue:
                scaled_dBvalue = value + abs(mindB)
                scaled_dBvalue *= scalingConstant
                scaled_dB_values.append(scaled_dBvalue)

            # find slope
            sumXX = 0
            sumXY = 0
            sumX = sum(bins)
            sumY = sum(scaled_dB_values)

            for bin in bins:
                currentX = bin
                sumXX += currentX ** 2
                sumXY += currentX * scaled_dB_values[bin]

            sXX = sumXX - ((sumX * sumX) / len(bins))
            sXY = sumXY - ((sumX * sumY) / len(bins))
            spectral_tilt = sXY / sXX
            return {"Spectral Tilt": spectral_tilt}
        except Exception as e:
            return {"Spectral Tilt": str(e)}
