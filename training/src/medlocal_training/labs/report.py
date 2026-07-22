from dataclasses import dataclass
from enum import StrEnum

from medlocal_training.labs.analyte import Analyte, ReferenceRange, Sex


class Flag(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


def flag_value(value: float, reference: ReferenceRange) -> Flag:
    if reference.low is not None and value < reference.low:
        return Flag.LOW
    if reference.high is not None and value > reference.high:
        return Flag.HIGH
    return Flag.NORMAL


@dataclass(frozen=True)
class LabResult:
    key: str
    analyte: Analyte
    value: float
    reference: ReferenceRange

    @property
    def flag(self) -> Flag:
        return flag_value(self.value, self.reference)


@dataclass(frozen=True)
class LabReport:
    sex: Sex
    age: int
    results: tuple[LabResult, ...]

    def flagged(self) -> tuple[LabResult, ...]:
        return tuple(result for result in self.results if result.flag is not Flag.NORMAL)
