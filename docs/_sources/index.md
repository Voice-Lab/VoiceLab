% This Sphynx rst file depends on sphinxcontrib-inlinesyntaxhighlight

# Voice Lab Interface

```{eval-rst}
.. highlight:: rst
```

```{eval-rst}
.. role:: python(code)
    :language: python
```

```{eval-rst}
.. toctree::
    :numbered:
    :maxdepth: 2
```



Voice Lab is an automated voice analysis software. What this software does is allow you to measure, manipulate, and visualize many voices at once, without messing with analysis parameters. You can also save all of your data, analysis parameters, manipulated voices, and full colour spectrograms with the press of one button.

Voice Lab is written in Python and relies heavily on a package called parselmouth-praat. parselmouth-praat is a Python package that essentially turns Praat's source code written in C and C++ into a Pythonic interface. What that means is that any praat measurement in this software is using actual Praat source code, so you can trust the underlying algorithms. Voice Lab figures out all of the analysis parameters for you, but you can always use your own, and these are the same parameters as in Praat, and they do the exact same thing because it is Praat's source code powering everything. That means if you are a beginner an expert, or anything in-between, you can use this software to automate your acoustical analyses.

All of the code is open source and available on our GitHub repository, so if this manual isn't in-depth enough, and you want to see exactly what's going on, go for it. It is under the MIT license, so you are free to do what you like with the software as long as you give us credit. For more info on that license, see here.

## Load Voices Tab

```{image} _static/LoadVoices.png
:alt: Load voices window
:width: 400
```

### Load Sound File

Press this button to load sound files. You can load as many files as you like.
At the moment, Voice Lab processes the following file types:

- wav
- mp3
- aiff
- ogg
- aifc
- au
- nist
- flac

### Remove Sound File

Use this button to remove the selected sound file(s) from the list.

### Start

Pressing this begins analysis. If you want to run the default analysis, press this button.
If you want to select different analyses or adjust analysis parameters, go to the 'Settings' tab and press the 'Advanced Settings' button.
Only the files selected (in blue) will be analyzed. By default we will select all files.

(settings)=

## Settings Tab

```{image} _static/settings.png
:alt: Settings window
:width: 400
```

To choose different analyses, select the {python}`Use Advanced Settings` checkbox. From here, you'll be given the option to select different analyses. You can also change any analysis parameters. If you do change analysis parameters, make sure you know what you are doing, and remember that those same analysis parameters will be used on all voice files that are selected. If you don't alter these parameters, we determine analysis parameters automatically for you, so they are tailored for each voice to give the best measurements.

### Save Results

Save Results saves two xlsx files. One is the results.xlsx file and one is the settings.xlsx file. Here you can choose the directory you want to save the files into. You don't have to click on a file, just go to the directory and press the button.

#### results.xlsx

The results file saves all of the voice measurements that you made. Each measurement gets a separate tab in the xlsx file.

#### settings.xlsx

This file saves all of the parameters used in each measurement. Each measurement gets a separate tab in the xlsx file. This is great if you want to know what happened. It can also accompany a manuscript or paper to help others replicate analyses.

### Results Tab

```{image} _static/output_window.png
:alt: Results window
:width: 400
```

This is where you can view results. You can select each voice file on the left and view each measurement result on the bottom frame. You can also view your spectrograms in the spectrogram window. You can change the size of any of these frames in order to see things better. Press {python}`Save Results` to save data. All data (results & settings), manipulated voices, and spectrograms are saved automatically when this button is pressed. All you have to do is choose which folder to save into. Don't worry about picking file names, Voice Lab will make those automatically for you.

#### Output formats

- All data files are saved as xlsx
- All sound files are saved as wav
- All image files are saved as png

# Documentation and API Reference

THe API is not a supported way to run Voicelab, but it works, with some elbow grease.
You need to clone the github repo and run it from the command line, but not if you install it from PyPi or Binary. You
can adapt this process for any node.  See source code for the node you want to run for more details. I have the
directory structure set up below in the code examples. It's just at test file, but you can see how to make it work.
In short, The prepare_node() function sets up the node with the sound file the way it likes it and returns the node. The
process() method runs the node.

## Automated Settings

VoiceLab uses automated settings for pitch floor and ceiling, and also uses these to set the centre frequency parameter in the FormantPath formant analysis.

(floor-ceiling)=

### Automated pitch floor and ceiling parameters

