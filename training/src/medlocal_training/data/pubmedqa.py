import json
from collections.abc import Sequence
from typing import Any
from urllib.request import urlopen

from datasets import load_dataset

from medlocal_training.data.sample import QaSample
from medlocal_training.data.source import SplitName
from medlocal_training.data.splits import SplitIds, split_by_held_out_ids

_REPO = "qiaojin/PubMedQA"
_OFFICIAL_TEST_IDS_URL = (
    "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/test_ground_truth.json"
)


class PubMedQaSource:
    """Expert-labelled questions for validation and test, machine-labelled ones for training."""

    labels = ("yes", "no", "maybe")

    def __init__(self, splits: SplitIds) -> None:
        self._splits = splits

    def load(self, split: SplitName) -> Sequence[QaSample]:
        if split == "train":
            return _read("pqa_artificial")

        wanted = set(self._splits.validation if split == "validation" else self._splits.test)
        return [sample for sample in _read("pqa_labeled") if sample.id in wanted]


def build_official_splits() -> SplitIds:
    with urlopen(_OFFICIAL_TEST_IDS_URL, timeout=30) as response:
        official_test_ids = set(json.load(response))

    return split_by_held_out_ids((s.id for s in _read("pqa_labeled")), official_test_ids)


def _read(subset: str) -> list[QaSample]:
    rows = load_dataset(_REPO, subset, split="train")
    return [_to_sample(row) for row in rows]


def _to_sample(row: dict[str, Any]) -> QaSample:
    return QaSample(
        id=str(row["pubid"]),
        question=row["question"],
        context="\n".join(row["context"]["contexts"]),
        answer=row["final_decision"],
    )
