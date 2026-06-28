from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, PositiveInt

from medlocal_training.data.source import SplitName


class EvaluationConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    model_id: str
    dataset: Literal["pubmedqa"]
    splits_file: Path
    split: SplitName
    batch_size: PositiveInt

    @classmethod
    def read(cls, path: Path) -> "EvaluationConfig":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
