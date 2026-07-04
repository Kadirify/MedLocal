import re
from collections.abc import Sequence
from dataclasses import dataclass

_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class ReportMetrics:
    samples: int
    rouge_l: float
    mean_reference_words: float
    mean_generated_words: float


def score_reports(references: Sequence[str], generated: Sequence[str]) -> ReportMetrics:
    if len(references) != len(generated):
        raise ValueError(f"{len(references)} references but {len(generated)} generated reports")
    if not references:
        raise ValueError("cannot score an empty set")

    pairs = [(_words(r), _words(g)) for r, g in zip(references, generated, strict=True)]
    count = len(pairs)

    return ReportMetrics(
        samples=count,
        rouge_l=sum(rouge_l(r, g) for r, g in pairs) / count,
        mean_reference_words=sum(len(r) for r, _ in pairs) / count,
        mean_generated_words=sum(len(g) for _, g in pairs) / count,
    )


def rouge_l(reference: Sequence[str], candidate: Sequence[str]) -> float:
    """F1 over the longest common subsequence of words."""
    common = _longest_common_subsequence(reference, candidate)
    if common == 0:
        return 0.0

    precision = common / len(candidate)
    recall = common / len(reference)
    return 2 * precision * recall / (precision + recall)


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _longest_common_subsequence(a: Sequence[str], b: Sequence[str]) -> int:
    previous = [0] * (len(b) + 1)
    for item in a:
        current = [0]
        for index, other in enumerate(b, start=1):
            if item == other:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1]
