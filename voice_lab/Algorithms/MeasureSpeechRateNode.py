from __future__ import annotations

import math
import numpy as np

from typing import Union
import parselmouth

from ...pipeline.Node import Node
from parselmouth.praat import call
from .VoicelabNode import VoicelabNode


###########################################################################
#                                                                         #
#  Praat Script Syllable Nuclei                                           #
#  Copyright (C) 2008  Nivja de Jong and Ton Wempe                        #
#                                                                         #
#    This program is free software: you can redistribute it and/or modify #
#    it under the terms of the GNU General Public License as published by #
#    the Free Software Foundation, either version 3 of the License, or    #
#    (at your option) any later version.                                  #
#                                                                         #
#    This program is distributed in the hope that it will be useful,      #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
#    GNU General Public License for more details.                         #
#                                                                         #
#    You should have received a copy of the GNU General Public License    #
#    along with this program.  If not, see http://www.gnu.org/licenses/   #
#                                                                         #
###########################################################################
#
# modified 2010.09.17 by Hugo Quené, Ingrid Persoon, & Nivja de Jong
# Overview of changes:
# + change threshold-calculator: rather than using median, use the almost maximum
#     minus 25dB. (25 dB is in line with the standard setting to detect silence
#     in the "To TextGrid (silences)" function.
#     Almost maximum (.99 quantile) is used rather than maximum to avoid using
#     irrelevant non-speech sound-bursts.
# + add silence-information to calculate articulation rate and ASD (average syllable
#     duration.
#     NB: speech rate = number of syllables / total time
#         articulation rate = number of syllables / phonation time
# + remove max number of syllable nuclei
# + refer to objects by unique identifier, not by name
# + keep track of all created intermediate objects, select these explicitly,
#     then Remove
# + provide summary output in Info window
# + do not save TextGrid-file but leave it in Object-window for inspection
#     (if requested in startup-form)
# + allow Sound to have starting time different from zero
#      for Sound objects created with Extract (preserve times)
# + programming of checking loop for self.args['mindip'] adjusted
#      in the orig version, precedingtime was not modified if the peak was rejected !!
#      var precedingtime and precedingint renamed to currenttime and currentint
#
# + bug fixed concerning summing total pause, feb 28th 2011

# Translated to Python in 2019 by David Feinberg
# - Removed unused varaibles
# - Removed old comments

###########################################################################


# counts syllables of all sound utterances in a directory
# NB unstressed syllables are sometimes overlooked
# NB filter sounds that are quite noisy beforehand
# NB use Silence threshold (dB) = -25 (or -20?)
# NB use Minimum dip between peaks (dB) = between 2-4 (you can first try;
#                                                      For clean and filtered: 4)


