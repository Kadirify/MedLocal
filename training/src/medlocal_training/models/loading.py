from pathlib import Path

import torch
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoProcessor,
    AutoTokenizer,
    BitsAndBytesConfig,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    ProcessorMixin,
)

# Pre-quantized Qwen3-VL checkpoints fail in bitsandbytes 0.50 with transformers 5.5: the
# vision merger layers load as Linear4bit without a quant state. Image encoders are also the
# part that loses most from 4-bit, so they stay in bf16 under every naming used by our models.
_UNQUANTIZED_MODULES = ["visual", "vision_tower", "multi_modal_projector", "lm_head"]


def load_quantized_causal_lm(
    model_id: str, adapter_dir: Path | None = None
) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Loads a checkpoint that ships its own bitsandbytes 4-bit quantization config."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map={"": 0}, dtype=torch.bfloat16)
    if adapter_dir is not None:
        model = PeftModel.from_pretrained(model, str(adapter_dir))
    return model, tokenizer


def load_quantized_vision_lm(model_id: str) -> tuple[PreTrainedModel, ProcessorMixin]:
    """Quantizes the language model to NF4 on load and keeps the image encoder in bf16."""
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        llm_int8_skip_modules=_UNQUANTIZED_MODULES,
    )
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForImageTextToText.from_pretrained(
        model_id, device_map={"": 0}, dtype=torch.bfloat16, quantization_config=quantization
    )
    return model, processor
