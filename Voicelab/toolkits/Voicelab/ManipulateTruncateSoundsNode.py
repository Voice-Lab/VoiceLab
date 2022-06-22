import pandas as pd
import numpy as np
import os

from Voicelab.pipeline.Node import Node
import parselmouth
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

from PyQt5.QtWidgets import QMessageBox


class ManipulateTruncateSoundsNode(VoicelabNode):
    """Manipulate raise pitch and formants

    Arguments
    ----------
    self.args : dict
        Arguments for the node
        self.args["Trim silences"]: bool, default=True
            Trim silences
        self.args["Silence Ratio"]: int, float, default=10.0
            Silence ratio is the ratio of how loud a silence should be relative to the rest of the sound
        self.args["Trim sound"]: bool, default=True
            Trim sound
        self.args["Percent to trim from each end"]: int, float, default=10.0
            Percent of total sound duration to trim from each end
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
            "Trim silences": True,
            "Silence Ratio": 10.0,
            "Trim sound": True,
            "Percent to trim from each end": 10.0
        }


    def process(self):
        """Truncate the sound(s)

        :return: Dictionary of manipulated sound
        :rtype:  dict of [str, parselmouth.Sound]
        """
        filename: str = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        if self.args["Trim silences"]:
            try:
                sound = self.trim_silences(filename)
            except:
                self.args["Trim silences"] = False

        if self.args["Trim sound"]:
            try:
                sound: parselmouth.Sound = self.trim_sound(filename)
            except:
                self.args["Trim sound"] = False

        sound.name = self.get_output_file_name(filename)
        sound.save(sound.name, "WAV")
        return {"voice": sound,
                "Trim Sound": True}

    def get_output_file_name(self, filename: str) -> str:
        """Get the output file name

        :arg filename: The input file name
        :type filename: str

        :return: The output file name
        :rtype: str
        """
        base_filename = os.path.basename(filename)
        no_extension_filename = os.path.splitext(base_filename)[0]
        suffix = '_trimmed'
        if self.args["Trim silences"]:
            suffix += f"_silences_{self.args['Silence Ratio']}"
        if self.args["Trim sound"]:
            suffix += f"_sound_{(self.args['Percent to trim from each end'] / 100)}"
        new_filename = ''.join([no_extension_filename, suffix])
        return new_filename


    def trim_silences(self, filename: str) -> parselmouth.Sound:
        """Saves out the loudest 90% of the sound

        :arg filename: The input file name
        :type filename: str

        :return: Trimmed sound object
        :rtype: parselmouth.Sound
        """
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        intensity = sound.to_intensity(50)
        if (intensity.get_maximum() - intensity.get_minimum()) > 10:
            proportion_intensity = (
                    (intensity.get_maximum() - intensity.get_minimum())
                    * -self.args["Silence Ratio"]
                    / 100
            )
            intensity_textgrid = call(
                intensity,
                "To TextGrid (silences)",
                proportion_intensity,
                0.1,
                0.05,
                "silent",
                "sounding",
            )
            _, trimmed_sound, _ = call(
                [sound, intensity_textgrid], "Extract all intervals", 1, "yes"
            )
        else:
            trimmed_sound = sound
        return trimmed_sound

    def trim_sound(self, filename: str) -> parselmouth.Sound:
        """Trim the sound

        :arg filename: The input file name
        :type filename: str

        :return: Trimmed sound object
        :rtype: parselmouth.Sound
        """
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        start = sound.duration * (self.args['Percent to trim from each end'] / 100)
        end = sound.duration * (1 - (self.args['Percent to trim from each end'] / 100))
        trimmed_sound = call(sound, "Extract part", start, end, 'rectangular', 1.0, 'no')
        return trimmed_sound
