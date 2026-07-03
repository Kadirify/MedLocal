import pytest

from medlocal_training.evaluation.report_metrics import rouge_l, score_reports


def test_identical_reports_score_one() -> None:
    words = ["lungs", "are", "clear"]

    assert rouge_l(words, words) == 1.0


def test_unrelated_reports_score_zero() -> None:
    assert rouge_l(["lungs", "are", "clear"], ["cardiomegaly", "present"]) == 0.0


def test_rewards_shared_words_only_when_they_keep_their_order() -> None:
    reference = ["no", "pleural", "effusion", "or", "pneumothorax"]

    in_order = rouge_l(reference, ["no", "effusion", "pneumothorax"])
    shuffled = rouge_l(reference, ["pneumothorax", "effusion", "no"])

    assert in_order == pytest.approx(0.75)
    assert shuffled == pytest.approx(0.25)


def test_scoring_ignores_case_and_punctuation() -> None:
    metrics = score_reports(["Lungs are clear."], ["lungs are clear"])

    assert metrics.rouge_l == 1.0
    assert metrics.mean_reference_words == 3


def test_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="generated"):
        score_reports(["a"], [])
