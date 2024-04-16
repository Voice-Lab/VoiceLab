from __future__ import annotations

import parselmouth
from parselmouth.praat import call
from typing import Union
from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode



class ManipulateRaiseFormantsNode(VoicelabNode):
    """Manipulate all of the formants of a voice to be lower.

    Attributes:
    -----------
    self.args: dict
        Dictionary of arguments for the node.

        self.args{'formant_shift_ratio'} (float, default=1.15):
            The amount of formant shift to apply. >1 makes higher formants.  Less than 1 makes lower formants.
            It's recommended to use a number > 1, and if you want to lower formants, use the lower formants node instead to avoid confusion.

        self.args{'normalize amplitude'} (bool, default=True):
            If true, the amplitude of the manipulated voice will be normalized to 70dB RMS.  Default is True.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize with default arguments
        self.args: dict[str | Union[float, int], str | bool] = {
            'formant_shift_ratio': 1.15,
            'normalize amplitude': True,
        }

        # These are default arguments from Praat's Change Gender Function
        # We don't want the user to adjust them, so they're hidden from the GUI and API
        self.new_pitch_median: Union[int, float] = 0
        self.pitch_range_factor: Union[int, float] = 1
        self.duration_factor: Union[int, float] = 1

    def process(self) -> dict[Union[str, parselmouth.Sound]]:
        """Raise all formants of the voice.

        Attributes:
        -----------
            self.args{'formant_shift_ratio'} (float, default=0.1.15):
                The amount of formant shift to apply. 0-1 than one makes lower formants.  Greater than 1 makes higher formants.
                It's recommended to use a number between 0 and 1, and if you want to raise formants, use the raise formants node instead to avoid confusion.
            self.args{'normalize amplitude'} (bool, default=True):
                If true, the amplitude of the manipulated voice will be normalized to 70dB RMS.  Default is True.


        :return: Manipulated parselmouth.Sound object.
        :rtype: manipulated_voice: parselmouth.Sound
        """
        # get the arguments
        normalize_amplitude: bool = self.args['normalize amplitude']
        file_path: str = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        formant_shift_ratio: Union[int, float] = self.args["formant_shift_ratio"]
        new_pitch_median: Union[int, float] = self.new_pitch_median
        pitch_range_factor: Union[int, float] = self.pitch_range_factor
        duration_factor: Union[int, float] = self.duration_factor

        f0min: Union[int, float]
        f0max: Union[int, float]
        f0min, f0max = self.pitch_bounds(file_path)

        output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
        output_file_name: str = (
            f"{output_file_name}_manipulate_formants_{formant_shift_ratio}"
        )
        number_of_channels: Union[int, float] = call(sound, 'Get number of channels')
        if number_of_channels == 2:
            sound: parselmouth.Sound = call(sound, 'Convert to mono')
        manipulated_sound: parselmouth.Sound = call(
            sound,
            "Change gender",
            f0min,
            f0max,
            formant_shift_ratio,
            new_pitch_median,
            pitch_range_factor,
            duration_factor,
        )

        if normalize_amplitude:
            manipulated_sound.scale_intensity(70)

        manipulated_sound.name = output_file_name

        return {"voice": manipulated_sound}
