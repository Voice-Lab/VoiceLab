from typing import Union

from ...pipeline.Node import Node
from parselmouth.praat import call
import parselmouth
from parselmouth.praat import run
import numpy as np
from .VoicelabNode import VoicelabNode



class RotateSpectrumNode(VoicelabNode):
    """A Class to rotate the spectrum of the voice file.

       Script by Chris Darwin: http://www.lifesci.sussex.ac.uk/home/Chris_Darwin/Praatscripts/Spectral%20Rotation

            Attributes:
            -----------
            self.args: dict
                Dictionary of arguments for the node.

                self.args{'maximum_frequency'} (float):
                    maximum frequency. Spectrum will be resampled to 2x this frequency.
                    Once rotated, this will be the new minimum frequency, but set to 0.

            Methods:
            --------
            self.process():
                Rotates the spectrum of the voice file.
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Parameters:
            *args:
            **kwargs:
        """

        self.args = {
            'maximum_frequency': 5000,
        }

    def process(self) -> dict[str, Union[parselmouth.Sound, str]]:
        """
        process: WARIO hook called once for each voice file.

           Rotate the spectrum of the voice file.
           Script by Chris Darwin: http://www.lifesci.sussex.ac.uk/home/Chris_Darwin/Praatscripts/Spectral%20Rotation

                Parameters:
                    self.args{'maximum_frequency'} (float): maximum frequency

                Returns:
                    {"voice": new_sound[0]} (dict[str, Union[parselmouth.Sound, str]]): the rotated sound object (not a wav file, but a praat object), or an error message
        """

        file_path: str = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
        output_file_name: str = f"{output_file_name}_rotated_spectrum"
        sf: float = sound.sampling_frequency
        maximum_frequency: float = self.args["maximum_frequency"]

        script: str = f"""
        # and a second that has the non-zero part of the spectrum rotated about its midpoint.
        # Script by Chris Darwin: http://www.lifesci.sussex.ac.uk/home/Chris_Darwin/Praatscripts/Spectral%20Rotation
        # Reproduced with permission of the author.
        
        sound$ = Read from file... {file_path}
        durn = Get duration
        sf = {sf}
        halfsf = sf / 2
        maximum_frequency = {maximum_frequency}
        if maximum_frequency > halfsf
            exit Maximum frequency must be less than  'halfsf' Hz
        endif
        To Spectrum

        # zero out spectrum above maximum frequency
        Copy... 'sound$'_'maximum_frequency'
        bw = Get bin width
        topbin = maximum_frequency/ bw
        Copy... 'sound$'_'maximum_frequency'x
        Formula... if col > 'topbin' then 0 else Spectrum_'sound$'_'maximum_frequency'[row,'topbin'-col] endif
        To Sound
        Reverse
        Extract part... 0 durn Rectangular 1.0 no
        """

        try:
            new_sound: list = run(script)
            new_sound[0].name = output_file_name.lower()
            return {"voice": new_sound[0]}
        except Exception as e:
            return {"voice": str(e)}
