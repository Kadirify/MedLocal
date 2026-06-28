# Datasets

Everything under `data/` is gitignored except this file and `splits/`. Datasets are downloaded on demand into the Hugging Face cache.

| Dataset | Source | Licence | Access | Used for |
|---|---|---|---|---|
| PubMedQA | [qiaojin/PubMedQA](https://huggingface.co/datasets/qiaojin/PubMedQA), [pubmedqa/pubmedqa](https://github.com/pubmedqa/pubmedqa) | MIT | open | text model training and evaluation |

## Splits

`splits/pubmedqa.json` holds the PubMedQA ids used for validation and test. The test ids are the 500 from the official `test_ground_truth.json`, so numbers are comparable with published results. The other 500 expert-labelled questions are the validation split. Training uses the separate machine-labelled `pqa_artificial` subset.

Regenerate with `uv run medlocal pubmedqa-splits --out ../data/splits/pubmedqa.json` from `training/`.
