import parselmouth

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class MeasureIntensityNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {"minimum_pitch": 100}

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################

    def process(self):
        voice = self.args["voice"]
        try:
            minimum_pitch = self.args["minimum_pitch"]
            intensity = voice.to_intensity(minimum_pitch)
            mean_intensity = intensity.get_average()
            return {
                "Intensity": intensity,
                "Mean Intensity (dB)": mean_intensity
            }
        except:
            return {
                # "Intensity": intensity,
                "Mean Intensity (dB)": "Intensity measure failed"
            }
