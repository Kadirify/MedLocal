import pytest

from medlocal_training.evaluation.text_overlap import rouge_l


def test_identical_texts_score_one() -> None:
    assert rouge_l("Your ferritin is low.", "your ferritin is low") == 1.0


def test_unrelated_texts_score_zero() -> None:
    assert rouge_l("ferritin is low", "cholesterol looks fine") == 0.0


def test_rewards_shared_words_only_when_they_keep_their_order() -> None:
    reference = "no sign of low iron stores"

    in_order = rouge_l(reference, "no low stores")
    shuffled = rouge_l(reference, "stores low no")

    assert in_order == pytest.approx(2 / 3)
    assert shuffled == pytest.approx(2 / 9)
