import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from datasets import Dataset

from medlocal_training.data.chat_format import render_training_text
from medlocal_training.data.sample import QaSample
from medlocal_training.trainers.config import TextTrainingConfig

_LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

# ChatML turn markers used by Qwen; loss is only computed after the assistant marker
_USER_TURN = "<|im_start|>user\n"
_ASSISTANT_TURN = "<|im_start|>assistant\n"


@dataclass(frozen=True)
class TrainingSummary:
    adapter_dir: Path
    steps: int
    final_train_loss: float
    best_validation_loss: float


def train_text_qlora(
    config: TextTrainingConfig,
    train: Sequence[QaSample],
    validation: Sequence[QaSample],
    labels: Sequence[str],
    run_dir: Path,
) -> TrainingSummary:
    # unsloth patches transformers and trl when imported: it stays out of the evaluation
    # path and has to come before trl
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only

    # isort: split
    from trl import SFTConfig, SFTTrainer

    model, tokenizer = FastLanguageModel.from_pretrained(
        config.base_model_id, max_seq_length=config.max_seq_length, load_in_4bit=True
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=config.lora.rank,
        lora_alpha=config.lora.alpha,
        lora_dropout=config.lora.dropout,
        target_modules=_LORA_TARGETS,
        use_gradient_checkpointing="unsloth",
        random_state=config.seed,
    )

    def as_text(samples: Sequence[QaSample]) -> Dataset:
        texts = [render_training_text(tokenizer, sample, labels) for sample in samples]
        return Dataset.from_dict({"text": texts})

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=as_text(train),
        eval_dataset=as_text(validation),
        args=SFTConfig(
            output_dir=str(run_dir / "checkpoints"),
            dataset_text_field="text",
            eos_token=tokenizer.eos_token,
            max_length=config.max_seq_length,
            # worker processes cannot be forked on Windows
            dataset_num_proc=1,
            per_device_train_batch_size=config.batch_size,
            per_device_eval_batch_size=config.batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            learning_rate=config.learning_rate,
            num_train_epochs=config.epochs,
            warmup_steps=config.warmup_steps,
            lr_scheduler_type="cosine",
            optim="adamw_8bit",
            bf16=True,
            logging_steps=config.logging_steps,
            eval_strategy="steps",
            eval_steps=config.eval_steps,
            save_strategy="no",
            seed=config.seed,
            report_to="none",
        ),
    )
    trainer = train_on_responses_only(
        trainer, instruction_part=_USER_TURN, response_part=_ASSISTANT_TURN
    )
    result = trainer.train()

    adapter_dir = run_dir / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    history = trainer.state.log_history
    (run_dir / "log_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")

    return TrainingSummary(
        adapter_dir=adapter_dir,
        steps=result.global_step,
        final_train_loss=result.training_loss,
        best_validation_loss=min(e["eval_loss"] for e in history if "eval_loss" in e),
    )