Praat suggests adjusting pitch settings based on [gender](http://www.fon.hum.uva.nl/praat/manual/Intro_4_2__Configuring_the_pitch_contour.html) . It's not gender per se that is important, but the pitch of voice. To mitigate this, VoiceLab first casts a wide net in  floor and ceiling settings to learn the range of probable fundamental frequencies is a voice. Then it remeasures the voice pitch using different settings for higher and lower pitched voices. VoiceLab by default uses employs {python}`very accurate`. VoiceLab returns {python}`minimum pitch`, {python}`maximum pitch`, {python}`mean pitch`, and {python}`standard deviation of pitch`. By default VoiceLab uses  autocorrelation for {ref}`Measuring Pitch<Pitch>`, and cross-correlation for {ref}`harmonicity<HNR>`, {ref}`Jitter<Jitter>`, and {ref}`Shimmer<Shimmer>`,

## Measurement Nodes

(pitch)=

### Measure Pitch

This measures voice pitch or fundamental frequency. Users can measure pitch using any number of the following algorithms:
: - Praat Autocorrelation
  - Praat Cross Correlation
  - Yin (From Librosa)
  - Subharmonics (from Open Sauce)

By default it will measure all of these.

This uses Praat's {python}`Sound: To Pitch (ac)...`, by default. You can also use the cross-correlation algorithm: {python}`Sound: To Pitch (cc)...`. For full details on these algorithms, see the [praat manual pitch page](http://www.fon.hum.uva.nl/praat/manual/Pitch.html).
{python}`Measure Pitch` returns the following measurements:

> - A list of the pitch values
> - Minimum Pitch
> - Maximum Pitch
> - Mean Pitch
> - Standard Deviation of Pitch
> - Pitch Floor (used to set window length)
> - Pitch Ceiling (no candidates above this value will be considered)

We use the automated pitch floor and ceiling parameters described {ref}`here.<floor-ceiling>`

#### Measure Pitch Yin

This is the Yin implementation from Librosa.  This is now run out of the Measure Pitch Node.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasurePitchNode
   :members:

```

#### Measure Subharmonics

This measures subharmonic pitch and subharmonic to harmonic ratio. Subharmonic to harmonic ratio and Subharmonic pitch are measures from Open Sauce (Yu et al., 2019), a Python port of Voice Sauce (Shue et al., 2011).  These measurements do not use any Praat or Parselmouth code.  As in (Shue et al., 2011) and (Yu et al., 2019), subharmonic raw values are padded with NaN values to 201 data points.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSHRPNode
   :members:

```

(cpp)=

### Measure CPP (Cepstral Peak Prominence)

This measures Cepstral Peak Prominance in Praat. You can adjust interpolation, qeufrency upper and lower bounds, line type, and fit method.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureCPPNode
   :members:
```

(duration)=

### Measure Duration

This measures the full duration of the sound file. There are no parameters to adjust.

(energy)=

### Measure Energy

This is my port of VoiceSauce's Energy Algorithm.  It is different than the old RMS Energy algorithm in previous
versions of VoiceLab, which was RMS of the file and is still available. This code is not in OpenSauce. It is a line-by
line translation of the Voice Sauce MatLab and Praat Code.  Validation analyses for automatic analysis settings and
Energy can be found [here\<https://osf.io/3wr6k/files/>][here<https://osf.io/3wr6k/files/>].

It is a normal Energy calculation, but the widow size is equal to 5 pitch periods, estimated by my port of Voice
Sauce's Praat script to Python using the praat-parselmouth package.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureEnergyNode
   :members:
```

(formants)=

### Measure Formants

This returns the mean of the first 4 formant frequencies of the voice using the {python}`To FormantPath` algorithm using
5.5 maximum number of formants and a variable centre frequency, set automatically or user-specified.  All other values
are Praat defaults for Formant Path.  Formant path picks the best formant ceiling value by fitting each prediction to a
polynomial curve, and choosing the best fit for each formant. The centre frequency is determined in the automatic
settings You can also use your own settings for {python}`To Formant Burg...` if you want to.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureFormantNode
   :members:

```

### Measure Vocal Tract Length Estimates

This returns the following vocal tract length estimates:

#### Average Formant

This calculates the mean $\frac {\sum _{i=1}^{n} {f_i}}{n}$ of the first four formant frequencies for each sound.

Pisanski, K., & Rendall, D. (2011). The prioritization of voice fundamental frequency or formants in listeners’ assessments of speaker size, masculinity, and attractiveness. The Journal of the Acoustical Society of America, 129(4), 2201-2212.

#### Principle Components Analysis

This returns the first factor from a Principle Components Analysis (PCA) of the 4 formants.

Babel, M., McGuire, G., & King, J. (2014). Towards a more nuanced view of vocal attractiveness. PloS one, 9(2), e88616.

#### Geometric Mean

This calculates the geometric mean $\left(\prod _{i=1}^{n}f_{i}\right)^{\frac {1}{n}}$ of the first 4 formant frequencies for each sound.

Smith, D. R., & Patterson, R. D. (2005). The interaction of glottal-pulse rate andvocal-tract length in judgements of speaker size, sex, and age.Journal of theAcoustical Society of America, 118, 3177e3186.

#### Formant Dispersion

$\frac {\sum _{i=2}^{n} {f_i - f_{i-1}}}{n}$

Fitch, W. T. (1997). Vocal-tract length and formant frequency dispersion correlate with body size in rhesus macaques.Journal of the Acoustical Society of America,102,1213e1222.

#### VTL

$\frac {\sum _{i=1}^{n} (2n-1) \frac {f_i}{4c}}{n}$

Fitch, W. T. (1997). Vocal-tract length and formant frequency dispersion correlate with body size in rhesus macaques.Journal of the Acoustical Society of America,102,1213e1222.

Titze, I. R. (1994).Principles of voice production. Englewood Cliffs, NJ: Prentice Hall.

#### VTL Δf

$f_i$ = The slope of 0 intercept regression between $F_i = \frac {(2i-1)}{2} Δf$ and the mean of each of the first 4 formant frequencies.

$VTL f_i = \frac {\sum _{i=1}^{n} (2n-1)(\frac {c}{4f_i})}{n}$

$VTL \Delta f = \frac {c}{2Δf}$

Reby,D.,&McComb,K.(2003).Anatomical constraints generate honesty: acoustic cues to age and weight in the roars of red deer stags. Animal Behaviour, 65,519e530.

(formant-position)=

#### Measure Formant Positions Node

This node measures formant position. This node is executed by MeasureVocalTractEstimatesNode.

Formant Position is set to only run on samples of 30 or greater because this measure is based on scaling the data. Without a large enough sample, this measurement could be suspicious.

The algorithm is as follows:
: - First, measure formants at each gottal pulse.

  - Second, scale each formant separately.

  - Third, find the mean of the scaled formants.

    > - $\frac{1}{n} {\sum _{i=1}^{n}{f_i}}$

This algorithm deviates from the original in that it checks the data for a normal distribution before applying the z-score. If it is not normally distributed, it uses Scikit Learn's [Robust Scalar](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html)
The scalar method is recorded in the voicelab_settings.xlsx file.

Puts, D. A., Apicella, C. L., & Cárdenas, R. A. (2011). Masculine voices signal men's threat potential in forager and industrial societies. Proceedings of the Royal Society B: Biological Sciences, 279(1728), 601-609.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureVocalTractEstimatesNode
   :members:
```

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureFormantPositionsNode
   :members:

```

(hnr)=

### Measure Harmonicity

This measures mean harmonics-to-noise-ratio using automatic floor and ceiling settings described {ref}`here.<floor-ceiling>`  Full details of the algorithm can be found in the [Praat Manual Harmonicity Page\<http://www.fon.hum.uva.nl/praat/manual/Harmonicity.html>][praat manual harmonicity page<http://www.fon.hum.uva.nl/praat/manual/harmonicity.html>]. By default Voice Lab use {python}`To Harmonicity (cc)..`. You can select {python}`To Harmonicity (ac)` or change any other Praat parameters if you wish.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureHarmonicityNode
   :members:

```

### Measure Intensity

This returns the mean of Praat's  {python}`Sound: To Intensity...` function in dB. You can adjust the minimum pitch parameter. For more information, see Praat
s [Configuring the intensity contour Page](https://www.fon.hum.uva.nl/praat/manual/Intro_6_2__Configuring_the_intensity_contour.html).

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureIntensityNode
   :members:

```

(jitter)=

### Measure Jitter

This measures and returns values of all of [Praat's jitter algorithms](http://www.fon.hum.uva.nl/praat/manual/Voice_2__Jitter.html). This can be a bit overwhelming or difficult to understand which measure to use and why, or can lead to multiple colinear comparisons. To address this, by default, Voice Lab returns a the first component from a principal components analysis of those jitter algorithms taken across all selected voices. The underlying reasoning here is that each of these algorithms measures something about how noisy the voice is due to perturbations in period length. The PCA finds what is common about all of these measures of noise, and gives you a score relative to your sample. With a large enough sample, the PCA score should be a more robust measure of jitter than any single measurement. Voice Lab uses use it's {ref}`automated pitch floor and ceiling algorithm.<floor-ceiling>` to set analysis parameters.

Jitter Measures:

- Jitter (local)
- Jitter (local, absolute)
- Jitter (rap)
- Jitter (ppq5)
- Jitter (ddp)

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureJitterNode
   :members:

```

(shimmer)=

### Measure Shimmer

This measures and returns values of all of [Praat's shimmer algorithms](http://www.fon.hum.uva.nl/praat/manual/Voice_3__Shimmer.html). This can be a bit overwhelming or difficult to understand which measure to use and why, or can lead to multiple colinear comparisons. To address this, by default, Voice Lab returns a the first component from a principal components analysis of those shimmer algorithms taken across all selected voices. The underlying reasoning here is that each of these algorithms measures something about how noisy the voice is due to perturbations in amplitude of periods. The PCA finds what is common about all of these measures of noise, and gives you a score relative to your sample. With a large enough sample, the PCA score should be a more robust measure of shimmer than any single measurement. Voice Lab uses use it's {ref}`automated pitch floor and ceiling algorithm.<floor-ceiling>` to set analysis parameters.

Shimmer Measures:

- Shimmer (local)
- Shimmer (local, dB)
- Shimmer (apq3)
- Shimmer (aqp5)
- Shimmer (apq11)
- Shimmer (ddp)

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureShimmerNode
   :members:

```

### Measure LTAS

This measures several items from the Long-Term Average Spectrum using Praat's default settings.

- mean (dB)
- slope (dB)
- local peak height (dB)
- standard deviation (dB)
- spectral tilt slope (dB/Hz)
- spectral tilt intercept (dB)

You can adjust:
\- Pitch correction
\- Bandwidth
\- Max Frequency
\- Shortest and longest periods
\- Maximum period factor

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureLTASNode
   :members:

```

### Measure MFCC

This node measures the first 24 Mel Cepstral Coeffecients of the sound.  There are no options to set. If you want fewer coeffecients, you can delete the one's you don't want. If you need the same number of values for each sound for Machine Learning, make sure the sounds are the same length before running the analysis.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureMFCCNode
   :members:

```

### Measure Spectral Shape

This measures spectral:
\- Centre of Gravity
\- Standard Deviation
\- Kurtosis
\- Band Energy Difference
\- Band Density Difference

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpectralShapeNode
   :members:
```

### Measure Spectral Tilt

This measures spectral tilt by returning the slope of a regression between freqeuncy and amplitude of each sound. This is from a script written by Michael J. Owren, with sorting errors corrected. This is not the same equation in Voice Sauce.

Owren, M.J. GSU Praat Tools: Scripts for modifying and analyzing sounds using Praat acoustics software. Behavior Research Methods (2008) 40:  822–829. <https://doi.org/10.3758/BRM.40.3.822>

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpectralTiltNode
   :members:

```

### Measure Speech Rate

This function is an implementation of the Praat script published here:
De Jong, N.H. & Wempe, T. (2009). Praat script to detect syllable nuclei and measure speech rate automatically. Behavior research methods, 41 (2), 385 - 390.

Voice Lab used version 2 of the script, available [here](https://sites.google.com/site/speechrate/Home/praat-script-syllable-nuclei-v2).

This returns:
: - Number of Syllables
  - Number of Pauses
  - Duration(s)
  - Phonation Time(s)
  - Speech Rate (Number of Syllables / Duration)
  - Articulation Rate (Number of Syllables / Phonation Time)
  - Average Syllable Duration (Speaking Time / Number of Syllables)

You can adjust:
\- silence threshold {python}`mindb`

- mimimum dip between peaks (dB) {python}`mindip`. This should be between 2-4. Try 4 for clean and filtered sounds, and lower numbers for noisier sounds.
- minimum pause length {python}`minpause`

This command really only words on sounds with a few syllables, since Voice Lab is measuring how fast someone speaks. For monosyllabic sounds, use the {ref}`Measure Duration function.<Duration>`

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpeechRateNode
   :members:

```

## Manipulation Nodes

### Lower Pitch

This lowers pitch using the PSOLA method. By default, this lowers  by 0.5 ERBs (Equivalent Rectangular Bandwidths) which is about 20 Hz at a 120 Hz pitch centre and about -/+ 25 Hz at a 240 Hz pitch centre. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulatePitchLowerNode
   :members:
```

### Raise Pitch

This raises pitch using the PSOLA method. By default, this lowers  by 0.5 ERBs (Equivalent Rectangular Bandwidths) which is about 20 Hz at a 120 Hz pitch centre and about -/+ 25 Hz at a 240 Hz pitch centre. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulatePitchHigherNode
   :members:
```

### Lower Formants

This lowers formants using Praat's Change Gender Function. By default, Formants are lowered by 15%. This manipulation resamples a sound by the Formant scaling factor (which can be altered in the Settings tab). Then, the sampling rate is overriden to the sound's original sampling rate. Then PSOLA is employed to stretch time and pitch back (separately) into their original values. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateLowerFormantsNode
   :members:
```

### Raise Formants

This raises formants using Praat's Change Gender Function. By default, Formants are raised by 15%. This manipulation resamples a sound by the Formant scaling factor (which can be altered in the Settings tab). Then, the sampling rate is overriden to the sound's original sampling rate. Then PSOLA is employed to stretch time and pitch back (separately) into their original values. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateRaiseFormantsNode
   :members:
```

### Lower Pitch and Formants

This manipulation lowers both pitch and formants in the same direction by the same or independent amounts. This uses the algorithm described in Manipulate Formants, but allows the user to scale or shift pitch to a designated degree. By default, pitch is also lowered by 15%. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateLowerPitchAndFormantsNode
   :members:
```

### Raise Pitch and Formants

This manipulation raises both pitch and formants in the same direction by the same or independent amounts. This uses the algorithm described in Manipulate Formants, but allows the user to scale or shift pitch to a designated degree. By default, pitch is also raised by 15%. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateRaisePitchAndFormantsNode
   :members:
```

### Reverse Sounds

This reverses the selected sounds. Use this if you want to play sounds backwards. Try a Led Zepplin or Beatles song.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ReverseSoundsNode
   :members:
```

### Resample Sounds

This is a quick and easy way to batch process resampling sounds. 44.1kHz is the default. Change this value in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ResampleSoundsNode
   :members:
```

### Rotate Spectrum

This resamples the sound, rotates the selected sounds by 180 degrees and reverses it so it's just the inverted frequency spectrum.
This script is from Chris Darwin and reproduced here with permission: [The original script can be found here](http://www.lifesci.sussex.ac.uk/home/Chris_Darwin/Praatscripts/Spectral%20Rotation).

A similar technique was used here: Bédard, C., & Belin, P. (2004). A “voice inversion effect?”. Brain and cognition, 55(2), 247-249.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.RotateSpectrumNode
   :members:

```

### Scale Intensity

This scales intensity with Peak or RMS. Use this if you want your sounds to all be at an equivalent amplitude. By default intensity is normalized to 70 dB using RMS. If you use peak, it is scaled between -1 and 1, so pick a number between -1 and 1 to normalize to peak.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ScaleIntensityNode
   :members:

```

### Truncate Sounds

This trims and/or truncates sounds. You can trim a % of time off the ends of the sound, or voicelab can automatically detect silences at the beginning and end of the sound, and clip those out also.
If you have trouble with trimming silences, try adjusting the silence ratio in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateTruncateSoundsNode
   :members:

```

## Visualization Nodes

### Spectrograms

```{image} _static/spectrogram.png
:alt: Spectrogram
:width: 400
```

VoiceLab creates full colour spectrograms. By default we use a wide-band window. You can adjust the window length. For example, for a narrow-band spectrogram, you can try 0.005 as a window length. You can also select a different colour palate. You can also overlay pitch, the first four formant frequencies, and intensity measures on the spectrogram.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.VisualizeVoiceNode
   :members:

```

### Power Spectra

```{image} _static/power_spectrum.png
:alt: Power spectrum
:width: 400
```

VoiceLab creates power spectra of sounds and overlays an LPC curve over the top.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.VisualizeSpectrumNode
   :members:
```

% This Sphynx rst file depends on sphinxcontrib-inlinesyntaxhighlight

# Voice Lab Interface

```{eval-rst}
.. highlight:: rst
```

```{eval-rst}
.. role:: python(code)
    :langua.. This Sphynx rst file depends on sphinxcontrib-inlinesyntaxhighlight



```

# Voice Lab Interface

```{eval-rst}
.. highlight:: rst
```

```{eval-rst}
.. role:: python(code)
    :language: python
```

```{eval-rst}
.. toctree::
    :numbered:
    :maxdepth: 2
```

Voice Lab is an automated voice analysis software. What this software does is allow you to measure, manipulate, and visualize many voices at once, without messing with analysis parameters. You can also save all of your data, analysis parameters, manipulated voices, and full colour spectrograms with the press of one button.

Voice Lab is written in Python and relies heavily on a package called parselmouth-praat. parselmouth-praat is a Python package that essentially turns Praat's source code written in C and C++ into a Pythonic interface. What that means is that any praat measurement in this software is using actual Praat source code, so you can trust the underlying algorithms. Voice Lab figures out all of the analysis parameters for you, but you can always use your own, and these are the same parameters as in Praat, and they do the exact same thing because it is Praat's source code powering everything. That means if you are a beginner an expert, or anything in-between, you can use this software to automate your acoustical analyses.

All of the code is open source and available on our GitHub repository, so if this manual isn't in-depth enough, and you want to see exactly what's going on, go for it. It is under the MIT license, so you are free to do what you like with the software as long as you give us credit. For more info on that license, see here.

## Load Voices Tab

```{image} _static/LoadVoices.png
:alt: Load voices window
:width: 400
```

### Load Sound File

Press this button to load sound files. You can load as many files as you like.
At the moment, Voice Lab processes the following file types:

- wav
- mp3
- aiff
- ogg
- aifc
- au
- nist
- flac

### Remove Sound File

Use this button to remove the selected sound file(s) from the list.

### Start

Pressing this begins analysis. If you want to run the default analysis, press this button.
If you want to select different analyses or adjust analysis parameters, go to the 'Settings' tab and press the 'Advanced Settings' button.
Only the files selected (in blue) will be analyzed. By default we will select all files.

(id7)=

## Settings Tab

```{image} _static/settings.png
:alt: Settings window
:width: 400
```

To choose different analyses, select the {python}`Use Advanced Settings` checkbox. From here, you'll be given the option to select different analyses. You can also change any analysis parameters. If you do change analysis parameters, make sure you know what you are doing, and remember that those same analysis parameters will be used on all voice files that are selected. If you don't alter these parameters, we determine analysis parameters automatically for you, so they are tailored for each voice to give the best measurements.

### Save Results

Save Results saves two xlsx files. One is the results.xlsx file and one is the settings.xlsx file. Here you can choose the directory you want to save the files into. You don't have to click on a file, just go to the directory and press the button.

#### results.xlsx

The results file saves all of the voice measurements that you made. Each measurement gets a separate tab in the xlsx file.

#### settings.xlsx

This file saves all of the parameters used in each measurement. Each measurement gets a separate tab in the xlsx file. This is great if you want to know what happened. It can also accompany a manuscript or paper to help others replicate analyses.

### Results Tab

```{image} _static/output_window.png
:alt: Results window
:width: 400
```

This is where you can view results. You can select each voice file on the left and view each measurement result on the bottom frame. You can also view your spectrograms in the spectrogram window. You can change the size of any of these frames in order to see things better. Press {python}`Save Results` to save data. All data (results & settings), manipulated voices, and spectrograms are saved automatically when this button is pressed. All you have to do is choose which folder to save into. Don't worry about picking file names, Voice Lab will make those automatically for you.

#### Output formats

- All data files are saved as xlsx
- All sound files are saved as wav
- All image files are saved as png

# Documentation and API Reference

This API is not yet complete. It is a work in progress. But, for now, there's enough for you to run any node as long
as you can understand the code.  Reproducing Voicelab's exact behaviour in the command line is a bit more difficult as
there is a state dictionary and and {python}`end()` method for some nodes.

All nodes can be imported and run without the VoiceLab GUI if you program their execution in Python.

You'll need to supply: {python}`args['file_path']`, which is the file path, and
{python}`args['voice']`, which is the {python}`parselmouth.Sound` object created by running
{python}`parselmouth.Sound(args['file_path'])`.  You may also set additional parameters by creating an
instance of a node, and setting the dictionary {python}`args` to the appropriate values as specified
in each node. The output of each node is a dictionary of the results. If the node is a manipulation
node, it will return a {python}`parselmouth.Sound` object. If the node is a plot, it will return a matplotlib figure.
Otherwise, it will return mixed types of floats, integers, strings, and lists in the dictionary.

Validation analyses for automatic analysis settings and Energy can be found [here\<https://osf.io/3wr6k/files/>][here<https://osf.io/3wr6k/files/>].

## Automated Settings

VoiceLab uses automated settings for pitch floor and ceiling, and also uses these to set the centre frequency parameter in the FormantPath formant analysis.

(id16)=

### Automated pitch floor and ceiling parameters

Praat suggests adjusting pitch settings based on [gender](http://www.fon.hum.uva.nl/praat/manual/Intro_4_2__Configuring_the_pitch_contour.html) . It's not gender per se that is important, but the pitch of voice. To mitigate this, VoiceLab first casts a wide net in  floor and ceiling settings to learn the range of probable fundamental frequencies is a voice. Then it remeasures the voice pitch using different settings for higher and lower pitched voices. VoiceLab by default uses employs {python}`very accurate`. VoiceLab returns {python}`minimum pitch`, {python}`maximum pitch`, {python}`mean pitch`, and {python}`standard deviation of pitch`. By default VoiceLab uses  autocorrelation for {ref}`Measuring Pitch<Pitch>`, and cross-correlation for {ref}`harmonicity<HNR>`, {ref}`Jitter<Jitter>`, and {ref}`Shimmer<Shimmer>`,

## Measurement Nodes

(id19)=

### Measure Pitch

This measures voice pitch or fundamental frequency. Users can measure pitch using any number of the following algorithms:
: - Praat Autocorrelation
  - Praat Cross Correlation
  - Yin (From Librosa)
  - Subharmonics (from Open Sauce)

By default it will measure all of these.

This uses Praat's {python}`Sound: To Pitch (ac)...`, by default. You can also use the cross-correlation algorithm: {python}`Sound: To Pitch (cc)...`. For full details on these algorithms, see the [praat manual pitch page](http://www.fon.hum.uva.nl/praat/manual/Pitch.html).
{python}`Measure Pitch` returns the following measurements:

> - A list of the pitch values
> - Minimum Pitch
> - Maximum Pitch
> - Mean Pitch
> - Standard Deviation of Pitch
> - Pitch Floor (used to set window length)
> - Pitch Ceiling (no candidates above this value will be considered)

We use the automated pitch floor and ceiling parameters described {ref}`here.<floor-ceiling>`

#### Measure Pitch Yin

This is the Yin implementation from Librosa.  This is now run out of the Measure Pitch Node.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasurePitchNode
   :members:

```

#### Measure Subharmonics

This measures subharmonic pitch and subharmonic to harmonic ratio. Subharmonic to harmonic ratio and Subharmonic pitch are measures from Open Sauce (Yu et al., 2019), a Python port of Voice Sauce (Shue et al., 2011).  These measurements do not use any Praat or Parselmouth code.  As in (Shue et al., 2011) and (Yu et al., 2019), subharmonic raw values are padded with NaN values to 201 data points.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSHRPNode
   :members:

```

(id23)=

### Measure CPP (Cepstral Peak Prominence)

This measures Cepstral Peak Prominance in Praat. You can adjust interpolation, qeufrency upper and lower bounds, line type, and fit method.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureCPPNode
   :members:
```

(id25)=

### Measure Duration

This measures the full duration of the sound file. There are no parameters to adjust.

(id27)=

### Measure Energy

This is my port of VoiceSauce's Energy Algorithm.  It is different than the old RMS Energy algorithm in previous versions of VoiceLab. This code is not in OpenSauce.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureEnergyNode
   :members:
```

(id29)=

### Measure Formants

This returns the mean of the first 4 formant frequencies of the voice using the {python}`To FormantPath` algorithm using
5.5 maximum number of formants and a variable centre frequency, set automatically or user-specified.  All other values
are Praat defaults for Formant Path.  Formant path picks the best formant ceiling value by fitting each prediction to a
polynomial curve, and choosing the best fit for each formant. The centre frequency is determined in the automatic
settings You can also use your own settings for {python}`To Formant Burg...` if you want to.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureFormantNode
   :members:

```

### Measure Vocal Tract Length Estimates

This returns the following vocal tract length estimates:

#### Average Formant

This calculates the mean $\frac {\sum _{i=1}^{n} {f_i}}{n}$ of the first four formant frequencies for each sound.

Pisanski, K., & Rendall, D. (2011). The prioritization of voice fundamental frequency or formants in listeners’ assessments of speaker size, masculinity, and attractiveness. The Journal of the Acoustical Society of America, 129(4), 2201-2212.

#### Principle Components Analysis

This returns the first factor from a Principle Components Analysis (PCA) of the 4 formants.

Babel, M., McGuire, G., & King, J. (2014). Towards a more nuanced view of vocal attractiveness. PloS one, 9(2), e88616.

#### Geometric Mean

This calculates the geometric mean $\left(\prod _{i=1}^{n}f_{i}\right)^{\frac {1}{n}}$ of the first 4 formant frequencies for each sound.

Smith, D. R., & Patterson, R. D. (2005). The interaction of glottal-pulse rate andvocal-tract length in judgements of speaker size, sex, and age.Journal of theAcoustical Society of America, 118, 3177e3186.

#### Formant Dispersion

$\frac {\sum _{i=2}^{n} {f_i - f_{i-1}}}{n}$

Fitch, W. T. (1997). Vocal-tract length and formant frequency dispersion correlate with body size in rhesus macaques.Journal of the Acoustical Society of America,102,1213e1222.

#### VTL

$\frac {\sum _{i=1}^{n} (2n-1) \frac {f_i}{4c}}{n}$

Fitch, W. T. (1997). Vocal-tract length and formant frequency dispersion correlate with body size in rhesus macaques.Journal of the Acoustical Society of America,102,1213e1222.

Titze, I. R. (1994).Principles of voice production. Englewood Cliffs, NJ: Prentice Hall.

#### VTL Δf

$f_i$ = The slope of 0 intercept regression between $F_i = \frac {(2i-1)}{2} Δf$ and the mean of each of the first 4 formant frequencies.

$VTL f_i = \frac {\sum _{i=1}^{n} (2n-1)(\frac {c}{4f_i})}{n}$

$VTL \Delta f = \frac {c}{2Δf}$

Reby,D.,&McComb,K.(2003).Anatomical constraints generate honesty: acoustic cues to age and weight in the roars of red deer stags. Animal Behaviour, 65,519e530.

(id38)=

#### Measure Formant Positions Node

This node measures formant position. This node is executed by MeasureVocalTractEstimatesNode.

Formant Position is set to only run on samples of 30 or greater because this measure is based on scaling the data. Without a large enough sample, this measurement could be suspicious.

The algorithm is as follows:
: - First, measure formants at each gottal pulse.

  - Second, scale each formant separately.

  - Third, find the mean of the scaled formants.

    > - $\frac{1}{n} {\sum _{i=1}^{n}{f_i}}$

This algorithm deviates from the original in that it checks the data for a normal distribution before applying the z-score. If it is not normally distributed, it uses Scikit Learn's [Robust Scalar](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html)
The scalar method is recorded in the voicelab_settings.xlsx file.

Puts, D. A., Apicella, C. L., & Cárdenas, R. A. (2011). Masculine voices signal men's threat potential in forager and industrial societies. Proceedings of the Royal Society B: Biological Sciences, 279(1728), 601-609.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureVocalTractEstimatesNode
   :members:
```

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureFormantPositionsNode
   :members:

```

(id40)=

### Measure Harmonicity

This measures mean harmonics-to-noise-ratio using automatic floor and ceiling settings described {ref}`here.<floor-ceiling>`  Full details of the algorithm can be found in the [Praat Manual Harmonicity Page\<http://www.fon.hum.uva.nl/praat/manual/Harmonicity.html>][praat manual harmonicity page<http://www.fon.hum.uva.nl/praat/manual/harmonicity.html>]. By default Voice Lab use {python}`To Harmonicity (cc)..`. You can select {python}`To Harmonicity (ac)` or change any other Praat parameters if you wish.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureHarmonicityNode
   :members:

```

### Measure Intensity

This returns the mean of Praat's  {python}`Sound: To Intensity...` function in dB. You can adjust the minimum pitch parameter. For more information, see Praat
s [Configuring the intensity contour Page](https://www.fon.hum.uva.nl/praat/manual/Intro_6_2__Configuring_the_intensity_contour.html).

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureIntensityNode
   :members:

```

(id43)=

### Measure Jitter

This measures and returns values of all of [Praat's jitter algorithms](http://www.fon.hum.uva.nl/praat/manual/Voice_2__Jitter.html). This can be a bit overwhelming or difficult to understand which measure to use and why, or can lead to multiple colinear comparisons. To address this, by default, Voice Lab returns a the first component from a principal components analysis of those jitter algorithms taken across all selected voices. The underlying reasoning here is that each of these algorithms measures something about how noisy the voice is due to perturbations in period length. The PCA finds what is common about all of these measures of noise, and gives you a score relative to your sample. With a large enough sample, the PCA score should be a more robust measure of jitter than any single measurement. Voice Lab uses use it's {ref}`automated pitch floor and ceiling algorithm.<floor-ceiling>` to set analysis parameters.

Jitter Measures:

- Jitter (local)
- Jitter (local, absolute)
- Jitter (rap)
- Jitter (ppq5)
- Jitter (ddp)

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureJitterNode
   :members:

```

(id45)=

### Measure Shimmer

This measures and returns values of all of [Praat's shimmer algorithms](http://www.fon.hum.uva.nl/praat/manual/Voice_3__Shimmer.html). This can be a bit overwhelming or difficult to understand which measure to use and why, or can lead to multiple colinear comparisons. To address this, by default, Voice Lab returns a the first component from a principal components analysis of those shimmer algorithms taken across all selected voices. The underlying reasoning here is that each of these algorithms measures something about how noisy the voice is due to perturbations in amplitude of periods. The PCA finds what is common about all of these measures of noise, and gives you a score relative to your sample. With a large enough sample, the PCA score should be a more robust measure of shimmer than any single measurement. Voice Lab uses use it's {ref}`automated pitch floor and ceiling algorithm.<floor-ceiling>` to set analysis parameters.

Shimmer Measures:

- Shimmer (local)
- Shimmer (local, dB)
- Shimmer (apq3)
- Shimmer (aqp5)
- Shimmer (apq11)
- Shimmer (ddp)

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureShimmerNode
   :members:

```

### Measure LTAS

This measures several items from the Long-Term Average Spectrum using Praat's default settings.

- mean (dB)
- slope (dB)
- local peak height (dB)
- standard deviation (dB)
- spectral tilt slope (dB/Hz)
- spectral tilt intercept (dB)

You can adjust:
\- Pitch correction
\- Bandwidth
\- Max Frequency
\- Shortest and longest periods
\- Maximum period factor

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureLTASNode
   :members:

```

### Measure MFCC

This node measures the first 24 Mel Cepstral Coeffecients of the sound.  There are no options to set. If you want fewer coeffecients, you can delete the one's you don't want. If you need the same number of values for each sound for Machine Learning, make sure the sounds are the same length before running the analysis.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureMFCCNode
   :members:

```

### Measure Spectral Shape

This measures spectral:
\- Centre of Gravity
\- Standard Deviation
\- Kurtosis
\- Band Energy Difference
\- Band Density Difference

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpectralShapeNode
   :members:
```

### Measure Spectral Tilt

This measures spectral tilt by returning the slope of a regression between freqeuncy and amplitude of each sound. This is from a script written by Michael J. Owren, with sorting errors corrected. This is not the same equation in Voice Sauce.

Owren, M.J. GSU Praat Tools: Scripts for modifying and analyzing sounds using Praat acoustics software. Behavior Research Methods (2008) 40:  822–829. <https://doi.org/10.3758/BRM.40.3.822>

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpectralTiltNode
   :members:

```

### Measure Speech Rate

This function is an implementation of the Praat script published here:
De Jong, N.H. & Wempe, T. (2009). Praat script to detect syllable nuclei and measure speech rate automatically. Behavior research methods, 41 (2), 385 - 390.

Voice Lab used version 2 of the script, available [here](https://sites.google.com/site/speechrate/Home/praat-script-syllable-nuclei-v2).

This returns:
: - Number of Syllables
  - Number of Pauses
  - Duration(s)
  - Phonation Time(s)
  - Speech Rate (Number of Syllables / Duration)
  - Articulation Rate (Number of Syllables / Phonation Time)
  - Average Syllable Duration (Speaking Time / Number of Syllables)

You can adjust:
\- silence threshold {python}`mindb`

- mimimum dip between peaks (dB) {python}`mindip`. This should be between 2-4. Try 4 for clean and filtered sounds, and lower numbers for noisier sounds.
- minimum pause length {python}`minpause`

This command really only words on sounds with a few syllables, since Voice Lab is measuring how fast someone speaks. For monosyllabic sounds, use the {ref}`Measure Duration function.<Duration>`

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpeechRateNode
   :members:

```

## Manipulation Nodes

### Lower Pitch

This lowers pitch using the PSOLA method. By default, this lowers  by 0.5 ERBs (Equivalent Rectangular Bandwidths) which is about 20 Hz at a 120 Hz pitch centre and about -/+ 25 Hz at a 240 Hz pitch centre. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulatePitchLowerNode
   :members:
```

### Raise Pitch

This raises pitch using the PSOLA method. By default, this lowers  by 0.5 ERBs (Equivalent Rectangular Bandwidths) which is about 20 Hz at a 120 Hz pitch centre and about -/+ 25 Hz at a 240 Hz pitch centre. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulatePitchHigherNode
   :members:
```

### Lower Formants

This lowers formants using Praat's Change Gender Function. By default, Formants are lowered by 15%. This manipulation resamples a sound by the Formant scaling factor (which can be altered in the Settings tab). Then, the sampling rate is overriden to the sound's original sampling rate. Then PSOLA is employed to stretch time and pitch back (separately) into their original values. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateLowerFormantsNode
   :members:
```

### Raise Formants

This raises formants using Praat's Change Gender Function. By default, Formants are raised by 15%. This manipulation resamples a sound by the Formant scaling factor (which can be altered in the Settings tab). Then, the sampling rate is overriden to the sound's original sampling rate. Then PSOLA is employed to stretch time and pitch back (separately) into their original values. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateRaiseFormantsNode
   :members:
```

### Lower Pitch and Formants

This manipulation lowers both pitch and formants in the same direction by the same or independent amounts. This uses the algorithm described in Manipulate Formants, but allows the user to scale or shift pitch to a designated degree. By default, pitch is also lowered by 15%. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateLowerPitchAndFormantsNode
   :members:
```

### Raise Pitch and Formants

This manipulation raises both pitch and formants in the same direction by the same or independent amounts. This uses the algorithm described in Manipulate Formants, but allows the user to scale or shift pitch to a designated degree. By default, pitch is also raised by 15%. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateRaisePitchAndFormantsNode
   :members:
```

### Reverse Sounds

This reverses the selected sounds. Use this if you want to play sounds backwards. Try a Led Zepplin or Beatles song.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ReverseSoundsNode
   :members:
```

### Resample Sounds

This is a quick and easy way to batch process resampling sounds. 44.1kHz is the default. Change this value in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ResampleSoundsNode
   :members:
```

### Rotate Spectrum

This resamples the sound, rotates the selected sounds by 180 degrees and reverses it so it's just the inverted frequency spectrum.
This script is from Chris Darwin and reproduced here with permission: [The original script can be found here](http://www.lifesci.sussex.ac.uk/home/Chris_Darwin/Praatscripts/Spectral%20Rotation).

A similar technique was used here: Bédard, C., & Belin, P. (2004). A “voice inversion effect?”. Brain and cognition, 55(2), 247-249.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.RotateSpectrumNode
   :members:

```

### Scale Intensity

This scales intensity with Peak or RMS. Use this if you want your sounds to all be at an equivalent amplitude. By default intensity is normalized to 70 dB using RMS. If you use peak, it is scaled between -1 and 1, so pick a number between -1 and 1 to normalize to peak.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ScaleIntensityNode
   :members:

```

### Truncate Sounds

This trims and/or truncates sounds. You can trim a % of time off the ends of the sound, or voicelab can automatically detect silences at the beginning and end of the sound, and clip those out also.
If you have trouble with trimming silences, try adjusting the silence ratio in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateTruncateSoundsNode
   :members:

```

## Visualization Nodes

### Spectrograms

```{image} _static/spectrogram.png
:alt: Spectrogram
:width: 400
```

VoiceLab creates full colour spectrograms. By default we use a wide-band window. You can adjust the window length. For example, for a narrow-band spectrogram, you can try 0.005 as a window length. You can also select a different colour palate. You can also overlay pitch, the first four formant frequencies, and intensity measures on the spectrogram.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.VisualizeVoiceNode
   :members:

```

### Power Spectra

```{image} _static/power_spectrum.png
:alt: Power spectrum
:width: 400
```

VoiceLab creates power spectra of sounds and overlays an LPC curve over the top.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.VisualizeSpectrumNode
   :members:
```

ge: python

```{eval-rst}
.. toctree::
    :numbered:
    :maxdepth: 2
```

Voice Lab is an automated voice analysis software. What this software does is allow you to measure, manipulate, and visualize many voices at once, without messing with analysis parameters. You can also save all of your data, analysis parameters, manipulated voices, and full colour spectrograms with the press of one button.

Voice Lab is written in Python and relies heavily on a package called parselmouth-praat. parselmouth-praat is a Python package that essentially turns Praat's source code written in C and C++ into a Pythonic interface. What that means is that any praat measurement in this software is using actual Praat source code, so you can trust the underlying algorithms. Voice Lab figures out all of the analysis parameters for you, but you can always use your own, and these are the same parameters as in Praat, and they do the exact same thing because it is Praat's source code powering everything. That means if you are a beginner an expert, or anything in-between, you can use this software to automate your acoustical analyses.

All of the code is open source and available on our GitHub repository, so if this manual isn't in-depth enough, and you want to see exactly what's going on, go for it. It is under the MIT license, so you are free to do what you like with the software as long as you give us credit. For more info on that license, see here.

## Load Voices Tab

```{image} _static/LoadVoices.png
:alt: Load voices window
:width: 400
```

### Load Sound File

Press this button to load sound files. You can load as many files as you like.
At the moment, Voice Lab processes the following file types:

- wav
- mp3
- aiff
- ogg
- aifc
- au
- nist
- flac

### Remove Sound File

Use this button to remove the selected sound file(s) from the list.

### Start

Pressing this begins analysis. If you want to run the default analysis, press this button.
If you want to select different analyses or adjust analysis parameters, go to the 'Settings' tab and press the 'Advanced Settings' button.
Only the files selected (in blue) will be analyzed. By default we will select all files.

(id71)=

## Settings Tab

```{image} _static/settings.png
:alt: Settings window
:width: 400
```

To choose different analyses, select the {python}`Use Advanced Settings` checkbox. From here, you'll be given the option to select different analyses. You can also change any analysis parameters. If you do change analysis parameters, make sure you know what you are doing, and remember that those same analysis parameters will be used on all voice files that are selected. If you don't alter these parameters, we determine analysis parameters automatically for you, so they are tailored for each voice to give the best measurements.

### Save Results

Save Results saves two xlsx files. One is the results.xlsx file and one is the settings.xlsx file. Here you can choose the directory you want to save the files into. You don't have to click on a file, just go to the directory and press the button.

#### results.xlsx

The results file saves all of the voice measurements that you made. Each measurement gets a separate tab in the xlsx file.

#### settings.xlsx

This file saves all of the parameters used in each measurement. Each measurement gets a separate tab in the xlsx file. This is great if you want to know what happened. It can also accompany a manuscript or paper to help others replicate analyses.

### Results Tab

```{image} _static/output_window.png
:alt: Results window
:width: 400
```

This is where you can view results. You can select each voice file on the left and view each measurement result on the bottom frame. You can also view your spectrograms in the spectrogram window. You can change the size of any of these frames in order to see things better. Press {python}`Save Results` to save data. All data (results & settings), manipulated voices, and spectrograms are saved automatically when this button is pressed. All you have to do is choose which folder to save into. Don't worry about picking file names, Voice Lab will make those automatically for you.

#### Output formats

- All data files are saved as xlsx
- All sound files are saved as wav
- All image files are saved as png

# Documentation and API Reference

VoiceLab was not written with an API in mind but I am providing functionality anyways.  For now, it's a bit rough.

This API is not yet complete. It is a work in progress. But, for now, there's enough for you to run any node as long
as you can understand the code.  Reproducing Voicelab's exact behaviour in the command line is a bit more difficult as
there is a state dictionary and and {python}`end()` method for nodes whose measures depend on other nodes (e.g Voice Tract-Length Estimates).

All nodes can be imported and run without the VoiceLab GUI if you program their execution in Python.

You'll need to do some prep work to get your sounds in a form the nodes read. We are preparing for multiprocessing, and Parselmouth.Sound obejects don't pickle
So, to avoid multiple disk reads and slow things down, we pass the values and sampling rate through the nodes.
That means to use this at the command line you need:

\: {python}`args['file_path']`, which is the file path, and
{python}`args['voice']`, which is the {python}`parselmouth.Sound` object created by running
{python}`parselmouth.Sound(args['file_path'])`.
You also need {python}`signal`, and {python}`sampling_rate`, which you can get by doing:
{python}`signal = args['voice'].values` and {python}`sampling_rate  = args['voice'].sampling_frequency`.

You may also set additional parameters by creating an
instance of a node, and setting the dictionary {python}`args` to the appropriate values as specified
in each node. The output of each node is a dictionary of the results. If the node is a manipulation
node, it will return a {python}`parselmouth.Sound` object. If the node is a plot, it will return a matplotlib figure.
Otherwise, it will return mixed types of floats, integers, strings, and lists in the dictionary.

Validation analyses for automatic analysis settings and Energy can be found [here\<https://osf.io/3wr6k/files/>][here<https://osf.io/3wr6k/files/>].

## Automated Settings

VoiceLab uses automated settings for pitch floor and ceiling, and also uses these to set the centre frequency parameter in the FormantPath formant analysis.

(id80)=

### Automated pitch floor and ceiling parameters

Praat suggests adjusting pitch settings based on [gender](http://www.fon.hum.uva.nl/praat/manual/Intro_4_2__Configuring_the_pitch_contour.html) . It's not gender per se that is important, but the pitch of voice. To mitigate this, VoiceLab first casts a wide net in  floor and ceiling settings to learn the range of probable fundamental frequencies is a voice. Then it remeasures the voice pitch using different settings for higher and lower pitched voices. VoiceLab by default uses employs {python}`very accurate`. VoiceLab returns {python}`minimum pitch`, {python}`maximum pitch`, {python}`mean pitch`, and {python}`standard deviation of pitch`. By default VoiceLab uses  autocorrelation for {ref}`Measuring Pitch<Pitch>`, and cross-correlation for {ref}`harmonicity<HNR>`, {ref}`Jitter<Jitter>`, and {ref}`Shimmer<Shimmer>`,

## Measurement Nodes

(id83)=

### Measure Pitch

This measures voice pitch or fundamental frequency. Users can measure pitch using any number of the following algorithms:
: - Praat Autocorrelation
  - Praat Cross Correlation
  - Yin (From Librosa)
  - Subharmonics (from Open Sauce)

By default it will measure all of these.

This uses Praat's {python}`Sound: To Pitch (ac)...`, by default. You can also use the cross-correlation algorithm: {python}`Sound: To Pitch (cc)...`. For full details on these algorithms, see the [praat manual pitch page](http://www.fon.hum.uva.nl/praat/manual/Pitch.html).
{python}`Measure Pitch` returns the following measurements:

> - A list of the pitch values
> - Minimum Pitch
> - Maximum Pitch
> - Mean Pitch
> - Standard Deviation of Pitch
> - Pitch Floor (used to set window length)
> - Pitch Ceiling (no candidates above this value will be considered)

We use the automated pitch floor and ceiling parameters described {ref}`here.<floor-ceiling>`

#### Measure Pitch Yin

This is the Yin implementation from Librosa.  This is now run out of the Measure Pitch Node.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasurePitchNode
   :members:

```

#### Measure Subharmonics

This measures subharmonic pitch and subharmonic to harmonic ratio. Subharmonic to harmonic ratio and Subharmonic pitch are measures from Open Sauce (Yu et al., 2019), a Python port of Voice Sauce (Shue et al., 2011).  These measurements do not use any Praat or Parselmouth code.  As in (Shue et al., 2011) and (Yu et al., 2019), subharmonic raw values are padded with NaN values to 201 data points.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSHRPNode
   :members:

```

(id87)=

### Measure CPP (Cepstral Peak Prominence)

This measures Cepstral Peak Prominance in Praat. You can adjust interpolation, qeufrency upper and lower bounds, line type, and fit method.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureCPPNode
   :members:
```

(id89)=

### Measure Duration

This measures the full duration of the sound file. There are no parameters to adjust.

(id91)=

### Measure Energy

This is my port of VoiceSauce's Energy Algorithm.  It is different than the old RMS Energy algorithm in previous versions of VoiceLab. This code is not in OpenSauce.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureEnergyNode
   :members:
```

(id93)=

### Measure Formants

This returns the mean of the first 4 formant frequencies of the voice using the {python}`To FormantPath` algorithm using
5.5 maximum number of formants and a variable centre frequency, set automatically or user-specified.  All other values
are Praat defaults for Formant Path.  Formant path picks the best formant ceiling value by fitting each prediction to a
polynomial curve, and choosing the best fit for each formant. The centre frequency is determined in the automatic
settings You can also use your own settings for {python}`To Formant Burg...` if you want to.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureFormantNode
   :members:

```

### Measure Vocal Tract Length Estimates

This returns the following vocal tract length estimates:

#### Average Formant

This calculates the mean $\frac {\sum _{i=1}^{n} {f_i}}{n}$ of the first four formant frequencies for each sound.

Pisanski, K., & Rendall, D. (2011). The prioritization of voice fundamental frequency or formants in listeners’ assessments of speaker size, masculinity, and attractiveness. The Journal of the Acoustical Society of America, 129(4), 2201-2212.

#### Principle Components Analysis

This returns the first factor from a Principle Components Analysis (PCA) of the 4 formants.

Babel, M., McGuire, G., & King, J. (2014). Towards a more nuanced view of vocal attractiveness. PloS one, 9(2), e88616.

#### Geometric Mean

This calculates the geometric mean $\left(\prod _{i=1}^{n}f_{i}\right)^{\frac {1}{n}}$ of the first 4 formant frequencies for each sound.

Smith, D. R., & Patterson, R. D. (2005). The interaction of glottal-pulse rate andvocal-tract length in judgements of speaker size, sex, and age.Journal of theAcoustical Society of America, 118, 3177e3186.

#### Formant Dispersion

$\frac {\sum _{i=2}^{n} {f_i - f_{i-1}}}{n}$

Fitch, W. T. (1997). Vocal-tract length and formant frequency dispersion correlate with body size in rhesus macaques.Journal of the Acoustical Society of America,102,1213e1222.

#### VTL

$\frac {\sum _{i=1}^{n} (2n-1) \frac {f_i}{4c}}{n}$

Fitch, W. T. (1997). Vocal-tract length and formant frequency dispersion correlate with body size in rhesus macaques.Journal of the Acoustical Society of America,102,1213e1222.

Titze, I. R. (1994).Principles of voice production. Englewood Cliffs, NJ: Prentice Hall.

#### VTL Δf

$f_i$ = The slope of 0 intercept regression between $F_i = \frac {(2i-1)}{2} Δf$ and the mean of each of the first 4 formant frequencies.

$VTL f_i = \frac {\sum _{i=1}^{n} (2n-1)(\frac {c}{4f_i})}{n}$

$VTL \Delta f = \frac {c}{2Δf}$

Reby,D.,&McComb,K.(2003).Anatomical constraints generate honesty: acoustic cues to age and weight in the roars of red deer stags. Animal Behaviour, 65,519e530.

(id102)=

#### Measure Formant Positions Node

This node measures formant position. This node is executed by MeasureVocalTractEstimatesNode.

Formant Position is set to only run on samples of 30 or greater because this measure is based on scaling the data. Without a large enough sample, this measurement could be suspicious.

The algorithm is as follows:
: - First, measure formants at each gottal pulse.

  - Second, scale each formant separately.

  - Third, find the mean of the scaled formants.

    > - $\frac{1}{n} {\sum _{i=1}^{n}{f_i}}$

This algorithm deviates from the original in that it checks the data for a normal distribution before applying the z-score. If it is not normally distributed, it uses Scikit Learn's [Robust Scalar](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html)
The scalar method is recorded in the voicelab_settings.xlsx file.

Puts, D. A., Apicella, C. L., & Cárdenas, R. A. (2011). Masculine voices signal men's threat potential in forager and industrial societies. Proceedings of the Royal Society B: Biological Sciences, 279(1728), 601-609.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureVocalTractEstimatesNode
   :members:
```

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureFormantPositionsNode
   :members:

```

(id104)=

### Measure Harmonicity

This measures mean harmonics-to-noise-ratio using automatic floor and ceiling settings described {ref}`here.<floor-ceiling>`  Full details of the algorithm can be found in the [Praat Manual Harmonicity Page\<http://www.fon.hum.uva.nl/praat/manual/Harmonicity.html>][praat manual harmonicity page<http://www.fon.hum.uva.nl/praat/manual/harmonicity.html>]. By default Voice Lab use {python}`To Harmonicity (cc)..`. You can select {python}`To Harmonicity (ac)` or change any other Praat parameters if you wish.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureHarmonicityNode
   :members:

```

### Measure Intensity

This returns the mean of Praat's  {python}`Sound: To Intensity...` function in dB. You can adjust the minimum pitch parameter. For more information, see Praat
s [Configuring the intensity contour Page](https://www.fon.hum.uva.nl/praat/manual/Intro_6_2__Configuring_the_intensity_contour.html).

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureIntensityNode
   :members:

```

(id107)=

### Measure Jitter

This measures and returns values of all of [Praat's jitter algorithms](http://www.fon.hum.uva.nl/praat/manual/Voice_2__Jitter.html). This can be a bit overwhelming or difficult to understand which measure to use and why, or can lead to multiple colinear comparisons. To address this, by default, Voice Lab returns a the first component from a principal components analysis of those jitter algorithms taken across all selected voices. The underlying reasoning here is that each of these algorithms measures something about how noisy the voice is due to perturbations in period length. The PCA finds what is common about all of these measures of noise, and gives you a score relative to your sample. With a large enough sample, the PCA score should be a more robust measure of jitter than any single measurement. Voice Lab uses use it's {ref}`automated pitch floor and ceiling algorithm.<floor-ceiling>` to set analysis parameters.

Jitter Measures:

- Jitter (local)
- Jitter (local, absolute)
- Jitter (rap)
- Jitter (ppq5)
- Jitter (ddp)

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureJitterNode
   :members:

```

(id109)=

### Measure Shimmer

This measures and returns values of all of [Praat's shimmer algorithms](http://www.fon.hum.uva.nl/praat/manual/Voice_3__Shimmer.html). This can be a bit overwhelming or difficult to understand which measure to use and why, or can lead to multiple colinear comparisons. To address this, by default, Voice Lab returns a the first component from a principal components analysis of those shimmer algorithms taken across all selected voices. The underlying reasoning here is that each of these algorithms measures something about how noisy the voice is due to perturbations in amplitude of periods. The PCA finds what is common about all of these measures of noise, and gives you a score relative to your sample. With a large enough sample, the PCA score should be a more robust measure of shimmer than any single measurement. Voice Lab uses use it's {ref}`automated pitch floor and ceiling algorithm.<floor-ceiling>` to set analysis parameters.

Shimmer Measures:

- Shimmer (local)
- Shimmer (local, dB)
- Shimmer (apq3)
- Shimmer (aqp5)
- Shimmer (apq11)
- Shimmer (ddp)

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureShimmerNode
   :members:

```

### Measure LTAS

This measures several items from the Long-Term Average Spectrum using Praat's default settings.

- mean (dB)
- slope (dB)
- local peak height (dB)
- standard deviation (dB)
- spectral tilt slope (dB/Hz)
- spectral tilt intercept (dB)

You can adjust:
\- Pitch correction
\- Bandwidth
\- Max Frequency
\- Shortest and longest periods
\- Maximum period factor

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureLTASNode
   :members:

```

### Measure MFCC

This node measures the first 24 Mel Cepstral Coeffecients of the sound.  There are no options to set. If you want fewer coeffecients, you can delete the one's you don't want. If you need the same number of values for each sound for Machine Learning, make sure the sounds are the same length before running the analysis.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureMFCCNode
   :members:

```

### Measure Spectral Shape

This measures spectral:
\- Centre of Gravity
\- Standard Deviation
\- Kurtosis
\- Band Energy Difference
\- Band Density Difference

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpectralShapeNode
   :members:
```

### Measure Spectral Tilt

This measures spectral tilt by returning the slope of a regression between freqeuncy and amplitude of each sound. This is from a script written by Michael J. Owren, with sorting errors corrected. This is not the same equation in Voice Sauce.

Owren, M.J. GSU Praat Tools: Scripts for modifying and analyzing sounds using Praat acoustics software. Behavior Research Methods (2008) 40:  822–829. <https://doi.org/10.3758/BRM.40.3.822>

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpectralTiltNode
   :members:

```

### Measure Speech Rate

This function is an implementation of the Praat script published here:
De Jong, N.H. & Wempe, T. (2009). Praat script to detect syllable nuclei and measure speech rate automatically. Behavior research methods, 41 (2), 385 - 390.

Voice Lab used version 2 of the script, available [here](https://sites.google.com/site/speechrate/Home/praat-script-syllable-nuclei-v2).

This returns:
: - Number of Syllables
  - Number of Pauses
  - Duration(s)
  - Phonation Time(s)
  - Speech Rate (Number of Syllables / Duration)
  - Articulation Rate (Number of Syllables / Phonation Time)
  - Average Syllable Duration (Speaking Time / Number of Syllables)

You can adjust:
\- silence threshold {python}`mindb`

- mimimum dip between peaks (dB) {python}`mindip`. This should be between 2-4. Try 4 for clean and filtered sounds, and lower numbers for noisier sounds.
- minimum pause length {python}`minpause`

This command really only words on sounds with a few syllables, since Voice Lab is measuring how fast someone speaks. For monosyllabic sounds, use the {ref}`Measure Duration function.<Duration>`

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpeechRateNode
   :members:

```

## Manipulation Nodes

### Lower Pitch

This lowers pitch using the PSOLA method. By default, this lowers  by 0.5 ERBs (Equivalent Rectangular Bandwidths) which is about 20 Hz at a 120 Hz pitch centre and about -/+ 25 Hz at a 240 Hz pitch centre. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulatePitchLowerNode
   :members:
```

### Raise Pitch

This raises pitch using the PSOLA method. By default, this lowers  by 0.5 ERBs (Equivalent Rectangular Bandwidths) which is about 20 Hz at a 120 Hz pitch centre and about -/+ 25 Hz at a 240 Hz pitch centre. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.voicelab.src.Voicelab.toolkits.Voicelab.ManipulatePitchHigherNode
   :members:
```

### Lower Formants

This lowers formants using Praat's Change Gender Function. By default, Formants are lowered by 15%. This manipulation resamples a sound by the Formant scaling factor (which can be altered in the Settings tab). Then, the sampling rate is overriden to the sound's original sampling rate. Then PSOLA is employed to stretch time and pitch back (separately) into their original values. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateLowerFormantsNode
   :members:
```

### Raise Formants

This raises formants using Praat's Change Gender Function. By default, Formants are raised by 15%. This manipulation resamples a sound by the Formant scaling factor (which can be altered in the Settings tab). Then, the sampling rate is overriden to the sound's original sampling rate. Then PSOLA is employed to stretch time and pitch back (separately) into their original values. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateRaiseFormantsNode
   :members:
```

### Lower Pitch and Formants

This manipulation lowers both pitch and formants in the same direction by the same or independent amounts. This uses the algorithm described in Manipulate Formants, but allows the user to scale or shift pitch to a designated degree. By default, pitch is also lowered by 15%. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateLowerPitchAndFormantsNode
   :members:
```

### Raise Pitch and Formants

This manipulation raises both pitch and formants in the same direction by the same or independent amounts. This uses the algorithm described in Manipulate Formants, but allows the user to scale or shift pitch to a designated degree. By default, pitch is also raised by 15%. By default VoiceLab also normalizes intensity to 70 dB RMS, but you can turn this off by deselecting the box in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateRaisePitchAndFormantsNode
   :members:
```

### Reverse Sounds

This reverses the selected sounds. Use this if you want to play sounds backwards. Try a Led Zepplin or Beatles song.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ReverseSoundsNode
   :members:
```

### Resample Sounds

This is a quick and easy way to batch process resampling sounds. 44.1kHz is the default. Change this value in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ResampleSoundsNode
   :members:
```

### Rotate Spectrum

This resamples the sound, rotates the selected sounds by 180 degrees and reverses it so it's just the inverted frequency spectrum.
This script is from Chris Darwin and reproduced here with permission: [The original script can be found here](http://www.lifesci.sussex.ac.uk/home/Chris_Darwin/Praatscripts/Spectral%20Rotation).

A similar technique was used here: Bédard, C., & Belin, P. (2004). A “voice inversion effect?”. Brain and cognition, 55(2), 247-249.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.RotateSpectrumNode
   :members:

```

### Scale Intensity

This scales intensity with Peak or RMS. Use this if you want your sounds to all be at an equivalent amplitude. By default intensity is normalized to 70 dB using RMS. If you use peak, it is scaled between -1 and 1, so pick a number between -1 and 1 to normalize to peak.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ScaleIntensityNode
   :members:

```

### Truncate Sounds

This trims and/or truncates sounds. You can trim a % of time off the ends of the sound, or voicelab can automatically detect silences at the beginning and end of the sound, and clip those out also.
If you have trouble with trimming silences, try adjusting the silence ratio in the Settings tab.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.ManipulateTruncateSoundsNode
   :members:

```

## Visualization Nodes

### Spectrograms

```{image} _static/spectrogram.png
:alt: Spectrogram
:width: 400
```

VoiceLab creates full colour spectrograms. By default we use a wide-band window. You can adjust the window length. For example, for a narrow-band spectrogram, you can try 0.005 as a window length. You can also select a different colour palate. You can also overlay pitch, the first four formant frequencies, and intensity measures on the spectrogram.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.VisualizeVoiceNode
   :members:

```

### Power Spectra

```{image} _static/power_spectrum.png
:alt: Power spectrum
:width: 400
```

VoiceLab creates power spectra of sounds and overlays an LPC curve over the top.

```{eval-rst}
.. automodule:: voicelab.src.Voicelab.toolkits.Voicelab.VisualizeSpectrumNode
   :members:

```

(codeexample)=

### Code Example

Running Voicelab from the command line was never intended, but you can hack your way through.
This is a code example from the tests. It shows how to run Voicelab from the command line.
This is not a supported way to run Voicelab, but it works.
This will work if you clone the github repo and run it from the command line, but not if you install it from
PyPi or Binary.
You can adapt this for any node.  See source code for the node you want to run for more details.
I have the directory structure set up below.  You might need to fiddle with it.
The `prepare_node()` function sets up the node with the sound file the way it likes it and returns the node.
The `process()` method runs the node.

```Python import sys import os import parselmouth import numpy as np import pytest
# Set up paths
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
VOICELAB_DIR = os.path.dirname(TEST_DIR)
AUDIO_DIR = os.path.join(VOICELAB_DIR, 'tests/assets/audio')

# in order for the relative imports in the files we are testing to run correctly,
# we need to add these directories to the path
sys.path.insert(0, ''.join([VOICELAB_DIR, "/src/Voicelab/toolkits/Voicelab"]))
sys.path.insert(0, ''.join([VOICELAB_DIR, "/src"]))
import ReverseSoundsNode  # Pycharm doesn't like this, but it works
```

```Python
# Arrange
def get_test_files():
  number_of_test_files = len(os.listdir(AUDIO_DIR)) - 1  # -1 because the first file is a broken sound
  test_files = sorted(os.listdir(AUDIO_DIR))[1:]
  return number_of_test_files, test_files
```

```Python
# Arrange
def prepare_node(test_file):
  file_path = os.path.join(AUDIO_DIR, test_file)
  node = ReverseSoundsNode.ReverseSoundsNode()
  node.args['file_path'] = file_path
  # Load the sound and setup the node
  try:
      sound: parselmouth.Sound = parselmouth.Sound(file_path)
      signal = sound.values
      sampling_rate = sound.sampling_frequency
  except:
      signal = None
      sampling_rate = None
  node.voice = (signal, sampling_rate)
  node.args['voice'] = (signal, sampling_rate)
  print((f"{file_path=}..{sampling_rate=}"))
  return node
```

```Python
# Arrange
def get_reversed_test_sound(test_file):
  file_path = os.path.join(AUDIO_DIR, test_file)
  validation_sound = parselmouth.Sound(file_path)
  validation_sound.reverse()
  return validation_sound.values
```

```Python
# Arrange
def get_number_of_test_files():
  number_of_test_files, _ = get_test_files()
  return number_of_test_files
```

```Python
# Arrange
def generate_numpy_arrays(execution_number):
  number_of_test_files, test_files = get_test_files()
  filename = test_files[execution_number]
  node = prepare_node(filename)
  # Run the node
  results = node.process()
  print(results)
  # Validate the results
  validation_sound = get_reversed_test_sound(filename)
  test_sound = results['voice'].values
  return test_sound, validation_sound

# Act
@pytest.mark.parametrize('execution_number', range(len(os.listdir(AUDIO_DIR)) - 1))
def test_ReverseSoundsNode(execution_number):
  test_sound, validation_sound = generate_numpy_arrays(execution_number)
  assert np.array_equal(test_sound, validation_sound)
```