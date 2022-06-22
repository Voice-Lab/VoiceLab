from __future__ import annotations

import numpy as np
import parselmouth
from parselmouth.praat import call

from sklearn.preprocessing import StandardScaler,  RobustScaler
import statistics
from scipy import stats
from typing import Union

from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from Voicelab.toolkits.Voicelab.MeasurePitchNode import measure_pitch_praat


class MeasureFormantPositionsNode(VoicelabNode):
    """Measure Formnat Positions Node. This measures formant frequency position. This code is called from the MeasureVocalTractEstimatesNode. It's recommended you use that node to access this code.
    """
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
        }

    # On each file we want to calculate the formants at the glottal pulses
    def process(self):
        """This runs the formant position measurement on each file. Results are passed to the end() method where they are sent to the Data Model.

            :return results: A dictionary of results for each file.
            :rtype results: dict
        """
        file_path: str = self.args["file_path"]
        voice: parselmouth.Sound = parselmouth.Sound(file_path)
        formant_object: parselmouth.Formant = self.args["Formants"]

        pitch_floor: float = self.args["Pitch Floor"]
        pitch_ceiling: float = self.args["Pitch Ceiling"]
        pitch: tuple[float, list[float], float, float, float, float] = measure_pitch_praat(
            file_path=file_path,
            method="cc",
            floor=pitch_floor,
            ceiling=pitch_ceiling
        )

        point_process: parselmouth.Data = call([voice, pitch], "To PointProcess (cc)")  # Create PointProcess object
        num_points: Union[float, int] = call(point_process, "Get number of points")

        f1_list: list = []
        f2_list: list = []
        f3_list: list = []
        f4_list: list = []
        measurement_times: list = []
        normalization_method_list: list = []

        point: Union[float, int]
        for point in range(0, num_points):
            point += 1
            t: float = call(point_process, "Get time from index", point)
            measurement_times.append(t)
            f1: float = call(formant_object, "Get value at time", 1, t, "Hertz", "Linear")
            f2: float = call(formant_object, "Get value at time", 2, t, "Hertz", "Linear")
            f3: float = call(formant_object, "Get value at time", 3, t, "Hertz", "Linear")
            f4: float = call(formant_object, "Get value at time", 4, t, "Hertz", "Linear")
            f1_list.append(f1)
            f2_list.append(f2)
            f3_list.append(f3)
            f4_list.append(f4)

        f1_list = [f1 for f1 in f1_list if str(f1) != "nan"]
        f2_list = [f2 for f2 in f2_list if str(f2) != "nan"]
        f3_list = [f3 for f3 in f3_list if str(f3) != "nan"]
        f4_list = [f4 for f4 in f4_list if str(f4) != "nan"]

        # calculate mean
        if len(f1_list) > 0:
            f1_mean_pf: Union[float, str] = sum(f1_list) / len(f1_list)
        else:
            f1_mean_pf: Union[float, str] = "N/A"
        if len(f2_list) > 0:
            f2_mean_pf: Union[float, str] = sum(f2_list) / len(f2_list)
        else:
            f2_mean_pf: Union[float, str] = "N/A"
        if len(f3_list) > 0:
            f3_mean_pf: Union[float, str] = sum(f3_list) / len(f3_list)
        else:
            f3_mean_pf: Union[float, str] = "N/A"
        if len(f4_list) > 0:
            f4_mean_pf: Union[float, str] = sum(f4_list) / len(f4_list)
        else:
            f4_mean_pf: Union[float, str] = "N/A"

        results: dict = {}

        # collect all means values, these will be needed at the end to calculate the formant positions
        self.state["f1_mean_pf_list"].append(f1_mean_pf)
        self.state["f2_mean_pf_list"].append(f2_mean_pf)
        self.state["f3_mean_pf_list"].append(f3_mean_pf)
        self.state["f4_mean_pf_list"].append(f4_mean_pf)

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

        formant_mean_lists = [
            f1_mean_pf_list,
            f2_mean_pf_list,
            f3_mean_pf_list,
            f4_mean_pf_list,
        ]

        # append it to the results of all of them
        formant_positions, normalization_type = self.calculate_formant_position(formant_mean_lists)
        for i, result in enumerate(results):
            if isinstance(formant_positions, str):
                results[i][self]["Formant Position"] = formant_positions
            else:
                results[i][self]["Formant Position"] = float(formant_positions[i])
            results[i][self]["Formant Position Normalization"] = normalization_type

        return results

    # to calcualte the formant position we need the formants at glotal pulses
    def calculate_formant_position(self, formant_mean_lists):
        """Calculate the formant position for each voice.

        :param formant_mean_lists: List of lists of formant means.
        :type formant_mean_lists: list

        :returns: Formant position and normalization type.
        :rtype: tuple of (Union[float, str, list, np.ndarray], str)
        """
        if len(formant_mean_lists[0]) < 30:
            return "Not enough samples, requires at least 30", "Not enough samples, requires at least 30"

        # Normality test for mean data
        _, p_f1_mean = stats.normaltest(formant_mean_lists[0])
        _, p_f2_mean = stats.normaltest(formant_mean_lists[1])
        _, p_f3_mean = stats.normaltest(formant_mean_lists[2])
        _, p_f4_mean = stats.normaltest(formant_mean_lists[3])

        # Check if data are normally distributed, if not, use Robust Scaler, if so, use Standard Scaler (z-score).
        if p_f1_mean >= 0.5 or p_f2_mean >= 0.5 or p_f3_mean >= 0.5 or p_f4_mean >= 0.5:
            scalar = RobustScaler
            scalar_type = "Robust"
        else:
            scalar = StandardScaler
            scalar_type = "z-score"

        zf1_mean = scalar().fit_transform((np.array(formant_mean_lists[0]).reshape(-1, 1))).reshape(-1, 1)
        zf2_mean = scalar().fit_transform((np.array(formant_mean_lists[1]).reshape(-1, 1))).reshape(-1, 1)
        zf3_mean = scalar().fit_transform((np.array(formant_mean_lists[2]).reshape(-1, 1))).reshape(-1, 1)
        zf4_mean = scalar().fit_transform((np.array(formant_mean_lists[3]).reshape(-1, 1))).reshape(-1, 1)
        pf_mean = (zf1_mean + zf2_mean + zf3_mean + zf4_mean) / 4
        return pf_mean, scalar_type

