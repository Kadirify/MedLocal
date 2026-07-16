from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict


class GgufExportConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    base_model_id: str
    adapter_dir: Path
    llama_cpp_dir: Path
    output_dir: Path
    outtype: Literal["f16", "bf16", "q8_0"]

    @classmethod
    def read(cls, path: Path) -> "GgufExportConfig":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
