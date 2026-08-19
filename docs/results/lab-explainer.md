# Lab explainer

| | |
|---|---|
| Date | 2026-09-19 |
| Student | `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` + QLoRA (rank 16, alpha 16, all attention and MLP projections) |
| Teacher | `qwen3:14b` through Ollama, given vetted background text from `reference/analytes.yaml` |
| Dataset | `data/synthetic/lab-explanations.jsonl`: 976 train, 99 validation, 149 test, all synthetic |
| Training | 183 steps (3 epochs), lr 1e-4 cosine, batch 2 x 8 accumulation, bf16, about 20 minutes on an RTX 5070 12 GB |
| Decoding | greedy, 400 new tokens at most |
| Prompt | `reference/explainer-prompt.json`, version 1. The student never sees the teacher's background text. |

## Test split, 149 reports

"Passed every check" is the share of explanations that satisfy all rules in `labs/explanation_checks.py`. ROUGE-L is measured against the teacher's explanation of the same report and only shows how close the wording is; it says nothing about correctness.

| Model | Passed every check | ROUGE-L to teacher | Mean words |
|---|---|---|---|
| Qwen3-4B, untuned | 0.779 | 0.337 | 105 |
| Qwen3-4B + QLoRA (NF4 base + adapter) | **0.940** | 0.643 | 106 |
| Same model as Q8_0 GGUF in Ollama (`medlocal-lab:q8_0`) | **0.946** | 0.603 | 108 |

Share of explanations failing each rule:

| Rule | Untuned | Fine-tuned | In Ollama |
|---|---|---|---|
| states or implies a diagnosis | 0.168 | 0.020 | 0.020 |
| leaves out a flagged result | 0.027 | 0.020 | 0.000 |
| wrong or missing direction | 0.020 | 0.000 | 0.007 |
| length outside 50 to 280 words | 0.013 | 0.020 | 0.027 |
| no referral to a doctor | 0.007 | 0.000 | 0.000 |

The untuned model's main problem was phrasing findings as a diagnosis ("this means you have..."), one report in six. Fine-tuning brings that to one in fifty. Validation loss fell steadily from 0.764 to 0.295 with no sign of overfitting inside three epochs.

## What this does and does not show

- The numbers measure rule compliance on synthetic reports. They do not measure medical accuracy, and nothing here has been reviewed by a clinician.
- The rules are pattern based. They miss paraphrased diagnoses and would accept a fluent explanation that is wrong in a way no rule covers.
- The teacher failed the checks five times in a row on 26 of 1,250 planned reports, mostly ones with many flagged results, so the hardest cases are under-represented in training and test alike.
- The teacher's own pass rate on the test split is 1.0 by construction: only accepted explanations were kept.

## Bugs found while building the dataset

- A search term matched inside other words: "ast" in "fasting" and "waste". Correct explanations of AST were rejected for stating the wrong direction. Names are now matched as whole words.
- "blood sugar" was listed as a way to mention fasting glucose and matched the HbA1c sentence instead.
- The teacher copied the upper-case flag from its background notes ("a HIGH result"). Notes are lower-case now, and a rule rejects flag tokens in the output.
- Once, the teacher called a high calcium normal. The direction rule caught it.

## Next

- Read a sample of fine-tuned outputs by hand, in particular the nine that fail a rule.
- Hard cases as a separate table: all normal, a single borderline value, five or more flags.
- Turkish explanations.
