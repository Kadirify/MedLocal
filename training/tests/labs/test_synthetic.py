from pathlib import Path

import pytest

from medlocal_training.labs.analyte import AnalyteCatalog, Language
from medlocal_training.labs.prompt import render_report
from medlocal_training.labs.report import Flag, LabReport
from medlocal_training.labs.synthetic import SyntheticReportGenerator

CATALOG = AnalyteCatalog.read(Path(__file__).parents[3] / "reference" / "analytes.yaml")


def _reports(seed: int, count: int) -> list[LabReport]:
    generator = SyntheticReportGenerator(CATALOG, seed)
    return [generator.generate() for _ in range(count)]


def _values(report: LabReport) -> dict[str, float]:
    return {result.key: result.value for result in report.results}


def test_same_seed_generates_the_same_reports() -> None:
    first = [render_report(r, Language.ENGLISH) for r in _reports(1, 20)]
    second = [render_report(r, Language.ENGLISH) for r in _reports(1, 20)]

    assert first == second


def test_values_never_reach_critical_limits() -> None:
    for report in _reports(2, 500):
        for result in report.results:
            critical = result.analyte.critical
            assert critical.low is None or result.value > critical.low
            assert critical.high is None or result.value < critical.high
            assert result.value >= 0


def test_reports_are_a_mix_of_all_normal_and_flagged() -> None:
    flagged_counts = [len(report.flagged()) for report in _reports(3, 300)]

    assert 20 < flagged_counts.count(0) < 100
    assert max(flagged_counts) >= 4


def test_red_cell_indices_follow_from_the_values_they_are_calculated_from() -> None:
    checked = 0
    for report in _reports(4, 300):
        values = _values(report)
        if not {"hemoglobin", "hematocrit", "red_blood_cells", "mch", "mchc"} <= set(values):
            continue
        checked += 1
        hemoglobin, hematocrit = values["hemoglobin"], values["hematocrit"]
        assert 2.85 <= hematocrit / hemoglobin <= 3.15
        assert values["mch"] == pytest.approx(hemoglobin * 10 / values["red_blood_cells"], abs=0.3)
        assert values["mchc"] == pytest.approx(hemoglobin * 100 / hematocrit, abs=0.3)

    assert checked > 10


def test_white_cell_shares_add_up_and_counts_follow_from_them() -> None:
    checked = 0
    for report in _reports(5, 300):
        values = _values(report)
        if "neutrophils_abs" not in values:
            continue
        checked += 1
        shares = [values[f"{cell}_pct"] for cell in _CELLS]
        assert sum(shares) == pytest.approx(100, abs=0.3)
        expected = values["white_blood_cells"] * values["neutrophils_pct"] / 100
        assert values["neutrophils_abs"] == pytest.approx(expected, abs=0.06)

    assert checked > 10


def test_a_full_panel_is_never_combined_with_its_short_version() -> None:
    for report in _reports(6, 300):
        keys = [result.key for result in report.results]
        assert len(keys) == len(set(keys))


@pytest.mark.parametrize("language", list(Language))
def test_rendering_prints_one_line_per_result(language: Language) -> None:
    report = _reports(7, 1)[0]
    text = render_report(report, language)

    assert text.count("\n- ") == len(report.results)
    for result in report.results:
        assert f"- {result.analyte.display_name(language)}: " in text


def test_turkish_rendering_uses_turkish_flags() -> None:
    report = next(r for r in _reports(8, 50) if any(x.flag is Flag.LOW for x in r.results))

    assert "DÜŞÜK" in render_report(report, Language.TURKISH)
    assert "LOW" not in render_report(report, Language.TURKISH)


_CELLS = ("neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils")
