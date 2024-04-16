from __future__ import annotations
import parselmouth
from parselmouth.praat import call
from typing import Union
from ...pipeline.Node import Node
from .VoicelabNode import VoicelabNode


class MeasureDurationNode(VoicelabNode):
    """Measure the duration of the sound file."""
    def process(self) -> dict[str | Union[float, str]]:
        try:
            """Returns the total duration of a sound file."""
            file_path: str = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            sound: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            return {"Voice Duration": sound.duration}
        except Exception as e:
            return {"Voice Duration": str(e)}
