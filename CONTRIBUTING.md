# Contributing

Development notes for MedLocal.

## Layout

```
training/   Python. Data prep, QLoRA fine-tuning, evaluation, GGUF export.
apps/api/   NestJS. Domain logic, PDF parsing, Ollama access.
apps/web/   Next.js. Upload and result UI.
models/     Ollama Modelfiles. Weights are never committed.
reference/  Analyte catalog: reference ranges, critical limits, vetted background text.
data/       Local datasets, gitignored.
docs/       PLAN.md (roadmap), ARCHITECTURE.md, decisions/ (ADRs).
```

`training/` and `apps/` only meet at the Ollama HTTP API, the GGUF files in `models/` and the data in `reference/`. Neither imports from the other.

## Commands

Python (run inside `training/`):

```
uv sync
uv run medlocal doctor
uv run medlocal build-lab-dataset configs/data/lab-explanations.yaml
uv run medlocal train-text configs/train/<name>.yaml
uv run medlocal evaluate configs/eval/pubmedqa-<name>.yaml
uv run medlocal export-gguf configs/export/<name>.yaml
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

`export-gguf` needs a llama.cpp checkout in `tools/llama.cpp` (gitignored). Import the result with `ollama create <name>:q8_0 -f Modelfile` from the model's folder under `models/`.

Node (run at the repo root, pnpm 10):

```
pnpm install
pnpm --filter api dev          # http://127.0.0.1:3001, reads apps/api/.env
pnpm --filter web dev          # http://localhost:3000
pnpm --filter api test
pnpm -r lint
pnpm -r typecheck
pnpm --filter api sample-pdf   # rewrites apps/web/public/sample-lab-report.pdf
```

Nest 12 is ESM-only: relative imports end in `.js`, tests run on Vitest with the SWC plugin.

`reference/explainer-prompt.json` is the contract between training and the API. Change the prompt in `training/src/medlocal_training/labs/prompt.py`, regenerate the file, and retrain; both test suites fail until the three agree.

## Conventions

- Follow `docs/PLAN.md` phase by phase. Finish and verify a phase before opening the next one.
- Measure before and after. A training run without a baseline number on the same test split is not done.
- Record non-obvious technical choices as a short ADR in `docs/decisions/`.
- Coding guidelines are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Hardware budget

RTX 5070 12 GB, 32 GB RAM, Windows 11. Anything that does not fit in 12 GB VRAM with QLoRA is out of scope. Prefer 4B models, 8B at most. The 14B teacher only runs for inference through Ollama.
