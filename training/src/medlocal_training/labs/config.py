from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, NonNegativeFloat, PositiveInt

from medlocal_training.data.source import SplitName


class LabDatasetConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    catalog_file: Path
    output_file: Path
    seed: int
    teacher_model: str
    teacher_url: str
    temperature: NonNegativeFloat
    max_attempts: PositiveInt
    sizes: dict[SplitName, PositiveInt]

    @classmethod
    def read(cls, path: Path) -> "LabDatasetConfig":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
