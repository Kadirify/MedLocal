# 1. Quantize vision models on load

Date: 2026-09-19

## Context

The text baseline loads a pre-quantized `unsloth/...-bnb-4bit` checkpoint, which is a 3 GB download instead of 8 GB. The same approach failed for Qwen3-VL-4B: with transformers 5.5 and bitsandbytes 0.50 both the `bnb-4bit` and `unsloth-bnb-4bit` checkpoints raise an assertion in `fix_4bit_weight_quant_state_from_module` inside the vision deepstack merger. Those layers are built as `Linear4bit` but their weights arrive without a quant state.

MedGemma is only published in full precision, so it needs on-load quantization anyway.

## Decision

Vision-language models are loaded from the full-precision checkpoint and quantized to NF4 (double quantization, bf16 compute) at load time. The image encoder, the multimodal projector and `lm_head` are excluded and stay in bf16.

## Consequences

- Both vision models go through one loader with identical quantization, so the comparison is like for like.
- The image encoder keeps full precision. It is small next to the language model and the most sensitive to 4-bit.
- Downloads are larger (about 9 GB per model) and loading takes a little longer.
- Measured on Qwen3-VL-4B: 3.4 GB peak VRAM at batch size 4, 1.4 s per study.
