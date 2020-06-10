import pandas as pd
import numpy as np
from scipy import stats

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode


class MeasureFormantNode(VoicelabNode):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.args = {
            "time step": 0.0025,  # a zero value is equal to 25% of the window length
            "max number of formants": 5,  # always one more than you are looking for
            "window length(s)": 0.025,
            "pre emphasis from": 50,
            "max_formant": 5500,
        }
        self.state = {
            "f1 means": [],
            "f2 means": [],
            "f3 means": [],
            "f4 means": [],
        }

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################
    def process(self):
        "formants"
        sound = self.args["voice"]
        audioFilePath = self.args["file_path"]

        active_widgets = self.list_loaded_voices.selectedItems()
        active_files = [i.text() for i in active_widgets]

        # Step 1 get formant values from Praat's Manual
        f1 = self.args["F1 Mean"]
        f2 = self.args["F2 Mean"]
        self.state["f1 means"].append(f1)
        self.state["f2 means"].append(f2)
        praat_manual_formant_data = pd.DataFrame(active_files, f1, f2, columns=["File", "F1", "F2"])
        print(praat_manual_formant_data.head())

        # Step 2 classify vowels using kmeans
        x = praat_manual_formant_data[['F1 Bark', 'F2 Bark']].values  # Put data into a matrix
        praat_manual_formant_data['F1 Bark'] = hz_to_bark(praat_manual_formant_data['F1'])
        praat_manual_formant_data['F2 Bark'] = hz_to_bark(praat_manual_formant_data['F2'])
        number_of_clusters = determine_number_of_clusters_gmm(x)
        # Determine best number of vowels with Gausian Mixture Model
        # Get "Vowels" from kmeans
        praat_manual_formant_data['vowels'] = classify_data_kmeans(praat_manual_formant_data, number_of_clusters)
        print(praat_manual_formant_data.head())
        # Step 3 For each vowel, find the set of input parameters that minimize F1F2 variance
        ceiling_df = ceiling_sweep(sound)  # todo figure out how to get this data into state

        # Step 4 return those measures



def hz_to_bark(hz):
    bark = 7 * np.log(hz / 650 + np.sqrt(1 + (hz / 650) ** 2))
    return bark


def determine_number_of_clusters_gmm(x):
    cv_types = ['spherical', 'tied', 'diag', 'full']
    models = []
    clusters = []
    cvs = []
    for cv_type in cv_types:
        for number_of_clusters in range(1, 11):
            model = GaussianMixture(number_of_clusters, covariance_type=cv_type, random_state=0).fit(x)
            models.append(model)
            clusters.append(number_of_clusters)
            cvs.append(cv_type)
    bics = [(model.bic(x), cluster, cv) for model, cluster, cv in zip(models, clusters, cvs)]
    lowest_bic = min(bics)[0]
    number_of_clusters = min(bics)[1]
    covariance_type = min(bics)[2]
    print(f'number_of_clusters {number_of_clusters}')
    print(f'covariance type {covariance_type}')
    print(f'BIC {lowest_bic}')
    prediction = GaussianMixture(number_of_clusters, covariance_type=covariance_type, random_state=0).fit_predict(x)
    model = GaussianMixture(number_of_clusters, covariance_type=covariance_type, random_state=0)
    return number_of_clusters


def draw_ellipse(position, covariance, ax=None, **kwargs):
    """Draw an ellipse with a given position and covariance"""
    ax = ax or plt.gca()

    # Convert covariance to principal axes
    if covariance.shape == (2, 2):
        U, s, Vt = np.linalg.svd(covariance)
        angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        angle = 0
        width, height = 2 * np.sqrt(covariance)

    # Draw the Ellipse
    for nsig in range(1, 4):
        ax.add_patch(Ellipse(position, nsig * width, nsig * height,
                             angle, **kwargs))

def plot_gmm(gmm, X, label=True, ax=None):
    ax = ax or plt.gca()
    labels = gmm.fit(X).predict(X)
    if label:
        ax.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis', zorder=2)
    else:
        ax.scatter(X[:, 0], X[:, 1], s=40, zorder=2)
    ax.axis('equal')

    w_factor = 0.2 / gmm.weights_.max()
    for pos, covar, w in zip(gmm.means_, gmm.covariances_, gmm.weights_):
        draw_ellipse(pos, covar, alpha=w * w_factor)

def plot_means(df, model):
    x = df[['F1 Bark', 'F2 Bark']].values
    gmm = model
    plot_gmm(gmm, x)
    fig1 = plt.gcf()
    plt.show()
    fig1.savefig('f1-f2-GMM.png')
    return plt

