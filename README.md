# MedLocal

A lab report explainer that runs entirely on your own machine.

Upload a lab PDF and get out-of-range values flagged by deterministic rules, then explained in plain language by a small fine-tuned model. No cloud calls, no patient data leaving the device.

> MedLocal is a research and learning project. It is not a medical device and does not provide diagnosis or treatment advice.

## Status

Early setup. See [docs/PLAN.md](docs/PLAN.md) for the roadmap and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design.

## Stack

| Part | Tech |
|---|---|
| Fine-tuning | Python, PyTorch, Unsloth, QLoRA |
| Serving | Ollama (GGUF) |
| API | NestJS |
| Web | Next.js |

## Licence

TBD
