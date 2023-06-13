from __future__ import annotations

from ...pipeline.Node import Node
from parselmouth.praat import call
import parselmouth
from .VoicelabNode import VoicelabNode

from typing import Union


class ManipulateLowerFormantsNode(VoicelabNode):
    """Manipulate all of the formants of a voice to be lower.

    Attributes:
    -----------
    self.args: dict
        Dictionary of arguments for the node.

        self.args{'formant_shift_ratio'} (float, default=0.85):
            The amount of formant shift to apply. 0-1 than one makes lower formants.  Greater than 1 makes higher formants.
            It's recommended to use a number between 0 and 1, and if you want to raise formants, use the raise formants node instead to avoid confusion.

        self.args{'normalize amplitude'} (bool, default=True):
            If true, the amplitude of the manipulated voice will be normalized to 70dB RMS.  Default is True.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize with default arguments
        self.args: dict[str | Union[int, float], str | bool] = {
            "formant_shift_ratio": 0.85,
            "normalize amplitude": True
        }

        # These are default arguments from Praat's Change Gender Function
        # We don't want the user to adjust them, so they're hidden from the GUI and API
        self.new_pitch_median = 0
        self.pitch_range_factor = 1
        self.duration_factor = 1

    def process(self) -> dict[Union[str, parselmouth.Sound]]:
        """Lower all formants of the voice.

        Attributes:
        -----------
            self.args{'formant_shift_ratio'} (float, default=0.85):
                The amount of formant shift to apply. 0-1 than one makes lower formants.  Greater than 1 makes higher formants.
                It's recommended to use a number between 0 and 1, and if you want to raise formants, use the raise formants node instead to avoid confusion.
            self.args{'formant_shift_ratio'} (float, default=0.85):



        :return: Manipulated parselmouth.Sound object.
        :rtype: manipulated_voice: parselmouth.Sound

        """

        # get the arguments
        normalize_amplitude: bool = self.args['normalize amplitude']
        file_path: str = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        #sound: parselmouth.Sound = parselmouth.Sound(file_path)
        formant_shift_ratio: Union[int, float] = self.args["formant_shift_ratio"]
        new_pitch_median: Union[int, float] = self.new_pitch_median
        pitch_range_factor: Union[int, float] = self.pitch_range_factor
        duration_factor: Union[int, float] = self.duration_factor

        try:
            f0min: Union[float, int]
            f0max: Union[float, int]
            f0min, f0max = self.pitch_bounds(file_path)

            output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
            output_file_name: str = (
                f"{output_file_name}_manipulate_formants_{formant_shift_ratio}"
            )
            number_of_channels: Union[float, int] = call(sound, 'Get number of channels')
            if number_of_channels == 2:
                sound: parselmouth.Sound = call(sound, 'Convert to mono')

            manipulated_sound: parselmouth.Sound = call(sound, "Change gender", f0min, f0max, formant_shift_ratio,
                                                        new_pitch_median, pitch_range_factor, duration_factor,)
            if normalize_amplitude:
                manipulated_sound.scale_intensity(70)

            manipulated_sound.name = output_file_name

            return {"voice": manipulated_sound}
        except Exception as e:
            return {"voice": str(e)}
