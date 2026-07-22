import random

from medlocal_training.labs.analyte import Analyte, AnalyteCatalog, ReferenceRange, Sex
from medlocal_training.labs.report import LabReport, LabResult

_ALL_NORMAL_SHARE = 0.2
_ABNORMAL_SHARE = 0.3
_MAX_PANELS = 3
_MAX_DEVIATION = 0.4
# keeps generated values clear of the limits that the app answers with a fixed message
_CRITICAL_MARGIN = 0.05

# hematocrit is close to three times hemoglobin in real samples; independent draws would
# produce reports no laboratory could print
_HEMATOCRIT_PER_HEMOGLOBIN = (2.9, 3.1)


class SyntheticReportGenerator:
    def __init__(self, catalog: AnalyteCatalog, seed: int) -> None:
        self._catalog = catalog
        self._rng = random.Random(seed)

    def generate(self) -> LabReport:
        rng = self._rng
        sex = rng.choice(list(Sex))
        keys = self._pick_analytes()

        all_normal = rng.random() < _ALL_NORMAL_SHARE
        abnormal = set() if all_normal else {k for k in keys if rng.random() < _ABNORMAL_SHARE}
        if not all_normal and not abnormal:
            abnormal = {rng.choice(keys)}

        values = {
            key: self._draw(self._catalog.analytes[key], sex, abnormal=key in abnormal)
            for key in keys
        }
        self._couple_hematocrit(values)

        results = tuple(
            LabResult(key, self._catalog.analytes[key], values[key], self._range(key, sex))
            for key in keys
        )
        return LabReport(sex=sex, age=rng.randint(18, 85), results=results)

    def _range(self, key: str, sex: Sex) -> ReferenceRange:
        return self._catalog.analytes[key].range_for(sex)

    def _pick_analytes(self) -> list[str]:
        panels = self._rng.sample(sorted(self._catalog.panels), self._rng.randint(1, _MAX_PANELS))
        ordered = [key for panel in panels for key in self._catalog.panels[panel]]
        return list(dict.fromkeys(ordered))

    def _draw(self, analyte: Analyte, sex: Sex, *, abnormal: bool) -> float:
        reference = analyte.range_for(sex)
        value = self._outside(analyte, reference) if abnormal else self._inside(reference)
        return round(value, analyte.decimals)

    def _inside(self, reference: ReferenceRange) -> float:
        low = reference.low if reference.low is not None else 0.5 * _required(reference.high)
        high = reference.high if reference.high is not None else 1.8 * _required(reference.low)
        margin = 0.05 * (high - low)
        return self._rng.uniform(low + margin, high - margin)

    def _outside(self, analyte: Analyte, reference: ReferenceRange) -> float:
        sides = [side for side in ("low", "high") if getattr(reference, side) is not None]
        side = self._rng.choice(sides)
        deviation = self._rng.uniform(0.03, _MAX_DEVIATION)

        if side == "low":
            floor = (analyte.critical.low or 0.0) * (1 + _CRITICAL_MARGIN)
            return max(_required(reference.low) * (1 - deviation), floor)

        value = _required(reference.high) * (1 + deviation)
        if analyte.critical.high is None:
            return value
        return min(value, analyte.critical.high * (1 - _CRITICAL_MARGIN))

    def _couple_hematocrit(self, values: dict[str, float]) -> None:
        if "hemoglobin" not in values or "hematocrit" not in values:
            return
        ratio = self._rng.uniform(*_HEMATOCRIT_PER_HEMOGLOBIN)
        decimals = self._catalog.analytes["hematocrit"].decimals
        values["hematocrit"] = round(values["hemoglobin"] * ratio, decimals)


def _required(bound: float | None) -> float:
    if bound is None:
        raise ValueError("reference range is missing the bound being sampled")
    return bound
