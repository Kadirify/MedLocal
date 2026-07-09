import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from medlocal_training.data.iu_xray import IuXraySource
from medlocal_training.data.pubmedqa import PubMedQaSource, build_official_splits
from medlocal_training.data.report_source import ReportSource
from medlocal_training.data.source import DatasetSource
from medlocal_training.data.splits import SplitIds
from medlocal_training.device import CudaUnavailableError, require_cuda
from medlocal_training.evaluation.config import EvaluationConfig, ReportEvaluationConfig
from medlocal_training.evaluation.label_logit_predictor import LabelLogitPredictor
from medlocal_training.evaluation.report_run import evaluate_reports
from medlocal_training.evaluation.run import evaluate
from medlocal_training.evaluation.run_directory import RunDirectory
from medlocal_training.evaluation.vision_chat_report_generator import VisionChatReportGenerator
from medlocal_training.models.loading import load_quantized_causal_lm, load_quantized_vision_lm
from medlocal_training.trainers.config import TextTrainingConfig
from medlocal_training.trainers.text_qlora import train_text_qlora

_RUNS_DIR = Path("runs")

_DATASETS: dict[str, Callable[[SplitIds], DatasetSource]] = {
    "pubmedqa": PubMedQaSource,
}

_REPORT_DATASETS: dict[str, Callable[[], ReportSource]] = {
    "iu-xray": IuXraySource,
}


def _doctor(_: argparse.Namespace) -> int:
    gpu = require_cuda()
    major, minor = gpu.compute_capability
    print(f"gpu      {gpu.name}")
    print(f"vram     {gpu.total_vram_gb} GB")
    print(f"compute  sm_{major}{minor}")
    print(f"torch    {gpu.torch_version} (cuda {gpu.cuda_version})")
    return 0


def _pubmedqa_splits(args: argparse.Namespace) -> int:
    splits = build_official_splits()
    splits.write(args.out)
    sizes = f"train {len(splits.train)}  validation {len(splits.validation)}"
    print(f"{sizes}  test {len(splits.test)}  -> {args.out}")
    return 0


def _evaluate(args: argparse.Namespace) -> int:
    require_cuda()
    config = EvaluationConfig.read(args.config)

    source = _DATASETS[config.dataset](SplitIds.read(config.splits_file))
    model, tokenizer = load_quantized_causal_lm(config.model_id, config.adapter_dir)
    predictor = LabelLogitPredictor(model, tokenizer, config.batch_size)

    metrics, run_dir = evaluate(config, source, predictor, _RUNS_DIR)
    print(f"samples   {metrics.samples}")
    print(
        f"accuracy  {metrics.accuracy:.3f}  (majority class {metrics.majority_class_accuracy:.3f})"
    )
    print(f"macro f1  {metrics.macro_f1:.3f}")
    print(f"run       {run_dir}")
    return 0


def _train_text(args: argparse.Namespace) -> int:
    require_cuda()
    config = TextTrainingConfig.read(args.config)

    source = PubMedQaSource(
        SplitIds.read(config.splits_file), config.artificial_train_samples, config.seed
    )
    run = RunDirectory(_RUNS_DIR, config.name)
    run.write_config(config)

    summary = train_text_qlora(
        config, source.load("train"), source.load("validation"), source.labels, run.path
    )
    run.write_metrics(summary)
    print(f"steps            {summary.steps}")
    print(f"train loss       {summary.final_train_loss:.4f}")
    print(f"validation loss  {summary.best_validation_loss:.4f} (best)")
    print(f"adapter          {summary.adapter_dir}")
    return 0


def _evaluate_reports(args: argparse.Namespace) -> int:
    require_cuda()
    config = ReportEvaluationConfig.read(args.config)

    source = _REPORT_DATASETS[config.dataset]()
    model, processor = load_quantized_vision_lm(config.model_id)
    generator = VisionChatReportGenerator(
        model, processor, config.batch_size, config.max_new_tokens
    )

    metrics, run_dir = evaluate_reports(config, source, generator, _RUNS_DIR)
    print(f"samples  {metrics.samples}")
    print(f"rouge-l  {metrics.rouge_l:.3f}")
    print(f"words    {metrics.mean_generated_words:.0f} generated")
    print(f"         {metrics.mean_reference_words:.0f} reference")
    print(f"run      {run_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="medlocal")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="check that the GPU is usable for training")
    doctor.set_defaults(handler=_doctor)

    splits = commands.add_parser("pubmedqa-splits", help="write the official PubMedQA split ids")
    splits.add_argument("--out", type=Path, required=True)
    splits.set_defaults(handler=_pubmedqa_splits)

    evaluation = commands.add_parser("evaluate", help="score a model on a dataset split")
    evaluation.add_argument("config", type=Path)
    evaluation.set_defaults(handler=_evaluate)

    train_text = commands.add_parser("train-text", help="fine-tune a text model with QLoRA")
    train_text.add_argument("config", type=Path)
    train_text.set_defaults(handler=_train_text)

    reports = commands.add_parser("evaluate-reports", help="score generated X-ray findings")
    reports.add_argument("config", type=Path)
    reports.set_defaults(handler=_evaluate_reports)

    args = parser.parse_args()
    handler: Callable[[argparse.Namespace], int] = args.handler
    try:
        return handler(args)
    except CudaUnavailableError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
