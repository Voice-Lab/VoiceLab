from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


# MANIPULATE PITCH NODE
# WARIO pipeline node for manipulating the pitch of a voice.
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
# RETURNS


class ScaleIntensityNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {
            "value": 70, # Positive number
            "method": ("RMS (dB)", ["RMS (dB)", "Peak (-1, 1)"])
            # todo check for legal values
        }
        # process: WARIO hook called once for each voice file.

    def process(self):
        value = self.args["value"]
        file_path = self.args["file_path"]
        sound = self.args["voice"]
        method = self.args["method"]
        if method == "RMS":
            sound.scale_intensity(value)
        elif method == "Peak":
            call(sound, "Scale peak", value)
        else:
            sound.scale_intensity(value)
        output_file_name: str = file_path.split("/")[-1].split(".wav")[0]
        output_file_name = f"{output_file_name}_intensity_{value}_{method[0]}"
        sound.name = output_file_name

        return {"voice": sound}
