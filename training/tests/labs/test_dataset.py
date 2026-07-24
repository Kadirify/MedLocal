from pathlib import Path

from medlocal_training.labs.analyte import AnalyteCatalog
from medlocal_training.labs.dataset import build_examples, read_examples
from medlocal_training.labs.prompt import render_report
from medlocal_training.labs.report import LabReport
from medlocal_training.labs.synthetic import SyntheticReportGenerator

CATALOG = AnalyteCatalog.read(Path(__file__).parents[3] / "reference" / "analytes.yaml")
FILLER = " ".join(["This sentence only adds length to the text."] * 6)


class CarefulWriter:
    def __init__(self) -> None:
        self.calls = 0

    def write(self, report: LabReport, attempt: int) -> str:
        self.calls += 1
        flagged = " ".join(f"{r.analyte.name} is {r.flag.value.lower()}." for r in report.flagged())
        return f"Here is an overview. {flagged} {FILLER} Please talk to your doctor."


class SloppyThenCarefulWriter(CarefulWriter):
    def write(self, report: LabReport, attempt: int) -> str:
        text = super().write(report, attempt)
        return "Too short." if attempt == 0 else text


def test_writes_every_planned_example(tmp_path: Path) -> None:
    output = tmp_path / "examples.jsonl"

    summary = build_examples(
        SyntheticReportGenerator(CATALOG, seed=1),
        CarefulWriter(),
        {"test": 3, "train": 5},
        max_attempts=1,
        output=output,
    )

    examples = read_examples(output)
    assert summary.written == 8
    assert [e.split for e in examples] == ["test"] * 3 + ["train"] * 5


def test_a_rejected_attempt_is_retried(tmp_path: Path) -> None:
    summary = build_examples(
        SyntheticReportGenerator(CATALOG, seed=1),
        SloppyThenCarefulWriter(),
        {"train": 4},
        max_attempts=2,
        output=tmp_path / "examples.jsonl",
    )

    assert summary.written == 4
    assert summary.rejected_attempts["length"] == 4


def test_an_interrupted_build_resumes_with_the_same_reports(tmp_path: Path) -> None:
    whole, resumed = tmp_path / "whole.jsonl", tmp_path / "resumed.jsonl"
    sizes = {"train": 6}
    build_examples(SyntheticReportGenerator(CATALOG, seed=9), CarefulWriter(), sizes, 1, whole)

    build_examples(
        SyntheticReportGenerator(CATALOG, seed=9), CarefulWriter(), {"train": 2}, 1, resumed
    )
    writer = CarefulWriter()
    summary = build_examples(SyntheticReportGenerator(CATALOG, seed=9), writer, sizes, 1, resumed)

    assert (summary.already_present, summary.written, writer.calls) == (2, 4, 4)
    assert resumed.read_text(encoding="utf-8") == whole.read_text(encoding="utf-8")


def test_a_stored_example_rebuilds_the_same_report(tmp_path: Path) -> None:
    output = tmp_path / "examples.jsonl"
    build_examples(
        SyntheticReportGenerator(CATALOG, seed=5), CarefulWriter(), {"train": 1}, 1, output
    )

    rebuilt = read_examples(output)[0].to_report(CATALOG)

    assert render_report(rebuilt) == render_report(SyntheticReportGenerator(CATALOG, 5).generate())
