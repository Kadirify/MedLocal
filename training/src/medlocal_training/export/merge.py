from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def merge_adapter(base_model_id: str, adapter_dir: Path, output_dir: Path) -> None:
    """Folds LoRA weights into a full-precision copy of the base model.

    The base is loaded unquantized on the CPU: merging into NF4 weights would bake the
    quantization error into the exported model.
    """
    base = AutoModelForCausalLM.from_pretrained(base_model_id, dtype=torch.bfloat16)
    merged = PeftModel.from_pretrained(base, str(adapter_dir)).merge_and_unload()

    output_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(output_dir), safe_serialization=True)
    AutoTokenizer.from_pretrained(base_model_id).save_pretrained(str(output_dir))