def classify_data_gmm(df):
    df.dropna()
    df['F1 Bark'] = hz_to_bark(df['F1'])
    df['F2 Bark'] = hz_to_bark(df['F2'])
    x = df[['F1 Bark', 'F2 Bark']].values
    number_of_clusters, covariance_type = determine_number_of_clusters_gmm(x)
    df['Vowel'] = prediction[0]
    return df, model, number_of_clusters, covariance_type

def determine_number_of_clusters_kmeans(x):
    models = []
    clusters = []
    inertias = []
    for number_of_clusters in range(1, 11):
        model = KMeans(n_clusters=number_of_clusters, random_state=0, n_jobs=-1)
        model.fit(df[['F1 Bark', 'F2 Bark']])
        models.append(model)
        clusters.append(number_of_clusters)
        inertias.append(model.inertia_)
        print(f'inertia {model.inertia_}')
    inertia_clusters = list(zip(inertias, clusters))
    lowest_inertia = min(inertia_clusters)[0]
    number_of_clusters = min(inertia_clusters)[1]
    print(f'number_of_clusters {number_of_clusters}')
    print(f'lowest_inertia {lowest_inertia}')
    return number_of_clusters, model

def classify_data_kmeans(df, number_of_clusters):
    df.dropna()
    df['F1 Bark'] = hz_to_bark(df['F1'])
    df['F2 Bark'] = hz_to_bark(df['F2'])
    x = df[['F1 Bark', 'F2 Bark']].values
    kmean = KMeans(n_clusters=number_of_clusters, random_state=0, n_jobs=-1)
    vowels = kmean.fit_predict(x)
    return vowels

def kmeans_n_clusters(df, n):
    kmean = KMeans(n_clusters=n, random_state=0, n_jobs=-1)
    kmean.fit(df[['F1 Bark', 'F2 Bark']])
    print('Cluster centres:\n', kmean.cluster_centers_)

def plot_kmeans(df, kmean):
    sns.lmplot(data=df, x='F1 Bark', y='F2 Bark', hue='Vowel', palette="husl", fit_reg=False)
    fig1 = plt.gcf()
    means = list(kmean.cluster_centers_)
    colours = ['g', 'r', 'y', 'k', 'b']
    for i, value in enumerate(means):
        plt.scatter(means[i][0], means[i][1], s=200, c=colours[i], marker='s')
    plt.show()
    fig1.savefig('f1-f2-kmeans.png')
    return plt

def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)

def classify_vowels(self, df):
    df, model, number_of_clusters, covariance_type = classify_data_gmm(df)
    plot_means(df, model)
    print(df.head())
    df.to_csv('tmp.csv')
    return df

def ceiling_sweep(sound):
    lower_range = 4000
    upper_range = 6000
    frequency_steps = 10
    for ceiling in range(lower_range, upper_range, frequency_steps):
        formants = measure_formants(sound, ceiling)
        f1f2 = (20 * math.log10(formants[0])) + (20 * math.log10(formants[1]))
        f1f2_list.append(f1f2)
        formants_list.append(formants)
        ceiling_list.append(ceiling)
    ceiling_df = pd.DataFrame(ceiling_list, f1f2_list)
    print(ceiling_df.head())
    return ceiling_df

def calculate_best_ceiling(list_of_files):
    vowel_classification_data = vowel_classifier.classify_vowels(list_of_files)
    ceilings = [ceiling_sweep(filename) for filename in glob.glob(f'{directory}*.wav')]
    df = pd.DataFrame(ceilings, vowel_classification_data)
    df['Variance'] = df.groupby['Vowel'].var()
    print(df.head())
    # minimum_variance = ceiling_data["variance"].min()
    # best_ceiling = df[df['f1f2_list'] == minimum_variance]['ceiling_list']

def measure_the_files(directory):
    formant_data: list = []
    for i, filename in enumerate(file_list):
        this_file = str(filename[2:])
        for current_ceiling in list_of_ceilings:  # go through the list of ceilings
            if this_file == current_ceiling[0]:  # pick the right ceiling for this person
                ceiling = current_ceiling[1].item()  # need .item() here because it's a numpy array, not a number
        full_filename = f"{directory}{filename}"  # reconstruct the filename that corresponds to the person and vowel
        formants = measure_formants(full_filename, ceiling)
        formant_data.append(formants)
    formant_datas = pd.DataFrame(formant_data)
    cols = ["F1", "F2", "F3", "F4"]
    formant_datas.columns = cols
    formant_datas["Voice"] = file_list
    vowels_df = vowel_classifier.classify_data(formant_datas)
    formant_datas = pd.concat(formant_datas, vowels_df)
    print(formant_datas.head())
    formant_datas.to_csv(f'{directory}formant_data_young.csv')

