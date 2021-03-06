from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

###################################################################################################
# MANIPULATE FORMANTS NODE
# WARIO pipeline node for manipulating voice formants.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
# 'unit'    :
# 'factor'  :
###################################################################################################
# RETURNS
# 'manipulated_voice'   : sound file of the original voice with modifications
###################################################################################################



class ManipulateFormantsNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        # initialize with default arguments
        self.args = {"unit": ("percent", []), "factor": 0.85}

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################
    def process(self):
        try:
            sound = self.args["voice"]
            file_path = self.args["file_path"]
            unit = self.args["unit"][0]
            factor = self.args["factor"]

            factor_percent = round(factor * 100)
            f0min, f0max = self.pitch_bounds(sound)

            output_file_name = file_path.split("/")[-1].split(".wav")[0]
            output_file_name = (
                output_file_name + "_manipulate_formants_" + str(factor) + "_" + str(unit)
            )

            manipulated_sound = call(sound, "Change gender", f0min, f0max, factor, 0, 1, 1)
            manipulated_sound.scale_intensity(70)
            manipulated_sound.name = output_file_name

            return {"voice": manipulated_sound}
        except:
            return {"voice": "Manipulation failed"}
