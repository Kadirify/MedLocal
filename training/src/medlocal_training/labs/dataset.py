import re
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from medlocal_training.data.source import SplitName
from medlocal_training.labs.analyte import AnalyteCatalog, Sex
from medlocal_training.labs.explanation_checks import failed_checks
from medlocal_training.labs.explanation_writer import ExplanationWriter
from medlocal_training.labs.report import LabReport, LabResult
from medlocal_training.labs.synthetic import SyntheticReportGenerator

_BLANK_LINES = re.compile(r"\s*\n\s*")


class StoredResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    analyte: str
    value: float


class LabExplanationExample(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    split: SplitName
    sex: Sex
    age: int
    results: tuple[StoredResult, ...]
    explanation: str

    @classmethod
    def from_report(
        cls, example_id: str, split: SplitName, report: LabReport, explanation: str
    ) -> "LabExplanationExample":
        results = tuple(StoredResult(analyte=r.key, value=r.value) for r in report.results)
        return cls(
            id=example_id,
            split=split,
            sex=report.sex,
            age=report.age,
            results=results,
            explanation=explanation,
        )

    def to_report(self, catalog: AnalyteCatalog) -> LabReport:
        results = tuple(
            LabResult(
                stored.analyte,
                catalog.analytes[stored.analyte],
                stored.value,
                catalog.analytes[stored.analyte].range_for(self.sex),
            )
            for stored in self.results
        )
        return LabReport(sex=self.sex, age=self.age, results=results)


def read_examples(path: Path) -> list[LabExplanationExample]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [LabExplanationExample.model_validate_json(line) for line in lines if line]


@dataclass(frozen=True)
class BuildSummary:
    written: int
    already_present: int
    gave_up: int
    rejected_attempts: dict[str, int]


def build_examples(
    generator: SyntheticReportGenerator,
    writer: ExplanationWriter,
    sizes: dict[SplitName, int],
    max_attempts: int,
    output: Path,
) -> BuildSummary:
    """Appends as it goes, so an interrupted build resumes where it stopped.

    Reports are always drawn in the same order; an id that is already in the file only
    advances the generator.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    present = {example.id for example in read_examples(output)} if output.exists() else set()

    written = gave_up = 0
    rejected: Counter[str] = Counter()

    with output.open("a", encoding="utf-8") as file:
        for example_id, split in _planned_ids(sizes):
            report = generator.generate()
            if example_id in present:
                continue

            explanation = _write_accepted(writer, report, max_attempts, rejected)
            if explanation is None:
                gave_up += 1
                continue

            example = LabExplanationExample.from_report(example_id, split, report, explanation)
            file.write(example.model_dump_json() + "\n")
            file.flush()
            written += 1

    return BuildSummary(written, len(present), gave_up, dict(rejected))


def _planned_ids(sizes: dict[SplitName, int]) -> Iterator[tuple[str, SplitName]]:
    for split, size in sizes.items():
        for index in range(size):
            yield f"{split}-{index:05d}", split


def _write_accepted(
    writer: ExplanationWriter, report: LabReport, max_attempts: int, rejected: Counter[str]
) -> str | None:
    for attempt in range(max_attempts):
        explanation = _BLANK_LINES.sub("\n", writer.write(report, attempt))
        failures = failed_checks(report, explanation)
        if not failures:
            return explanation
        rejected.update(failures)
    return None
