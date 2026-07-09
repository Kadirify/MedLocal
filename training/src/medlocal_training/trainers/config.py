from pathlib import Path
from typing import Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
)


class LoraSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rank: PositiveInt
    alpha: PositiveInt
    dropout: NonNegativeFloat


class TextTrainingConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    base_model_id: str
    dataset: Literal["pubmedqa"]
    splits_file: Path
    artificial_train_samples: NonNegativeInt
    seed: int
    max_seq_length: PositiveInt
    lora: LoraSettings
    learning_rate: PositiveFloat
    epochs: PositiveFloat
    batch_size: PositiveInt
    gradient_accumulation_steps: PositiveInt
    warmup_steps: NonNegativeInt
    logging_steps: PositiveInt
    eval_steps: PositiveInt

    @classmethod
    def read(cls, path: Path) -> "TextTrainingConfig":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
