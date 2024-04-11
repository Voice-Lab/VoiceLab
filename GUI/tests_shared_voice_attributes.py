import unittest
from sharedVoiceAttributes import VoiceAttributes, VoiceFile
import numpy as np

class TestSharedVoiceAttributes(unittest.TestCase):
    def setUp(self):
        self.sound_file = '/home/david/Dropbox/Work/stimuli/Yiddish/reyd-dataset/audio/lit1/vz1279.wav'
        self.sva = VoiceAttributes(self.sound_file)  

    def test_load_sound_praat(self):
        result = self.sva.load_sound_praat()
        self.assertIsInstance(result, VoiceFile)
        self.assertTrue(isinstance(result.signal, np.ndarray))
        self.assertTrue(isinstance(result.sampling_rate, (int, float)))
        self.assertTrue(isinstance(result.time_vector, np.ndarray))
        # Checking for additional attribute 'sound' presence
        self.assertIn('sound', result.extra_attributes)

    def test_get_unscaled_signal(self):
        result = self.sva.get_unscaled_signal()
        self.assertIsInstance(result, VoiceFile)
        self.assertTrue(isinstance(result.signal, np.ndarray))
        self.assertTrue(isinstance(result.sampling_rate, (int, float)))
        self.assertTrue(isinstance(result.time_vector, np.ndarray))
        # Ensure 'duration' is a float
        self.assertTrue(isinstance(result.duration, float))

if __name__ == '__main__':
    unittest.main()
