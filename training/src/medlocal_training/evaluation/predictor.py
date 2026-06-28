from collections.abc import Sequence
from typing import Protocol

from medlocal_training.data.sample import QaSample


class AnswerPredictor(Protocol):
    def predict(self, samples: Sequence[QaSample], labels: Sequence[str]) -> list[str]: ...
