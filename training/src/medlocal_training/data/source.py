from collections.abc import Sequence
from typing import Literal, Protocol

from medlocal_training.data.sample import QaSample

SplitName = Literal["train", "validation", "test"]


class DatasetSource(Protocol):
    @property
    def labels(self) -> tuple[str, ...]: ...

    def load(self, split: SplitName) -> Sequence[QaSample]: ...
