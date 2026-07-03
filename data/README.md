# Datasets

Everything under `data/` is gitignored except this file and `splits/`. Datasets are downloaded on demand into the Hugging Face cache.

| Dataset | Source | Licence | Access | Used for |
|---|---|---|---|---|
| PubMedQA | [qiaojin/PubMedQA](https://huggingface.co/datasets/qiaojin/PubMedQA), [pubmedqa/pubmedqa](https://github.com/pubmedqa/pubmedqa) | MIT | open | text model training and evaluation |
| IU X-Ray (Open-i) | [Open-i, NLM](https://openi.nlm.nih.gov/), via the [CAIR-M3LLM/IU-Xray](https://huggingface.co/datasets/CAIR-M3LLM/IU-Xray) mirror | CC BY-NC-ND 4.0 | open | vision model training and evaluation |

IU X-Ray is non-commercial and no-derivatives. The images and reports are never redistributed from this repo. Whether fine-tuned weights may be published is decided before Phase 5, not assumed.

## Splits

`splits/pubmedqa.json` holds the PubMedQA ids used for validation and test. The test ids are the 500 from the official `test_ground_truth.json`, so numbers are comparable with published results. The other 500 expert-labelled questions are the validation split. Training uses the separate machine-labelled `pqa_artificial` subset.

Regenerate with `uv run medlocal pubmedqa-splits --out ../data/splits/pubmedqa.json` from `training/`.

IU X-Ray uses the split shipped with the mirror (2,069 / 296 / 590 studies), which is the R2Gen split used across the report-generation literature. The mirror's per-study user prompts hint at the findings, so only the images and the reference findings are read.
