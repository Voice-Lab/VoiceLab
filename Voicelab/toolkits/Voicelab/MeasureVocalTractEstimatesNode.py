from __future__ import annotations

import sklearn.decomposition

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from Voicelab.toolkits.Voicelab.MeasureFormantPositionsNode import MeasureFormantPositionsNode
from typing import Union
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA



class MeasureVocalTractEstimatesNode(VoicelabNode):
    """Measure Voice Tract Estimates Node

    Arguments:
    ----------
    self.args: dict
        Dictionary of arguments passed to the node
        self.args["Measure Formant PCA"]: bool
            Whether to measure the formant PCA
        self.args["Measure Formant Positions"]: bool
            Whether to measure the formant positions
        self.args["Measure Formant Dispersion"]: bool
            Whether to measure the formant dispersion
        self.args["Measure Average Formant"]: bool
            Whether to measure the average formant
        self.args["Measure Geometric Mean"]: bool
            Whether to measure the geometric mean
        self.args["Measure Fitch VTL"]: bool
            Whether to measure Fitch VTL
        self.args["Measure Delta F"]: bool
            Whether to measure Delta F
        self.args["Measure VTL Delta F"]: bool
            Whether to measure VTL Delta F


    self.state: dict
        Dictionary of state variables passed to the node. This includes the mean formants measured by MeasureFormantsNode.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "Measure Formant PCA": True,  # Formant PCA is messed up and needs re-written
            "Measure Formant Positions": True,
            "Measure Formant Dispersion": True,
            "Measure Average Formant": True,
            "Measure Geometric Mean": True,
            "Measure Fitch VTL": True,
            "Measure Delta F": True,
            "Measure VTL Delta F": True,
        }
        self.state = {
            "f1 means": [],
            "f2 means": [],
            "f3 means": [],
            "f4 means": [],
            "f1 medians": [],
            "f2 medians": [],
            "f3 medians": [],
            "f4 medians": [],
        }

    def process(self):
        """Estimate Vocal Tract Length using several methods
        The process node runs on each sound file in the pipeline run, and passes the data on to state for processing in the end() method run.

        Returns:
        --------
        :return: A dictionary of the results or an error message. The number of varaibles returned depends on the arguments passed to the node.
        :rtype: dict[str, Union[float, str]
        """
        try:
            # F1 - F4 Means are calculated in the MeasureFormantNode
            f1: float = self.args["F1 Mean"]
            f2: float = self.args["F2 Mean"]
            f3: float = self.args["F3 Mean"]
            f4: float = self.args["F4 Mean"]

            self.state["f1 means"].append(f1)
            self.state["f2 means"].append(f2)
            self.state["f3 means"].append(f3)
            self.state["f4 means"].append(f4)

            if self.args["Measure Formant Dispersion"]:
                formant_dispersion: Union[float, str] = self.get_formant_dispersion(f1=f1, f4=f4)
            else:
                formant_dispersion = "Not Selected"

            if self.args["Measure Average Formant"]:
                average_formant: Union[float, str] = self.get_average_formant(f1=f1, f2=f2, f3=f3, f4=f4)
            else:
                average_formant = "Not Selected"

            if self.args["Measure Geometric Mean"]:
                geometric_mean: Union[float, str] = self.get_geometric_mean(f1=f1, f2=f2, f3=f3, f4=f4)
            else:
                geometric_mean = "Not Selected"

            if self.args["Measure Fitch VTL"]:
                fitch_vtl: Union[float, str] = self.get_fitch_vtl(f1=f1, f2=f2, f3=f3, f4=f4)
            else:
                fitch_vtl = "Not Selected"

            # Reby Method
            if self.args["Measure Delta F"]:
                delta_f: Union[float, str] = self.get_delta_f(f1=f1, f2=f2, f3=f3, f4=f4)
            else:
                delta_f: Union[float, str] = "Not Selected"

            if self.args["Measure VTL Delta F"]:
                vtl_delta_f: Union[float, str] = self.get_vtl_delta_f(f1=f1, f2=f2, f3=f3, f4=f4)
            else:
                vtl_delta_f: Union[float, str] = "Not Selected"

            return {
                "formant_dispersion": formant_dispersion,
                "average_formant": average_formant,
                "geometric_mean": geometric_mean,
                "fitch_vtl": fitch_vtl,
                "delta_f": delta_f,
                "vtl_delta_f": vtl_delta_f,
            }

        except Exception as e:
            return {
                "formant_dispersion": str(e),
                "average_formant": str(e),
                "geometric_mean": str(e),
                "fitch_vtl": str(e),
                "delta_f": str(e),
                "vtl_delta_f": str(e),
                "PCA": str(e),
            }
    # PCA analysis is run once for all files, so we want to hook up an event for when this is
    def end(self, results):
        """ This node does all of the vocal tract length calculations. To employ this code outside of the VoiceLab GUI, you'll need to supply a state dictionary with 4 keys:

            - self.state["f1 means"]
            - self.state["f2 means"]
            - self.state["f3 means"]
            - self.state["f4 means"]

            In the GUI, these are supplied via self (ie they are instance attributes).

        Each of those values should be a list of the formant means for each file.

        You'll also need to supply a dictionary of the arguments to the node. The keys are set in the process() method in the GUI, but you can set them on your own. They are as follows:

            - "Measure Formant PCA": True
            - "Measure Formant Positions": True
            - "Measure Formant Dispersion": True
            - "Measure Average Formant": True
            - "Measure Geometric Mean": True
            - "Measure Fitch VTL": True
            - "Measure Delta F": True
            - "Measure VTL Delta F": True

        As of now, all measurements except Formant Positions are calculated in this function (I know, I know).  Formant Positions are calculated in the FormantPositionsNode, and is documented :ref:`here <Formant-Position>`.

        :argument results: The results of the pipeline run.
        :type results: dict

        :return: The selected vocal-tract-length estimates or an error message, or note that some measurements were not selected.
        :rtype: dict of Union[float, str]
        """

        formant_mean_lists: list[list[float], list[float], list[float], list[float]] = [
            self.state["f1 means"],
            self.state["f2 means"],
            self.state["f3 means"],
            self.state["f4 means"],
        ]

        if self.args["Measure Formant PCA"]:
            # Check if there's a reasonable enough sample size to run a PCA.
            if len(self.state["f1 means"]) < 2:
                principal_components: Union[float, str] = 'Not enough samples for PCA analysis'
            else:
                # If there is enough data, run the PCA
                principal_components: Union[np.ndarray, str]
                pca: sklearn.decomposition.PCA
                principal_components, pca = self.get_formants_pca()

            # Populate results list with the principal components or an error message
            for i, result in enumerate(results):
                print(f'{principal_components=}')
                if isinstance(principal_components, str):
                    results[i][self]["PCA"]: Union[float, str] = principal_components
                    results[i][self]["PCA % Variance Explained"]: Union[float, str] = principal_components
                else:
                    results[i][self]["PCA"]: Union[float, str] = principal_components[i].item()
                    results[i][self]["PCA % Variance Explained"]: Union[float, str] = pca.explained_variance_ratio_[0].item() * 100

        if self.args["Measure Formant Positions"]:
            try:
                # Calculate formant position
                formant_positions, normalization_method = self.get_formant_positions(formant_mean_lists)

                # Add the formant positions to the results.
                for i, result in enumerate(results):
                    if isinstance(formant_positions, str):
                        results[i][self]["Formant Position"]: Union[float, str, list, np.ndarray] = formant_positions
                    else:
                        print(f'{formant_positions[i]=}')
                        results[i][self]["Formant Position"] = float(formant_positions[i])
                    results[i][self]["Formant Position Normalization Method"]: str = normalization_method
            except Exception as e:
                for i, result in enumerate(results):
                    if 'formant_positions' in locals():
                        if isinstance(formant_positions, str):
                            results[i][self]["Formant Position"] = str(e)
                        else:
                            results[i][self]["Formant Position"] = str(e)
                    else:
                        if results[i][self]["Formant Position"] != 'Not enough samples, requires at least 30':
                            results[i][self]["Formant Position"] = str(e)
        return results

    def get_formant_dispersion(self, f1: Union[float, int], f4: Union[float, int], *args, **kwargs) -> float:
        """Get the formant dispersion from F1 and F4. Since F2 and F3 cancel each other out in the equation, we save
        time and memeory and only ask for the 2 formants. args and kwargs are there in case people add F2 and F3 so
        it doesn't crash

        :argument f1: The first formant in Hz
        :type f1: Union[float, int]
        :argument f4: The fourth formant in Hz
        :type f4: Union[float, int]
        :return: The formant dispersion
        :rtype: float
        """
        return (f4 - f1) / 3

    def get_average_formant(self, f1: Union[float, int], f2: Union[float, int], f3: Union[float, int], f4: Union[float, int]) -> float:
        """Get the average formant from F1, F2, F3, and F4.

        :argument f1: The first formant in Hz
        :type f1: Union[float, int]
        :argument f2: The second formant in Hz
        :type f2: Union[float, int]
        :argument f3: The third formant in Hz
        :type f3: Union[float, int]
        :argument f4: The fourth formant in Hz
        :type f4: Union[float, int]
        :return: The average formant
        :rtype: float
        """
        return (f1 + f2 + f3 + f4) / 4

    def get_geometric_mean(self, f1: float | int, f2: float | int, f3: float | int, f4: float | int) -> float:
        """Get the geometric mean of the formants.

        :argument f1: The first formant in Hz
        :type f1: float | int
        :argument f2: The second formant in Hz
        :type f2: float | int
        :argument f3: The third formant in Hz
        :type f3: float | int
        :argument f4: The fourth formant in Hz
        :type f4: float | int
        :return: The geometric mean of the formants
        :rtype: float
        """

        return (f1 * f2 * f3 * f4) ** 0.25

    def get_fitch_vtl(self, f1, f2, f3, f4):
        """Get Fitch VTL from the formants.

        :argument f1: The first formant in Hz
        :type f1: Union[float, int]
        :argument f2: The second formant in Hz
        :type f2: Union[float, int]
        :argument f3: The third formant in Hz
        :type f3: Union[float, int]
        :argument f4: The fourth formant in Hz
        :type f4: Union[float, int]
        :return: The Fitch VTL
        :rtype: float
        """
        return ((1 * (35000 / (4 * f1))) + (3 * (35000 / (4 * f2))) + (5 * (35000 / (4 * f3))) + (7 * (35000 / (4 * f4)))) / 4

    def get_delta_f(self, f1: float | int, f2: float | int, f3: float | int, f4: float | int) -> float:
        """Get the delta f from the formants.

        :argument f1: The first formant in Hz
        :type f1: Union[float, int]
        :argument f2: The second formant in Hz
        :type f2: Union[float, int]
        :argument f3: The third formant in Hz
        :type f3: Union[float, int]
        :argument f4: The fourth formant in Hz
        :type f4: Union[float, int]
        :return delta_f: The delta f
        :rtype delta_f: float
        """

        xysum: float = (0.5 * f1) + (1.5 * f2) + (2.5 * f3) + (3.5 * f4)
        xsquaredsum: float = (0.5 ** 2) + (1.5 ** 2) + (2.5 ** 2) + (3.5 ** 2)
        delta_f: Union[float, str] = xysum / xsquaredsum
        return delta_f

    def get_vtl_delta_f(self, f1: float, f2: float, f3: float, f4: float) -> float:
        """Get the VTL delta f from the formants.

        :argument f1: The first formant in Hz
        :type f1: Union[float, int]
        :argument f2: The second formant in Hz
        :type f2: Union[float, int]
        :argument f3: The third formant in Hz
        :type f3: Union[float, int]
        :argument f4: The fourth formant in Hz
        :type f4: Union[float, int]
        :return delta_f: The delta f
        :rtype delta_f: float
        """
        delta_f: float = self.get_delta_f(f1, f2, f3, f4)
        return 35000 / (2 * delta_f)

    def get_formants_pca(self):
        """Get the formants from the PCA.


        :return: The PCA of the formants
        :rtype: list

        :return: THe PCA object
        :
        """

        pca_dataframe: pd.DataFrame = pd.DataFrame(
            {
                'F1': self.state["f1 means"],
                'F2': self.state["f2 means"],
                'F3': self.state["f3 means"],
                'F4': self.state["f4 means"],
            }
        )
        # Z-Score the data
        try:
            data_zscored: Union[pd.DataFrame, str] = (pca_dataframe - pca_dataframe.mean()) / pca_dataframe.std()
        except Exception as e:
            data_zscored: Union[pd.DataFrame, str] = str(e)

        # Create pca instance from sklearn
        pca: PCA = PCA(n_components=1)

        # Run the PCA
        try:
            principal_components: Union[np.ndarray, str] = pca.fit_transform(data_zscored)
        except Exception as e:
            principal_components = str(e)
            pca = str(e)
        return principal_components, pca

    def get_formant_positions(
            self,
            formant_mean_lists: list[list[float], list[float], list[float], list[float]]
    ) -> tuple(list, list):
        formant_positions: Union[float, str, list, np.ndarray]
        normalization_method: str
        result_list = []
        measure_formant_positions_instance: MeasureFormantPositionsNode(VoicelabNode) = MeasureFormantPositionsNode()
        formant_positions, normalization_method = measure_formant_positions_instance.calculate_formant_position(
            formant_mean_lists=formant_mean_lists
        )
        return formant_positions, normalization_method
