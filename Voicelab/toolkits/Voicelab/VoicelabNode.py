from __future__ import annotations

import numpy as np
import parselmouth
from parselmouth.praat import call

from Voicelab.pipeline.Node import Node


class VoicelabNode(Node):
    """Extends the basic node with some shared voicelab functionalities
    """
    def pitch_bounds(self, file_path):
        """Finds pitch ceiling and floor

        :param file_path: path to the file
        :type file_path: str

        :returns: tuple of pitch ceiling and pitch floor
        :rtype: tuple[float, float]
        """

        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        # sound: parselmouth.Sound = parselmouth.Sound(file_path)
        # measure pitch ceiling and floor
        
        try:
            broad_pitch: float = sound.to_pitch_ac(
            None, 50, 15, True, 0.03, 0.45, 0.01, 0.35, 0.14, 500
            )
            broad_mean_f0: float = call(broad_pitch, "Get mean", 0, 0, "hertz")  # get mean pitch
        except:
            broad_mean_f0 = 0

        if broad_mean_f0 > 170:
            pitch_floor = 100
            pitch_ceiling = 500
        elif broad_mean_f0 < 170:
            pitch_floor = 50
            pitch_ceiling = 300
        else:
            pitch_floor = 50
            pitch_ceiling = 500
        return pitch_floor, pitch_ceiling

    def pitch_floor(self, file_path):
        """ Returns the pitch floor
        :param file_path: path to the file
        :type file_path: str

        :returns: pitch floor
        :rtype: float
        """
        #sound: parselmouth.Sound = parselmouth.Sound(file_path)
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        return self.pitch_bounds(file_path)[0]

    def pitch_ceiling(self, file_path):
        """ Returns the pitch ceiling
        :param file_path: path to the file
        :type file_path: str

        :returns: pitch floor
        :rtype: float
        """
        #sound: parselmouth.Sound = parselmouth.Sound(file_path)
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        return self.pitch_bounds(file_path)[1]

    def max_formant(self, file_path, method="praat_manual"):
        """Find the best maximum formant frequency for formant analysis based on voice pitch.

        :param file_path: path to the file
        :type file_path: str
        :param method: method to use for finding the maximum formant frequency, default is praat_manual
        :type method: str

        :returns: maximum formant frequency
        :rtype: float
        """
        try:
            #sound: parselmouth.Sound = parselmouth.Sound(file_path)
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            if method == "praat_manual":
                pitch: parselmouth.Pitch = sound.to_pitch(None, 50, 600)  # check pitch to set formant settings
                mean_f0: float = call(pitch, "Get mean", 0, 0, "Hertz")
                max_formant: float
                if 170 <= mean_f0 <= 300:
                    max_formant = 5500
                elif mean_f0 < 170:
                    max_formant = 5000
                else:
                    max_formant = 5500
                return max_formant
            else:
                max_formant = 5500
        except:
            max_formant = 5500
        return max_formant

    def hz_to_bark(self, hertz):
        """Convert Herts to Bark

        :parameter hertz: Frequency in Hz
        :type hertz: Union[float, int]

        :returns bark: The Frequency in Bark
        :rtype bark: float
        """
        bark = 7.0 * np.log(hertz / 650 + np.sqrt(1 + (hertz / 650) ** 2))
        return bark


