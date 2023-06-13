from __future__ import annotations

from typing import Union

from ...pipeline.Node import Node
import parselmouth
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode

from PyQt5.QtWidgets import QMessageBox


class ManipulatePitchLowerNode(VoicelabNode):
    """This node manipulates the pitch of the sound by raising it.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
            "unit": ("ERB", ["ERB", "Hertz", "mel", "logHertz", "semitones"]),
            "method": ("Shift frequencies", ["Shift frequencies", "Multiply frequencies"]),
            "amount": -0.5,
            "time_step": 0.001,
            "normalize amplitude": True,
        }
        """
        The args dictionary is used to store the arguments of the node.
        The keys are the names of the arguments and the values are a tuple of the following format:
        (default value, [list of possible values]).

        :arg unit: The unit of the pitch. Possible values are: "ERB", "Hertz", "mel", "logHertz", "semitones".
        :type unit: str
        :arg method: The method of manipulating the pitch. Possible values are: "Shift frequencies", "Multiply frequencies". If the method is "Shift frequencies", the amount is in Hertz. If the methods is "Multiply frequencies", the amount is a proportion.
        :type method: str
        :arg amount: The amount of the pitch manipulation. This should be a negative number. If you want to raise pitch, use that node instead.
        :type amount: float
        :arg time_step: The time step of the pitch manipulation.
        :type time_step: float
        :arg normalize amplitude: Whether to normalize the amplitude of the pitch manipulation.
        :type normalize amplitude: bool
        """

    def process(self):
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
        try:
            # initialize values
            file_path = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            unit = self.args["unit"][0]

            # This is because the first item in the unit tuple is a string, but the rest are a tuple
            # This needs to be fixed eventually instead of hacked
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

            method: str = self.args["method"][0]
            if method == "S":
                method = "Shift frequencies"
            elif method == "M":
                method = "Multiply frequencies"

            time_step = self.args["time_step"]
            f0min, f0max = self.pitch_bounds(file_path)
            self.args['f0min'], self.args['f0max'] = f0min, f0max
            # create manipulation object
            manipulation = call(sound, "To Manipulation", time_step, f0min, f0max)
            # extract pitch tier
            pitch_tier = call(manipulation, "Extract pitch tier")
            # modify pitch tier and replace it
            # Shift frequencies has an additional 'unit' argument
            amount = self.args['amount']
            if method[0] == "S":  # "S" is for 'Shift frequencies'
                call(pitch_tier, method, sound.xmin, sound.xmax, amount, unit)

            # Multiply frequencies does not have a unit argument
            else:
                if amount <= 0:
                    warning_window = QMessageBox()
                    warning_window.setWindowTitle("Warning")
                    warning_window.setText("You cannot multiply freqeuncies by a number less than or equal to 0.\nWe have used the absolute value of your number")
                    warning_window.setIcon(QMessageBox.Critical)
                    warning_window.exec_()
                    amount *= -1

                call(pitch_tier, method, sound.xmin, sound.xmax, amount)

            call([pitch_tier, manipulation], "Replace pitch tier")
            # resynthesize voices
            manipulated_sound = call(manipulation, "Get resynthesis (overlap-add)")
            if self.args["normalize amplitude"]:
                manipulated_sound.scale_intensity(70)

            output_file_name = file_path.split("/")[-1].split(".wav")[0]
            output_file_name = f"{output_file_name}_lower_pitch_{method}_{amount}_{unit}"

            manipulated_sound.name = output_file_name
        except Exception as e:
            manipulated_sound = str(e)

        return {"voice": manipulated_sound}





