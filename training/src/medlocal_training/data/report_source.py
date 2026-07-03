from collections.abc import Sequence
from typing import Protocol

from medlocal_training.data.report_sample import ReportSample
from medlocal_training.data.source import SplitName


class ReportSource(Protocol):
    def load(self, split: SplitName) -> Sequence[ReportSample]: ...
