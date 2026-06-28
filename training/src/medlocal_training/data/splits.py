from collections.abc import Collection, Iterable
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class SplitIds(BaseModel):
    model_config = ConfigDict(frozen=True)

    validation: tuple[str, ...]
    test: tuple[str, ...]

    @classmethod
    def read(cls, path: Path) -> "SplitIds":
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")


def split_by_held_out_ids(all_ids: Iterable[str], held_out: Collection[str]) -> SplitIds:
    ids = sorted(set(all_ids))
    missing = set(held_out) - set(ids)
    if missing:
        raise ValueError(f"{len(missing)} held-out ids are not in the dataset")

    return SplitIds(
        validation=tuple(i for i in ids if i not in held_out),
        test=tuple(i for i in ids if i in held_out),
    )
