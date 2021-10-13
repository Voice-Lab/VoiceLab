from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from Voicelab.toolkits.Voicelab.MeasurePitchNode import measure_pitch
from scipy import stats
import statistics


class MeasureFormantPositionsNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            # 'Method': 'formants_praat_manual'
        }

        self.state = {
            "f1_mean_pf_list": [],
            "f2_mean_pf_list": [],
            "f3_mean_pf_list": [],
            "f4_mean_pf_list": [],
            #'f1_median_pf_list': [],
            #'f2_median_pf_list': [],
            #'f3_median_pf_list': [],
            #'f4_median_pf_list': [],
        }

    # On each file we want to calculate the formants at the glottal pulses
    def process(self):

        voice: object = self.args["voice"]

        # method = self.args['Method']
        # pitch = self.args['Pitch']
        formant_object = self.args["Formants"]

        pitch_floor = self.args["Pitch Floor"]
        pitch_ceiling = self.args["Pitch Ceiling"]
        pitch = measure_pitch(
            voice=voice, measure="cc", floor=pitch_floor, ceiling=pitch_ceiling
        )

        point_process = call(
            [voice, pitch], "To PointProcess (cc)"
        )  # Create PointProcess object
        num_points = call(point_process, "Get number of points")

        f1_list = []
        f2_list = []
        f3_list = []
        f4_list = []
        measurement_times = []

        for point in range(0, num_points):
            point += 1
            t = call(point_process, "Get time from index", point)
            measurement_times.append(t)
            f1 = call(formant_object, "Get value at time", 1, t, "Hertz", "Linear")
            f2 = call(formant_object, "Get value at time", 2, t, "Hertz", "Linear")
            f3 = call(formant_object, "Get value at time", 3, t, "Hertz", "Linear")
            f4 = call(formant_object, "Get value at time", 4, t, "Hertz", "Linear")
            f1_list.append(f1)
            f2_list.append(f2)
            f3_list.append(f3)
            f4_list.append(f4)

        f1_list = [f1 for f1 in f1_list if str(f1) != "nan"]
        f2_list = [f2 for f2 in f2_list if str(f2) != "nan"]
        f3_list = [f3 for f3 in f3_list if str(f3) != "nan"]
        f4_list = [f4 for f4 in f4_list if str(f4) != "nan"]

        # calculate mean & median formants across pulses
        if len(f1_list) > 0:
            f1_mean_pf = sum(f1_list) / len(f1_list)
            # f1_median_pf = statistics.median(f1_list)
        else:
            f1_mean_pf = "N/A"
            f1_median_pf = "N/A"

        if len(f2_list) > 0:
            f2_mean_pf = sum(f2_list) / len(f2_list)
            f2_median_pf = statistics.median(f2_list)
        else:
            f2_mean_pf = "N/A"
            f2_median_pf = "N/A"

        if len(f3_list) > 0:
            f3_mean_pf = sum(f3_list) / len(f3_list)
            f3_median_pf = statistics.median(f3_list)
        else:
            f3_mean_pf = "N/A"
            f3_median_pf = "N/A"

        if len(f4_list) > 0:
            f4_mean_pf = sum(f4_list) / len(f4_list)
            f4_median_pf = statistics.median(f4_list)
        else:
            f4_mean_pf = "N/A"
            f4_median_pf = "N/A"

        results = {}

        # collect all means and median values, these will be needed at the end to calculate the formant positions
        self.state["f1_mean_pf_list"].append(f1_mean_pf)
        self.state["f2_mean_pf_list"].append(f2_mean_pf)
        self.state["f3_mean_pf_list"].append(f3_mean_pf)
        self.state["f4_mean_pf_list"].append(f4_mean_pf)

        self.state["f1_median_pf_list"].append(f1_median_pf)
        self.state["f2_median_pf_list"].append(f2_median_pf)
        self.state["f3_median_pf_list"].append(f3_median_pf)
        self.state["f4_median_pf_list"].append(f4_median_pf)

        return results

    # Once all of the files have been processed, we want to calculate the position across all of them
    def end(self, results):

        """
        Args:
            results:
        """
        f1_mean_pf_list = self.state["f1_mean_pf_list"]
        f2_mean_pf_list = self.state["f2_mean_pf_list"]
        f3_mean_pf_list = self.state["f3_mean_pf_list"]
        f4_mean_pf_list = self.state["f4_mean_pf_list"]

        f1_median_pf_list = self.state["f1_median_pf_list"]
        f2_median_pf_list = self.state["f2_median_pf_list"]
        f3_median_pf_list = self.state["f3_median_pf_list"]
        f4_median_pf_list = self.state["f4_median_pf_list"]

        formant_mean_lists = [
            f1_mean_pf_list,
            f2_mean_pf_list,
            f3_mean_pf_list,
            f4_mean_pf_list,
        ]
        formant_median_lists = [
            f1_median_pf_list,
            f2_median_pf_list,
            f3_median_pf_list,
            f4_median_pf_list,
        ]

        # append it to the results of all of them
        formant_positions = self.calculate_formant_position(formant_mean_lists)
        for i, result in enumerate(results):
            if isinstance(formant_positions, str):
                results[i][self]["Formant Position"] = formant_positions
            else:
                results[i][self]["Formant Position"] = float(formant_positions[i])

        return results

    # to calcualte the formant position we need the formants at glotal pulses for each file we rans
    def calculate_formant_position(self, formant_mean_lists, formant_median_lists):
        """
        Args:
            formant_mean_lists:
            formant_median_lists:
        """
        if len(formant_mean_lists[0]) < 30:  # or len(formant_medians_lists[0]) < 8:
            return "Not enough samples, requires at least 30"

        # Normality test for mean data
        _, p_f1_mean = stats.normaltest(formant_mean_lists[0])
        _, p_f2_mean = stats.normaltest(formant_mean_lists[1])
        _, p_f3_mean = stats.normaltest(formant_mean_lists[2])
        _, p_f4_mean = stats.normaltest(formant_mean_lists[3])
        if p_f1_mean >= 0.5 or p_f2_mean >= 0.5 or p_f3_mean >= 0.5 or p_f4_mean >= 0.5:
            return "formants not normally distributed"

        else:
            zf1_mean = stats.zscore(formant_mean_lists[0])
            zf2_mean = stats.zscore(formant_mean_lists[1])
            zf3_mean = stats.zscore(formant_mean_lists[2])
            zf4_mean = stats.zscore(formant_mean_lists[3])
            pf_mean = (zf1_mean + zf2_mean + zf3_mean + zf4_mean) / 4
            return pf_mean

        # normality test for median data
        _, p_f1_median = stats.normaltest(formant_medians_lists[0])
        _, p_f2_median = stats.normaltest(formant_medians_lists[1])
        _, p_f3_median = stats.normaltest(formant_medians_lists[2])
        _, p_f4_median = stats.normaltest(formant_medians_lists[3])

        if (
            p_f1_median >= 0.5
            or p_f2_median >= 0.5
            or p_f3_median >= 0.5
            or p_f4_median >= 0.5
        ):
            return "formants not normally distributed"

        else:
            zf1_median = stats.zscore(formant_medians_lists[0])
            zf2_median = stats.zscore(formant_medians_lists[1])
            zf3_median = stats.zscore(formant_medians_lists[2])
            zf4_median = stats.zscore(formant_medians_lists[3])

            pf_median = (zf1_median + zf2_median + zf3_median + zf4_median) / 4
            return pf_median
