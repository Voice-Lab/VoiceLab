from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


import crepe
import os
import pandas as pd
import parselmouth
from scipy.io import wavfile
from parselmouth.praat import call

class MeasurePitchCrepeNode(VoicelabNode):

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
            voice = self.args["voice"]
            voice.save("tmp.wav", "WAV")
            filename = "tmp.wav"
            sr, audio = wavfile.read(filename)
            time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)
            data = (list(zip(time, frequency, confidence)))
            df = pd.DataFrame(data, columns=["time", "frequency", "confidence"])
            pitch_data = df[df.confidence > 0.7]
            mean_pitch = pitch_data.frequency.mean().item()
            min_pitch = pitch_data.frequency.min().item()
            max_pitch = pitch_data.frequency.max().item()
            stdev_pitch = pitch_data.frequency.std().item()
            os.remove("tmp.wav")
            return{
                "Mean Pitch Crepe": mean_pitch,
                "Minimum Pitch Crepe": min_pitch,
                "Maximum Pitch Crepe": max_pitch,
                "Standard Deviation Pitch Crepe": stdev_pitch,
            }
        except:
            return{
                "Mean Pitch Crepe": "Measure Crepe Failed",
                "Minimum Pitch Crepe": "Measure Crepe Failed",
                "Maximum Pitch Crepe": "Measure Crepe Failed",
                "Standard Deviation Pitch Crepe": "Measure Crepe Failed",
            }
