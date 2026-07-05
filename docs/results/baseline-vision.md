# Vision baseline

Untuned models, measured before any fine-tuning. Qwen3-VL-4B is the model that will be fine-tuned. MedGemma-4B was already trained on chest X-rays and is only a reference point: the question for Phase 4 is how much of the gap a small QLoRA run closes.

| | |
|---|---|
| Date | 2026-09-19 |
| Dataset | IU X-Ray, R2Gen test split, 590 studies (1,180 images) |
| Loading | NF4 on load, image encoder in bf16 (see `docs/decisions/0001`) |
| Prompt | one fixed system and user prompt for every study, all views of the study attached |
| Decoding | greedy, 160 new tokens at most, batch size 4 |
| Hardware | RTX 5070 12 GB |

## Result

| Model | Config | ROUGE-L | Words generated | Words in reference |
|---|---|---|---|---|
| `Qwen/Qwen3-VL-4B-Instruct` | `iu-xray-qwen3vl-4b-base.yaml` | 0.157 | 78 | 28 |
| `google/medgemma-4b-it` | `iu-xray-medgemma-4b.yaml` | 0.278 | 23 | 28 |

## Reading the numbers

Qwen3-VL writes almost three times as much as a radiologist does and describes anatomy in general prose. It also asserts findings that are not there: a rough keyword count over the 359 studies whose reference reads as normal finds an abnormality claim, most often a "slightly enlarged cardiac silhouette", in about 258 of its drafts. That count is a regex heuristic, not a metric, and is here only to show the size of the problem.

MedGemma matches the length and phrasing of real reports and defaults to a normal study, which is the majority case in this dataset.

## Limits of this measurement

ROUGE-L scores word overlap. "No pleural effusion" and "pleural effusion" overlap almost completely, and a model that always writes the same normal report scores well on a dataset where most studies are normal. It is good enough to show that style and length are off; it cannot show clinical correctness. A finding-level metric has to be in place before Phase 4 results are interpreted.
