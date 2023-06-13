from __future__ import annotations

import numpy as np
import parselmouth
from parselmouth.praat import call

from ...pipeline.Node import Node


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

    def hz_to_mel(self, hz):
        return float(parselmouth.praat.call("Calculator", "hertzToMel({})".format(hz)))

    def mel_to_hz(self, mel):
        return float(parselmouth.praat.call("Calculator", "melToHertz({})".format(mel)))

    def hz_to_bark(self, hz):
        return float(parselmouth.praat.call("Calculator", "hertzToBark({})".format(hz)))

    def bark_to_hz(self, bark):
        return float(parselmouth.praat.call("Calculator", "barkToHertz({})".format(bark)))

    def hz_to_erbs(self, hz):
        return float(parselmouth.praat.call("Calculator", "hertzToERBs({})".format(hz)))

    def erbs_to_hz(self, erbs):
        return float(parselmouth.praat.call("Calculator", "ERBsToHertz({})".format(erbs)))

    def hz_to_semitones_re_0(self, hz):
        return float(parselmouth.praat.call("Calculator", "hertzToSemitonesRe1Hz({})".format(hz)))

    def semitones_re_0_to_hz(self, semitones):
        return float(parselmouth.praat.call("Calculator", "semitonesRe1HzToHertz({})".format(semitones)))

    def dB_to_pa(self, dB):
        return 10 ** (np.abs(dB) / 20)

    def pa_to_dB(self, dB):
        return 20 * np.log10(dB)


    #def hz_to_bark(self, hertz):
    #    """Convert Herts to Bark

    #    :parameter hertz: Frequency in Hz
    #    :type hertz: Union[float, int]

    #    :returns bark: The Frequency in Bark
    #    :rtype bark: float
    #    """
    #    bark = 7.0 * np.log(hertz / 650 + np.sqrt(1 + (hertz / 650) ** 2))
    #    return bark

    def round_half_away_from_zero(self, x) -> np.int_:
        """Rounds a number according to round half away from zero method

        :argument x: number to round
        :type x: Union[float, int]
        :return: rounded number
        :rtype: np.int_


        For example:
           - round_half_away_from_zero(3.5) = 4
           - round_half_away_from_zero(3.2) = 3
           - round_half_away_from_zero(-2.7) = -3
           - round_half_away_from_zero(-4.3) = -4

        The reason for writing our own rounding function is that NumPy uses the round-half-to-even method. There is a Python round() function, but it doesn't work on NumPy vectors. So we wrote our own round-half-away-from-zero method here.
        """
        q: np.int_ = np.int_(np.sign(x) * np.floor(np.abs(x) + 0.5))

        return q

