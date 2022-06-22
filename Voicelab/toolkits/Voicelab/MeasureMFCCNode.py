from __future__ import annotations
import parselmouth
from typing import Union

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class MeasureMFCCNode(VoicelabNode):
    """Measure 24 MFCCs of a sound

    :argument self.args['file_path']: the path to the file to be analysed
    :type self.args['file_path']: str

    :return: dict of results
    :rtype: dict[str, Union[int, float, str, list]]
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize with default arguments
        self.args = {
        }

        # process: WARIO hook called once for each voice file.
    def process(self):
        """Run the MFCC analysis

        :argument self.args['file_path']: the path to the file to be analysed
        :type self.args['file_path']: str

        :return: dict of results
        :rtype: dict[str, Union[int, float, str, list]]
        """
        file_path = self.args['file_path']
        sound = parselmouth.Sound(file_path)
        try:
            mfcc = sound.to_mfcc(number_of_coefficients=24)
            return {
                "mfcc": mfcc.extract_features().values.tolist()
            }
        except Exception as e:
            return {
                "mfcc": str(e)
            }

