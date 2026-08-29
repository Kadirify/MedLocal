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
from medlocal_training.evaluation.ollama_answer_predictor import OllamaAnswerPredictor
from medlocal_training.evaluation.predictor import AnswerPredictor
from medlocal_training.evaluation.run import evaluate
from medlocal_training.evaluation.run_directory import RunDirectory
from medlocal_training.export.config import GgufExportConfig
from medlocal_training.export.gguf import LlamaCppNotFoundError, convert_to_gguf
from medlocal_training.export.merge import merge_adapter
from medlocal_training.labs.analyte import AnalyteCatalog
from medlocal_training.labs.config import ExplanationEvaluationConfig, LabDatasetConfig
from medlocal_training.labs.contract import write_prompt_contract
from medlocal_training.labs.dataset import build_examples, read_examples
from medlocal_training.labs.evaluation import score_explanations
from medlocal_training.labs.explainer import CausalLmExplainer, Explainer, OllamaExplainer
from medlocal_training.labs.explanation_writer import OllamaExplanationWriter
from medlocal_training.labs.synthetic import SyntheticReportGenerator
from medlocal_training.models.loading import load_quantized_causal_lm
from medlocal_training.trainers.config import TextTrainingConfig
from medlocal_training.trainers.text_qlora import train_text_qlora
from medlocal_training.trainers.training_sets import load_training_examples

_RUNS_DIR = Path("runs")
_OLLAMA_TIMEOUT_SECONDS = 120.0

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
    sizes = f"train {len(splits.train)}  validation {len(splits.validation)}"
    print(f"{sizes}  test {len(splits.test)}  -> {args.out}")
    return 0


def _label_logit_predictor(config: EvaluationConfig) -> AnswerPredictor:
    require_cuda()
    model, tokenizer = load_quantized_causal_lm(config.model_id, config.adapter_dir)
    return LabelLogitPredictor(model, tokenizer, config.batch_size)


def _ollama_predictor(config: EvaluationConfig) -> AnswerPredictor:
    return OllamaAnswerPredictor(config.ollama_url, config.model_id, _OLLAMA_TIMEOUT_SECONDS)


_PREDICTORS: dict[str, Callable[[EvaluationConfig], AnswerPredictor]] = {
    "label-logits": _label_logit_predictor,
    "ollama": _ollama_predictor,
}


def _evaluate(args: argparse.Namespace) -> int:
    config = EvaluationConfig.read(args.config)

    source = _DATASETS[config.dataset](SplitIds.read(config.splits_file))
    predictor = _PREDICTORS[config.predictor](config)

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

    train = load_training_examples(config.data, "train", config.seed)
    validation = load_training_examples(config.data, "validation", config.seed)

    run = RunDirectory(_RUNS_DIR, config.name)
    run.write_config(config)
    summary = train_text_qlora(config, train, validation, run.path)
    run.write_metrics(summary)
    print(f"steps            {summary.steps}")
    print(f"train loss       {summary.final_train_loss:.4f}")
    print(f"validation loss  {summary.best_validation_loss:.4f} (best)")
    print(f"adapter          {summary.adapter_dir}")
    return 0


def _build_lab_dataset(args: argparse.Namespace) -> int:
    config = LabDatasetConfig.read(args.config)
    generator = SyntheticReportGenerator(AnalyteCatalog.read(config.catalog_file), config.seed)
    writer = OllamaExplanationWriter(
        config.teacher_url, config.teacher_model, config.temperature, _OLLAMA_TIMEOUT_SECONDS
    )

    summary = build_examples(
        generator, writer, config.sizes, config.max_attempts, config.output_file
    )
    print(f"written   {summary.written} (already present {summary.already_present})")
    print(f"gave up   {summary.gave_up}")
    print(f"rejected  {summary.rejected_attempts}")
    return 0


def _write_prompt_contract(args: argparse.Namespace) -> int:
    write_prompt_contract(AnalyteCatalog.read(args.catalog), args.out)
    print(f"prompt contract -> {args.out}")
    return 0


def _causal_lm_explainer(config: ExplanationEvaluationConfig) -> Explainer:
    require_cuda()
    model, tokenizer = load_quantized_causal_lm(config.model_id, config.adapter_dir)
    return CausalLmExplainer(model, tokenizer, config.batch_size, config.max_new_tokens)


def _ollama_explainer(config: ExplanationEvaluationConfig) -> Explainer:
    return OllamaExplainer(
        config.ollama_url, config.model_id, config.max_new_tokens, _OLLAMA_TIMEOUT_SECONDS
    )


_EXPLAINERS: dict[str, Callable[[ExplanationEvaluationConfig], Explainer]] = {
    "causal-lm": _causal_lm_explainer,
    "ollama": _ollama_explainer,
}


def _evaluate_explanations(args: argparse.Namespace) -> int:
    config = ExplanationEvaluationConfig.read(args.config)
    catalog = AnalyteCatalog.read(config.catalog_file)
    examples = [
        example
        for example in read_examples(config.examples_file)
        if example.split == config.split and config.language in (None, example.language)
    ]
    reports = [(example.to_report(catalog), example.language) for example in examples]

    generated = _EXPLAINERS[config.explainer](config).explain(reports)
    metrics = score_explanations(reports, [e.explanation for e in examples], generated)

    run = RunDirectory(_RUNS_DIR, config.name)
    run.write_config(config)
    run.write_metrics(metrics)
    run.write_predictions(
        {"id": example.id, "expected": example.explanation, "predicted": text}
        for example, text in zip(examples, generated, strict=True)
    )
    print(f"samples             {metrics.samples}")
    print(f"passed every check  {metrics.passed_every_check:.3f}")
    print(f"failures            {metrics.failure_rate_per_check}")
    print(f"rouge-l to teacher  {metrics.rouge_l_to_teacher:.3f}")
    print(f"mean words          {metrics.mean_words:.0f}")
    print(f"run                 {run.path}")
    return 0


def _export_gguf(args: argparse.Namespace) -> int:
    config = GgufExportConfig.read(args.config)
    merged_dir = config.output_dir / "merged"
    gguf_file = config.output_dir / f"{config.name}-{config.outtype}.gguf"

    merge_adapter(config.base_model_id, config.adapter_dir, merged_dir)
    convert_to_gguf(merged_dir, config.llama_cpp_dir, gguf_file, config.outtype)
    print(f"gguf  {gguf_file}")
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

    lab_dataset = commands.add_parser(
        "build-lab-dataset", help="write synthetic lab reports with teacher explanations"
    )
    lab_dataset.add_argument("config", type=Path)
    lab_dataset.set_defaults(handler=_build_lab_dataset)

    contract = commands.add_parser(
        "write-prompt-contract", help="write the explainer prompt shared with the API"
    )
    contract.add_argument("--catalog", type=Path, required=True)
    contract.add_argument("--out", type=Path, required=True)
    contract.set_defaults(handler=_write_prompt_contract)

    explanations = commands.add_parser(
        "evaluate-explanations", help="score generated lab explanations"
    )
    explanations.add_argument("config", type=Path)
    explanations.set_defaults(handler=_evaluate_explanations)

    export = commands.add_parser("export-gguf", help="merge an adapter and convert it to GGUF")
    export.add_argument("config", type=Path)
    export.set_defaults(handler=_export_gguf)

    args = parser.parse_args()
    handler: Callable[[argparse.Namespace], int] = args.handler
    try:
        return handler(args)
    except (CudaUnavailableError, LlamaCppNotFoundError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
