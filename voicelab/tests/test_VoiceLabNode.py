import sys
import os
import parselmouth
import pytest
import pandas as pd
from glob import glob


# Set up paths
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
VOICELAB_DIR = os.path.dirname(TEST_DIR)
AUDIO_DIR = os.path.join(VOICELAB_DIR, 'tests/assets/audio')

# in order for the relative imports in the files we are testing to run correctly,
# we need to add these directories to the path
sys.path.insert(0, ''.join([VOICELAB_DIR, "/src/Voicelab/toolkits/Voicelab"]))
sys.path.insert(0, ''.join([VOICELAB_DIR, "/src"]))
import VoicelabNode  # Pycharm doesn't like this, but it works


# Arrange
def get_pitch_bounds_validation_data():
    df = pd.read_csv(os.path.join(VOICELAB_DIR, '/home/david/Dropbox/voicelab-poetry/voicelab/tests/assets/audio/pitch_bounds.csv'), header=0)
    return df


# Arrange
def get_max_formant_validation_data():
    df = pd.read_csv(os.path.join(VOICELAB_DIR, '/home/david/Dropbox/voicelab-poetry/voicelab/tests/assets/audio/max_formant.csv'), header=0)
    return df

# Arrange
def get_test_files():
    test_files = sorted(glob(os.path.join(AUDIO_DIR, '*.wav')))[1:]
    number_of_test_files = len(test_files)
    return number_of_test_files, test_files


# Arrange
def prepare_node(file_path):
    node = VoicelabNode.VoicelabNode()
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
def get_number_of_test_files():
    number_of_test_files, _ = get_test_files()
    return number_of_test_files


# Arrange
def generate_pitch_bounds(execution_number):
    number_of_test_files, test_files = get_test_files()
    filename = test_files[execution_number]
    node = prepare_node(filename)
    # Run the node
    test_pitch_floor, test_pitch_ceiling = node.pitch_bounds(filename)
    print(f"{filename}, {test_pitch_floor= }, {test_pitch_ceiling=}")
    # Validate the results
    validation_data = get_pitch_bounds_validation_data()
    validation_floor = validation_data.iloc[execution_number]['floor']
    validation_ceiling = validation_data.iloc[execution_number]['ceiling']
    return test_pitch_floor, test_pitch_ceiling, validation_floor, validation_ceiling

def generate_pitch_floor(execution_number):
    number_of_test_files, test_files = get_test_files()
    filename = test_files[execution_number]
    node = prepare_node(filename)
    # Run the node
    test_pitch_floor = node.pitch_floor(filename)
    print(f"{filename}, {test_pitch_floor= }")
    # Validate the results
    validation_data = get_pitch_bounds_validation_data()
    validation_floor = validation_data.iloc[execution_number]['floor']
    return test_pitch_floor, validation_floor

def generate_pitch_floor(execution_number):
    number_of_test_files, test_files = get_test_files()
    filename = test_files[execution_number]
    node = prepare_node(filename)
    # Run the node
    test_pitch_floor = node.pitch_floor(filename)
    print(f"{filename}, {test_pitch_floor= }")
    # Get the validation data
    validation_data = get_pitch_bounds_validation_data()
    validation_floor = validation_data.iloc[execution_number]['floor']
    return test_pitch_floor, validation_floor

def generate_max_formant(execution_number):
    number_of_test_files, test_files = get_test_files()
    filename = test_files[execution_number]
    node = prepare_node(filename)
    # Run the node
    test_max_formant = node.max_formant(filename)
    print(f"{filename}, {test_max_formant= }")
    # Get the validation data
    validation_data = get_max_formant_validation_data()
    validation_max_formant = validation_data.iloc[execution_number]['max_formant']
    return test_max_formant, validation_max_formant

# Act
@pytest.mark.parametrize('execution_number', range(get_number_of_test_files()))
def test_PitchBounds(execution_number):
    test_floor, test_ceiling, validation_floor, validation_ceiling = generate_pitch_bounds(execution_number)
    assert test_floor == validation_floor and test_ceiling == validation_ceiling

# Act
@pytest.mark.parametrize('execution_number', range(get_number_of_test_files()))
def test_PitchFloor(execution_number):
    test_floor, _, validation_floor, _ = generate_pitch_bounds(execution_number)
    assert test_floor == validation_floor

# Act
@pytest.mark.parametrize('execution_number', range(get_number_of_test_files()))
def test_PitchCeiling(execution_number):
    _, test_ceiling, _, validation_ceiling = generate_pitch_bounds(execution_number)
    assert test_ceiling == validation_ceiling
