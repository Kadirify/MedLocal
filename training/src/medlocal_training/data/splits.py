import random
from collections.abc import Collection, Iterable
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class SplitIds(BaseModel):
    model_config = ConfigDict(frozen=True)

    train: tuple[str, ...]
    validation: tuple[str, ...]
    test: tuple[str, ...]

    @classmethod
    def read(cls, path: Path) -> "SplitIds":
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")


def split_by_held_out_ids(
    all_ids: Iterable[str], held_out: Collection[str], validation_size: int, seed: int
) -> SplitIds:
    ids = sorted(set(all_ids))
    missing = set(held_out) - set(ids)
    if missing:
        raise ValueError(f"{len(missing)} held-out ids are not in the dataset")

    remaining = [i for i in ids if i not in held_out]
    if validation_size >= len(remaining):
        raise ValueError(f"validation_size {validation_size} leaves no training ids")

    random.Random(seed).shuffle(remaining)
    return SplitIds(
        train=tuple(sorted(remaining[validation_size:])),
        validation=tuple(sorted(remaining[:validation_size])),
        test=tuple(i for i in ids if i in held_out),
    )
