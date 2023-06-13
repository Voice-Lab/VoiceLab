import sys
import os
import parselmouth
import numpy as np
import pytest

# Set up paths
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
VOICELAB_DIR = os.path.dirname(TEST_DIR)
AUDIO_DIR = os.path.join(VOICELAB_DIR, 'tests/assets/audio')

# in order for the relative imports in the files we are testing to run correctly,
# we need to add these directories to the path
sys.path.insert(0, ''.join([VOICELAB_DIR, "/src/Voicelab/toolkits/Voicelab"]))
sys.path.insert(0, ''.join([VOICELAB_DIR, "/src"]))
import ReverseSoundsNode  # Pycharm doesn't like this, but it works


# Arrange
def get_test_files():
    number_of_test_files = len(os.listdir(AUDIO_DIR)) - 1  # -1 because the first file is a broken sound
    test_files = sorted(os.listdir(AUDIO_DIR))[1:]
    return number_of_test_files, test_files

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

# Arrange
def get_reversed_test_sound(test_file):
    file_path = os.path.join(AUDIO_DIR, test_file)
    validation_sound = parselmouth.Sound(file_path)
    validation_sound.reverse()
    return validation_sound.values

# Arrange
def get_number_of_test_files():
    number_of_test_files, _ = get_test_files()
    return number_of_test_files

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
