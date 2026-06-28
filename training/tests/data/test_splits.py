from pathlib import Path

import pytest

from medlocal_training.data.splits import SplitIds, split_by_held_out_ids


def test_held_out_ids_become_the_test_split() -> None:
    splits = split_by_held_out_ids(["3", "1", "2", "4"], {"2", "4"})

    assert splits.test == ("2", "4")
    assert splits.validation == ("1", "3")


def test_rejects_held_out_ids_missing_from_the_dataset() -> None:
    with pytest.raises(ValueError, match="not in the dataset"):
        split_by_held_out_ids(["1"], {"1", "99"})


def test_survives_a_round_trip_to_disk(tmp_path: Path) -> None:
    splits = SplitIds(validation=("1",), test=("2", "3"))
    path = tmp_path / "nested" / "splits.json"

    splits.write(path)

    assert SplitIds.read(path) == splits
