from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
import parselmouth
import numpy as np
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode
from Voicelab.toolkits.Voicelab.MeasurePitchNode import MeasurePitchNode
from pprint import pprint

def run_node(filename):
    node = MeasurePitchNode()
    node.args['file_path'] = filename
    node.args['voice'] = parselmouth.Sound(node.args['file_path'])
    results = node.process()
    return node, results


def test_results(results):
    # Check if pitch object is a valid pitch object
    assert isinstance(results['Pitch'], parselmouth.Pitch)

    # Check that we get expected results for the sound file
    assert results['Pitch Ceiling'] == 300
    assert results['Pitch Floor'] == 50
    assert results['Pitch Max (F0)'] == 110.62170729714686
    assert results['Pitch Min (F0)'] == 63.73360992459041
    assert results['Standard Deviation Pitch (F0)'] == 11.64020748154102

    # Check that the pitch values are a list of floats
    assert isinstance(results['Pitches'], list)
    assert all(isinstance(pitch, float) for pitch in results['Pitches'])


filename = '/home/david/Desktop/Sderfahrer_mHK66.wav'
node, results = run_node(filename)
test_results(results)