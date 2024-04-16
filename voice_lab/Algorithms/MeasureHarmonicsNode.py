from __future__ import division
from ...pipeline.Node import Node
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode

import numpy as np
from scipy.io import wavfile
from scipy.fftpack import fft
from scipy.interpolate import interp1d
import scipy.optimize as scio



###################################################################################################
# MEASURE DURATION NODE
# WARIO pipeline node for measuring the duration of a voice.
###################################################################################################
# ARGUMENTS
# 'filename'   : sound path
###################################################################################################
# RETURNS
# 'Subharmonic-to-Harmonic Ratio'  :Subharmonic-to-Harmonic Ratio
# 'Subharmonic Pitch'        :Pitch measured by subharmonics
###################################################################################################


class MeasureHarmonicsNode(VoicelabNode):

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################
    def process(self):
        try:
            """Returns subharmonic-to-harmonic ratio and Pitch from Subharmonics."""
            filename = self.args["file_path"]
            wav_data, wavdata_int, fps = wavread(filename)




            return {
                "H1: Amplitude": H1_amp,
                "H1: Frequency": H1_freq,
                "H2: Amplitude": H2_amp,
                "H2: Frequency": H2_freq,
                "H3: Amplitude": H3_amp,
                "H3: Frequency": H3_freq,

            }

        except Exception as e:
            print(e)
            return {
                "subharmonic-to-harmonic ratio": "Measurement failed",
                "Subharmonic Mean Pitch": "Measurement failed",
                "Subharmonic Pitch Values": "Measurement failed",
                "Subharmonic Pitch": "Measurement failed",
            }





"""Harmonic amplitude estimation
"""

# Licensed under Apache v2 (see LICENSE)



def correction_iseli_i(f, F_i, B_i, fs):
    """Return the i-th correction (dB) to the harmonic amplitude using the
       algorithm developed by Iseli and Alwan. Note this correction should be
       *subtracted* from the amplitude. The total correction is computed by
       subtracting all of the i-th corrections from the amplitude.

       Reference -- M. Iseli and A. Alwan, An improved correction formula for
       the estimation of harmonic magnitudes and its application to open
       quotient estimation.

    Args:
        f      - frequency/harmonic to be corrected (Hz) [NumPy vector]
        F_i    - i-th formant frequency (Hz) [NumPy vector]
        B_i    - i-th formant bandwidth (Hz) [NumPy vector]
        fs     - sampling frequency (Hz)
    Returns:
        corr_i - i-th correction to harmonic amplitude in dB [NumPy vector]
    """
    # These variable names are from the Iseli-Alwan paper
    # Normalize frequencies to sampling frequency
    r_i = np.exp(- np.pi * B_i / fs)
    omega_i = 2 * np.pi * F_i / fs
    omega  = 2 * np.pi * f / fs

    # Factors needed to compute correction
    numerator_sqrt = r_i**2 + 1 - 2 * r_i * np.cos(omega_i)
    denom_factor1 = r_i**2 + 1 - 2 * r_i * np.cos(omega_i + omega)
    denom_factor2 = r_i**2 + 1 - 2 * r_i * np.cos(omega_i - omega)

    # Correction in the z-domain
    # corr = 10 * log10(numerator_sqrt**2 / (denom_factor1 * denom_factor2))
    # Formula simplifies due to logarithm arithmetic
    corr_i = 20 * np.log10(numerator_sqrt) - 10 * np.log10(denom_factor1) - 10 * np.log10(denom_factor2)

    return corr_i

