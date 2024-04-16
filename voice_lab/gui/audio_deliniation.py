import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import plotly.graph_objects as go
import parselmouth
from parselmouth.praat import call
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout


class IdentifyChanges:
    def __init__(self, signal):
        self.signal = signal

    def identify_silent_segments(self):
        """
        Identify silent and non-silent portions of a sound based on the amplitude or energy vector.
        
        Parameters:
        - signal: A NumPy array or a list containing the amplitude or energy values for each frame.
        - silence_threshold: A numeric value representing the threshold below which a segment is considered silent.
        
        Returns:
        - silent_segments: A list of tuples, where each tuple represents the start and end indices of silent segments.
        - non_silent_segments: A list of tuples, where each tuple represents the start and end indices of non-silent segments.
        """
        # Initialize variables
        silence_threshold = self.estimate_silence_threshold()
        silent_segments = []
        non_silent_segments = []
        # Determine if the first segment is silent or non-silent
        is_silent = self.signal[0] < silence_threshold
        
        start_index = 0

        # Iterate over the energy vector to identify segments
        for i in range(1, len(self.signal)):
            # Check for a transition
            if (self.signal[i] < silence_threshold) != is_silent or i == len(self.signal) - 1:
                # End of a segment
                end_index = i if i < len(self.signal) - 1 else i + 1
                # Save the segment
                if is_silent:
                    silent_segments.append((start_index, end_index))
                else:
                    non_silent_segments.append((start_index, end_index))
                # Prepare for the next segment
                start_index = i
                is_silent = not is_silent

        return silent_segments, non_silent_segments

    def estimate_silence_threshold(self, percentile=10, margin_factor=1.5):
        """
        Automatically estimate the silence threshold for an audio signal.
        
        Parameters:
        - signal: A NumPy array containing the amplitude or energy values for each frame.
        - percentile: The percentile to use for threshold estimation (default: 10).
        - margin_factor: A factor to adjust the threshold to ensure it's above the noise level (default: 1.5).
        
        Returns:
        - silence_threshold: The estimated silence threshold.
        """
        # Calculate the threshold based on the chosen percentile
        base_threshold = np.percentile(self.signal, percentile)
        
        return base_threshold * margin_factor  # Adjust the threshold to account for noise

    def detect_formant_transitions(self, formants, threshold=25):
        """
        Detects significant formant transitions over time.
        
        Parameters:
        - formants: A 2D NumPy array with shape (time_frames, num_formants),
                    where each column represents a formant frequency over time.
        - threshold: The threshold for detecting significant changes in Hz. Default is 25 Hz.
                    
        Returns:
        - transitions: A list of time frames where significant formant transitions occur.
        """
        # Calculate the rate of change (derivative) of the formant frequencies
        formant_deltas = np.abs(np.diff(formants, axis=0))
        
        # Find where the change exceeds the threshold
        significant_changes = np.any(formant_deltas > threshold, axis=1)
        
        # Identify the time frames of these changes
        transitions = np.where(significant_changes)[0] + 1  # Add 1 because diff reduces the index by 1
        
        return transitions




class AudioPlotWidget(QWidget):
    def __init__(self, sound, spectrogram, signal, silent_segments, non_silent_segments, parent=None):
        super().__init__(parent)
        self.sound = sound
        self.signal = signal
        self.spectrogram = spectrogram
        self.silent_segments = silent_segments
        self.non_silent_segments = non_silent_segments

        # Set up the matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)  # Connect scroll event

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)

        # Add zoom buttons
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.zoom_in_button)
        button_layout.addWidget(self.zoom_out_button)
        self.layout.addLayout(button_layout)

        self.plot()

    def plot(self):
        self.figure.clear()

        # Create a grid layout for spectrogram and signal plot
        gs = self.figure.add_gridspec(2, 1, height_ratios=[1, 1])

        # Spectrogram plot
        self.ax1 = self.figure.add_subplot(gs[0, 0])
        self.draw_spectrogram(self.ax1, self.spectrogram)

        # Signal plot
        self.ax2 = self.figure.add_subplot(gs[1, 0])
        self.plot_signal_with_segments(self.ax2)
        self.canvas.draw()

    def plot_signal_with_segments(self, ax):
        time_vector = np.arange(len(self.signal)) / self.sound.sampling_frequency
        ax.plot(time_vector, self.signal, label='Energy', color='blue')
        # Highlight segments on the signal plot
        for start, end in self.silent_segments + self.non_silent_segments:
            start_time = start / self.sound.sampling_frequency
            end_time = end / self.sound.sampling_frequency
            ax.axvspan(start_time, end_time, color='green', alpha=0.3)

        ax.set_title('Signal with Silent and Non-Silent Segments')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Amplitude')

    def adjust_zoom(self, factor, center=None):
        # Adjust zoom for both axes
        for ax in [self.ax1, self.ax2]:
            xlim = ax.get_xlim()
            if center is None:
                center = sum(xlim) / 2
            new_width = (xlim[1] - xlim[0]) * factor / 2
            ax.set_xlim([center - new_width, center + new_width])
        self.canvas.draw()

    def zoom_in(self):
        self.adjust_zoom(0.8)  # Smaller factor to zoom in

    def zoom_out(self):
        self.adjust_zoom(1.25)  # Larger factor to zoom out


    def on_scroll(self, event):
        factor = 0.9 if event.button == 'up' else 1.1
        # Zoom centered on the current mouse position
        center = event.xdata
        self.adjust_zoom(factor, center=center)
        
    def draw_spectrogram(self, ax, spectrogram, dynamic_range=70):
        X, Y = spectrogram.x_grid(), spectrogram.y_grid()
        sg_db = 10 * np.log10(spectrogram.values)
        cax = ax.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
        #ax.figure.colorbar(cax, ax=ax)
        ax.set_ylim([spectrogram.ymin, spectrogram.ymax])
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Frequency [Hz]")
        ax.set_title('Spectrogram')
        # no legend for spectrogram



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Segments Visualization")
        self.plot_widget = AudioPlotWidget(sound, spectrogram, signal, silent_segments, non_silent_segments)
        self.setCentralWidget(self.plot_widget)


if __name__ == '__main__':
    file = '/home/david/Dropbox/Work/stimuli/Yiddish/reyd-dataset/audio/lit1/vz1279.wav'
    sound = parselmouth.Sound(file)
    sound.resample(16000)
    sound = call(sound, "Convert to mono")
    spectrogram = sound.to_spectrogram()
    signal = sound.values
    signal = np.squeeze(signal) # Convert to 1D array
    print(np.shape(signal))
    time = sound.xs()
    print(np.shape(time))
    print(len(signal), len(time))
    sampling_rate = sound.sampling_frequency
    ic = IdentifyChanges(signal)
    silence_threshold = ic.estimate_silence_threshold()
    print(silence_threshold)
    silent_segments, non_silent_segments = ic.identify_silent_segments()

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


#print(silent_segments, non_silent_segments)