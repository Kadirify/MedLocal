import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)


def load_quantized_causal_lm(model_id: str) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Loads a checkpoint that ships its own bitsandbytes 4-bit quantization config."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map={"": 0}, dtype=torch.bfloat16)
    return model, tokenizer