def bandwidth_hawks_miller(F_i, F0):
    """Return formant bandwidth estimated from the formant frequency and the
       fundamental frequency

       For each formant frequency, estimate the bandwidth from a 5th order
       power series with coefficients C1 or C2 depending on whether the
       frequency is less or greater than 500 Hz, then scale by a factor that
       depends on the fundamental frequency.

       Reference -- J.W. Hawks and J.D. Miller, A formant bandwidth estimation
       procedure for vowel synthesis, JASA, Vol. 97, No. 2, 1995

    Args:
        F_i - i-th formant frequency (Hz) [NumPy vector]
        F0  - Fundamental frequency (Hz) [NumPy vector]
    Returns:
        B_i - Bandwidth corresponding to i-th formant (Hz) [NumPy vector]
    """
    # Bandwidth scaling factor as a function of F0,
    # to accommodate the wider bandwidths of female speech
    S = 1 + 0.25 * (F0 - 132) / 88

    # Coefficients C1 (for F_i < 500 Hz) and C2 (F_i >= 500 Hz)
    #
    # There are 6 coefficients for each term in a 5th order power series
    C1 = np.array([165.327516, -6.73636734e-1, 1.80874446e-3, -4.52201682e-6, 7.49514000e-9, -4.70219241e-12])
    C2 = np.array([15.8146139, 8.10159009e-2, -9.79728215e-5, 5.28725064e-8, -1.07099364e-11, 7.91528509e-16])

    # Construct matrix that is a 5th order power series
    # of the formant frequency
    F_i_mat = np.vstack((F_i**0, F_i**1, F_i**2, F_i**3, F_i**4, F_i**5))

    # Construct mask for formant frequency < 500 Hz
    #
    # Set NaN values in F_i to 0, so that when we do the boolean operation
    # F_i < 500, it doesn't throw a runtime error about trying to do boolean
    # operations on NaN, which is an invalid value.
    # It doesn't matter what value we replace NaN with, because regardless of
    # the values in the Boolean mask corresponding to F_i = NaN, these will
    # get multiplied by NaN again in the formant bandwidth estimation below
    # and NaN * False = NaN * True = NaN. Any arithmetic operation on NaN
    # results in another NaN value.
    F_i_dummy = F_i.copy()
    F_i_dummy[np.isnan(F_i_dummy)] = 0
    # Tile/repeat the mask for each of the 6 terms in the power series
    mask_less_500 = np.tile(F_i_dummy < 500, (len(C1), 1))

    # Formant bandwidth estimation
    #
    # For each formant frequency, estimate the bandwidth from a 5th order power
    # series with coefficients C1 or C2 depending on whether the frequency is
    # less or greater than 500 Hz, then scale by a factor that depends on the
    # fundamental frequency
    B_i = S * (np.dot(C1, F_i_mat * mask_less_500) + np.dot(C2, F_i_mat * np.logical_not(mask_less_500)))

    return B_i


def wavread(fn):
    """Read in a 16-bit integer PCM WAV file for processing

    Args:
        fn - filename of WAV file [string]

    Returns:
         y_float - Audio samples in float format [NumPy vector]
         y_int - Audio samples in int format [NumPy vector]
        fs - Sampling frequency in Hz [integer]

    Emulate the parts of the Matlab wavread function that we need.

    Matlab's wavread is used by voicesauce to read in the wav files for
    processing.  As a consequence, all the translated algorithms assume the
    data from the wav file is in matlab form, which in this case means a double
    precision float between -1 and 1.  The corresponding scipy function returns
    the actual integer PCM values from the file, which range between -32768 and
    32767.  (matlab's wavread *can* return the integers, but does not by
    default and voicesauce uses the default).  Consequently, after reading the
    data using scipy's io.wavfile, we convert to float by dividing each integer
    by 32768.

    Also, save the 16-bit integer data in another NumPy vector.

    The input WAV file is assumed to be in 16-bit integer PCM format.
    """
    # For reference, I figured this out from:
    # http://mirlab.org/jang/books/audiosignalprocessing/matlab4waveRead.asp?title=4-2%20Reading%20Wave%20Files
    # XXX: if we need to handle 8 bit files we'll need to detect them and
    # special case them here.
    try:
        fs, y = wavfile.read(fn)
    except ValueError:
        raise
    if y.dtype != 'int16':
        raise IOError('Input WAV file must be in 16-bit integer PCM format')

    return y/np.float64(32768.0), y, fs


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


def toframes(samples, curpos, segmentlen, window_type):
    last_index = len(samples) - 1
    num_frames = len(curpos)
    start = curpos - int(round(segmentlen/2))
    offset = np.arange(segmentlen)
    index_start = np.nonzero(start < 1)[0]
    start[index_start] = 0
    endpos = start + segmentlen - 1
    index = np.nonzero(endpos > last_index)[0]
    endpos[index] = last_index
    start[index] = last_index + 1 - segmentlen
    frames = samples[(np.tile(np.expand_dims(start, 1),
                     (1, segmentlen)) + np.tile(offset, (num_frames, 1)))]
    window_vector = np.tile(window(segmentlen, window_type), (num_frames, 1))
    return np.multiply(frames, window_vector)


# ---- voicing ----
# func_Get_SHRP does not use these, because CHECK_VOICING is always 0

def postvda(segment, curf0, Fs, r_threshold):
    raise NotImplementedError


def zcr(x, dur):
    raise NotImplementedError


# ---- window -----
def _pi_arange(width):
    return 2*np.pi*np.arange(width)/(width-1)


def _not_implemented():
    raise NotImplementedError


def _triangular(n):
    m = (n-1)/2
    res = np.arange(np.floor(m+1))/m
    return np.append(res, res[int(np.ceil(m))-1::-1])

