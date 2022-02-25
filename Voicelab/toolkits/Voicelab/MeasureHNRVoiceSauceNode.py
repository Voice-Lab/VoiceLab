# -*- coding: utf-8 -*-
from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
import numpy as np
from scipy.fftpack import fft
from scipy.interpolate import interp1d
from scipy.io import wavfile
from scipy.io.wavfile import read as wavread
import librosa


class MeasureHNRVoiceSauceNode(VoicelabNode):

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################
    def process(self):
        #try:
        """Returns harmonic-to-harmonic ratio Voice Sauce Style."""
        filename = self.args["file_path"]
        fs, y = wavread(filename)
        print(f'{y=}')
        #fmin = self.args["min f0"]
        #fmax = self.args["max f0"]
        librosa_y, sr = librosa.load(filename)
        F0 = librosa.yin(librosa_y, fmin=40, fmax=600, sr=sr)

        variables = {
            "Nperiods_EC": 5,
            "frameshift": 1,
        }
        hnrs = run(y, fs, F0, variables)
        print(hnrs)
        return {
            "harmonic-to-harmonic ratio": hrs,

        }

        #except:
        #    return {
        #        "subharmonic-to-harmonic ratio": "Measurement failed",
        #        "Subharmonic Mean Pitch": "Measurement failed",
        #        "Subharmonic Pitch Values": "Measurement failed",
        #        "Subharmonic Pitch": "Measurement failed",
        #    }





"""
Created on Mon Apr 14 21:51:49 2014
@author: Helene
"""
# import numpy as np moved to top of file


def run(y, Fs, F0, variables):
    """
    INPUT
    y, FS - fr wav-read
    F0 - vector of fundamental frequency
    variables - global settings
    OUTPUT
    N vectors
    NOTES
    Calculates the harmonic to noise ration based on the method described in de
    Krom, 1993 - A cepstrum-based technique for determining a harmonic-to-noise
    ratio in speech signals, JSHR.
    AUTHOR
    Yen-Liang Shue, Speech Processing and Auditory Perception Laboratory, UCLA
    Copyright UCLA SPAPL 2009
    """
    N_periods = int(variables['Nperiods_EC'])
    sampleshift = (Fs / (1000 * int(variables['frameshift'])))

    HNR05 = np.zeros(len(F0))# * None
    HNR15 = np.zeros(len(F0))# * None
    HNR25 = np.zeros(len(F0))# * None
    HNR35 = np.zeros(len(F0))# * None

    print('reached the first for loop')
    for k in range(1, len(F0)):  # check this with the k multiplcation stuff below
        print('loop!')
        ks = np.round(k * sampleshift)

        if ks <= 0 or ks > len(y):
            continue

        F0_curr = F0[k]

        if F0_curr == 0:
            continue

        N0_curr = 1/(F0_curr * Fs)

        if not F0_curr:
            continue

        ystart = round(ks - N_periods/2*N0_curr)
        yend = round(ks + N_periods/2*N0_curr)-1

        if (yend-ystart + 1) % 2 == 0:
            yend -= 1

        if ystart <= 0 or yend > len(y):
            continue

        yseg = y[ystart:yend]

        hnr = getHNR(yseg, Fs, F0_curr, [500, 1500, 2500, 3500])

        HNR05[k] = hnr[0]
        HNR15[k] = hnr[1]
        HNR25[k] = hnr[2]
        HNR35[k] = hnr[3]
        print([HNR05, HNR15, HNR25, HNR35])
    return [HNR05, HNR15, HNR25, HNR35]


def getHNR(y, Fs, F0, Nfreqs):
    print('holla')
    print(f'{y=}')
    NBins = len(y)
    print(f'{NBins=}')
    N0 = round(Fs/F0)
    N0_delta = round(N0 * 0.1)
    y = [x*z for x, z in zip(np.hamming(len(y)), y)]
    fftY = np.fft.fft(y, NBins)
    aY = np.log10(abs(fftY))
    ay = np.ifft(aY)

    peakinx = np.zeros(np.floor(len(y))/2/N0)
    for k in range(1, len(peakinx)):
        ayseg = ay[(k*N0 - N0_delta):(k*N0 + N0_delta)]
        val, inx = max(abs(ayseg))  # MAX does not behave the same - doesn't return inx??
        peakinx[k] = inx + (k * N0) - N0_delta - 1

        s_ayseg = np.sign(np.diff(ayseg))

        l_inx = inx - np.find((np.sign(s_ayseg[inx-1:-1:1]) != np.sign(inx)))[0] + 1
        r_inx = inx + np.find(np.sign(s_ayseg[inx+1:]) == np.sign(inx))[0]

        l_inx = l_inx + k*N0 - N0_delta - 1
        r_inx = r_inx + k*N0 - N0_delta - 1

        for num in range(l_inx, r_inx):
            ay[num] = 0

    midL = round(len(y)/2)+1
    ay[midL:] = ay[(midL-1):-1:(midL-1-(len(ay)-midL))]

    Nap = np.real(np.fft(ay))
    N = Nap  # ???? why?
    Ha = aY - Nap  # change these names ffs

    Hdelta = F0/Fs * len(y)
    for f in [num+0.0001 for num in range(Hdelta, round(len(y)/2), Hdelta)]:
        fstart = np.ceil(f - Hdelta)
        Bdf = abs(min(Ha[fstart:round(f)]))
        N[fstart:round(f)] = N[fstart:round(f)] - Bdf

    H = aY - N
    n = np.zeros(len(Nfreqs))

    for k in range(1, len(Nfreqs)):
        Ef = round(Nfreqs[k] / Fs * len(y))
        n[k] = (20 * np.mean(H[1:Ef])) - (20 * np.mean(N[1:Ef]))

    return n