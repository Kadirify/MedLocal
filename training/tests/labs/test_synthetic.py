from pathlib import Path

from medlocal_training.labs.analyte import AnalyteCatalog
from medlocal_training.labs.prompt import render_report
from medlocal_training.labs.report import Flag
from medlocal_training.labs.synthetic import SyntheticReportGenerator

CATALOG = AnalyteCatalog.read(Path(__file__).parents[3] / "reference" / "analytes.yaml")


def test_same_seed_generates_the_same_reports() -> None:
    first = SyntheticReportGenerator(CATALOG, seed=1)
    second = SyntheticReportGenerator(CATALOG, seed=1)

    assert [render_report(first.generate()) for _ in range(20)] == [
        render_report(second.generate()) for _ in range(20)
    ]


def test_values_never_reach_critical_limits() -> None:
    generator = SyntheticReportGenerator(CATALOG, seed=2)

    for _ in range(500):
        for result in generator.generate().results:
            critical = result.analyte.critical
            assert critical.low is None or result.value > critical.low
            assert critical.high is None or result.value < critical.high
            assert result.value >= 0


def test_reports_are_a_mix_of_all_normal_and_flagged() -> None:
    generator = SyntheticReportGenerator(CATALOG, seed=3)
    flagged_counts = [len(generator.generate().flagged()) for _ in range(300)]

    assert 30 < flagged_counts.count(0) < 100
    assert max(flagged_counts) >= 3


def test_hematocrit_follows_hemoglobin() -> None:
    generator = SyntheticReportGenerator(CATALOG, seed=4)

    for _ in range(300):
        values = {result.key: result.value for result in generator.generate().results}
        if "hemoglobin" in values and "hematocrit" in values:
            assert 2.85 <= values["hematocrit"] / values["hemoglobin"] <= 3.15


def test_rendered_flags_match_the_printed_range() -> None:
    report = SyntheticReportGenerator(CATALOG, seed=5).generate()
    text = render_report(report)

    assert text.startswith(f"Patient: {report.sex.value}, {report.age} years old")
    for result in report.results:
        assert f"- {result.analyte.name}: " in text
    assert text.count(Flag.NORMAL.value) == sum(r.flag is Flag.NORMAL for r in report.results)
