from pathlib import Path

import torch
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)


def load_quantized_causal_lm(
    model_id: str, adapter_dir: Path | None = None
) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Loads a checkpoint that ships its own bitsandbytes 4-bit quantization config."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map={"": 0}, dtype=torch.bfloat16)
    if adapter_dir is not None:
        model = PeftModel.from_pretrained(model, str(adapter_dir))
    return model, tokenizer
