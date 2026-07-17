# Text model after QLoRA

| | |
|---|---|
| Date | 2026-09-19 |
| Base | `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` |
| Method | QLoRA, rank 16, alpha 16, all attention and MLP projections, loss on the answer tokens only |
| Optimisation | AdamW 8-bit, lr 1e-4 cosine, 10 warmup steps, batch 2 x 8 accumulation, bf16 |
| Dataset | PubMedQA: 350 expert-labelled questions plus an equal-share yes/no sample of `pqa_artificial` |
| Selection | validation split (150 expert-labelled questions), by macro F1 |
| Test | official PubMedQA test split, 500 questions, evaluated once for the selected run |
| Hardware | RTX 5070 12 GB, about 6 GB VRAM, 13 to 22 minutes per run |

## Validation

| Run | Artificial samples | Epochs | Accuracy | Macro F1 | F1 yes | F1 no | F1 maybe |
|---|---|---|---|---|---|---|---|
| base | - | - | 0.613 | 0.532 | 0.808 | 0.553 | 0.235 |
| `r16` | 1500 | 2 | 0.773 | 0.549 | 0.819 | 0.828 | 0.000 |
| `r16-mix400` | 400 | 3 | **0.787** | **0.618** | 0.829 | 0.835 | 0.190 |

`r16` stopped answering "maybe" altogether: 38 of its 1,850 training samples carried that label. Cutting the artificial share brought the label back and improved both metrics, so `r16-mix400` was selected. Its validation loss bottoms out at step 80 of 141 (0.321) and drifts up to 0.352 afterwards, so the third epoch is already mild overfitting.

## Test

| Model | Accuracy | Macro F1 | F1 yes | F1 no | F1 maybe |
|---|---|---|---|---|---|
| base | 0.596 | 0.510 | 0.754 | 0.588 | 0.188 |
| `r16-mix400` | **0.764** | **0.542** | 0.841 | 0.787 | 0.000 |
| always "yes" | 0.552 | 0.237 | | | |

| expected \ predicted | yes | no | maybe |
|---|---|---|---|
| yes | 240 | 29 | 7 |
| no | 21 | 142 | 6 |
| maybe | 34 | 21 | 0 |

Accuracy rises by 16.8 points. The base model's main failure, hedging with "maybe" on questions the abstract answers (147 times), is gone, and "no" improves the most.

"Maybe" is not solved. The model uses the label 13 times on the test split and is wrong every time, so macro F1 moves far less than accuracy. With roughly 38 training examples of that label this is a data problem before it is a modelling one.

## Exported model

The selected adapter was merged, converted to Q8_0 GGUF and served by Ollama as `medlocal-pubmedqa:q8_0` (see `docs/decisions/0002`). Scored through the Ollama HTTP API by generating the answer, on the same test split:

| Served as | Accuracy | Macro F1 |
|---|---|---|
| NF4 base + adapter, label logits | 0.764 | 0.542 |
| Q8_0 GGUF in Ollama, generated answer | 0.766 | 0.551 |

The two agree on 470 of 500 answers, and every generated answer was one of the three labels. Merging, conversion and the Modelfile template did not change the model's behaviour.

## A failed first run

The first training run scored 0.120 on validation and answered "maybe" for every question. The Qwen3 chat template puts an empty `<think></think>` block in front of an assistant message, while the generation prompt used at inference has none, so the model had learned a prefix it never saw again. The tell was a starting loss of 9.6 instead of about 1.0. Training text is now built as the exact inference prompt followed by the answer, and a unit test pins that.

## Next

- Oversample or augment "maybe" and select on macro F1 again.
- Stop at the validation-loss minimum instead of a fixed epoch count.
