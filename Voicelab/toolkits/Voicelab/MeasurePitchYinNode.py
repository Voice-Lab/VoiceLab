from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from parselmouth.praat import call
import parselmouth
import inspect
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

    def process(self, audioFilePath=None, *args, **kwargs):
        try:
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
            yin_standard_deviation_pitch = np.nanstd(pitches).item()
            return {
                'Min Pitch (Yin)': yin_min_pitch,
                'Max Pitch (Yin)': yin_max_pitch,
                'Mean Pitch (Yin)': yin_mean_pitch,
                'Median Pitch (Yin)': yin_median_pitch,
                'Standard Deviation Pitch (Yin)': yin_standard_deviation_pitch,
                'Pitch Values (Yin)': pitches_full.tolist()
            }

        except Exception as e:
            return {
                'Min Pitch (Yin)': str(e),
                'Max Pitch (Yin)': str(e),
                'Mean Pitch (Yin)': str(e),
                'Median Pitch (Yin)': str(e),
                'Pitch Values (Yin)': str(e),
            }
