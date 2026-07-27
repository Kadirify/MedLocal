# 2. Export text models as Q8_0 GGUF

Date: 2026-09-19

## Context

The plan called for Q4_K_M. Producing k-quants needs the `llama-quantize` binary from llama.cpp. Ollama 0.34 does not fill the gap: it refuses to quantize a GGUF on import, and for safetensors imports it only offers its own `int4`, `int8`, `nvfp4`, `mxfp4` and `mxfp8` types.

`convert_hf_to_gguf.py` is pure Python and can write `f16`, `bf16` and `q8_0` directly.

## Decision

The adapter is merged into a bf16 copy of the full-precision base on the CPU, converted to Q8_0 with the llama.cpp script from `tools/llama.cpp`, and imported into Ollama through a Modelfile that pins the ChatML template used in training.

## Consequences

- No prebuilt binaries are needed. The toolchain is one git checkout.
- A 4B model is 4.3 GB on disk and about 5 GB in VRAM, well inside 12 GB.
- Q8_0 is close to lossless: the exported model scores 0.766 on the PubMedQA test split against 0.764 for the NF4 base with the adapter, and agrees with it on 470 of 500 answers.
- Q4_K_M stays open for later. It would roughly halve the size and needs `llama-quantize`.
