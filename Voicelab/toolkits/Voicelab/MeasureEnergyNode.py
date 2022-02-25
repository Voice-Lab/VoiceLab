from Voicelab.pipeline.Node import Node
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

import numpy as np
import librosa
from parselmouth.praat import call
import parselmouth
import pysptk
from scipy.io.wavfile import read as wavread
import pandas as pd


class MeasureEnergyNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "pitch algorithm": ("Praat", ["Praat", "Yin"]),
            "start": 0.0,
            "end": 0.0,
            "number of periods": 5,
            "frameshift": 1,
            'fmin': 40,
            'fmax': 500,

        }  # 0 means select all

    def process(self):
        """
        Get energy of a signal using Algorithm from Voice Sauce ported to Python.
        """

        #try:
        # Get the pitch in order to set a variable window length based on 5 pitch periods
        sound = self.args["voice"]
        audioFilePath = self.args["file_path"]
        self.Fs = sound.sampling_frequency
        self.audioFilePath = self.args["file_path"]
        if isinstance(self.args["pitch algorithm"], tuple):
            self.method = self.args["pitch algorithm"][0]
        else:
            self.method = self.args["pitch algorithm"]
        self.fmin = self.args['fmin']
        self.fmax = self.args['fmax']

        # Get the number of periods in the signal
        N_periods = 5  # Nperiods_EC
        self.N_periods = N_periods
        frameshift = 1  # variables.frameshift
        # y, sr = librosa.load(audioFilePath, sr=16000)
        time_praat, F0_praat = get_raw_pitch(audioFilePath)
        F0 = refine_pitch_voice_sauce(time_praat, F0_praat)
        self.F0 = F0
        sound = parselmouth.Sound(audioFilePath)
        y = sound.values.T
        Fs =  sound.sampling_frequency
        self.Fs = Fs

        sampleshift = (Fs / 1000 * frameshift)
        self.sampleshift = sampleshift

        # Calculate Energy
        E, mean_energy = get_energy_voice_sauce(audioFilePath)

        praat_rms = call(sound, "Get root-mean-square", 0, 0)

        return {
            "Energy Voice Sauce": E,
            "Mean Energy Energy Voice Sauce": mean_energy,
            "RMS Energy Praat": praat_rms,
        }
        #except:
        #    return {
        #        "Energy Voice Sauce": "Measurement failed",
        #        "Mean Energy Voice Sauce": "Measurement failed",
        #        "RMS Energy Praat": "Measurement failed",
        #    }

def get_energy_voice_sauce(audioFilePath):
    """
    Get energy of a signal
    """

    # Get the number of periods in the signal
    N_periods = 5  # Nperiods_EC
    frameshift = 1 # variables.frameshift
    time_praat, F0_praat = get_raw_pitch(audioFilePath)
    F0 = refine_pitch_voice_sauce(time_praat, F0_praat)
    sound = parselmouth.Sound(audioFilePath)
    sound.resample(16000)
    y = sound.values.T
    Fs = sound.sampling_frequency
    sampleshift = (Fs / 1000 * frameshift)

    # Calculate Energy
    E = np.full(len(F0), np.nan)
    for k, F0_curr in enumerate(F0):
        ks = round_half_away_from_zero(k * sampleshift)
        if ks <= 0:
            continue
        if ks >= len(y):
            continue

        F0_curr = F0[k]
        if np.isnan(F0_curr):
            continue
        if F0_curr == 0:
            continue
        N0_curr = Fs / F0_curr
        ystart = int(round_half_away_from_zero(ks - N_periods / 2 * N0_curr))
        yend = int(round_half_away_from_zero(ks + N_periods / 2 * N0_curr) - 1)

        if ystart <= 0:
            continue

        if yend > len(y):
            continue

        yseg = y[ystart:yend]
        E[k] = np.sum(yseg ** 2)
        EWithNoZero = E[E > 0]
        mean_energy = np.nanmean(EWithNoZero)
    return E.tolist(), mean_energy.item()

def get_raw_pitch(audioFilePath):
    """
    get pitch from audio file
    """
    sound = parselmouth.Sound(audioFilePath)
    sound.resample(16000)
    pitch = sound.to_pitch_cc(
        time_step=0.001,
        pitch_floor=40,
        pitch_ceiling=500,
    )
    pitch_tier = call(pitch, "Down to PitchTier")
    call(pitch_tier, "Write to headerless spreadsheet file", "parselmouth_cc.txt")
    df = pd.read_csv('parselmouth_cc.txt', sep='\t', header=None)
    df.columns = ['Time', 'Frequency']
    return df.Time.values, df.Frequency.values

def refine_pitch_voice_sauce(times, frequencies):
    """Estimate F0 and formants using Praat

    """

    # Licensed under Apache v2 (see LICENSE)
    # Based on VoiceSauce files func_PraatPitch.m (authored by Yen-Liang Shue
    # and Kristine Yu) and func_PraatFormants.m (authored by Yen-Liang Shue and
    # Kristine Yu)


    # Praat will sometimes set numerical values to the string '--undefined--'
    # But NumPy can't have a string in a float array, so we convert the
    # '--undefined--' values to NaN
    # Python 3 reads the undefined strings as byte literals, so we also have to
    # check for the byte literal b'--undefined--'
    undef = lambda x: np.nan if x == '--undefined--' or x == b'--undefined--' else x
    frame_shift = 1
    frame_precision = 1
    # Gather raw Praat F0 estimates
    t_raw, F0_raw = np.array(times), np.array(frequencies)
    data_len = len(t_raw)
    # Initialize F0 measurement vector with NaN
    F0 = np.full(data_len, 0, dtype=float)
    # Convert time from seconds to nearest whole millisecond
    t_raw_ms = np.int_(round_half_away_from_zero(t_raw * 1000))

    # Raw Praat estimates are at time points that don't completely match
    # the time points in our measurement vectors, so we need to interpolate.
    # We use a crude interpolation method, that has precision set by
    # frame_precision.

    # Determine start and stop times
    start = 0
    if t_raw_ms[-1] % frame_shift == 0:
        stop = t_raw_ms[-1] + frame_shift
    else:
        stop = t_raw_ms[-1]
    # Iterate through timepoints corresponding to each frame in time range
    for idx_f, t_f in enumerate(range(start, stop, frame_shift)):
        # Find closest time point among calculated Praat values
        min_idx = np.argmin(np.abs(t_raw_ms - t_f))

        # If closest time point is too far away, skip
        if np.abs(t_raw_ms[min_idx] - t_f) > frame_precision * frame_shift:
            continue

        # If index is in range, set value of F0
        if (idx_f >= 0) and (idx_f < data_len): # pragma: no branch
            F0[idx_f] = F0_raw[min_idx]
    return F0

def round_half_away_from_zero(x):
    """Rounds a number according to round half away from zero method
    Args:
        x - number [float]
    Returns:
        q - rounded number [integer]
    For example:
       round_half_away_from_zero(3.5) = 4
       round_half_away_from_zero(3.2) = 3
       round_half_away_from_zero(-2.7) = -3
       round_half_away_from_zero(-4.3) = -4
    The reason for writing our own rounding function is that NumPy uses the
    round-half-to-even method. There is a Python round() function, but it
    doesn't work on NumPy vectors. So we wrote our own
    round-half-away-from-zero method here.
    """
    q = np.int_(np.sign(x) * np.floor(np.abs(x) + 0.5))

    return q