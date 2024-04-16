import parselmouth
from parselmouth.praat import call
import numpy as np
import soundfile as sf
from hashlib import sha256
from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import Any
import numpy as np

@dataclass
class Unionable:
    def __or__(self, other):
        # Ensure both objects are instances of Unionable
        if not isinstance(other, Unionable):
            return NotImplemented

        # Initialize a new instance of the class without setting any fields
        new_instance = self.__class__.__new__(self.__class__)

        # Merge fields defined in the dataclass
        for field in fields(self):
            value = getattr(other, field.name, getattr(self, field.name, None))
            setattr(new_instance, field.name, value)

        # Merge dynamically added attributes
        dynamic_attrs = set(self.__dict__.keys()).union(other.__dict__.keys()) - {field.name for field in fields(self)}
        for attr in dynamic_attrs:
            value = getattr(other, attr, getattr(self, attr, None))
            setattr(new_instance, attr, value)

        return new_instance

@dataclass
class VoiceFile(Unionable):
    unique_id: str
    path_to_file: str
    filename: str
    signal: np.ndarray
    sampling_rate: int | float
    duration: float
    time_vector: np.ndarray
    
    def add_attribute(self, key: str, value: Any):
        """
        Dynamically adds or updates an optional attribute associated with the voice file.

        :param key: The attribute name.
        :param value: The attribute value.
        """
        setattr(self, key, value)


class VoiceAttributes:
    def __init__(self, filename):
        self.id = sha256(filename.encode()).hexdigest()
        self.sound_file = filename
        self.filename = self.get_filename()
        self.sound = None
        self.signal = None
        self.sampling_rate = None
        self.time_vector = None
        self.unscaled_signal = None

    def get_filename(self):
        return self.sound_file.split('/')[-1]
    
    def generate_unique_identifier(self):
        """Generate a unique identifier for a file. This example uses the file name."""
        return sha256(self.sound.file_name.encode()).hexdigest()
    
    def get_duration_from_signal(self, signal, sampling_rate):
        return len(signal) / sampling_rate

    def load_sound_praat(self):
        self.sound = parselmouth.Sound(self.sound_file)
        # if sound is stereo, convert to mono
        if self.sound.n_channels == 2:
            self.sound = call(self.sound, "Convert to mono")
        # get the signal from Praat
        self.signal = self.sound.values.T
        # get the sampling rate
        self.sampling_rate = self.sound.sampling_frequency
        # get the time vector
        self.time_vector = self.sound.xs()

        voice_file = VoiceFile(
            unique_id=self.id,
            path_to_file=self.sound_file,
            filename=self.filename,
            signal=self.signal,
            sampling_rate=self.sampling_rate,
            duration=self.sound.duration,
            time_vector=self.time_vector
        )
        voice_file.add_attribute('praat_sound_object', self.sound)
        return voice_file

    def get_unscaled_signal(self):
        # read signal with soundfile
        self.unscaled_signal, self.sampling_rate = sf.read(self.sound_file)
        
        # if signal is stereo, convert to mono
        if len(self.unscaled_signal.shape) == 2:
            self.unscaled_signal = np.mean(self.unscaled_signal, axis=1)
        
        # create time vector
        self.time_vector = np.arange(0, len(self.unscaled_signal)) / self.sampling_rate
        
        # get duration
        duration = self.get_duration_from_signal(self.unscaled_signal, self.sampling_rate)
        
        # return the data in the VoiceFile object
        return VoiceFile(
            unique_id=self.id,
            path_to_file=self.sound_file,
            filename=self.filename,
            signal=self.unscaled_signal,
            sampling_rate=self.sampling_rate,
            duration=duration,
            time_vector=self.time_vector
        )