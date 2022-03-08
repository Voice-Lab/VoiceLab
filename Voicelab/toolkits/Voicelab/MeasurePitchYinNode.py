from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from parselmouth.praat import call
import parselmouth

import numpy as np
# from scipy.io.wavfile import read as wavread
# from scipy.signal import resample
# import statistics
import librosa


class MeasurePitchYinNode(VoicelabNode):

    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        # initialize with default arguments
        self.args = {
            'min f0': 40,
            'max f0': 600,
        }

    def process(self):
        try:
            audioFilePath = self.args["file_path"]
            if audioFilePath[-3:].lower() != "wav":
                tmp_praat_object = parselmouth.Sound(audioFilePath)
                tmp_praat_object.save("tmp.wav", "WAV")
                audioFilePath = 'tmp.wav'
            y, sr = librosa.load(audioFilePath)
            fmin = self.args["min f0"]
            fmax = self.args["max f0"]
            pitches_full = librosa.yin(y, fmin, fmax, sr) #
            pitches = pitches_full[pitches_full != 0]
            yin_min_pitch = np.nanmin(pitches).item()
            yin_max_pitch = np.nanmax(pitches).item()
            yin_mean_pitch = np.nanmean(pitches).item()
            yin_median_pitch = np.nanmedian(pitches).item()
            return {
                'min_pitch_yin': yin_min_pitch,
                'max_pitch_yin': yin_max_pitch,
                'mean_pitch_yin': yin_mean_pitch,
                'median_pitch_yin': yin_median_pitch,
                'pitches_yin': pitches_full.tolist()
            }

        except Exception as e:
            print(e)
            return {
                'min_pitch_yin': "Measure Pitch Yin Failed",
                'max_pitch_yin': "Measure Pitch Yin Failed",
                'mean_pitch_yin': "Measure Pitch Yin Failed",
                'median_pitch_yin': "Measure Pitch Yin Failed",
                'pitches_yin': "Measure Pitch Yin Failed",
            }