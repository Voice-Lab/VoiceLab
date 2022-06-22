from __future__ import annotations

from typing import Union

from Voicelab.pipeline.Node import Node
import numpy as np
import seaborn as sns
import os
import parselmouth
from parselmouth.praat import call
import matplotlib.pyplot as plt

from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
# from Voicelab.VoicelabWizard.SpectrumPlotWindow import SpectrumPlotWindow

class VisualizeSpectrumNode(VoicelabNode):
    """Create a power spectrum of the sound with or without an LPC curve plotted over it.

    :parameter self.args: dictionary of settings to be passed into the node
    :type parameter: dict

        :parameter self.args['Max Frequency']: Maximum frequency used to resample sound to 2x this number
        :type self.args['Max Frequency']: Union[float, int]

        :parameter self.args['Plot LPC Curve']: Whether to plot the LPC curve
        :type self.args['Plot LPC Curve']: bool

    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)


        self.args = {
            "Max Frequency": 5500,  # Max frequency, usually highest formant
            "Plot LPC Curve": True,
        }
###############################################################

    def process(self):
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        max_freq = self.args["Max Frequency"]

        spectrum = sound.to_spectrum()
        spectrum_values = spectrum.values[0,:] + 1j * spectrum.values[1,:]
        power_spectral_density = 10 * np.log10(2 * abs(spectrum_values)**2 * spectrum.dx / 4e-10)
        frequencies = np.array([spectrum.get_frequency_from_bin_number(bin + 1) for bin in range(spectrum.get_number_of_bins())])
        # Create subplots so we can overlay the plots
        fig, ax = plt.subplots()

        # First plot the spectrum as we do normally
        ax.plot(frequencies, power_spectral_density, color='black', linewidth=0.25)
        plt.xlim(xmin=-4e-10, xmax=5500)
        plt.ylim(ymin=0, ymax=np.nanmax(power_spectral_density))
        ax.set_xlabel("Frequency bin (Hz)")
        ax.set_ylabel("Amplitude (dB) / Frequency(Hz)")

        # Plot LPC Curve if user specifies.
        if self.args["Plot LPC Curve"]:
            # Measure the formants
            try:
                formant_path_object = call(sound,
                                           "To FormantPath (burg)",
                                           0.0025,
                                           5,
                                           max_freq,
                                           0.025,
                                           50,
                                           0.025,
                                           5)
                formant_object = call(formant_path_object, "Extract Formant")


                # Create LPC object
                lpc = call(formant_object, 'To LPC', max_freq*2)

                # Extract Spectral Density (Amplitude) and Frequency Bins from LPC analysis
                lpc_spectrum = call(lpc, 'To Spectrum (slice)', 0, 20, 0, 50)
                lpc_spectrum_values = lpc_spectrum.values[0,:] + 1j * lpc_spectrum.values[1,:]
                lpc_power_spectral_density = 10 * np.log10(2 * abs(lpc_spectrum_values)**2 * lpc_spectrum.dx / 4e-10)
                lpc_frequencies = np.array([lpc_spectrum.get_frequency_from_bin_number(bin + 1) for bin in range(lpc_spectrum.get_number_of_bins())])

                # plot the LPC curve
                ax.plot(lpc_frequencies, lpc_power_spectral_density, color='blue', linewidth=5)
                # plt.ylim(ymin=0, ymax=np.nanmax(lpc_power_spectral_density + 10))
                ax.set_xlim(xmin=-4e-10, xmax=5500)
                ax.set_ylim(ymin=0, ymax=np.nanmax(lpc_power_spectral_density))

            except Exception as e:
                str(e)

            plt.close(fig)
            return {"spectrum": fig}
