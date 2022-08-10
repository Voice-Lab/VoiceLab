from Voicelab.pipeline.Node import Node
import parselmouth
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
import numpy as np
from scipy.fftpack import fft
from scipy.interpolate import interp1d
from scipy.io import wavfile

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


class MeasureSHRPNode(VoicelabNode):
    def __init__(self, *args, **kwargs):

        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {

        }


    def process(self, filename=None, *args, **kwargs):
        """Returns subharmonic-to-harmonic ratio and Pitch from Subharmonics."""

        try:
            if filename is None:
                filename = self.args['file_path']
            # filename = self.args["file_path"]
            # If it's an mp3, convert it to wav
            if filename[-3:].lower() != "wav":
                signal, sampling_rate = self.args['voice']
                tmp_praat_object: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
                # If it's stereo, convert it to mo
                number_of_channels = call(tmp_praat_object, 'Get number of channels')
                if number_of_channels == 2:
                    tmp_praat_object = call(tmp_praat_object, 'Convert to mono')
                tmp_praat_object.save("tmp.wav", "WAV")
                filename = 'tmp.wav'


            wav_data, wavdata_int, fps = wavread(filename)
            shr, f0 = shr_pitch(wav_data, fps, datalen=200)
            mean_shr = np.nanmean(shr)
            median_shr = np.nanmedian(shr)
            sd_shr = np.nanstd(shr)


            mean_f0 = np.nanmean(f0)
            return {
                "subharmonic-to-harmonic ratio": mean_shr.item(),
                "Subharmonic Mean Pitch": mean_f0.item(),
                "Subharmonic Median Pitch": median_shr.item(),
                "Subharmonic Stdev of Pitch": sd_shr.item(),
                "Subharmonic Pitch Values": f0.tolist() # padded or truncated to 200 values
            }



        except Exception as e:
            return {
                "subharmonic-to-harmonic ratio": str(e),
                "Subharmonic Mean Pitch": str(e),
                "Subharmonic Median Pitch": str(e),
                "Subharmonic Stdev of Pitch": str(e),
                "Subharmonic Pitch Values": str(e),
            }


""" 
SHRP - a pitch determination algorithm based on subharmonic-to-harmonic ratio.
"""

# Licensed under Apache v2 (see LICENSE)

# imports moved to top of file import numpy as np
# imports moved to top of file from scipy.fftpack import fft
# imports moved to top of file from scipy.interpolate import interp1d
# imports moved to top of file from scipy.io import wavfile
# Comments in quotes are copied from the matlab source.


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



# ---- func_GetSHRP ----

# Based func_GetSHRP.m from voicesauce v1.25, by Kristine Yu, which in turn was
# based on func_PraatPitch.m by Yen-Liang Shue.



def shr_pitch(wav_data, fps, window_length=None, frame_shift=1,
              min_pitch=50, max_pitch=500, shr_threshold=None,
              frame_precision=1, datalen=None):
    """Return a list of Subharmonic ratios and F0 values computed from wav_data.

    wav_data        a vector of data read from a wav file
    fps             frames rate of the wav file
    windows_length  width of analysis window
    frame_shift     distance to move window for each analysis iteration
    min_pitch       minimum pitch in Hz used in SHR estimation
    max_pitch       maximum pitch in Hz used in SHR estimation
    shr_threshold   subharmonic-to-harmonic ratio threshold in the range of
                        [0,1].  If the estimated SHR is greater than the
                        threshold, the subharmonic is regarded as F0 candidate.
                        Otherwise, the harmonic is favored.
    frame_precision maximum number of frames the time alignment can be off
                        by when selecting values for output
    datalen         the number of values in the output vector; leftover
                        input data is dropped, and the vector is padded
                        with NaNs when no input data corresponds to
                        the output frame time.

    """
    # XXX the octave code produces 201 output points given a datalen
    # of 200.  Presumably a bug in the matlab code.  But we'll emulate it.
    datalen += 1
    kw = {}
    # XXX This is awkward, fix it in refactoring later.
    if len(list(filter(None, (min_pitch, max_pitch)))) == 1:
        raise ValueError('none or both of min_pitch, max_pitch must be specified')
    elif min_pitch:
        kw['F0MinMax'] = (min_pitch, max_pitch)
    if window_length is not None:
        kw['frame_length'] = window_length
    if frame_shift is not None:
        kw['timestep'] = frame_shift
    if shr_threshold is not None:
        kw['SHR_Threshold'] = shr_threshold
    f0_time, f0_value, shr_value, f0_candidates = shrp(wav_data, fps, **kw)

    # "Postprocess subharmonic-harmonic ratios and f0 tracks"

    # "Initialize F0 and subharmonic-harmonic ratio values"
    F0 = np.full(datalen, np.nan)
    SHR = np.full(datalen, np.nan)

    # "time locations rounded to nearest ms"
    #
    # VoiceSauce uses Matlab, and Matlab's round function uses the
    # round-half-away-from-zero method.  However, NumPy uses the
    # round-half-to-even method.  So we use our own round-half-away-from-zero
    # method here.
    t = round_half_away_from_zero(f0_time)

    # "Like timecoures from Praat, we might have missing values so pad with NaNs at
    # beginning and end if necessary."
    # RDM XXX note that it looks to me like after the leading NaN padding this
    # actually ends up padding with frame_precision copies of the first frame
    # that comes within the precision window, and then offsets all of the
    # others by frame_precision*frame_shift.  This algorithm could use a lot of
    # improvement I think.  But for now, we are emulating the voicesauce code.
    start = 0
    finish = t[-1]
    increment = frame_shift
    for k in np.arange(start, finish, increment):
        # "try to find the closest value"
        dabs = np.abs(t - k)
        inx = np.argmin(dabs)
        if dabs[inx] > frame_precision * frame_shift:
            # "no valid value found"
            continue
        n = int(round(k / frame_shift)) + 1
        if n < 0 or n >= datalen:
            continue
        F0[n] = f0_value[inx]
        SHR[n] = shr_value[inx]
        # "I eventually would like to get candidates as well"
    return SHR, F0


