from __future__ import annotations

from typing import Union

import numpy as np
import parselmouth

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

class MeasureJitterNode(VoicelabNode):
    """Measure Jitter using each algorithm from Praat. Also provides an option to take a 1-factor PCA of the results.

    Arguments:
    ----------
    self.args: dict
        Dictionary of arguments to be passed to the node.
        self.args["file_path"]: str, default=0.0
            path to the file to be analyzed
        self.args['start_time']: float, default=0.0
            start time of the analysis
        self.args['end_time']: float, default=0.0001
            end time of the analysis
        self.args['shortest_period']: float
            shortest period to be considered
        self.args['longest_period']: float, default=0.02
            longest period to be considered
        self.args['maximum_period_factor']: float, default=1.3
            the largest possible difference between consecutive intervals that will be used in the computation of jitter
        self.args['Measure PCA']: bool, default=True

    self.state: dict
        Dictionary of state variables to be passed to the node. This saves the individual jitter measurements from process(), and passes them to end() for PCA.
            self.state["local_jitter_list"]: list
            self.state["localabsolute_jitter_list"]: list
            self.state["rap_jitter_list"]: list
            self.state["ppq5_jitter_list"]: list
            self.state["ddp_jitter_list"]: list
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "start_time": 0.0,
            "end_time": 0.0,
            "shortest_period": 0.0001,
            "longest_period": 0.02,
            "maximum_period_factor": 1.3,
            "Measure PCA": True,
        }

        self.state = {
            "local_jitter_list": [],
            "localabsolute_jitter_list": [],
            "rap_jitter_list": [],
            "ppq5_jitter_list": [],
            "ddp_jitter_list": [],
        }


    def process(self):
        """measure jitter
        :argument file_path: path to the file to be analyzed
        :type file_path: str

        :return: dictionary of jitter measurements
        :rtype dict:[str, Union[float, int, str]]
        """
        file_path = self.args["file_path"]
        voice = parselmouth.Sound(file_path)

        try:
            print(self.args["Measure PCA"])
            # Call the provided pitch bounds functions
            pitch_floor = self.pitch_floor(file_path)
            pitch_ceiling = self.pitch_ceiling(file_path)

            start_time = self.args["start_time"]
            end_time = self.args["end_time"]
            shortest_period = self.args["shortest_period"]
            longest_period = self.args["longest_period"]
            max_period_factor = self.args["maximum_period_factor"]

            point_process: object = call(
                voice, "To PointProcess (periodic, cc)", pitch_floor, pitch_ceiling
            )

            local_jitter: float = call(
                point_process,
                "Get jitter (local)",
                start_time,
                end_time,
                shortest_period,
                longest_period,
                max_period_factor,
            )

            localabsolute_jitter: float = call(
                point_process,
                "Get jitter (local, absolute)",
                start_time,
                end_time,
                shortest_period,
                longest_period,
                max_period_factor,
            )

            rap_jitter: float = call(
                point_process,
                "Get jitter (rap)",
                start_time,
                end_time,
                shortest_period,
                longest_period,
                max_period_factor,
            )

            ppq5_jitter: float = call(
                point_process,
                "Get jitter (ppq5)",
                start_time,
                end_time,
                shortest_period,
                longest_period,
                max_period_factor,
            )

            ddp_jitter: float = call(
                point_process,
                "Get jitter (ddp)",
                start_time,
                end_time,
                shortest_period,
                longest_period,
                max_period_factor,
            )

            self.state["local_jitter_list"].append(local_jitter)
            self.state["localabsolute_jitter_list"].append(localabsolute_jitter)
            self.state["rap_jitter_list"].append(rap_jitter)
            self.state["ppq5_jitter_list"].append(ppq5_jitter)
            self.state["ddp_jitter_list"].append(ddp_jitter)

            return {
                "Local Jitter": local_jitter,
                "Local Absolute Jitter": localabsolute_jitter,
                "RAP Jitter": rap_jitter,
                "ppq5 Jitter": ppq5_jitter,
                "ddp Jitter": ddp_jitter,
            }
        except:
            return {
                "Local Jitter": "Jitter Measurement Failed",
                "Local Absolute Jitter": "Jitter Measurement Failed",
                "RAP Jitter": "Jitter Measurement Failed",
                "ppq5 Jitter": "Jitter Measurement Failed",
                "ddp Jitter": "Jitter Measurement Failed",
            }

    def jitter_pca(self):
        """perform PCA on the jitter measurements

        These arguments are passed into the method by self.
        :argument local_jitter_list: list of local jitter measurements
        :type local_jitter_list: list
        :argument localabsolute_jitter_list: list of local absolute jitter measurements
        :type localabsolute_jitter_list: list
        :argument rap_jitter_list: list of rap jitter measurements
        :type rap_jitter_list: list
        :argument ppq5_jitter_list: list of ppq5 jitter measurements
        :type ppq5_jitter_list: list
        :argument ddp_jitter_list: list of ddp jitter measurements
        :type ddp_jitter_list: list

        :return principal_components: list of PCA values or an error message
        :rtype principal_components: Union[list, str]
        """
        local_jitter_list = self.state["local_jitter_list"]
        localabsolute_jitter_list = self.state["localabsolute_jitter_list"]
        rap_jitter_list = self.state["rap_jitter_list"]
        ppq5_jitter_list = self.state["ppq5_jitter_list"]
        ddp_jitter_list = self.state["ddp_jitter_list"]
        x = [
            local_jitter_list,
            localabsolute_jitter_list,
            rap_jitter_list,
            ppq5_jitter_list,
            ddp_jitter_list,
        ]

        try:
            # Z-score the data
            x = StandardScaler().fit_transform(x).T
            # Run the PCA
            pca = PCA(n_components=1)
            # Extract the components
            principal_components = pca.fit_transform(x).tolist()

        except:
            principal_components = "PCA Failed"

        return principal_components

    def end(self, results):
        """This method calls the jitter_pca method and returns the PCA results to the main program/

        :argument results: dictionary of jitter measurements
        :type results: dict
        :return results: dictionary of jitter measurements
        :rtype results: dict[str, Union[float, int, str]]
        """
        if self.args["Measure PCA"]:
            pca_results = self.jitter_pca()
            pca_results = [result[0] for result in pca_results]
            if pca_results is not None:
                print(f'{results=}')
                for i, result in enumerate(results):
                    try:
                        results[i][self]["PCA Result"] = pca_results[i]
                    except:
                        results[i][self]["PCA Result"] = ["Jitter PCA Failed"]
        return results
