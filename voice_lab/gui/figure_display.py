from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from voice_lab.Algorithms.VisualizeSpectrogramNode import VisualizeSpectrogramNode
import numpy as np
import parselmouth


# Define a class that inherits from FigureCanvas
class MplCanvas(FigureCanvas):
    """Class to create a matplotlib canvas for plotting
    This is used in the main window to display plots
    """
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
    
    def display_spectrogram(self, signal, sampling_rate):
        # Clear the previous plot
        self.axes.clear()  
        
        # Convert signal to ParSelmouth Sound object
        sound = parselmouth.Sound(signal.T, sampling_rate)
        
        # Calculate the spectrogram
        spectrogram = sound.to_spectrogram()
        X, Y = spectrogram.x_grid(), spectrogram.y_grid()
        
        # Calculate the spectrogram in dB
        sg_db = 10 * np.log10(spectrogram.values)
        dynamic_range = 70
        
        # Display the spectrogram using pcolormesh
        self.axes.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
        
        # Set labels
        self.axes.set_ylabel('Frequency [Hz]')
        self.axes.set_xlabel('Time [sec]')
        
        # Redraw canvas
        self.draw()