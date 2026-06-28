import json
from collections.abc import Sequence
from dataclasses import asdict
from datetime import date
from pathlib import Path

import yaml

from medlocal_training.data.sample import QaSample
from medlocal_training.data.source import DatasetSource
from medlocal_training.evaluation.config import EvaluationConfig
from medlocal_training.evaluation.metrics import ClassificationMetrics, score
from medlocal_training.evaluation.predictor import AnswerPredictor


def evaluate(
    config: EvaluationConfig, source: DatasetSource, predictor: AnswerPredictor, runs_dir: Path
) -> tuple[ClassificationMetrics, Path]:
    samples = source.load(config.split)
    predicted = predictor.predict(samples, source.labels)
    metrics = score([s.answer for s in samples], predicted, source.labels)

    run_dir = runs_dir / f"{date.today().isoformat()}-{config.name}"
    _write_run(run_dir, config, metrics, samples, predicted)
    return metrics, run_dir


def _write_run(
    run_dir: Path,
    config: EvaluationConfig,
    metrics: ClassificationMetrics,
    samples: Sequence[QaSample],
    predicted: Sequence[str],
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    config_text = yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False)
    (run_dir / "config.yaml").write_text(config_text, encoding="utf-8")

    metrics_text = json.dumps(asdict(metrics), indent=2) + "\n"
    (run_dir / "metrics.json").write_text(metrics_text, encoding="utf-8")

    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as file:
        for sample, answer in zip(samples, predicted, strict=True):
            row = {"id": sample.id, "expected": sample.answer, "predicted": answer}
            file.write(json.dumps(row) + "\n")
