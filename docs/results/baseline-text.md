# Text baseline

Untuned base model, measured before any fine-tuning. Every later text result is compared against this table on the same split.

| | |
|---|---|
| Date | 2026-09-19 |
| Model | `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` (NF4, bf16 compute) |
| Dataset | PubMedQA `pqa_labeled`, official test split, 500 questions |
| Config | `training/configs/eval/pubmedqa-qwen3-4b-base.yaml` |
| Method | zero-shot; the label whose first token has the highest next-token logit wins |
| Hardware | RTX 5070 12 GB, 102 s including model load |

## Result

| Metric | Value |
|---|---|
| Accuracy | 0.596 |
| Macro F1 | 0.510 |
| Majority-class accuracy (always "yes") | 0.552 |

| Label | F1 | Support |
|---|---|---|
| yes | 0.754 | 276 |
| no | 0.588 | 169 |
| maybe | 0.188 | 55 |

## Confusion

| expected \ predicted | yes | no | maybe |
|---|---|---|---|
| yes | 202 | 9 | 65 |
| no | 29 | 77 | 63 |
| maybe | 29 | 7 | 19 |

The base model answers "maybe" 147 times against 55 true cases. It rarely confuses yes with no; most of the lost accuracy is hedging on questions the abstract does answer. That is the behaviour fine-tuning has to fix, and the reason macro F1 is tracked next to accuracy.
