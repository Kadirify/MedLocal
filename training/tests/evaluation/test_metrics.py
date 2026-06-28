import pytest

from medlocal_training.evaluation.metrics import score

LABELS = ("yes", "no", "maybe")


def test_perfect_predictions_score_one() -> None:
    answers = ["yes", "no", "maybe"]

    metrics = score(answers, answers, LABELS)

    assert metrics.accuracy == 1.0
    assert metrics.macro_f1 == 1.0


def test_always_answering_yes_is_punished_by_macro_f1() -> None:
    expected = ["yes", "yes", "no", "maybe"]
    predicted = ["yes", "yes", "yes", "yes"]

    metrics = score(expected, predicted, LABELS)

    assert metrics.accuracy == 0.5
    assert metrics.f1_per_label == {"yes": pytest.approx(2 / 3), "no": 0.0, "maybe": 0.0}
    assert metrics.macro_f1 == pytest.approx(2 / 9)


def test_reports_the_majority_class_floor() -> None:
    metrics = score(["yes", "yes", "yes", "no"], ["no", "no", "no", "no"], LABELS)

    assert metrics.majority_class_accuracy == 0.75


def test_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="predictions"):
        score(["yes"], [], LABELS)