def rect(n):
    return np.ones(n)

def hann(n):
    return 0.5*(1 - np.cos(_pi_arange(n)))

def hamm(n):
    return 0.54 - 0.46 * np.cos(_pi_arange(n))

def blac(n):
    return (0.42 - 0.5*np.cos(_pi_arange(n)) + 0.08*np.cos(2*_pi_arange(n)))

def kais(n):
    return _not_implemented()



window_funcs = dict(
    rect = rect,
    tria = _triangular,
    hann = hann,
    hamm = hamm,
    blac = blac,
    kais = kais,
    )

def window(width, window_type, beta=None):
    """Generate a window function (1 dim ndarray) of length width.

    Given a window_type from the list 'rectangular', 'triangular', 'hanning',
    'hamming', 'blackman', 'kaiser', or at least the first four characters of
    one of those strings, return a 1 dimensional ndarray of floats expressing a
    window function of length 'width' using the 'window_type'.  'beta' is an
    additional input for the kaiser algorithm.  (XXX: kaiser is not currently
    implemented.)

    """
    algo = window_funcs.get(window_type[:4])
    if algo is None:
        raise ValueError(
            "Unknown window algorithm type {!r}".format(window_type))
    return algo(width)


def get_log_spectrum(segment, fftlen, limit, logf, interp_logf):
    spectra = fft(segment, fftlen)
    # "fftlen is always even here."
    amplitude = np.abs(spectra[0:fftlen//2+1])
    # "ignore the zero frequency component"
    amplitude = amplitude[1:limit+2]
    interp_amplitude = interp1d(logf, amplitude)(interp_logf)
    interp_amplitude = interp_amplitude - min(interp_amplitude)
    return interp_amplitude



def two_max(x, lowerbound, upperbound, unit_len):
    """Return up to two successive maximum peaks and their indices in x.

    Return the magnitudes of the peaks and the indices as two lists.
    If the first maximum is less than zero, just return it.  Otherwise
    look to the right of the first maximum, and if there is a second
    maximum that is greater than zero, add that to the returned lists.

    lowerbound and upperbound comprise a closed interval, unlike the
    normal python half closed interval.  [RDM XXX: fix this?]

    """
    # XXX The above description is not completely accurate: there's a window to
    # the search for the second peak, but I don't understand the goal well
    # enough to describe it better, and the original comments are less precise.
    max_index = min(upperbound, len(x)-1)
    # "find the maximum value"
    mag = np.array([np.amax(x[lowerbound:upperbound+1])])
    index = np.where(x == mag)[0]
    if mag < 0:
        return mag, index
    harmonics = 2
    limit = 0.0625  # "1/8 octave"
    startpos = index[0] + int(round(np.log2(harmonics-limit)/unit_len))
    if startpos <= max_index:
        # "for example, 100hz-200hz is one octave, 200hz-250hz is 1/4octave"
        endpos = index[0] + int(round(np.log2(harmonics + limit)/unit_len))
        endpos = min(max_index, endpos)
        # "find the maximum value at right side of last maximum"
        mag2 = np.amax(x[startpos:endpos+1])
        index2 = np.where(x[startpos:] == mag2)[0][0] + startpos
        if mag2 > 0:
            mag = np.append(mag, mag2)
            index = np.append(index, index2)
    return mag, index


# ---- vda -----
# func_Get_SHRP does not use this, because CHECK_VOICING is always 0
def vda(x, segmentdur, noisefloor, minzcr):
    raise NotImplementedError


# ---- ethreshold -----
# Although present in the matlab source this function is not used.

def ethreshold(frames):
    """Determine energy threshold for silence."""
    raise NotImplementedError



def getHarmonics(data,f_est,Fs):
    pi = np.pi
    exp = np.exp
    log10 = np.log10
    # this function is used from 1/8/09 onwards - optimization used
    #--------------------------------------------------------------------------
    #printf('FUNC_GETHARMONICS...\n');
    # find harmonic magnitudes in dB of time signal x
    # around a frequency estimate f_est
    # Fs, sampling rate
    # x, input row vector (is truncated to the first 25ms)
    # df_range, optional, default +-5    # of f_est

    df = 0.1    # search around f_est in steps of df (in Hz)
    df_range = round(f_est*df)    # search range (in Hz)

    f_min = f_est - df_range
    f_max = f_est + df_range

    f = func_EstMaxVal(x, data, Fs)


    #options = optimset('Display', 'off')
    #options = optimset('Display', 'off', 'OutputFcn', []);
    # fn = fieldnames(options);
    # for k=1:length(fn)
    # printf('opt(     #s )\n', fn{k});
    # end
    # return;


    #[x, val, exitflag, output] = fmincon(f, f_est, [], [], [], [], f_min, f_max, [], options);
    #[x, val, exitflag, output] = fminsearchbnd(f, f_est, f_min, f_max, options);

    x, val, exitflag, output = fminsearchbnd2(f, f_est, f_min, f_max)

    h = -1 * val
    fh = x

    return h, fh


def func_EstMaxVal(x, data, Fs):
    # x is the F0 estimate
    v = []
    for n in range(0,len(data)):
        v[n] = exp(-1j*2*pi*x*n/Fs)
        val = -1 * 20*log10(abs(data * v))
    return val


def fminsearchbnd(fxn, x0, LB, UB, options=None):
    exitflag, output = 0, 0
    xsize = len(x0)
    x0 = x0[:]
    n = len(x0)
    assert n == len(LB)
    assert n == len(UB)

# "optimset"
    options = {"FunValCheck": "off",
               "MaxFunEvals": 400,
               "MaxIter": 400,
               "OutputFcn": [],
               "TolFun": 1.0*(10**(-7)),
               "TolX": 1.0*(10**(-4)) }

    params = {}
    params["LB"] = LB
    params["UB"] = UB
    params["fxn"] = fxn
    params["n"] = n
    params["OutputFcn"] = []
    params["BoundClass"] = np.zeros(n)

    output = {}

    for i in range(n):
        k = np.isfinite(LB[i]) + 2 * np.isfinite(UB[i])
        params["BoundClass"][i] = k
        if k == 3 and LB[i] == UB[i]:
            params["BoundClass"][i] = 4

    x0u = x0
    k = 1
    for i in range(n):
        switch = params["BoundClass"][i]

        if switch == 1:
            if x0[i] <= LB[i]:
                x0u[k] = 0
            else:
                x0u[k] = np.sqrt(x0[i] - LB[i])
            k += 1

        elif switch == 2:
            if x0[i] >= UB[i]:
                x0u[k] = 0
            else:
                x0u[k] = np.sqrt(UB[i] - x0[i])
            k += 1

        elif switch == 3:
            if x0[i] <= LB[i]:
                x0u[k] = -1 * np.pi / 2
            elif x0[i] >= UB[i]:
                x0u[k] = np.pi / 2
            else:
                x0u[k] = 2 * (x0[i] - LB[i])/(UB[i] - LB[i]) - 1
                x0u[k] = 2 * np.pi + np.arcsin(max(-1, min(1, x0u[k])))
            k += 1

        elif switch == 0:
            x0u[k] = x0[i]
            k += 1

        elif switch == 4:
            pass

        else:
            print "bad switch?"

    if k <= n:
        x0u[k:n] = []

    if len(x0u) == 0:
        x = xtransform(x0u, params)
        x = np.reshape(x, xsize)
        fval = feval(params["fxn"], x, params.keys()[:])
        exitflag = 0
        output["iterations"] = 0
        output["funcount"] = 1
        output["algorithm"] = "fminsearch"
        output["message"] = "all variables were held fixed"

    if options.has_key("OutputFcn"):
        print "should be unreachable??"

    # options = {"FunValCheck": "off",
    #            "MaxFunEvals": 400,
    #            "MaxIter": 400,
    #            "OutputFcn": [],
    #            "TolFun": 1.0*(10**(-7)),
    #            "TolX": 1.0*(10**(-4)) }

    xtol = options["TolX"]
    ftol = options["TolFun"]
    maxiter = options["Maxiter"]
    (xu, fval, iters, funcalls, warnflag, allvecs) = scio.fminsearch(intrafun, x0u, xtol=xtol, ftol=ftol, maxiter=maxiter)
    x = xtransform(xu, params)
    x = np.reshape(x, xsize)

    # TODO outfun_wrapper


def feval(funcName, *args):
    return eval(funcName)(*args)

def intrafun(x, params):
    xtrans = xtransform(x, params)
    fval = feval(params["fxn"], xtrans, params.keys()[:])

def xtransform(x, params):
    xtrans = np.zeros((1, params["n"]))
    k = 1
    for i in range(params["n"]):
        switch = params["BoundClass"]
        if switch == 1:
            k += 1
        elif switch == 2:
            k += 1
        elif switch == 3:
            xtrans[i] = np.sin(x[k]+1)/2
            xtrans[i] = xtrans[i] * (params["UB"][i] - params["LB"][i]) + params["LB"][i]
            xtrans[i] = max(params["LB"][i], min(params["UB"][i], xtrans[i]))
            k += 1
        elif switch == 4:
            k += 1
        else:
            k += 1




