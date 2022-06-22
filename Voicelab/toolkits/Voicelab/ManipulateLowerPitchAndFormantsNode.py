from __future__ import annotations

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from typing import Union
import parselmouth


class ManipulateLowerPitchAndFormantsNode(VoicelabNode):
    """Manipulate lower pitch and formants

    Arguments
    ----------
    self.args : dict
        Arguments for the node
        self.args['formant_factor'] : float, default=0.85
            Factor to multiply formants by. Use a nunber between 0 and 1. For higher values, use ManipulateHigherPitchAndFormantsNode
        self.args['pitch_factor'] : float
            Factor to multiply pitch by
        self.args['normalize amplitude'] : bool, default=True
            Normalize amplitude to 70 dB RMS
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
                     "formant_factor": 0.85,
                     "pitch_factor":   0.85,
                     "normalize amplitude": True,
                     }

        # These are default settings for praat that we are hiding from the GUI and API
        self.pitch_range_factor = 1
        self.duration_factor = 1

    def process(self) -> dict[str, Union[str, parselmouth.Sound]]:
        """Lower pitch and formants

        :return: Dictionary of manipulated sound
        :rtype:  dict of [str, parselmouth.Sound]
        """

        file_path: str = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        pitch_range_factor: Union[int, float] = self.pitch_range_factor
        duration_factor: Union[int, float] = self.duration_factor
        formant_factor: Union[int, float] = self.args["formant_factor"]
        pitch_factor: Union[int, float] = self.args["pitch_factor"]
        duration: Union[int, float] = sound.get_total_duration()
        self.args['f0min'], self.args['f0max'] = self.pitch_bounds(file_path)
        f0min, f0max = self.args['f0min'], self.args['f0max']
        normalize_amplitude: bool = self.args["normalize amplitude"]

        pitch: parselmouth.Data = sound.to_pitch(pitch_floor=f0min, pitch_ceiling=f0max)
        median_pitch: float = call(pitch, "Get quantile", 0, duration, 0.5, "Hertz")

        new_pitch_median: Union[int, float] = pitch_factor * median_pitch

        output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
        output_file_name: str = (
            f"{output_file_name}_lower_pitch_and_formants_{pitch_factor}_{formant_factor}"
        )
        number_of_channels: Union[int, float] = call(sound, 'Get number of channels')
        if number_of_channels == 2:
            sound = call(sound, 'Convert to mono')

        manipulated_sound: parselmouth.Sound = call(
            sound,
            "Change gender",
            f0min,
            f0max,
            formant_factor,
            new_pitch_median,
            pitch_range_factor,
            duration_factor,
        )

        if normalize_amplitude:
            manipulated_sound.scale_intensity(70)

        manipulated_sound.name = output_file_name

        return {"voice": manipulated_sound}
