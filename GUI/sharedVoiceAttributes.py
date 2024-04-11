import parselmouth
from parselmouth.praat import call
import numpy as np
import soundfile as sf
from hashlib import sha256
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class Unionable:
    def __or__(self, other):
        self_dict = asdict(self)
        other_dict = asdict(other)

        # Merge the 'extra_attributes' dictionaries
        if 'extra_attributes' in self_dict and 'extra_attributes' in other_dict:
            self_dict['extra_attributes'] = {**self_dict['extra_attributes'], **other_dict['extra_attributes']}
            other_dict.pop('extra_attributes')

        # Remove 'unique_id' from 'extra_attributes' if it exists
        self_dict['extra_attributes'].pop('unique_id', None)
        other_dict.pop('unique_id', None)
        other_dict.pop('path_to_file', None)
        other_dict.pop('filename', None)
        other_dict.pop('signal', None)
        other_dict.pop('sampling_rate', None)
        other_dict.pop('duration', None)
        other_dict.pop('time_vector', None)
        

        return self.__class__(**self_dict, **other_dict)

@dataclass
class VoiceFile(Unionable):
    unique_id: str
    path_to_file: str
    filename: str
    signal: np.ndarray
    sampling_rate: int | float
    duration: float
    time_vector: np.ndarray
    extra_attributes: dict = field(default_factory=dict)

    def add_attribute(self, key: str, value: Any):
        """
        Adds or updates an optional attribute associated with the voice file.

        :param key: The attribute name.
        :param value: The attribute value.
        """
        self.extra_attributes[key] = value


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

        # store the data in the VoiceFile object
        return VoiceFile(
            unique_id=self.id,
            path_to_file=self.sound_file,
            filename=self.filename,
            signal=self.signal,
            sampling_rate=self.sampling_rate,
            duration=self.sound.duration,
            time_vector=self.time_vector,
            extra_attributes={
                "sound": self.sound
            }
        )

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