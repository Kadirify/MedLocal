from collections.abc import Sequence
from typing import Protocol

from medlocal_training.data.report_sample import ReportSample


class ReportGenerator(Protocol):
    def generate(self, samples: Sequence[ReportSample]) -> list[str]: ...
