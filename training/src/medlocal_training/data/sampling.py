import random
from collections import defaultdict
from collections.abc import Sequence


def balanced_indices(labels: Sequence[str], size: int, seed: int) -> list[int]:
    """Picks `size` positions with an equal share for every label."""
    by_label: dict[str, list[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        by_label[label].append(index)

    share, remainder = divmod(size, len(by_label))
    if remainder:
        raise ValueError(f"size {size} cannot be shared equally by {len(by_label)} labels")

    rng = random.Random(seed)
    picked: list[int] = []
    for label in sorted(by_label):
        if share > len(by_label[label]):
            raise ValueError(f"label {label!r} has only {len(by_label[label])} samples")
        picked.extend(rng.sample(by_label[label], share))

    rng.shuffle(picked)
    return picked
