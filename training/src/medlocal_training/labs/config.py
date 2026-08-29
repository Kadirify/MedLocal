from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, NonNegativeFloat, PositiveInt

from medlocal_training.data.source import SplitName
from medlocal_training.labs.analyte import Language


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


class ExplanationEvaluationConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    explainer: Literal["causal-lm", "ollama"]
    model_id: str
    adapter_dir: Path | None = None
    ollama_url: str = "http://127.0.0.1:11434"
    examples_file: Path
    catalog_file: Path
    split: SplitName
    language: Language | None = None
    batch_size: PositiveInt
    max_new_tokens: PositiveInt

    @classmethod
    def read(cls, path: Path) -> "ExplanationEvaluationConfig":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