# Remainder based on the shrp.m from voicesauce v1.25.
# XXX: This is not a full re-implementation of shrp.m: it only implements those
# functions actually used by the voicesauce func_GetSHRP function.

# Original copyright notice from above referenced shrp.m:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Permission to use, copy, modify, and distribute this software without fee is
#  hereby granted FOR RESEARCH PURPOSES only, provided that this copyright
#  notice appears in all copies and in all supporting documentation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For details of the algorithm, please see Sun, X.,"Pitch determination and
#  voice quality analysis using subharmonic-to-harmonic ratio" To appear in
#  the Proc. of ICASSP2002, Orlando, Florida, May 13 -17, 2002.  For update
#  information, please check http://mel.speech.nwu.edu/sunxj/pda.htm.
#
#  Copyright (c) 2001 Xuejing Sun
#  Department of Communication Sciences and Disorders
#  Northwestern University, USA
#  sunxj@northwestern.edu
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Function definitions are ordered the same as in the matlab source.


# ---- shrp -----

def shrp(Y, Fs, F0MinMax=[50, 500], frame_length=40, timestep=10,
         SHR_Threshold=0.4, ceiling=1250, med_smooth=0, CHECK_VOICING=0):
    """Return pitches for list of samples using subharmonic-to-harmonic ratio.

    Given:

        Y               input data
        Fs              sampling frequency (e.g.: 16000 Hz)
        F0MinMax        tuple [minf0 maxf0]; default: [50 550]
                            quick solutions:
                                for male speech: [50 250]
                                for female speech: [120 400]
        frame_length    length of each frame in milliseconds (default: 40 ms)
        TimeStep        interval for updating short-term analysis in
                            millisecond (default: 10 ms)
        SHR_Threshold   subharmonic-to-harmonic ratio threshold in the range of
                            [0,1] (default: 0.4).  If the estimated SHR is
                            greater than the threshold, the subharmonic is
                            regarded as F0 candidate. Otherwise, the harmonic
                            is favored.
        Ceiling         upper bound of the frequencies that are used for
                            estimating pitch. (default: 1250 Hz)
        med_smooth      the order of the median smoothing (default: 0 - no
                            smoothing)
        CHECK_VOICING   NOT IMPLEMENTED

    Return:

        f0_time:        an array of the times for the F0 points
        f0_value:       an array of the F0 values
        SHR:            an array of the subharmonic-to-harmonic ratio for each
                            frame
        f0_candidates:  a matrix of the f0 candidates for each frame.
                            Currently two f0 values generated for each frame.
                            Each row (a frame) contains two values in
                            increasing order, i.e., [low_f0 higher_f0].  For
                            SHR=0, the first f0 is 0. The purpose of this is
                            that when you want to test different SHR
                            thresholds, you don't need to re-run the whole
                            algorithm. You can choose to select the lower or
                            higher value based on the shr value of this frame.
    """
    minf0, maxf0 = F0MinMax
    segmentduration = frame_length

    # "--- pre-processing input signal ---"
    # "remove DC component"
    Y = Y - np.mean(Y)
    # "normalization"
    Y = Y/np.max(np.abs(Y))
    total_len = len(Y)
    # "--- specify some algorithm-specific thresholds ---"
    # "for FFT length"
    interpolation_depth = 0.5
    # "--- derived thresholds specific to the algorithm ---"
    maxlogf = np.log2(maxf0 / 2)
    # "the search region to compute SHR is as low as 0.5 minf0"
    minlogf = np.log2(minf0 / 2)
    # "maximum number harmonics"
    N = int(np.floor(ceiling / minf0))
    m = int(N % 2)
    N = N - m
    # "In fact, in most cases we don't need to multiply N by 4 and get equally
    # good results yet much faster."
    N = N * 4
    # "derive how many frames we have based on segment length and timestep."
    segmentlen = int(np.around(segmentduration * (Fs / 1000)))
    inc = int(np.around(timestep * (Fs / 1000)))
    nf = int(np.fix((total_len - segmentlen + inc) / inc))
    n = np.arange(nf)
    # "anchor time for each frame, the middle point"
    f0_time = np.transpose((n * timestep + segmentduration/2))
    # f0_time = np.transpose(((n - 1) * timestep)) # anchor starting from zero
    # "--- determine FFT length ---"
    fftlen = 1
    while fftlen < segmentlen * (1 + interpolation_depth):
        fftlen = fftlen * 2
    # "--- derive linear and log frequency scale ---"
    # "we ignore frequency 0 here since we need to do log transformation later
    # and won't use it anyway."
    frequency = Fs * np.arange(1, fftlen/2+1) / fftlen
    limit = np.where(frequency >= ceiling)[0][0]
    frequency = frequency[0:limit+1]
    logf = np.log2(frequency)
    # "clear some variables to save memory"
    del frequency
    # "the minimum distance between two points after interpolation"
    min_bin = logf[-1] - logf[-2]
    # "shift distance"
    shift = np.log2(N)
    # "the number of unit on the log x-axis"
    shift_units = int(np.around(shift/min_bin))
    i = np.arange(2, N+1)
    # "--- the followings are universal for all the frames ---"
    # "find out all the start position of each shift"
    startpos = shift_units + 1 - np.around(np.log2(i) / min_bin).astype(int)
    # "find out those positions that are less than 1"
    index = np.where(startpos < 1)[0]
    # set them to 1 since the array index starts from 1 in matlab"
    startpos[index] = 1
    # Correct for the fact that python is 0 origined, not 1.
    # XXX: I wonder if keeping the zeros and not doing this subtraction
    # would actually be more accurate.  Probably makes no real difference.
    startpos = startpos - 1
    interp_logf = np.arange(logf[0], logf[-1], min_bin)
    # "new length of the amplitude spectrum after interpolation"
    interp_len = len(interp_logf)
    totallen = shift_units + interp_len
    endpos = startpos + interp_len - 1
    index = np.where(endpos >= totallen)[0]
    # "make sure all the end positions not greater than the total length of
    # the shift spectrum"
    endpos[index] = totallen - 1
    # "the linear Hz scale derived from the interpolated log scale"
    newfre = np.power(2, interp_logf)
    # "find out the index of upper bound of search region on the log frequency
    # scale."
    upperbound = np.where(interp_logf >= maxlogf)[0][0]
    # "find out the index of lower bound of search region on the log frequency
    # scale."
    lowerbound = np.where(interp_logf >= minlogf)[0][0]
    # "--- segmentation of speech ---"
    # "position for each frame in terms of index, not time"
    curpos = np.around(f0_time / 1000 * Fs).astype(int) - 1
    frames = toframes(Y, curpos, segmentlen, 'hamm')
    nf, framelen = frames.shape
    del Y
    # "--- initialize vectors for f0 time, f0 values, and SHR ---"
    f0_value = np.zeros(nf)
    SHR = np.zeros(nf)
    f0_time = f0_time[0:nf+1]
    f0_candidates = np.zeros((nf, 2))
    # "--- voicing determination ---"
    if CHECK_VOICING:
        raise NotImplementedError
        #NoiseFloor=sum(frames(1,:).^2);
        #voicing=vda(frames,segmentduration/1000,NoiseFloor);
    else:
        voicing = np.ones(nf)
    # "--- the main loop ---"
    curf0 = 0
    cur_SHR = 0
    cur_cand1 = 0
    cur_cand2 = 0
    for n in range(nf):
        segment = frames[n, :]
        if voicing[n] == 0:
            curf0 = 0
            cur_SHR = 0
        else:
            log_spectrum = get_log_spectrum(
                segment,
                fftlen,
                limit,
                logf,
                interp_logf)
            peak_index, cur_SHR, shshift, all_peak_indices = compute_shr(
                log_spectrum,
                min_bin,
                startpos,
                endpos,
                lowerbound,
                upperbound,
                N,
                shift_units,
                SHR_Threshold)
            # "-1 indicates a possibly unvoiced frame, if CHECK_VOICING, set f0
            # to 0, otherwise uses previous value"
            if peak_index == -1:
                if CHECK_VOICING: # pragma: no cover
                    curf0 = 0
                    cur_cand1 = 0
                    cur_cand2 = 0
            else:
                curf0 = newfre[peak_index] * 2
                if curf0 > maxf0:
                    curf0 = curf0 / 2
                if len(all_peak_indices) == 1:
                    cur_cand1 = 0
                    cur_cand2 = newfre[all_peak_indices[0]] * 2
                else:
                    cur_cand1 = newfre[all_peak_indices[0]] * 2
                    cur_cand2 = newfre[all_peak_indices[1]] * 2
                if cur_cand1 > maxf0:
                    cur_cand1 = cur_cand1 / 2
                if cur_cand2 > maxf0:
                    cur_cand2 = cur_cand2 / 2
                if CHECK_VOICING: # pragma: no cover
                    raise NotImplementedError
                    #voicing(n)=postvda(segment,curf0,Fs);
                    #if (voicing(n)==0)
                    #    curf0=0;
                    #end
        f0_value[n] = curf0
        SHR[n] = cur_SHR
        f0_candidates[n, 0] = cur_cand1
        f0_candidates[n, 1] = cur_cand2
    # "--- post-processing ---"
    if med_smooth > 0:
        raise NotImplementedError
        # medsmooth is by the same author but is not included in voicesauce.
        # f0_value = medsmooth(f0_value, med_smooth)
    return f0_time, f0_value, SHR, f0_candidates


