from pathlib import Path

from medlocal_training.data.source import DatasetSource
from medlocal_training.evaluation.config import EvaluationConfig
from medlocal_training.evaluation.metrics import ClassificationMetrics, score
from medlocal_training.evaluation.predictor import AnswerPredictor
from medlocal_training.evaluation.run_directory import RunDirectory


def evaluate(
    config: EvaluationConfig, source: DatasetSource, predictor: AnswerPredictor, runs_dir: Path
) -> tuple[ClassificationMetrics, Path]:
    samples = source.load(config.split)
    predicted = predictor.predict(samples, source.labels)
    metrics = score([s.answer for s in samples], predicted, source.labels)

    run = RunDirectory(runs_dir, config.name)
    run.write_config(config)
    run.write_metrics(metrics)
    run.write_predictions(
        {"id": sample.id, "expected": sample.answer, "predicted": answer}
        for sample, answer in zip(samples, predicted, strict=True)
    )
    return metrics, run.path
