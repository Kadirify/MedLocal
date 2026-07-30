from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from medlocal_training.evaluation.text_overlap import rouge_l
from medlocal_training.labs.explanation_checks import failed_checks
from medlocal_training.labs.report import LabReport


@dataclass(frozen=True)
class ExplanationMetrics:
    samples: int
    passed_every_check: float
    failure_rate_per_check: dict[str, float]
    rouge_l_to_teacher: float
    mean_words: float


def score_explanations(
    reports: Sequence[LabReport], teacher: Sequence[str], generated: Sequence[str]
) -> ExplanationMetrics:
    if not (len(reports) == len(teacher) == len(generated)):
        raise ValueError("reports, teacher texts and generated texts differ in length")
    if not reports:
        raise ValueError("cannot score an empty set")

    failures = [failed_checks(r, text) for r, text in zip(reports, generated, strict=True)]
    per_check = Counter(name for failed in failures for name in failed)
    count = len(reports)

    return ExplanationMetrics(
        samples=count,
        passed_every_check=sum(not failed for failed in failures) / count,
        failure_rate_per_check={name: n / count for name, n in sorted(per_check.items())},
        rouge_l_to_teacher=sum(map(rouge_l, teacher, generated)) / count,
        mean_words=sum(len(text.split()) for text in generated) / count,
    )
