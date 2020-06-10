from Voicelab.pipeline.Node import Node
import numpy as np
import seaborn as sns
import parselmouth
from parselmouth.praat import call
import matplotlib.pyplot as plt

from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

###################################################################################################
# VISUALIZE VOICE NODE
# WARIO pipeline node for visualizing a voice as a spectrogram.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
###################################################################################################
# RETURNS
###################################################################################################


class VisualizeVoiceNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)


        self.args = {
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

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################

    def process(self):
        from pprint import pprint
        pprint(self.args)
        voice = self.args["voice"]
        window_length = self.args["window_length"]
        colour_map = self.args["colour_map"]
        plot_intensity = self.args["Plot Intensity"]
        plot_formants = self.args["Plot Formants"]
        plot_pitch = self.args["Plot Pitch"]

        pad_distance = 10

        fig = plt.figure()

        ax = fig.add_axes([0.2, 0.2, 0.6, 0.6])

        if isinstance(colour_map, tuple):
            colour_map = colour_map[0]

        pre_emphasized_voice = voice.copy()
        pre_emphasized_voice.pre_emphasize()

        spectrogram = pre_emphasized_voice.to_spectrogram(
            window_length=window_length, maximum_frequency=8000
        )
        x, y = spectrogram.x_grid(), spectrogram.y_grid()

        sg_db = 10 * np.log10(spectrogram.values)
        vgmin_value = sg_db.max() - 70
        ax.pcolormesh(x, y, sg_db, vmin=vgmin_value, cmap=colour_map)
        ax.set_ylim([spectrogram.ymin, spectrogram.ymax])
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Frequency [Hz]")

        ax.yaxis.label.set_color("w")
        ax.set_xlim([self.args["voice"].xmin, self.args["voice"].xmax])

        # if we have selected to plot intensity and an intensity value has been provided
        if plot_intensity and "Intensity" in self.args:
            #intensity = self.args["Intensity"]
            intensity = voice.to_intensity()
            intensity_axis = ax.twinx()
            self.plot_intensity(intensity_axis, intensity, pad_distance)
            del self.args["Intensity"]
            pad_distance = pad_distance + 30

        # if we have selected to plot formants and a formants value has been provided
        if plot_formants and "Formants" in self.args:
            #formants = self.args["Formants"]
            formants = voice.to_formant_burg()
            formants_axis = ax.twinx()
            self.plot_formants(formants_axis, formants, voice)
            del self.args["Formants"]

        # if we have selected to plot pitch and a pitch value has been provided
        if plot_pitch and "Pitch" in self.args:
            #pitch = self.args["Pitch"]
            pitch = voice.to_pitch()
            pitch_axis = ax.twinx()
            self.plot_pitch(pitch_axis, pitch, voice, pad_distance)
            del self.args["Pitch"]

        # fig.show()

        return {"figure": fig}


    def plot_intensity(self, axis, intensity, pad_distance):
        """
        Args:
            axis:
            intensity:
            pad_distance:
        """
        axis.tick_params(axis="y", pad=pad_distance, colors="g")
        axis.plot(intensity.xs(), intensity.values.T, linewidth=3, color="k")
        axis.plot(intensity.xs(), intensity.values.T, linewidth=2, color="w")
        axis.plot(intensity.xs(), intensity.values.T, linewidth=1, color="g")
        axis.grid(False)
        plt.ylim(50)
        axis.set_ylabel("Intensity [dB]", color="g")
        # axis.yaxis.label.set_color('g')

    def plot_pitch(self, axis, pitch, voice, pad_distance):
        """
        Args:
            axis:
            pitch:
            voice:
            pad_distance:
        """
        axis.tick_params(axis="y", pad=pad_distance, colors="b")
        # axis.yaxis.labelpad = 50

        pitch_values = pitch.selected_array["frequency"]
        intensity = voice.to_intensity()
        sample_times = pitch.xs()

        for i, time in enumerate(sample_times):
            intensity.values.T[intensity.values.T < 50] = np.nan
            intensity_value = call(intensity, "Get value at time", time, "cubic")
            if intensity_value < 50:
                pitch_values[i] = 0

        pitch_values[pitch_values == 0] = np.nan
        axis.plot(pitch.xs(), pitch_values, linestyle="-", color="k", linewidth=6)
        axis.plot(pitch.xs(), pitch_values, linestyle="-", color="w", linewidth=5)
        axis.plot(pitch.xs(), pitch_values, linestyle="-", color="b", linewidth=4)
        axis.grid(False)
        pitch_max = 500
        axis.set_ylim(0, pitch_max)
        axis.set_ylabel("Fundamental frequency [Hz]")
        axis.yaxis.label.set_color("b")

    def plot_formants(self, axis, formants, voice):
        """
        Args:
            axis:
            formants:
            voice:
        """
        axis.tick_params(bottom=False, top=False, left=False, right=False)
        ylabels = axis.get_yticklabels()
        for label in ylabels:
            label.set_fontsize(0.0)

        sample_times = formants.xs()
        intensity = voice.to_intensity()
        for i in range(4):  # How many formants do you want?
            formant_values = parselmouth.praat.call(
                formants, "To Matrix", i + 1
            ).values[0, :]
            j = 0
            for time in sample_times:
                j += 1
                intensity_value = parselmouth.praat.call(
                    intensity, "Get value at time", time, "cubic"
                )
                if intensity_value < 50:
                    formant_values[j] = 0
            formant_values[formant_values == 0] = np.nan
            axis.scatter(
                sample_times, formant_values, c="w", linewidth=3, marker="o", s=1
            )
            axis.scatter(sample_times, formant_values, c="r", linewidth=1, s=1)
            axis.grid(False)