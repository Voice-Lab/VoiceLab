from ...pipeline.Node import Node
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode

import parselmouth
from typing import Union


class ReverseSoundsNode(VoicelabNode):
    """A Class to reverse voice file temporally."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {}

    def process(self) -> dict[str, Union[parselmouth.Sound, str]]:
        """Run the node\nReverse the time of the voice file.
        :return: The reversed sound file or an error message
        :rtype: dict of {str, [parselmouth.Sound, str]}
        """

        try:
            file_path = self.args['file_path']
            """The path to the file to be reversed"""
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)

            """The parselmouth sound object to be reversed"""
            sound.reverse()
            output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
            """The output file name"""
            output_file_name:str = f"{output_file_name}_reversed"
            sound.name = output_file_name
        except Exception as e:
            sound = str(e)
        return {"voice": sound}
