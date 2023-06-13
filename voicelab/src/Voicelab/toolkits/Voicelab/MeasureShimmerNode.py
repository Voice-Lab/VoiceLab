import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ...pipeline.Node import Node
import parselmouth
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode


class MeasureShimmerNode(VoicelabNode):
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
            the largest possible difference between consecutive intervals that will be used in the computation of shimmer
        self.args['maximum_amplitude']: float, default=1.6
            The maximum amplitude factor.  Can't find anything on this in the Praat Manual
            Possibly the largest possible difference between consecutive amplitudes that will be used in the computation of shimmer
        self.args['Measure PCA']: str, default="Yes"

    self.state: dict
        Dictionary of state variables to be passed to the node. This saves the individual shimmer measurements from process(), and passes them to end() for PCA.
            self.state["local_shimmer_list"]: list
            self.state["localdb_shimmer_list"]: list
            self.state["apq3_shimmer"]: list
            self.state["aqpq5_shimmer"]: list
            self.state["apq11_shimmer"]: list
            self.state["dda_shimmer"]: list
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "start_time": 0,   # Positive float or 0
            "end_time": 0,   # Positive float or 0
            "shortest_period": 0.0001,   # Positive number
            "longest_period": 0.02,  # Positive number
            "maximum_period_factor": 1.3,  # Positive number
            "maximum_amplitude": 1.6,  # Positive number
            "Measure PCA": True,
        }

        self.state = {
            "local_shimmer": [],
            "localdb_shimmer": [],
            "apq3_shimmer": [],
            "aqpq5_shimmer": [],
            "apq11_shimmer": [],
            "dda_shimmer": [],
        }

    def end(self, results):
        """
        Args:
            results:
        """
        if self.args["Measure PCA"]:
            pca_results = self.shimmer_pca()
            if pca_results is not None:
                for i, result in enumerate(results):
                    try:
                        results[i][self]["PCA Result"] = float(pca_results[i])
                    except:
                        results[i][self]["PCA Result"] = "Shimmer PCA Failed"
        return results

    def process(self):
        """This function measures Shimmer.
        """

        file_path: str = self.args["file_path"]
        signal, sampling_rate = self.args['voice']
        sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
        try:
            pitch_floor = self.pitch_floor(file_path)
            pitch_ceiling = self.pitch_ceiling(file_path)

            point_process: object = call(
                sound, "To PointProcess (periodic, cc)", pitch_floor, pitch_ceiling
            )

            local_shimmer: float = call(
                [sound, point_process],
                "Get shimmer (local)",
                self.args["start_time"],
                self.args["end_time"],
                self.args["shortest_period"],
                self.args["longest_period"],
                self.args["maximum_period_factor"],
                self.args["maximum_amplitude"],
            )

            localdb_shimmer: float = call(
                [sound, point_process],
                "Get shimmer (local_dB)",
                self.args["start_time"],
                self.args["end_time"],
                self.args["shortest_period"],
                self.args["longest_period"],
                self.args["maximum_period_factor"],
                self.args["maximum_amplitude"],
            )

            apq3_shimmer: float = call(
                [sound, point_process],
                "Get shimmer (apq3)",
                self.args["start_time"],
                self.args["end_time"],
                self.args["shortest_period"],
                self.args["longest_period"],
                self.args["maximum_period_factor"],
                self.args["maximum_amplitude"],
            )

            aqpq5_shimmer: float = call(
                [sound, point_process],
                "Get shimmer (apq5)",
                self.args["start_time"],
                self.args["end_time"],
                self.args["shortest_period"],
                self.args["longest_period"],
                self.args["maximum_period_factor"],
                self.args["maximum_amplitude"],
            )

            apq11_shimmer: float = call(
                [sound, point_process],
                "Get shimmer (apq11)",
                self.args["start_time"],
                self.args["end_time"],
                self.args["shortest_period"],
                self.args["longest_period"],
                self.args["maximum_period_factor"],
                self.args["maximum_amplitude"],
            )

            dda_shimmer: float = call(
                [sound, point_process],
                "Get shimmer (dda)",
                self.args["start_time"],
                self.args["end_time"],
                self.args["shortest_period"],
                self.args["longest_period"],
                self.args["maximum_period_factor"],
                self.args["maximum_amplitude"],
            )

            self.state["local_shimmer"].append(local_shimmer)
            self.state["localdb_shimmer"].append(localdb_shimmer)
            self.state["apq3_shimmer"].append(apq3_shimmer)
            self.state["aqpq5_shimmer"].append(aqpq5_shimmer)
            self.state["apq11_shimmer"].append(apq11_shimmer)
            self.state["dda_shimmer"].append(dda_shimmer)

            return {
                "local_shimmer": local_shimmer,
                "localdb_shimmer": localdb_shimmer,
                "apq3_shimmer": apq3_shimmer,
                "aqpq5_shimmer": aqpq5_shimmer,
                "apq11_shimmer": apq11_shimmer,
                "dda_shimmer": dda_shimmer,
            }
        except Exception as e:
            return {
                "local_shimmer": str(e),
                "localdb_shimmer": str(e),
                "apq3_shimmer": str(e),
                "aqpq5_shimmer": str(e),
                "apq11_shimmer": str(e),
                "dda_shimmer": str(e),
            }

    def shimmer_pca(self):
        try:
            local_shimmer = self.state["local_shimmer"]
            localdb_shimmer = self.state["localdb_shimmer"]
            apq3_shimmer = self.state["apq3_shimmer"]
            aqpq5_shimmer = self.state["aqpq5_shimmer"]
            apq11_shimmer = self.state["apq11_shimmer"]
            dda_shimmer = self.state["dda_shimmer"]

            shimmer_data = pd.DataFrame(
                np.column_stack(
                    [
                        local_shimmer,
                        localdb_shimmer,
                        apq3_shimmer,
                        aqpq5_shimmer,
                        apq11_shimmer,
                        dda_shimmer,
                    ]
                ),
                columns=[
                    "localShimmer",
                    "localdbShimmer",
                    "apq3Shimmer",
                    "apq5Shimmer",
                    "apq11Shimmer",
                    "ddaShimmer",
                ],
            )

            shimmer_data = shimmer_data.dropna()
            # z-score the Shimmer measurements
            measures = [
                "localShimmer",
                "localdbShimmer",
                "apq3Shimmer",
                "apq5Shimmer",
                "apq11Shimmer",
                "ddaShimmer",
            ]

            # Set up the features as x
            x = shimmer_data.loc[:, measures].values
            # Z-score the data
            x = StandardScaler().fit_transform(x)
            # Run the PCA
            pca = PCA(n_components=1)
            principal_components = pca.fit_transform(x)
            shimmer_pca_df = pd.DataFrame(
                data=principal_components, columns=["ShimmerPCA"]
            )
            return shimmer_pca_df.values
        except Exception as e:
            return str(e)
