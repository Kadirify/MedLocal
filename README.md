# MedLocal

A medical assistant that runs entirely on your own machine.

- **Lab report explainer** — upload a lab PDF, get out-of-range values flagged by deterministic rules and explained in plain language by a fine-tuned local model.
- **Chest X-ray report drafting** — upload an image, get a findings draft from a fine-tuned vision-language model.

No cloud calls, no patient data leaving the device.

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