# ---- GetLogSpectrum -----

def get_log_spectrum(segment, fftlen, limit, logf, interp_logf):
    spectra = fft(segment, fftlen)
    # "fftlen is always even here."
    amplitude = np.abs(spectra[0:fftlen//2+1])
    # "ignore the zero frequency component"
    amplitude = amplitude[1:limit+2]
    interp_amplitude = interp1d(logf, amplitude)(interp_logf)
    interp_amplitude = interp_amplitude - min(interp_amplitude)
    return interp_amplitude


# ---- ComputeSHR -----

def compute_shr(log_spectrum, min_bin, startpos, endpos, lowerbound, upperbound,
                n, shift_units, shr_threshold):
    """ "compute subharmonic-to-harmonic ratio for a short-term signal"

       returns peak_index = -1 if frame appears to be unvoiced.
    """
    len_spectrum = len(log_spectrum)
    total_len = shift_units + len_spectrum
    # "initialize the subharmonic shift matrix; each row corresponds to a shift
    # version"
    shshift = np.zeros((n, total_len))
    # "place the spectrum at the right end of the first row"
    shshift[0, total_len-len_spectrum:total_len] = log_spectrum
    # "note that here startpos and endpos has n-1 rows, so we start from 2"
    # "the first row in shshift is the original log spectrum"
    # Actually we start from 1 since python is zero-origined.
    for i in range(1, n):
        # "store each shifted sequence"
        shshift[i, startpos[i-1]:endpos[i-1]+1] = (
            log_spectrum[:endpos[i-1]-startpos[i-1]+1])
    # "we don't need the stuff smaller than shift_units"
    shshift = shshift[:, shift_units:total_len]
    # odd and even are reversed from matlab due to different origin
    shseven = sum(shshift[0:n:2, :], 0)
    shsodd = sum(shshift[1:n-1:2, :], 0)
    difference = shsodd - shseven
    # "peak picking process"
    shr = 0
    # "only find two maxima"
    mag, index = two_max(difference, lowerbound, upperbound, min_bin)
    # "first mag is always the maximum, the second, if there is, is the second
    # max"
    num_pitch_candidates = len(mag)
    if num_pitch_candidates == 1:
        # "this is possible, mainly due to we put a constraint on search region,
        # i.e., f0 range"
        if mag <= 0:
            # "this must be an unvoiced frame"
            peak_index = -1
            return peak_index, shr, shshift, index
        peak_index = index
        shr = 0
    else:
        shr = (mag[0]-mag[1]) / (mag[0]+mag[1])
        if shr <= shr_threshold:
            # "subharmonic is weak, so favor the harmonic"
            peak_index = index[1]
        else:
            # "subharmonic is strong, so favor the subharmonic as F0"
            peak_index = index[0]
    return peak_index, shr, shshift, index


# ---- twomax -----

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


# ---- toframes ----

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

#window_funcs = dict(
#    rect = lambda n: np.ones(n),
#    tria = _triangular,
#    hann = lambda n: 0.5*(1 - np.cos(_pi_arange(n))),
#    hamm = lambda n: 0.54 - 0.46*np.cos(_pi_arange(n)),
#    blac = lambda n: (0.42 - 0.5*np.cos(_pi_arange(n)) + 0.08*np.cos(2*_pi_arange(n))),
#    kais = lambda n: _not_implemented(),
#    )

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


