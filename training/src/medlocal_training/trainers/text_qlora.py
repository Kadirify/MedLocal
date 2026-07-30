import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from datasets import Dataset

from medlocal_training.data.chat_format import render_training_text
from medlocal_training.data.training_example import TrainingExample
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
    train: Sequence[TrainingExample],
    validation: Sequence[TrainingExample],
    run_dir: Path,
) -> TrainingSummary:
    # unsloth patches transformers and trl when imported: it stays out of the evaluation
    # path and has to come before trl
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only

    # isort: split
    from transformers import EarlyStoppingCallback
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

    def as_text(examples: Sequence[TrainingExample]) -> Dataset:
        texts = [render_training_text(tokenizer, e.prompt, e.answer) for e in examples]
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
            save_strategy="steps",
            save_steps=config.eval_steps,
            save_total_limit=1,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            seed=config.seed,
            report_to="none",
        ),
        callbacks=[EarlyStoppingCallback(config.early_stopping_patience)],
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
