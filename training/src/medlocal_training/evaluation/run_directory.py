import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


class RunDirectory:
    def __init__(self, runs_dir: Path, name: str) -> None:
        self.path = runs_dir / f"{date.today().isoformat()}-{name}"
        self.path.mkdir(parents=True, exist_ok=True)

    def write_config(self, config: BaseModel) -> None:
        text = yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False)
        (self.path / "config.yaml").write_text(text, encoding="utf-8")

    def write_metrics(self, metrics: "DataclassInstance") -> None:
        text = json.dumps(asdict(metrics), indent=2) + "\n"
        (self.path / "metrics.json").write_text(text, encoding="utf-8")

    def write_predictions(self, rows: Iterable[Mapping[str, Any]]) -> None:
        with (self.path / "predictions.jsonl").open("w", encoding="utf-8") as file:
            for row in rows:
                file.write(json.dumps(row) + "\n")
