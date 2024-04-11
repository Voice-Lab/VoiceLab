import numpy as np
import parselmouth
from parselmouth.praat import call


class MeasureFormants:
    def __init__(self):
        self.formant_object = None
        self.sound = None
        self.spectrogram = None
        self.formants = []

    def load_sound(self):
        self.sound = parselmouth.Sound('/home/david/Dropbox/Work/stimuli/sample_sounds/m4090_vowels.wav')
        self.formant_object = self.sound.to_formant_burg()

    def get_formants(self):
        times = self.formant_object.xs()
        intensity = self.sound.to_intensity()
        intensities = []
        for time in times:
            intensity_value = call(intensity, "Get value at time", time, "linear")
            intensities.append(intensity_value)
        non_silent_segments = []
        non_silent_indices = [i for i, intensity in enumerate(intensities) if intensity > 50]
        start_index = None
        for i in range(len(non_silent_indices) - 1):
            if start_index is None:
                start_index = non_silent_indices[i]
            if non_silent_indices[i+1] - non_silent_indices[i] > 1:
                non_silent_segments.append((start_index, non_silent_indices[i]))
                start_index = None
        if start_index is not None:
            non_silent_segments.append((start_index, non_silent_indices[-1]))

        f1s = []
        f2s = []
        f3s = []
        f4s = []
        for i, time in enumerate(times):
            f1 = call(self.formant_object, "Get value at time", 1, time, "Hertz", "linear")
            f2 = call(self.formant_object, "Get value at time", 2, time, "Hertz", "linear")
            f3 = call(self.formant_object, "Get value at time", 3, time, "Hertz", "linear")
            f4 = call(self.formant_object, "Get value at time", 4, time, "Hertz", "linear")
            if intensities[i] < 50:
                f1 = f2 = f3 = f4 = 0
            f1s.append(f1)
            f2s.append(f2)
            f3s.append(f3)
            f4s.append(f4)
        return times, f1s, f2s, f3s, f4s, non_silent_segments

    def draw_spectrogram(self, dynamic_range=70):
        self.sound.pre_emphasize()
        self.spectrogram = self.sound.to_spectrogram(window_length=0.01, maximum_frequency=5500)
        X, Y = self.spectrogram.x_grid(), self.spectrogram.y_grid()
        sg_db = 10 * np.log10(self.spectrogram.values, where=(self.spectrogram.values > 0))
        return X, Y, sg_db, dynamic_range