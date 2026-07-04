from pathlib import Path

from medlocal_training.data.report_source import ReportSource
from medlocal_training.evaluation.config import ReportEvaluationConfig
from medlocal_training.evaluation.report_generator import ReportGenerator
from medlocal_training.evaluation.report_metrics import ReportMetrics, score_reports
from medlocal_training.evaluation.run_directory import RunDirectory


def evaluate_reports(
    config: ReportEvaluationConfig,
    source: ReportSource,
    generator: ReportGenerator,
    runs_dir: Path,
) -> tuple[ReportMetrics, Path]:
    samples = source.load(config.split)
    generated = generator.generate(samples)
    metrics = score_reports([s.findings for s in samples], generated)

    run = RunDirectory(runs_dir, config.name)
    run.write_config(config)
    run.write_metrics(metrics)
    run.write_predictions(
        {"id": sample.id, "expected": sample.findings, "predicted": report}
        for sample, report in zip(samples, generated, strict=True)
    )
    return metrics, run.path
