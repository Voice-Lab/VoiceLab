from __future__ import annotations

import parselmouth
from parselmouth.praat import call
from typing import Union
from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class ManipulateRaisePitchAndFormantsNode(VoicelabNode):
    """Manipulate raise pitch and formants

    Arguments
    ----------
    self.args : dict
        Arguments for the node
        self.args['formant_factor'] : float, default=1.15
            Factor to multiply formants by. Use a number >1. For lower values, use ManipulateLowerPitchAndFormantsNode
        self.args['pitch_factor'] : float
            Factor to multiply pitch by
        self.args['normalize amplitude'] : bool, default=True
            Normalize amplitude to 70 dB RMS
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
                     "formant_factor": 1.15,
                     "pitch_factor":   1.15,
                     "normalize amplitude": True,
                     }

        # These are default settings for praat that we are hiding from the GUI and API
        self.pitch_range_factor = 1
        self.duration_factor = 1

    def process(self) -> dict[Union[str, parselmouth.Sound]]:
        """Raise pitch and formants

        :return: Dictionary of manipulated sound
        :rtype:  dict of [str, parselmouth.Sound]
        """

        file_path = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        formant_factor = self.args["formant_factor"]
        pitch_factor = self.args["pitch_factor"]
        pitch_range_factor = self.pitch_range_factor
        duration_factor = self.duration_factor
        f0min, f0max = self.pitch_bounds(file_path)
        self.args['f0min'], self.args['f0max'] = f0min, f0max
        pitch = sound.to_pitch()
        print(f0min, f0max)
        median_pitch = call(pitch, "Get quantile", sound.xmin, sound.xmax, 0.5, "Hertz")

        new_pitch_median = pitch_factor * median_pitch

        output_file_name = file_path.split("/")[-1].split(".wav")[0]
        output_file_name = (
            f"{output_file_name}_raise_pitch_and_formants_{pitch_factor}_{formant_factor}"
        )
        number_of_channels = call(sound, 'Get number of channels')
        if number_of_channels == 2:
            sound = call(sound, 'Convert to mono')

        manipulated_sound = call(
            sound,
            "Change gender",
            f0min,
            f0max,
            formant_factor,
            new_pitch_median,
            pitch_range_factor,
            duration_factor,
        )

        if self.args["normalize amplitude"]:
            manipulated_sound.scale_intensity(70)

        manipulated_sound.name = output_file_name

        return {"voice": manipulated_sound}
