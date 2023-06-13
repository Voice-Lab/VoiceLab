from ...pipeline.Node import Node
import parselmouth
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode

from .MeasureFormantNode import MeasureFormantNode
from ...VoicelabGUI.VoicelabTab import VoicelabTab
from ...VoicelabGUI.F1F2PlotWindow import F1F2PlotWindow

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
import io
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import math
from numpy import random
from scipy.spatial import distance

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats


###################################################################################################
# F1F2PlotNode
# WARIO pipeline node for estimating the vocal tract of a voice.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
# 'state'   : saves formant data for each voice for processing in end method
###################################################################################################
# RETURNS   : an unnamed string to keep the pipeline running
#           : saves an image file to disk: 'f1f2.png
###################################################################################################


class F1F2PlotNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "Vowel Marker": ("Vowels", ["Vowels", "IPA Symbols", "None"]),
            "Comparison Data": (
                "Peterson & Barney 1952",
                ["Peterson & Barney 1952", "None"],
            ),
            "Scale": ("Bark", ["Bark", "Hz"]),
            "Colour Map": (
                "inferno",
                ["viridis", "plasma", "inferno", "magma", "cividis"],
            ),
            "Ellipses": (
                "My data",
                ["My data", "Peterson & Barney 1952 Data", "No ellipses"],
            ),
            "Vowel Marker": ("Vowels",
                             ["Vowels",
                              "IPA Symbols",
                              "None",
                              ]),
            "Comparison Data": ("Peterson & Barney 1952",
                                ["Peterson & Barney 1952", ]),
        }

        self.state = {
            "f1 means": [],
            "f2 means": [],
            "f3 means": [],
            "f4 means": [],
        }


    def process(self):
        #voice = self.args["voice"]
        f1 = self.args["F1 Mean"]
        f2 = self.args["F2 Mean"]
        f3 = self.args["F3 Mean"]
        f4 = self.args["F4 Mean"]

        self.state["f1 means"].append(f1)
        self.state["f2 means"].append(f2)
        self.state["f3 means"].append(f3)
        self.state["f4 means"].append(f4)
        return {}

        f1_means = self.state["f1 means"]
        f2_means = self.state["f2 means"]
        f3_means = self.state["f3 means"]
        f4_means = self.state["f4 means"]

        return {
        }


    def closest_node(self, point, points):
        closest_index = distance.cdist([point], points).argmin()
        return points[closest_index], closest_index


    def end(self, results):

        # Fix menu options
        self.vowel_marker = self.args["Vowel Marker"][0]
        self.colour_map = self.args["Colour Map"][0]
        self.scale = self.args["Scale"][0]
        self.should_we_draw_ellipses = self.args["Ellipses"][0][0].lower()

        if self.vowel_marker == "I":
            self.vowel_marker = "IPA Symbols"
        elif self.vowel_marker == "V":
            self.vowel_marker = "Vowels"
        elif self.vowel_marker == "N":
            self.vowel_marker = "None"

        if self.colour_map == "v":
            self.cmap = "viridis"
        elif self.colour_map == "p":
            self.cmap = "plasma"
        elif self.colour_map == "i":
            self.cmap = "inferno"
        elif self.colour_map == "m":
            self.cmap = "magma"
        elif self.colour_map == "c":
            self.cmap = "cividis"
        else:
            self.cmap = self.colour_map

        # create the plot
        fig, ax_kwargs = plt.subplots()
        ax_kwargs.axvline(c="grey", lw=1)
        ax_kwargs.axhline(c="grey", lw=1)

        # Get the Peterson-Barney data
        peterson_barney_data = gather_data()

        # Get IPA symbols
        ipa_conversion_dataframe = pd.DataFrame(
            {
                "IPA": [
                    "χ",
                    "θ",
                    "β",
                    "ʘ",
                    "ǃ",
                    "ǂ",
                    "ǁ",
                    "ǀ",
                    "ʢ",
                    "ʡ",
                    "ˤ",
                    "ʕ",
                    "ʔ",
                    "ʒ",
                    "ʑ",
                    "ʐ",
                    "z",
                    "ʏ",
                    "y",
                    "x",
                    "ʍ",
                    "ʷ",
                    "w",
                    "ʌ",
                    "ʋ",
                    "v",
                    "ʊ",
                    "ɰ",
                    "ɯ",
                    "ɥ",
                    "ʉ",
                    "u",
                    "ʈ",
                    "t",
                    "ʃ",
                    "ʂ",
                    "s",
                    "ʁ",
                    "ɾ",
                    "ɽ",
                    "ɻ",
                    "ɺ",
                    "ɹ",
                    "ʀ",
                    "r",
                    "q",
                    "ɸ",
                    "p",
                    "ɵ",
                    "ɔ",
                    "ɶ",
                    "œ",
                    "ø",
                    "o",
                    "ŋ",
                    "ɳ",
                    "ɲ",
                    "ɴ",
                    "ⁿ",
                    "n",
                    "ɱ",
                    "m",
                    "ʎ",
                    "ɮ",
                    "ɭ",
                    "ɬ",
                    "ɫ",
                    "ʟ",
                    "ˡ",
                    "l",
                    "k",
                    "ʄ",
                    "ɟ",
                    "ʝ",
                    "ʲ",
                    "j",
                    "ɨ",
                    "ɪ",
                    "i",
                    "ɧ",
                    "ɦ",
                    "ʜ",
                    "ħ",
                    "ʰ",
                    "h",
                    "ˠ",
                    "ɣ",
                    "ʛ",
                    "ɠ",
                    "ɢ",
                    "ɡ",
                    "f",
                    "ɤ",
                    "ɞ",
                    "ɜ",
                    "ɚ",
                    "ɘ",
                    "ɛ",
                    "ə",
                    "e",
                    "ɗ",
                    "ɖ",
                    "ð",
                    "d",
                    "ɕ",
                    "ç",
                    "c",
                    "ɓ",
                    "ʙ",
                    "b",
                    "ɒ",
                    "ɑ",
                    "ɐ",
                    "æ",
                    "a",
                    "ˑ",
                    "ː",
                    "◌ʼ",
                    "◌͡◌",
                    "◌˞",
                    "◌̹",
                    "◌̰",
                    "◌̥",
                    "◌̤",
                    "◌̪",
                    "◌̺",
                    "◌̻",
                    "◌̜",
                    "◌̟",
                    "◌̠",
                    "◌̘",
                    "◌̙",
                    "◌̝",
                    "◌̞",
                    "◌̩",
                    "◌̯",
                    "◌̚",
                    "◌̄",
                    "◌̃",
                    "◌̈",
                    "◌̊",
                    "◌̌",
                    "◌̂",
                    "◌̆",
                    "◌̀",
                    "◌́",
                    "|",
                    "ˌ",
                    "ˈ",
                    "‿",
                    "‖",
                    ".",
                ],
                "Symbol": [
                    r"\cf",
                    r"\tf",
                    r"\bf",
                    r"\O.",
                    r"!",
                    r"\|-",
                    r"\|2",
                    r"\|1",
                    r"\9-",
                    r"\?-",
                    r"\^9",
                    r"\9e",
                    r"\?g",
                    r"\zh",
                    r"\zc",
                    r"\z.",
                    r"z",
                    r"\yc",
                    r"y",
                    r"x",
                    r"\wt",
                    r"\^w",
                    r"w",
                    r"\vt",
                    r"\vs",
                    r"v",
                    r"\hs",
                    r"\ml",
                    r"\mt",
                    r"\ht",
                    r"\u-",
                    r"u",
                    r"\t.",
                    r"t",
                    r"\sh",
                    r"\s.",
                    r"s",
                    r"\ri",
                    r"\fh",
                    r"\f.",
                    r"\r.",
                    r"\rl",
                    r"\rt",
                    r"\rc",
                    r"r",
                    r"q",
                    r"\ff",
                    r"p",
                    r"\o-",
                    r"\ct",
                    r"\Oe",
                    r"\oe",
                    r"\o/",
                    r"o",
                    r"\ng",
                    r"\n.",
                    r"\nj",
                    r"\nc",
                    r"\^n",
                    r"n",
                    r"\mj",
                    r"m",
                    r"\yt",
                    r"\lz",
                    r"\l.",
                    r"\l-",
                    r"\l~",
                    r"\lc",
                    r"\^l",
                    r"l",
                    r"k",
                    r"\j^",
                    r"\j-",
                    r"\jc",
                    r"\^j",
                    r"j",
                    r"\i-",
                    r"\ic",
                    r"i",
                    r"\hj",
                    r"\h^",
                    r"\hc",
                    r"\h-",
                    r"\^h",
                    r"h",
                    r"\^G",
                    r"\gf",
                    r"\G^",
                    r"\g^",
                    r"\gc",
                    r"\gs",
                    r"f",
                    r"\rh",
                    r"\kb",
                    r"\er",
                    r"\sr",
                    r"\e-",
                    r"\ef",
                    r"\sw",
                    r"e",
                    r"\d^",
                    r"\d.",
                    r"\dh",
                    r"d",
                    r"\cc",
                    r"\c,",
                    r"c",
                    r"\b^",
                    r"\bc",
                    r"b",
                    r"\ab",
                    r"\as",
                    r"\at",
                    r"\ae",
                    r"a",
                    r"\.f",
                    r"\:f",
                    r"\ap",
                    r"\lip",
                    r"\hr",
                    r"\3v",
                    r"\~v",
                    r"\0v",
                    r"\:v",
                    r"\Nv",
                    r"\Uv",
                    r"\Dv",
                    r"\cv",
                    r"\+v",
                    r"\-v",
                    r"\T(",
                    r"\T)",
                    r"\T^",
                    r"\Tv",
                    r"\|v",
                    r"\nv",
                    r"\cn",
                    r"\-^",
                    r"\~^",
                    r"\:^",
                    r"\0^",
                    r"\v^",
                    r"\^^",
                    r"\N^",
                    r"\`^",
                    r"\'^",
                    r"|",
                    r"\'2",
                    r"\'1",
                    r"\_ub",
                    r"||",
                    r".",
                ],
            }
        )

        peterson_barney_data = pd.merge(peterson_barney_data, ipa_conversion_dataframe, how="inner", on="IPA")
        # Make a list of unique IPA symbols from the csv file
        ipa_symbols = list(peterson_barney_data["Symbol"].unique())

        # Make a list of unique vowels in Peterson & Barney
        vowels = list(set(peterson_barney_data["Vowel"]))

        # Use the list of vowels to specify a colour map for ellipses
        if self.vowel_marker == "Vowels" or self.vowel_marker == "None":
            colours = cm.get_cmap(self.cmap)(np.linspace(0, 1, len(vowels)))
        elif self.vowel_marker == "IPA Symbols":
            colours = cm.get_cmap(self.cmap)(np.linspace(0, 1, len(ipa_symbols)))

        # Create a dataframe of formants from user
        # we will match these values to Peterson & Barney
        # to create ellipses based on user data
        user_data = pd.DataFrame(
            {
                "F1": self.state["f1 means"],
                "F2": self.state["f2 means"],
            }
        )
        if self.scale == "Bark":
            # Convert Our formant measurements to bark
            f1_bark = [hz_to_bark(f1) for f1 in self.state["f1 means"]]
            f2_bark = [hz_to_bark(f2) for f2 in self.state["f2 means"]]
            user_data = pd.DataFrame(
                {
                    "F1 Bark": f1_bark,
                    "F2 Bark": f2_bark,
                }
            )

            # Set frequencies to bark
            freq1 = f1_bark
            freq2 = f2_bark
            # Set search data
            search_data = peterson_barney_data[["F1 Bark", "F2 Bark"]].values

        else:  # Frequencies in Hz
            freq1 = self.state["f1 means"]
            freq2 = self.state["f2 means"]
            search_data = peterson_barney_data[["F1", "F2"]].values

        # Draw points on the plot (dots, Vowels, or IPA symbols)
        user_vowels = []
        user_symbols = []

        for point in zip(freq1, freq2):
            # Find the closest vowel to our data in peterson barney in Euclidean space
            node, indexer = self.closest_node(point, search_data)
            # Set up marker
            # Locate best matches for Vowels and No marker
            if self.vowel_marker == "Vowels" or self.vowel_marker == "None":
                marker = f"{(peterson_barney_data['Vowel'].loc[[indexer]]).values[0]}"
                user_vowels.append(marker)
            # Locate best matches for IPA Symbols as markers
            elif self.vowel_marker == "IPA Symbols":
                ipa_symbol_location = ipa_conversion_dataframe[
                    ipa_conversion_dataframe["IPA"]
                    == (peterson_barney_data["IPA"].loc[[indexer]]).values[0]
                ]
                # Try to set the IPA markers
                try:
                    ipa_symbol = ipa_symbol_location["Symbol"].values.flat[0]
                    marker = ipa_symbol
                    user_symbols.append(marker)
                # If IPA markers fail, use an '*' instead
                except:
                    ipa_symbol = "*"
                    marker = ipa_symbol
                    user_symbols.append(marker)

            # set x and y coordinates for plotting
            y, x = point
            # Set marker to 'o' in LaTex if there is no marker set
            if self.vowel_marker == "None":
                ax_kwargs.text(x, y, f"$o$")
            # Set marker to user choice in LaTex
            else:
                ax_kwargs.text(x, y, f"${marker}$", fontsize=8)

        # Add symbols or vowels to the dataframe
        if len(user_vowels) > 0:
            user_data["Vowel"] = user_vowels
        elif len(user_symbols) > 0:
            user_data["Symbol"] = user_symbols

        # make a dataframe of the points to plot
        plot_points = pd.DataFrame(list(zip(freq2, freq1)))
        if self.vowel_marker is not None:
            alpha_value = 0
            dot_colour = "w"
        else:
            alpha_value = 100
            dot_colour = "k"

        # plot invisible points or regular points if not a vowel or ipa symbol
        ax_kwargs.plot(
            plot_points, marker="o", c=dot_colour, alpha=alpha_value, linestyle="None"
        )

        # Plot Ellipses
        if (
            self.should_we_draw_ellipses[0].lower() == "m"
            or self.should_we_draw_ellipses[0].lower() == "p"
        ):
            if self.should_we_draw_ellipses[0].lower() == "m":
                data_frame_we_use = user_data
            elif self.should_we_draw_ellipses[0].lower() == "p":
                data_frame_we_use = peterson_barney_data

            ells = []
            if self.vowel_marker == "Vowels" or self.vowel_marker == "None":
                for i, vowel in enumerate(vowels):
                    if self.scale == "Bark":
                        y, x = (
                            data_frame_we_use["F1 Bark"][
                                data_frame_we_use["Vowel"] == vowel
                            ],
                            data_frame_we_use["F2 Bark"][
                                data_frame_we_use["Vowel"] == vowel
                            ],
                        )
                    else:
                        y, x = (
                            data_frame_we_use["F1"][
                                data_frame_we_use["Vowel"] == vowel
                            ],
                            data_frame_we_use["F2"][
                                data_frame_we_use["Vowel"] == vowel
                            ],
                        )
                    if len(y) >= 2:
                        self.confidence_ellipse(
                            x,
                            y,
                            ax_kwargs,
                            n_std=2,
                            alpha=0.3,
                            facecolor=colours[i],
                            edgecolor="black",
                            zorder=0,
                        )
                        ells.append(self.ellipse)

            elif self.vowel_marker == "IPA Symbols":
                for i, this_ipa_symbol in enumerate(ipa_symbols):
                    if self.scale == "Bark":
                        print(data_frame_we_use.head())
                        y, x = (
                            data_frame_we_use["F1 Bark"][
                                data_frame_we_use["Symbol"] == this_ipa_symbol
                            ],
                            data_frame_we_use["F2 Bark"][
                                data_frame_we_use["Symbol"] == this_ipa_symbol
                            ],
                        )
                    else:
                        y, x = (
                            data_frame_we_use["F1"][
                                data_frame_we_use["Symbol"] == this_ipa_symbol
                            ],
                            data_frame_we_use["F2"][
                                data_frame_we_use["Symbol"] == this_ipa_symbol
                            ],
                        )
                    if len(y) >= 2:
                        self.confidence_ellipse(
                            x,
                            y,
                            ax_kwargs,
                            n_std=2,
                            alpha=0.3,
                            facecolor=colours[i],
                            edgecolor="black",
                            zorder=0,
                        )
                        ells.append(self.ellipse)

            if self.vowel_marker == "IPA Symbols":
                marker_column = ipa_symbols
                ax_kwargs.legend(ells, marker_column)
            elif self.vowel_marker == "Vowels" or self.vowel_marker == "None":
                marker_column = vowels
                ax_kwargs.legend(ells, marker_column)

        # Determine axis limits based size of ellipses
        cov = np.cov(freq2, freq1)
        self.scale_x = np.sqrt(cov[0, 0]) * 2
        xmin = self.scale_x - min(freq2)
        xmax = self.scale_x + max(freq2)
        self.scale_y = np.sqrt(cov[1, 1]) * 2
        ymin = self.scale_y - min(freq1)
        ymax = self.scale_y + max(freq1)

        # No negative axes please
        if xmin < 0: xmin = 0
        if ymin < 0: ymin = 0
        if xmax < 0: xmax = 0
        if ymax < 0: ymax = 0

        # Set plot axis limits
        plt.xlim(left=xmin)
        plt.ylim(bottom=ymin)
        plt.xlim(right=xmax)
        plt.ylim(top=ymax)

        # Set Plot Title
        ax_kwargs.set_title(f"F1 F2 Plot")

        # Set Plot Axis Labels
        if self.scale == "Bark":
            ax_kwargs.set_xlabel("F2 [Bark]")
            ax_kwargs.set_ylabel("F1 [Bark]")
        else:
            ax_kwargs.set_xlabel("F2 [Hz]")
            ax_kwargs.set_ylabel("F1 [Hz]")

        fig.subplots_adjust(hspace=0.25)
        fig1 = plt.gcf()
        plt.show()
        fig1.savefig(f"F1F2_Plot_{datetime.datetime.now()}.png", dpi=1000)
        self.f1f2plotwindow = F1F2PlotWindow()

        for i, result in enumerate(results):
            results[i][self]["F1F2 Plot"] = ["Figure Created"]
        return results

    def confidence_ellipse(self, x, y, ax, n_std=1, facecolor="none", **kwargs):

        vowel_marker = self.args["Vowel Marker"][0]
        # create the plot
        fig, ax_kwargs = plt.subplots()
        ax_kwargs.axvline(c='grey', lw=1)
        ax_kwargs.axhline(c='grey', lw=1)

        # Get the Peterson-Barney data
        df = gather_data()

        # Make a list of vowels
        vowels = list(set(df["Vowel"]))

        # Use the list of vowels to specify a colour map for ellipses
        colours = cm.plasma(np.linspace(0, 1, len(vowels)))
        ells = []

        # Convert Our formant measurements to bark
        f1_bark = [hz_to_bark(f1) for f1 in self.state['f1 means']]
        f2_bark = [hz_to_bark(f2) for f2 in self.state['f2 means']]

        # convert peterson barney f1 f2 data into numpy arrays
        search_data = df[["F1 Bark", "F2 Bark"]].values
        #ipa_conversion_dataframe = pd.read_csv('Voicelab/toolkits/Voicelab/IPA_Praat_symbols.csv', header=0)
        ipa_conversion_dataframe = gather_data()
        for point in zip(f1_bark, f2_bark):
            # Find the closest vowel to our data in peterson barney
            node, indexer = (self.closest_node(point, search_data))
            if vowel_marker == "Vowels":
                marker = f"{(df['Vowel'].loc[[indexer]]).values[0]}"
            elif "I" in vowel_marker:
                ipa_symbol_location = \
                    ipa_conversion_dataframe[ipa_conversion_dataframe["Praat"] == (df["IPA"].loc[[indexer]]).values[0]]
                try:
                    ipa_symbol = ipa_symbol_location["IPA"].values.flat[0]
                except:
                    ipa_symbol = '*'
                marker = f"{ipa_symbol}"
            else:
                marker = '.'

            y, x = point
            ax_kwargs.text(x, y, marker, fontsize=12)

        plot_points = pd.DataFrame(list(zip(f2_bark, f1_bark)))
        ax_kwargs.plot(plot_points, marker='o', c='w', alpha=0, linestyle="None")

        for i, vowel in enumerate(vowels):
            y, x = df['F1 Bark'][df['Vowel'] == vowel], df['F2 Bark'][df['Vowel'] == vowel]
            self.confidence_ellipse(x, y, ax_kwargs, n_std=2, alpha=0.3, facecolor=colours[i],
                                    edgecolor='black', zorder=0)
            ells.append(self.ellipse)


        ax_kwargs.legend(ells, vowels)
        ax_kwargs.set_title(f'F1 F2 Plot')

        plt.xlim(left=4)
        plt.xlim(right=20)
        plt.ylim(bottom=2)
        plt.ylim(top=10)
        ax_kwargs.set_xlabel("F2 Bark")
        ax_kwargs.set_ylabel("F1 Bark")
        fig.subplots_adjust(hspace=0.25)
        fig1 = plt.gcf()
        plt.show()

        fig1.savefig('f1f2.png', dpi=1000)
        results[i][self]["F1F2 Plot"] = ["Figure Created"]

        self.f1f2plotwindow = F1F2PlotWindow()
        return results


    def confidence_ellipse(self, x, y, ax, n_std=1, facecolor='none', **kwargs):
        """
        Create a plot of the covariance confidence ellipse of *x* and *y*.

        Parameters
        ----------
        x, y : array-like, shape (n, )
            Input data.

        ax : matplotlib.axes.Axes
            The axes object to draw the ellipse into.

        n_std : float
            The number of standard deviations to determine the ellipse's radiuses.

        Returns
        -------
        matplotlib.patches.Ellipse

        Other parameters
        ----------------
        kwargs : `~matplotlib.patches.Patch` properties
        """
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        cov = np.cov(x, y)
        pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
        # Using a special case to obtain the eigenvalues of this
        # two-dimensionl dataset.
        ell_radius_x = np.sqrt(1 + pearson)
        ell_radius_y = np.sqrt(1 - pearson)
        ellipse = Ellipse(
            (0, 0),
            width=ell_radius_x * 2,
            height=ell_radius_y * 2,
            facecolor=facecolor,
            **kwargs,
        )
        ellipse = Ellipse((0, 0),
                          width=ell_radius_x * 2,
                          height=ell_radius_y * 2,
                          facecolor=facecolor,
                          **kwargs)
        self.g_ell_center = ellipse.get_center()
        self.g_ell_width = ell_radius_x * 2
        self.g_ell_height = ell_radius_y * 2
        self.angle = 45

        # Calculating the stdandard deviation of x from
        # the squareroot of the variance and multiplying
        # with the given number of standard deviations.
        scale_x = np.sqrt(cov[0, 0]) * n_std

        mean_x = np.mean(x)

        # calculating the stdandard deviation of y ...
        scale_y = np.sqrt(cov[1, 1]) * n_std
        mean_y = np.mean(y)


        transf = (
            transforms.Affine2D()
            .rotate_deg(45)
            .scale(scale_x, scale_y)
            .translate(mean_x, mean_y)
        )

        transf = transforms.Affine2D() \
            .rotate_deg(45) \
            .scale(scale_x, scale_y) \
            .translate(mean_x, mean_y)
        ellipse.set_transform(transf + ax.transData)
        self.ellipse = ellipse
        return ax.add_patch(ellipse)


def hz_to_bark(hz):
    """
    This function converts Hz to Bark.
        Parameters
        ----------
        hz is the frequency in Hz

        Returns
        -------
        bark is the frequency in bark
    """

    bark = 7 * np.log(hz / 650 + np.sqrt(1 + (hz / 650) ** 2))
    return bark


def gather_data():
    """
    This function collects data from Peterson & Barney 1952 from Praat there is no input for the function.

        Returns
        -------
        peterson_barney a pandas dataframe that also includes bark measures using hz_to_bark function
    """

    peterson_barney = call("Create formant table (Peterson & Barney 1952)")
    peterson_barney = pd.read_csv(
        io.StringIO(call(peterson_barney, "List", True)), sep="\t", header=0
    ).dropna()
    peterson_barney["F1 Bark"] = hz_to_bark(peterson_barney["F1"])
    peterson_barney["F2 Bark"] = hz_to_bark(peterson_barney["F2"])
    peterson_barney = pd.read_csv(io.StringIO(call(peterson_barney, "List", True)), sep='\t').dropna()
    peterson_barney['F1 Bark'] = hz_to_bark(peterson_barney['F1'])
    peterson_barney['F2 Bark'] = hz_to_bark(peterson_barney['F2'])
    return peterson_barney
