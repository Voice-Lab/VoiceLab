import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

from PyQt5.QtWidgets import QMessageBox

###################################################################################################
# MEASURE FORMANTS NODE
# WARIO pipeline node for measuring the formants of a voice
###################################################################################################
# PIPELINE ARGUMENTS
# 'voice' :
# 'time step':
# 'max number of formants':
# 'window length(s):
# 'pre emphasis from'
# 'pitch floor'
# 'pitch ceiling'
# 'method': Option tuple for the praat algorithm to use, 0 = selected value, 1 = available options
# 'maximum formant': Maximum formant. Default is to dynamically calculate during runtime
###################################################################################################
# RETURNS
###################################################################################################


class MeasureFormantNode(VoicelabNode):
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "time step": 0.0025,  # a zero value is equal to 25% of the window length
            "max number of formants": 5,  # always one more than you are looking for
            "window length(s)": 0.025,
            "pre emphasis from": 50,
            "max_formant": 5500,
            "Ceiling Step Size": 0.025,
            'Number of Steps': 5,
            # 'method': ('formants_praat_manual', ['formants_praat_manual', 'sweep']),
            # 'Measure PCA': True
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

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################
    def process(self):
        """formants"""
        try:
            sound = self.args["voice"]
            # measure_PCA = self.args['Measure PCA']

            # Generate max_formant parameter
            self.args["max_formant"] = self.formant_max(sound)

            formant_path_object = call(sound,
                                       "To FormantPath (burg)",
                                       self.args["time step"],
                                       self.args["max number of formants"],
                                       self.args["max_formant"],
                                       self.args["window length(s)"],
                                       self.args["pre emphasis from"],
                                       self.args["Ceiling Step Size"],
                                       self.args['Number of Steps'])
            formant_object = call(formant_path_object, "Extract Formant")

            #formant_object = sound.to_formant_burg(
            #    self.args["time step"],
            #    self.args["max number of formants"],
            #    self.args["max_formant"],
            #    self.args["window length(s)"],
            #    self.args["pre emphasis from"],
            #)

            f1_mean = call(formant_object, "Get mean", 1, 0, 0, "Hertz")
            f2_mean = call(formant_object, "Get mean", 2, 0, 0, "Hertz")
            f3_mean = call(formant_object, "Get mean", 3, 0, 0, "Hertz")
            f4_mean = call(formant_object, "Get mean", 4, 0, 0, "Hertz")

            f1_median = call(formant_object, "Get quantile", 1, 0, 0, "Hertz", 0.5)
            f2_median = call(formant_object, "Get quantile", 2, 0, 0, "Hertz", 0.5)
            f3_median = call(formant_object, "Get quantile", 3, 0, 0, "Hertz", 0.5)
            f4_median = call(formant_object, "Get quantile", 4, 0, 0, "Hertz", 0.5)

            results = {
                "F1 Mean": f1_mean,
                "F2 Mean": f2_mean,
                "F3 Mean": f3_mean,
                "F4 Mean": f4_mean,
                "F1 Median": f1_median,
                "F2 Median": f2_median,
                "F3 Median": f3_median,
                "F4 Median": f4_median,
                "Formants": formant_object,
            }

            # save the current formants to the state variable so they can accessed in the callback
            # self.state['f1 means'].append(f1_mean)
            # self.state['f2 means'].append(f2_mean)
            # self.state['f3 means'].append(f3_mean)
            # self.state['f4 means'].append(f4_mean)

            # self.state['f1 medians'].append(f1_median)
            # self.state['f2 medians'].append(f2_median)
            # self.state['f3 medians'].append(f3_median)
            # self.state['f4 medians'].append(f4_median)
        except:
            results = {
                "F1 Mean": "Formant measurement failed",
                "F2 Mean": "Formant measurement failed",
                "F3 Mean": "Formant measurement failed",
                "F4 Mean": "Formant measurement failed",
                "F1 Median": "Formant measurement failed",
                "F2 Median": "Formant measurement failed",
                "F3 Median": "Formant measurement failed",
                "F4 Median": "Formant measurement failed",
                "Formants": "Formant measurement failed",
            }
        return results

    # PCA analysis is run once for all files, so we want to hook up an event for when this is
    def end(self, results):
        # formant_mean_lists = [
        #     self.state['f1 means'],
        #     self.state['f2 means'],
        #     self.state['f3 means'],
        #     self.state['f4 means'],
        # ]

        # formant_median_lists = [
        #     self.state['f1 medians'],
        #     self.state['f2 medians'],
        #     self.state['f3 medians'],
        #     self.state['f4 medians'],
        # ]

        # if self.args['Measure PCA']:
        #     # If we havn't already, we want to register a callback function to run pca
        #     # analysis once all of the files have been processed
        #     principal_components_means , principal_components_medians = self.formant_pca(formant_mean_lists, formant_median_lists)

        # for i, result in enumerate(results):

        #     results[i][self]['PCA_means'] = float(principal_components_means[i, 0])
        #     results[i][self]['PCA_medians'] = float(principal_components_medians[i, 0])

        """
        Args:
            results:
        """
        return results

    def formant_max(self, voice):
        """
        Args:
            voice:
        """
        try:
            pitch_floor, pitch_ceiling = self.pitch_bounds(voice)
            pitch = call(
                voice, "To Pitch", 0.0, pitch_floor, pitch_ceiling
            )  # check pitch to set formant settings
            mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")

            if 170 <= mean_f0 <= 300:
                max_formant = 5500

            elif mean_f0 < 170:
                max_formant = 5000

            else:
                max_formant = 8000

            return max_formant
        except:

            return 5500

    ###############################################################################################
    # formant_pca : Performs principle component analysis on the measured formants
    ## ARGUMENTS
    # + formants : Mean values for a list of formants
    ## RETURNS
    # - principle_components:
    ###############################################################################################
    def formant_pca(self, formant_mean_lists, formant_median_lists):

        """
        Args:
            formant_mean_lists:
            formant_median_lists:
        """
        formant_mean_data = pd.DataFrame(
            np.column_stack(
                [
                    formant_mean_lists[0],
                    formant_mean_lists[1],
                    formant_mean_lists[2],
                    formant_mean_lists[3],
                ]
            ),
            columns=["f1_mean", "f2_mean", "f3_mean", "f4_mean"],
        )
        formant_median_data = pd.DataFrame(
            np.column_stack(
                [
                    formant_median_lists[0],
                    formant_median_lists[1],
                    formant_median_lists[2],
                    formant_median_lists[3],
                ]
            ),
            columns=["f1_median", "f2_median", "f3_median", "f4_median"],
        )
        measures = ["f1_mean", "f2_mean", "f3_mean", "f4_mean"]
        x_means = formant_mean_data.loc[:, measures].values
        x_means = StandardScaler().fit_transform(x_means)
        pca_means = PCA(n_components=1)
        principal_components_means = pca_means.fit_transform(x_means)

        measures = ["f1_median", "f2_median", "f3_median", "f4_median"]
        x_medians = formant_median_data.loc[:, measures].values
        x_medians = StandardScaler().fit_transform(x_medians)
        pca_medians = PCA(n_components=1)
        principal_components_medians = pca_medians.fit_transform(x_medians)

        return principal_components_means, principal_components_medians
