import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from medlocal_training.data.pubmedqa import PubMedQaSource, build_official_splits
from medlocal_training.data.source import DatasetSource
from medlocal_training.data.splits import SplitIds
from medlocal_training.device import CudaUnavailableError, require_cuda
from medlocal_training.evaluation.config import EvaluationConfig
from medlocal_training.evaluation.label_logit_predictor import LabelLogitPredictor
from medlocal_training.evaluation.run import evaluate
from medlocal_training.models.loading import load_quantized_causal_lm

_RUNS_DIR = Path("runs")

_DATASETS: dict[str, Callable[[SplitIds], DatasetSource]] = {
    "pubmedqa": PubMedQaSource,
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
    print(f"validation {len(splits.validation)}  test {len(splits.test)}  -> {args.out}")
    return 0


def _evaluate(args: argparse.Namespace) -> int:
    require_cuda()
    config = EvaluationConfig.read(args.config)

    source = _DATASETS[config.dataset](SplitIds.read(config.splits_file))
    model, tokenizer = load_quantized_causal_lm(config.model_id)
    predictor = LabelLogitPredictor(model, tokenizer, config.batch_size)

    metrics, run_dir = evaluate(config, source, predictor, _RUNS_DIR)
    print(f"samples   {metrics.samples}")
    print(
        f"accuracy  {metrics.accuracy:.3f}  (majority class {metrics.majority_class_accuracy:.3f})"
    )
    print(f"macro f1  {metrics.macro_f1:.3f}")
    print(f"run       {run_dir}")
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

    args = parser.parse_args()
    handler: Callable[[argparse.Namespace], int] = args.handler
    try:
        return handler(args)
    except CudaUnavailableError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
