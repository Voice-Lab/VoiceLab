import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
from sklearn.impute import SimpleImputer
import sys
import os

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

from PyQt5.QtWidgets import QMessageBox


class ManipulateTruncateSoundsNode(VoicelabNode):
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "Trim silences": True,
            "Silence Ratio": 10,
            "Trim sound": True,
            "Percent to trim from each end": 10
        }


    def process(self):
        self.sound = self.args["voice"]
        if self.args["Trim silences"]:
            try:
                self.sound = self.trim_silences()
            except:
                self.args["Trim silences"] = False

        if self.args["Trim sound"]:
            try:
                self.sound = self.trim_sound()
            except:
                self.args["Trim sound"] = False

        self.sound.name = self.get_output_file_name()
        self.sound.save(self.sound.name, "WAV")
        return {"voice": self.sound,
                "Trim Sound": True}

    def get_output_file_name(self):
        filename = self.args["file_path"]
        base_filename = os.path.basename(filename)
        no_extension_filename = os.path.splitext(base_filename)[0]
        suffix = '_trimmed'
        if self.args["Trim silences"]:
            suffix += f"_silences_{self.args['Silence Ratio']}"
        if self.args["Trim sound"]:
            suffix += f"_sound_{(self.args['Percent to trim from each end'] / 100)}"
        new_filename = ''.join([no_extension_filename, suffix])
        return new_filename


    def trim_silences(self):
        """Saves out the loudest 90% of the sound"""
        intensity = self.sound.to_intensity(50)
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
                [self.sound, intensity_textgrid], "Extract all intervals", 1, "yes"
            )
        else:
            trimmed_sound = self.sound
        return trimmed_sound

    def trim_sound(self):
        start = self.sound.duration * (self.args['Percent to trim from each end'] / 100)
        end = self.sound.duration * (1 - (self.args['Percent to trim from each end'] / 100))
        trimmed_sound = call(self.sound, "Extract part", start, end, 'rectangular', 1.0, 'no')
        return trimmed_sound