from pathlib import Path

import pytest

from medlocal_training.data.splits import SplitIds, split_by_held_out_ids

IDS = [str(i) for i in range(10)]


def test_held_out_ids_become_the_test_split() -> None:
    splits = split_by_held_out_ids(IDS, {"2", "4"}, validation_size=3, seed=0)

    assert splits.test == ("2", "4")
    assert len(splits.validation) == 3
    assert len(splits.train) == 5


def test_splits_never_overlap_and_cover_every_id() -> None:
    splits = split_by_held_out_ids(IDS, {"2", "4"}, validation_size=3, seed=0)
    parts = [set(splits.train), set(splits.validation), set(splits.test)]

    assert set.union(*parts) == set(IDS)
    assert sum(len(part) for part in parts) == len(IDS)


def test_same_seed_gives_the_same_split() -> None:
    first = split_by_held_out_ids(IDS, {"1"}, validation_size=4, seed=7)
    second = split_by_held_out_ids(reversed(IDS), {"1"}, validation_size=4, seed=7)

    assert first == second


def test_rejects_held_out_ids_missing_from_the_dataset() -> None:
    with pytest.raises(ValueError, match="not in the dataset"):
        split_by_held_out_ids(["1", "2"], {"1", "99"}, validation_size=1, seed=0)


def test_rejects_a_validation_split_that_leaves_nothing_to_train_on() -> None:
    with pytest.raises(ValueError, match="no training ids"):
        split_by_held_out_ids(["1", "2", "3"], {"1"}, validation_size=2, seed=0)


def test_survives_a_round_trip_to_disk(tmp_path: Path) -> None:
    splits = SplitIds(train=("0",), validation=("1",), test=("2", "3"))
    path = tmp_path / "nested" / "splits.json"

    splits.write(path)

    assert SplitIds.read(path) == splits
