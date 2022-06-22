from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import parselmouth
from parselmouth.praat import call

from typing import Union

from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class VisualizeVoiceNode(VoicelabNode):
    """Create a spectrogram with optional overlays of Pitch, Amplitude, and Formant Frequencies.

    Attributes
    ----------

    self.show_figure': bool, default=True
        Whether to show the figure

    self.args: dict of parameters to be passed into the node
        self.args['window_length']: float, default=0.05
            The window length for the spectrogram analysis
        self.args['colour_map']: str, default = 'afmhot'
            Which matplotlib colour map to use. Watch out for the British/Canadian spelling.
        self.args["Plot Intensity"]: bool, default=True
            Whether to plot intensity
        self.args ["Plot Formants"]: bool, default=True
            Whether to plot formants
        self.args["Plot Pitch"]: bool, default=True
            Whether to plot pitch

    self.fontsize: int, default=16
        The font size for text in the plot
    """

    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.show_figure: bool = True
        self.args: dict = {
            "window_length": 0.05,  # Positive number
            "colour_map": (
                "afmhot",
                [
                    "binary",
                    "gist_yarg",
                    "gist_gray",
                    "gray",
                    "bone",
                    "pink",
                    "spring",
                    "summer",
                    "autumn",
                    "winter",
                    "cool",
                    "Wistia",
                    "hot",
                    "afmhot",
                    "gist_heat",
                    "copper",
                ],
            ),
            "Plot Intensity": True,
            "Plot Formants": True,
            "Plot Pitch": True,
        }

        self.fontsize: int = 16

    def process(self) -> dict[str: plt.Figure]:
        """Create the spectrogram plot

        :return: dict of the matplotlib figure object
        :rtype: dict of str | union[plt.figure, str]
        """
        file_path: str = self.args['file_path']
        #voice: parselmouth.Sound = parselmouth.Sound(file_path)
        signal, sampling_rate = self.args['voice']
        voice: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        window_length: float = self.args["window_length"]
        colour_map: Union[str, tuple] = self.args["colour_map"]
        plot_intensity: bool = self.args["Plot Intensity"]
        plot_formants: bool = self.args["Plot Formants"]
        plot_pitch: bool = self.args["Plot Pitch"]

        pad_distance: int = 10
        fig: plt.Figure = plt.figure()
        ax: plt.Axes = fig.add_axes([0.2, 0.2, 0.6, 0.6])

        if isinstance(colour_map, tuple):
            colour_map = colour_map[0]

        pre_emphasized_voice: parselmouth.Sound = voice.copy()
        pre_emphasized_voice.pre_emphasize()

        spectrogram: parselmouth.Spectrogram = pre_emphasized_voice.to_spectrogram(
            window_length=window_length, maximum_frequency=8000
        )
        x: np.ndarray
        y: np.ndarray
        x, y = spectrogram.x_grid(), spectrogram.y_grid()

        sg_db: np.ndarray = 10 * np.log10(spectrogram.values)
        vgmin_value: np.float64 = sg_db.max() - 50
        ax.pcolormesh(x, y, sg_db, vmin=vgmin_value, cmap=colour_map)
        ax.set_ylim([spectrogram.ymin, spectrogram.ymax])
        ax.set_xlabel("Time [s]", fontsize=16)
        ax.set_ylabel("Frequency [Hz]", fontsize=self.fontsize)
        plt.setp(ax.get_xticklabels(), fontsize=self.fontsize)
        plt.setp(ax.get_yticklabels(), fontsize=self.fontsize)
        #ax.yaxis.label.set_color("w")
        ax.set_xlim([voice.xmin, voice.xmax])

        # if we have selected to plot intensity and an intensity value has been provided
        if plot_intensity and "Intensity" in self.args:
            #intensity = self.args["Intensity"]
            intensity: parselmouth.Intensity = voice.to_intensity()
            intensity_axis: plt.Axes = ax.twinx()
            self.plot_intensity(intensity_axis, intensity, pad_distance)
            plt.ylim(0, round(intensity.values.max()))
            intensity_axis.set_xlabel("Intensity (dB)", fontsize=self.fontsize)
            plt.setp(intensity_axis.get_xticklabels(), fontsize=self.fontsize)
            plt.setp(intensity_axis.get_yticklabels(), fontsize=self.fontsize)
            del self.args["Intensity"]
            pad_distance = pad_distance + 30

        # if we have selected to plot formants and a formants value has been provided
        if plot_formants and "Formants" in self.args:
            formants: parselmouth.Formant = self.args["Formants"]
            self.formants_axis: plt.Axes = ax.twinx()
            self.plot_formants(self.formants_axis, formants)
            del self.args["Formants"]

        # if we have selected to plot pitch and a pitch value has been provided
        if plot_pitch and "Pitch" in self.args:
            pitch: parselmouth.Pitch = self.args["Pitch"]
            #pitch = voice.to_pitch()
            pitch_axis: plt.Axes = ax.twinx()
            adjustment: Union[float, int] = 0
            if self.args['Plot Intensity']:
                adjustment = 30
            self.plot_pitch(pitch_axis, pitch, pad_distance+adjustment)
            plt.setp(pitch_axis.get_xticklabels(), fontsize=self.fontsize)
            plt.setp(pitch_axis.get_yticklabels(), fontsize=self.fontsize)
            del self.args["Pitch"]
        return {"figure": fig}

    def plot_intensity(self, axis, intensity, pad_distance):
        """Plot the intensity on the spectrogram

            :argument axis: a matplotlib axis object
            :type axis: plt.axis

            :argument intensity: The parselmouth Intensity object
            :type intensity: parselmouth.Intensity

            :pad_distance: how many pixels to pad the intensity y-axis label
            :type pad_distance: int
        """
        axis.tick_params(axis="y", pad=pad_distance, colors="g")
        axis.plot(intensity.xs(), intensity.values.T, linewidth=3, color="k")
        axis.plot(intensity.xs(), intensity.values.T, linewidth=2, color="w")
        axis.plot(intensity.xs(), intensity.values.T, linewidth=1, color="g")
        axis.grid(False)
        plt.ylim(50)
        axis.set_ylabel("Intensity [dB]", color="g", fontsize=self.fontsize)
        # axis.yaxis.label.set_color('g')

    def plot_pitch(self, axis, pitch, pad_distance):
        """Plot pitch on the spectrogram
        :argument axis: a matplotlib axis object
        :type axis: plt.axis

        :argument pitch: The parselmouth Intensity object
        :type intensity: parselmouth.Intensity

        :argument voice: The parselmouth Sound object
        :type intensity: parselmouth.Sound

        :pad_distance: how many pixels to pad the pitch y-axis label, this is automatically adjusted if intensity is also displayed
        :type pad_distance: int
        """
        axis.tick_params(axis="y", pad=pad_distance, colors="b")

        signal, sampling_rate = self.args['voice']
        voice: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        pitch_values: np.ndarray = pitch.selected_array["frequency"]
        intensity: parselmouth.Intensity= voice.to_intensity()
        sample_times: np.ndarray = pitch.xs()

        for i, time in enumerate(sample_times):
            intensity.values.T[intensity.values.T < 50] = np.nan
            intensity_value: float = call(intensity, "Get value at time", time, "cubic")
            if intensity_value < 50:
                pitch_values[i] = 0

        pitch_values[pitch_values == 0] = np.nan
        axis.plot(pitch.xs(), pitch_values, linestyle="-", color="k", linewidth=6)
        axis.plot(pitch.xs(), pitch_values, linestyle="-", color="w", linewidth=5)
        axis.plot(pitch.xs(), pitch_values, linestyle="-", color="b", linewidth=4)
        axis.grid(False)
        pitch_max: int = 500
        axis.set_ylim(0, pitch_max)
        axis.set_ylabel("Fundamental frequency [Hz]", fontsize=self.fontsize)
        axis.yaxis.label.set_color("b")

    def plot_formants(self, axis, formants):
        """Plot formants on the spectrogram

        :argument axis: a matplotlib axis object
        :type axis: plt.axis

        :argument formants: The parselmouth Intensity object
        :type formants: parselmouth.Intensity

        :argument voice: The parselmouth Sound object
        :type intensity: parselmouth.Sound
        """
        signal, sampling_rate = self.args['voice']
        voice: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        axis.tick_params(bottom=False, top=False, left=False, right=False)
        ylabels: list = axis.get_yticklabels()
        for label in ylabels:
            label.set_fontsize(0.0)

        sample_times: np.ndarray = formants.xs()
        intensity: parselmouth.Intensity = voice.to_intensity()
        for i in range(4):  # How many formants do you want?
            formant_values: np.ndarray = parselmouth.praat.call(
                formants, "To Matrix", i + 1
            ).values[0, :]
            j = 0
            for time in sample_times:
                j += 1
                intensity_value: float = parselmouth.praat.call(
                    intensity, "Get value at time", time, "cubic"
                )
                if intensity_value < 50:
                    formant_values[j] = 0
            formant_values[formant_values == 0] = np.nan
            axis.scatter(
                sample_times, formant_values, c="w", linewidth=3, marker="o", s=1
            )
            axis.scatter(sample_times, formant_values, c="r", linewidth=1, s=1)
            axis.set_ylim(0, 8000)
            axis.grid(False)
