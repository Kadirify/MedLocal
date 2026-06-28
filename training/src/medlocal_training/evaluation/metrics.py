from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationMetrics:
    samples: int
    accuracy: float
    macro_f1: float
    f1_per_label: dict[str, float]
    majority_class_accuracy: float


def score(
    expected: Sequence[str], predicted: Sequence[str], labels: Sequence[str]
) -> ClassificationMetrics:
    if len(expected) != len(predicted):
        raise ValueError(f"{len(expected)} expected answers but {len(predicted)} predictions")
    if not expected:
        raise ValueError("cannot score an empty set")

    correct = sum(e == p for e, p in zip(expected, predicted, strict=True))
    f1_per_label = {label: _f1(expected, predicted, label) for label in labels}

    return ClassificationMetrics(
        samples=len(expected),
        accuracy=correct / len(expected),
        macro_f1=sum(f1_per_label.values()) / len(f1_per_label),
        f1_per_label=f1_per_label,
        majority_class_accuracy=Counter(expected).most_common(1)[0][1] / len(expected),
    )


def _f1(expected: Sequence[str], predicted: Sequence[str], label: str) -> float:
    pairs = list(zip(expected, predicted, strict=True))
    true_positive = sum(e == label and p == label for e, p in pairs)
    false_positive = sum(e != label and p == label for e, p in pairs)
    false_negative = sum(e == label and p != label for e, p in pairs)

    denominator = 2 * true_positive + false_positive + false_negative
    return 2 * true_positive / denominator if denominator else 0.0
