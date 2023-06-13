from __future__ import annotations
from typing import Union

from ...pipeline.Node import Node
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode

from PyQt5.QtWidgets import QMessageBox
import parselmouth


class ManipulatePitchHigherNode(VoicelabNode):
    """Manipulate pitch higher node.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args: dict[str, Union[float, tuple[str, list[str]], bool]] = {
            "unit": ("ERB", ["ERB", "Hertz", "mel", "logHertz", "semitones"]),
            "method": ("Shift frequencies", ["Shift frequencies", "Multiply frequencies"]),
            "amount": 0.5,
            "time_step": 0.001,
            "normalize amplitude": True,
        }
        """
        The args dictionary is used to store the arguments of the node.
        The keys are the names of the arguments and the values are a tuple of the following format:
        (default value, [list of possible values]).
        
        :arg unit: The unit of the pitch.
        :type unit: str
        :arg method: The method of manipulating the pitch.
        :type method: str
        :arg amount: The amount of the pitch manipulation.
        :type amount: float
        :arg time_step: The time step of the pitch manipulation.
        :type time_step: float
        :arg normalize amplitude: Whether to normalize the amplitude of the pitch manipulation.
        :type normalize amplitude: bool
        """

    def process(self) -> dict[Union[str, parselmouth.Sound]]:
        """
        The process function is the heart of the program.  It is called by default when you run a sound through
        VoiceLab, and it is also called when you click on "Start queue" in the GUI.  The process function takes in an
        array of arguments that are specified by whatever options you check off on the GUI or in VoiceLab's "Manipulate
        Pitch Higher" menu. These arguments are added to the args dictionary in the __init__ function.  The process
        function returns a dictionary of the results of the manipulation. This is either a parselmouth Sound object, or
        an error message.

        :param self: Used to Access the attributes and methods of the class in python.
        :return: A dictionary with the manipulated parselmouth.Sound object.
        :rtype: dict[str, Union[parselmouth.Sound, str]]
        """

        # Get the sound
        file_path: str = self.args["file_path"]
        """The file path of the sound"""
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        """The Parselmouth Sound object for this sound
        :type: parselmouth.Sound
        """
        unit: Union[str, list] = self.args["unit"][0]
        """The unit of the pitch: ERB, Hertz, mel, logHertz, semitones
        :type: str, List
        """

        # This is because the first item in the unit tuple is a string, but the rest are a tuple
        # This could be a case statement when we upgrade to python 3.10
        # Check for a workaround in another node
        if unit == 'E':
            unit = "ERB"
        elif unit == 'H':
            unit = "Hertz"
        elif unit == 'm':
            unit = 'mel'
        elif unit == 'l':
            unit = 'logHertz'
        elif unit == 's':
            unit = 'semitones'

        method: Union[str, list] = self.args["method"][0]
        # Sometimes we get 1st character, sometimes we get full string.  This fixes it.
        if method == "S":
            method = "Shift frequencies"
        elif method == "M":
            method = "Multiply frequencies"

        time_step: float = self.args["time_step"]
        f0min, f0max = self.pitch_bounds(file_path)
        self.args['f0min'], self.args['f0max'] = f0min, f0max
        # create manipulation object
        manipulation: parselmouth.Data = call(sound, "To Manipulation", time_step, f0min, f0max)
        # extract pitch tier
        pitch_tier: parselmouth.Data = call(manipulation, "Extract pitch tier")
        # modify pitch tier and replace it
        amount: Union[float, int] = self.args['amount']
        # Shift frequencies has an additional 'unit' argument
        # This is a hack to fix a bug in the GUI.  The GUI is supposed to return a string, but sometimes it returns the
        # first character of the string.  This is a hack to fix that.
        if method[0] == "S":  # "S" is for 'Shift frequencies'
            call(pitch_tier, method, sound.xmin, sound.xmax, amount, unit)
        # Multiply frequencies does not have a unit argument
        else:
            if amount <= 0:
                warning_window = QMessageBox()
                warning_window.setWindowTitle("Warning")
                warning_window.setText(
                    "You cannot multiply freqeuncies by a number less than or equal to 0.\nWe have used the absolute value of your number")
                warning_window.setIcon(QMessageBox.Critical)
                warning_window.exec_()
                amount *= -1
            call(pitch_tier, method, sound.xmin, sound.xmax, amount)
        call([pitch_tier, manipulation], "Replace pitch tier")
        # resynthesize voices
        manipulated_sound: parselmouth.Sound = call(manipulation, "Get resynthesis (overlap-add)")
        """The manipulated sound parselmouth Sound object
        :type: parselmouth.Sound
        """
        # Normalize amplitude if requested
        if self.args["normalize amplitude"]:
            manipulated_sound.scale_intensity(70)

        # create a sound name for the manipulated sound, and add that to the manipulated sound Sound object
        output_file_name = file_path.split("/")[-1].split(".wav")[0]
        """The output name of the manipulated sound file
        :type: str
        """
        output_file_name = f"{output_file_name}_raise_pitch_{method}_{amount}_{unit}"
        manipulated_sound.name = output_file_name
        return {"voice": manipulated_sound}
