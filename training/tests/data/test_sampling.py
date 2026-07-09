from collections import Counter

import pytest

from medlocal_training.data.sampling import balanced_indices

LABELS = ["yes"] * 90 + ["no"] * 10


def test_every_label_gets_an_equal_share() -> None:
    picked = balanced_indices(LABELS, size=10, seed=0)

    assert Counter(LABELS[i] for i in picked) == {"yes": 5, "no": 5}
    assert len(set(picked)) == 10


def test_same_seed_picks_the_same_positions() -> None:
    assert balanced_indices(LABELS, 10, seed=3) == balanced_indices(LABELS, 10, seed=3)


def test_rejects_a_share_larger_than_the_rarest_label() -> None:
    with pytest.raises(ValueError, match="only 10 samples"):
        balanced_indices(LABELS, size=40, seed=0)


def test_rejects_a_size_that_cannot_be_shared_equally() -> None:
    with pytest.raises(ValueError, match="shared equally"):
        balanced_indices(LABELS, size=5, seed=0)
