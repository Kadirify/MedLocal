import random

from medlocal_training.labs.analyte import Analyte, AnalyteCatalog, ReferenceRange, Sex
from medlocal_training.labs.report import LabReport, LabResult

_MAX_PANELS = 3
_MAX_DEVIATION = 0.4
# keeps generated values clear of the limits that the app answers with a fixed message
_CRITICAL_MARGIN = 0.05

# how many independently drawn results of a report are abnormal, and how often
_ABNORMAL_COUNTS = (0, 1, 2, 3, 4, 5, 6)
_ABNORMAL_WEIGHTS = (20, 30, 22, 14, 8, 4, 2)

# a panel listed here makes the shorter version of itself redundant
_SUPERSEDES = {
    "complete_blood_count": "short_blood_count",
    "liver": "liver_short",
    "thyroid": "thyroid_short",
}

# hematocrit is close to three times hemoglobin in real samples
_HEMATOCRIT_PER_HEMOGLOBIN = (2.9, 3.1)

_DIFFERENTIAL = ("neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils")
_DERIVED_FROM_RED_CELLS = ("hematocrit", "red_blood_cells", "mch", "mchc")
_DERIVED = {*_DERIVED_FROM_RED_CELLS, *(f"{cell}_abs" for cell in _DIFFERENTIAL)}


class SyntheticReportGenerator:
    """Draws reports a laboratory could plausibly print.

    Values that an analyser calculates from others (hematocrit, red cell indices, absolute
    white cell counts) are calculated here too, so a report never contradicts itself.
    """

    def __init__(self, catalog: AnalyteCatalog, seed: int) -> None:
        self._catalog = catalog
        self._rng = random.Random(seed)

    def generate(self) -> LabReport:
        rng = self._rng
        sex = rng.choice(list(Sex))
        keys = self._pick_analytes()

        drawn = [key for key in keys if key not in _DERIVED or not self._can_derive(key, keys)]
        wanted = rng.choices(_ABNORMAL_COUNTS, _ABNORMAL_WEIGHTS)[0]
        abnormal = set(rng.sample(drawn, min(wanted, len(drawn))))

        values = {
            key: self._draw(self._catalog.analytes[key], sex, abnormal=key in abnormal)
            for key in drawn
        }
        self._derive_red_cell_values(values, keys)
        self._derive_white_cell_counts(values, keys)

        results = tuple(self._result(key, values[key], sex) for key in keys)
        return LabReport(sex=sex, age=rng.randint(18, 85), results=results)

    def _result(self, key: str, value: float, sex: Sex) -> LabResult:
        analyte = self._catalog.analytes[key]
        kept_clear = _clear_of_critical(analyte, value)
        return LabResult(key, analyte, round(kept_clear, analyte.decimals), analyte.range_for(sex))

    def _pick_analytes(self) -> list[str]:
        panels = self._rng.sample(sorted(self._catalog.panels), self._rng.randint(1, _MAX_PANELS))
        redundant = {_SUPERSEDES[panel] for panel in panels if panel in _SUPERSEDES}
        ordered = [
            key for panel in panels if panel not in redundant for key in self._catalog.panels[panel]
        ]
        return list(dict.fromkeys(ordered))

    @staticmethod
    def _can_derive(key: str, keys: list[str]) -> bool:
        if key in _DERIVED_FROM_RED_CELLS:
            return "hemoglobin" in keys
        return "white_blood_cells" in keys and key.replace("_abs", "_pct") in keys

    def _draw(self, analyte: Analyte, sex: Sex, *, abnormal: bool) -> float:
        reference = analyte.range_for(sex)
        value = self._outside(reference) if abnormal else self._inside(reference)
        # clamped before anything is calculated from it, so derived values stay consistent
        return _clear_of_critical(analyte, value)

    def _inside(self, reference: ReferenceRange) -> float:
        low = reference.low if reference.low is not None else 0.5 * _required(reference.high)
        high = reference.high if reference.high is not None else 1.8 * _required(reference.low)
        margin = 0.05 * (high - low)
        return self._rng.uniform(low + margin, high - margin)

    def _outside(self, reference: ReferenceRange) -> float:
        sides = [side for side in ("low", "high") if getattr(reference, side) is not None]
        deviation = self._rng.uniform(0.03, _MAX_DEVIATION)
        if self._rng.choice(sides) == "low":
            return _required(reference.low) * (1 - deviation)
        return _required(reference.high) * (1 + deviation)

    def _derive_red_cell_values(self, values: dict[str, float], keys: list[str]) -> None:
        if "hemoglobin" not in values:
            return
        hemoglobin = values["hemoglobin"]
        hematocrit = _clear_of_critical(
            self._catalog.analytes["hematocrit"],
            hemoglobin * self._rng.uniform(*_HEMATOCRIT_PER_HEMOGLOBIN),
        )
        cell_volume = values.get("mcv", self._rng.uniform(84, 96))
        red_cells = hematocrit * 10 / cell_volume

        derived = {
            "hematocrit": hematocrit,
            "red_blood_cells": red_cells,
            "mch": hemoglobin * 10 / red_cells,
            "mchc": hemoglobin * 100 / hematocrit,
        }
        values.update({key: value for key, value in derived.items() if key in keys})

    def _derive_white_cell_counts(self, values: dict[str, float], keys: list[str]) -> None:
        shares = [f"{cell}_pct" for cell in _DIFFERENTIAL]
        if all(share in values for share in shares):
            total = sum(values[share] for share in shares)
            for share in shares:
                values[share] *= 100 / total

        for cell in _DIFFERENTIAL:
            count, share = f"{cell}_abs", f"{cell}_pct"
            if count in keys and count not in values:
                values[count] = values["white_blood_cells"] * values[share] / 100


def _clear_of_critical(analyte: Analyte, value: float) -> float:
    low, high = analyte.critical.low, analyte.critical.high
    if low is not None:
        value = max(value, low * (1 + _CRITICAL_MARGIN))
    if high is not None:
        value = min(value, high * (1 - _CRITICAL_MARGIN))
    return max(value, 0.0)


def _required(bound: float | None) -> float:
    if bound is None:
        raise ValueError("reference range is missing the bound being sampled")
    return bound