class MeasureSpeechRateNode(VoicelabNode):
    """Measure Speech Rate using the script found `here <https://sites.google.com/site/speechrate/Home/praat-script-syllable-nuclei-v2>`_.

    Arguments
    ---------

    self.args: dict
        Dictionary of values passed into the node.

        self.args['silencedb']: Union[float, int]
            The threshold for silence. Decibels are relative to 90.9691 dB, so we use negative dB values.
        self.args['mindib']: Union[float, int]
            The minimum dip between peaks
        self.args['minpause']: Union[float, int]
            The minimum pause duration


"""
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {"silencedb": -25.0,  # negative integer
                     "mindip": 4.0,  # positive integer
                     "minpause": 0.3  # Positive number
                     }

    def process(self):
        """Measure speechrate. 
        
        Returns
        -------
        A dictionary with the following keys (or an error message):

            - "Number of Syllables": voicedcount
                str | Union[float, int, str]
            - "Number of Pauses": npause
                str | Union[float, int, str]
            - "Duratrion(s)": originaldur
                str | Union[float, int, str]
            - "Phonation Time(s)": intensity_duration
                str | Union[float, int, str]
            - "speechrate(Number of Syllables / Duration)": speakingrate
                str | Union[float, int, str]
            - "Articulation Rate(Number of Syllables / phonationtime)": articulationrate,
                str | Union[float, int, str]
            - "ASD(Speaking Time / Number of Syllables)": asd
                str | Union[float, int, str]
        
        """
        try:
            file_path: str = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            snr = call(sound.to_harmonicity(), "Get mean", 0, 0)
            if snr < 60:
                self.args["mindip"] = 2
            originaldur = sound.duration
            intensity = sound.to_intensity(50)
            start = call(intensity, "Get time from frame number", 1)
            nframes = call(intensity, "Get number of frames")
            end = call(intensity, "Get time from frame number", nframes)
            min_intensity = call(intensity, "Get minimum", 0, 0, "Parabolic")
            max_intensity = call(intensity, "Get maximum", 0, 0, "Parabolic")

            # get .99 quantile to get maximum (without influence of non-speech sound bursts)
            max_99_intensity = call(intensity, "Get quantile", 0, 0, 0.99)

            # estimate Intensity threshold
            threshold = max_99_intensity + self.args["silencedb"]
            threshold2 = max_intensity - max_99_intensity
            threshold3 = self.args["silencedb"] - threshold2
            if threshold < min_intensity:
                threshold = min_intensity

            # get pauses (silences) and speakingtime
            textgrid = call(
                intensity,
                "To TextGrid (silences)",
                threshold3,
                self.args["minpause"],
                0.1,
                "silent",
                "sounding",
            )
            silencetier = call(textgrid, "Extract tier", 1)
            silencetable = call(silencetier, "Down to TableOfReal", "sounding")
            npauses = call(silencetable, "Get number of rows")
            speakingtot = 0
            for ipause in range(npauses):
                pause = ipause + 1
                beginsound = call(silencetable, "Get value", pause, 1)
                endsound = call(silencetable, "Get value", pause, 2)
                speakingdur = endsound - beginsound
                speakingtot += speakingdur

            intensity_matrix = call(intensity, "Down to Matrix")
            sound_from_intensity_matrix = call(intensity_matrix, "To Sound (slice)", 1)
            # use total duration, not end time, to find out duration of intdur (intensity_duration)
            # in order to allow nonzero starting times.
            intensity_duration = call(sound_from_intensity_matrix, "Get total duration")
            intensity_max = call(
                sound_from_intensity_matrix, "Get maximum", 0, 0, "Parabolic"
            )
            point_process = call(
                sound_from_intensity_matrix,
                "To PointProcess (extrema)",
                "Left",
                "yes",
                "no",
                "Sinc70",
            )
            # estimate peak positions (all peaks)
            numpeaks = call(point_process, "Get number of points")
            t = [
                call(point_process, "Get time from index", i + 1)
                for i in range(numpeaks)
            ]

            # fill array with intensity values
            timepeaks = []
            peakcount = 0
            intensities = []
            for i in range(numpeaks):
                value = call(
                    sound_from_intensity_matrix, "Get value at time", t[i], "Cubic"
                )
                if value > threshold:
                    peakcount += 1
                    intensities.append(value)
                    timepeaks.append(t[i])

            # fill array with valid peaks: only intensity values if preceding
            # dip in intensity is greater than self.args['mindip']
            validpeakcount = 0
            currenttime = timepeaks[0]
            currentint = intensities[0]
            validtime = []

            for p in range(peakcount - 1):
                following = p + 1
                followingtime = timepeaks[p + 1]
                dip = call(
                    intensity, "Get minimum", currenttime, timepeaks[p + 1], "None"
                )
                diffint = abs(currentint - dip)
                if diffint > self.args["mindip"]:
                    validpeakcount += 1
                    validtime.append(timepeaks[p])
                currenttime = timepeaks[following]
                currentint = call(
                    intensity, "Get value at time", timepeaks[following], "Cubic"
                )

            # Look for only voiced parts
            pitch = sound.to_pitch_ac(
                0.02, 30, 4, False, 0.03, 0.25, 0.01, 0.35, 0.25, 450
            )
            voicedcount: int = 0
            voicedpeak = []

            for time in range(validpeakcount):
                querytime = validtime[time]
                whichinterval = call(textgrid, "Get interval at time", 1, querytime)
                whichlabel = call(textgrid, "Get label of interval", 1, whichinterval)
                value = pitch.get_value_at_time(querytime)
                if not math.isnan(value):
                    if whichlabel == "sounding":
                        voicedcount += 1
                        voicedpeak.append(validtime[time])

            # calculate time correction due to shift in time for Sound object versus
            # intensity object
            timecorrection = originaldur / intensity_duration

            # Insert voiced peaks in TextGrid
            call(textgrid, "Insert point tier", 1, "syllables")
            for i in range(len(voicedpeak)):
                position = voicedpeak[i] * timecorrection
                call(textgrid, "Insert point", 1, position, "")

            # return results
            speakingrate = voicedcount / originaldur
            articulationrate = voicedcount / speakingtot
            npause = npauses - 1
            if voicedcount != 0:
                asd = speakingtot / voicedcount
            else:
                asd = np.nan

            return {
                "Number of Syllables": voicedcount,
                "Number of Pauses": npause,
                "Duratrion(s)": originaldur,
                "Phonation Time(s)": intensity_duration,
                "speechrate(Number of Syllables / Duration)": speakingrate,
                "Articulation Rate(Number of Syllables / phonationtime)": articulationrate,
                "ASD(Speaking Time / Number of Syllables)": asd,
            }
        except Exception as e:
            return {
                "Number of Syllables": str(e),
                "Number of Pauses": str(e),
                "Duratrion(s)": str(e),
                "Phonation Time(s)": str(e),
                "speechrate(Number of Syllables / Duration)": str(e),
                "Articulation Rate(Number of Syllables / phonationtime)": str(e),
                "ASD(Speaking Time / Number of Syllables)": str(e),
            }
