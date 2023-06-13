#############################
#
#  This script makes pitch tracks of the requested wav file and allows post-processing of the pitch tracks for smoothing/stylization.
 
#  Currently, only *.wav files are read.  Textgrids are ignored.
#
#  Input parameters include (in this order):
#  Input file, Time step, Minimum Pitch, Maximum Pitch, Silence Threshold,  
#  Voicing Threshold, Octave cost, octave-Jump Cost, Voiced/unvoiced cost, Kill octave jumps, Smooth, Interpolate, Method (ac or cc)
#
#  For each input, it creates a tab delimited text file with
#  measurement results in the same folder.  The file consists
#  of a pitch track created by the cross-correlation method (cc) or autocorrelation method.  Results  are saved as a *.cc or *.ac file
#############################

form Create Pitch Tracks
   comment See header of script for details. 

   comment Directory of input sound files
   text wavfile D:\tmp\

#   sentence Sound_file_extension .wav
#   comment Directory of TextGrid files
#   text textGrid_directory D:\tmp\
#   sentence TextGrid_file_extension .TextGrid
#   comment Full path of the resulting text file:
#   text resultfile D:\tmp\pitchresults.txt

# KY 20101013: edited to allow user input for all parameters and for ultrasmoothed (stylized) f0 contours

# kill octave jumps tries to remove pitch halving/doubling 
# smoothing allows smoothing at a given bandwidth in Hz
# interpolation allows interpolation over missing values (it is not clear to me if this linear, cubic spline, or what)

   comment F0 Measurement Parameters
   positive time_step 0.005
   positive minimum_pitch 50
   positive maximum_pitch 500
   positive silence_threshold 0.03
   positive voicing_threshold 0.45
   positive octave_cost 0.01
   positive octave_jump_cost 0.35
   positive voiced_unvoiced_cost 0.14
   boolean kill_octave_jumps no
   boolean smooth no
   positive smooth_bandwidth 5
   boolean interpolate no
   sentence Method cc
endform


# A sound file is opened
Read from file... 'wavfile$'
soundname$ = selected$ ("Sound", 1)

# KY 20101013: edited to allow user input for all parameters

# Allow cross or auto correlation
if method$ = "cc" 
    To Pitch (cc)... 'time_step' 'minimum_pitch' 15 no 'silence_threshold' 'voicing_threshold' 'octave_cost' 'octave_jump_cost' 'voiced_unvoiced_cost' 'maximum_pitch'
else
  To Pitch (ac)... 'time_step' 'minimum_pitch' 15 no 'silence_threshold' 'voicing_threshold' 'octave_cost' 'octave_jump_cost' 'voiced_unvoiced_cost' 'maximum_pitch'
endif

# KY 20101013:Postprocessing for smoothing/stylization

if 'kill_octave_jumps' = 1
    Kill octave jumps
endif

# Smooth 
if 'smooth' = 1
    Smooth... smooth_bandwidth
endif

# Interpolate over missing values

if 'interpolate' = 1
    Interpolate
endif

Down to PitchTier

# Write to file	
if method$ = "cc" 
    resultfile$ = "'wavfile$'.praatcc"
else
    resultfile$ = "'wavfile$'.praatac"
endif

# Check if the result file exists:
if fileReadable (resultfile$)
	filedelete 'resultfile$'
endif

Write to headerless spreadsheet file... 'resultfile$'
