from Voicelab.pipeline.Node import Node
from parselmouth.praat import call

###################################################################################################
# Extends the basic node with some shared voicelab functionalities
###################################################################################################


class VoicelabNode(Node):
    def pitch_bounds(self, sound):

        """measures the ceiling and floor for a given voice

        Args:
            sound:
        """

        # measure pitch ceiling and floor
        broad_pitch = sound.to_pitch_ac(
            None, 50, 15, True, 0.03, 0.45, 0.01, 0.35, 0.14, 500
        )
        broad_mean_f0: float = call(
            broad_pitch, "Get mean", 0, 0, "hertz"
        )  # get mean pitch

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

    def pitch_floor(self, sound):
        """
        Args:
            sound:
        """
        return self.pitch_bounds(sound)[0]

    def pitch_ceiling(self, sound):
        """
        Args:
            sound:
        """
        return self.pitch_bounds(sound)[1]

    def max_formant(self, voice, method="praat_manual"):
        """
        Args:
            voice:
            method:
        """
        if method == "praat_manual":
            pitch = voice.to_pitch(None, 50, 600)  # check pitch to set formant settings
            mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")
            if 130 <= mean_f0 <= 300:
                max_formant = 5500
            elif mean_f0 < 130:
                max_formant = 5000
            else:
                max_formant = 5500
            return max_formant
        else:
            max_formant = 5500
            return max_formant
