import json
from collections.abc import Sequence
from typing import Any
from urllib.request import urlopen

from datasets import load_dataset

from medlocal_training.data.sample import QaSample
from medlocal_training.data.sampling import balanced_indices
from medlocal_training.data.source import SplitName
from medlocal_training.data.splits import SplitIds, split_by_held_out_ids

_REPO = "qiaojin/PubMedQA"
_OFFICIAL_TEST_IDS_URL = (
    "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/test_ground_truth.json"
)
_VALIDATION_SIZE = 150
_SPLIT_SEED = 20260919


class PubMedQaSource:
    """Expert-labelled questions in every split, plus machine-labelled ones for training.

    The machine-labelled subset is 93% "yes" and has no "maybe", so it is sampled with equal
    shares per label and only ever added on top of the expert-labelled training questions.
    """

    labels = ("yes", "no", "maybe")

    def __init__(self, splits: SplitIds, artificial_train_samples: int = 0, seed: int = 0) -> None:
        self._splits = splits
        self._artificial_train_samples = artificial_train_samples
        self._seed = seed

    def load(self, split: SplitName) -> Sequence[QaSample]:
        wanted = set(getattr(self._splits, split))
        samples = [sample for sample in _read_labeled() if sample.id in wanted]

        if split == "train" and self._artificial_train_samples:
            samples += _read_artificial(self._artificial_train_samples, self._seed)
        return samples


def build_official_splits() -> SplitIds:
    with urlopen(_OFFICIAL_TEST_IDS_URL, timeout=30) as response:
        official_test_ids = set(json.load(response))

    labeled_ids = (sample.id for sample in _read_labeled())
    return split_by_held_out_ids(labeled_ids, official_test_ids, _VALIDATION_SIZE, _SPLIT_SEED)


def _read_labeled() -> list[QaSample]:
    return [_to_sample(row) for row in load_dataset(_REPO, "pqa_labeled", split="train")]


def _read_artificial(size: int, seed: int) -> list[QaSample]:
    rows = load_dataset(_REPO, "pqa_artificial", split="train")
    indices = balanced_indices(rows["final_decision"], size, seed)
    return [_to_sample(row) for row in rows.select(indices)]


def _to_sample(row: dict[str, Any]) -> QaSample:
    return QaSample(
        id=str(row["pubid"]),
        question=row["question"],
        context="\n".join(row["context"]["contexts"]),
        answer=row["final_decision"],
    )
