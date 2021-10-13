from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from parselmouth.praat import call
import parselmouth

import numpy as np
from scipy.io.wavfile import read as wavread
from scipy.signal import resample
import statistics
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

        }

    def process(self):
        try:
            audioFilePath = self.args["file_path"]
            sr, sig = wavread(audioFilePath)
            if sr != 22500:
                sr = 22500
            sig = resample(sig, sr)

            pitches, voiced_flag, voiced_probs = librosa.pyin(sig, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))  # recommended settings from docs are bad, need to figure out good ones
            #pitches = pitches[pitches != 0]
            yin_min_pitch = np.nanmin(pitches).item()
            yin_max_pitch = np.nanmax(pitches).item()
            yin_mean_pitch = np.nanmean(pitches).item()
            yin_median_pitch = np.nanmedian(pitches).item()
            print("yin_median_pitch")
            print("yin pitches", pitches)
            return {'min_pitch_yin': yin_min_pitch,
                    'max_pitch_yin': yin_max_pitch,
                    'mean_pitch_yin': yin_mean_pitch,
                    'median_pitch_yin': yin_median_pitch,
            }
        except Exception as e:
            print(e)
            return {'min_pitch_yin': "Measure Pitch Yin Failed",
                    'max_pitch_yin': "Measure Pitch Yin Failed",
                    'mean_pitch_yin': "Measure Pitch Yin Failed",
                    'median_pitch_yin': "Measure Pitch Yin Failed",
            }