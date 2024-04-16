from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode

from parselmouth.praat import call
import parselmouth

import numpy as np
import pysptk
from scipy.io.wavfile import read as wavread


class MeasurePitchRaptNode(VoicelabNode):

    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        # initialize with default arguments

        self.args = {
            "hopsize": 0.01,  # sampling rate times this number
            "min": 40,  # minimum frequency
            "max": 500,  # maximum frequency
            "Voiced/unvoiced threshold": 0.0,  # voice_bias
        }

    def process(self):
        try:
            audioFilePath = self.args["file_path"]
            fs, x = wavread(audioFilePath)
            x = x.astype(np.float32)
            hopsize = int(fs * self.args['hopsize'])
            min = self.args['min']
            max = self.args['max']
            voice_bias = self.args["Voiced/unvoiced threshold"]
            f0 = pysptk.sptk.rapt(x, fs, hopsize, min, max, voice_bias, otype='f0')
            f0_nozero = f0[f0 > 0]
            mean_f0 = np.nanmean(f0_nozero).item()
            min_f0 = np.nanmin(f0_nozero).item()
            max_f0 = np.nanmax(f0_nozero).item()
            return {
                'Mean Pitch RAPT': mean_f0,
                'Min Pitch RAPT': min_f0,
                'Max Pitch RAPT': max_f0,
                'Pitch Values RAPT': f0.tolist(),
            }

        except:
            return {
                'Mean Pitch RAPT': "Measure Pitch RAPT Failed",
                'Min Pitch RAPT': "Measure Pitch RAPT Failed",
                'Max Pitch RAPT': "Measure Pitch RAPT Failed",
                'Pitch Values RAPT': "Measure Pitch RAPT Failed",
            }
