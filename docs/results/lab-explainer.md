# Lab explainer

| | |
|---|---|
| Date | 2026-09-20 |
| Student | `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` + QLoRA (rank 16, alpha 16, all attention and MLP projections) |
| Teacher | `qwen3:14b` through Ollama |
| Catalog | `reference/analytes.yaml`: 58 analytes, 15 panels, English and Turkish |
| Dataset | `data/synthetic/lab-explanations.jsonl`: 2,113 train, 181 validation, 262 test, half Turkish, all synthetic |
| Training | 393 steps (3 epochs), lr 1e-4 cosine, batch 1 x 16 accumulation, bf16, about 80 minutes on an RTX 5070 12 GB; 28 examples longer than 1,792 tokens were left out rather than truncated |
| Decoding | greedy, 700 new tokens at most |
| Prompt | `reference/explainer-prompt.json`, version 3 |

## Test split, 262 reports

"Passed every rule" is the share of explanations that satisfy all eleven rules in `labs/explanation_checks.py`.

| Model | Prompt | English (122) | Turkish (140) |
|---|---|---|---|
| Qwen3-4B, untuned | results only | 41.0% | 17.1% |
| Qwen3-4B, untuned | results + catalog background | 63.9% | 20.0% |
| v2: fine-tuned | results only | 89.3% | 95.0% |
| **v3: fine-tuned** | **results + catalog background** | **89.3%** | **92.1%** |

Most common failures:

| Rule | Untuned EN | v3 EN | Untuned TR | v3 TR |
|---|---|---|---|---|
| passes a verdict on the patient's health | 15.6% | 0.0% | 70.0% | 1.4% |
| names a condition the catalog does not | 3.3% | 0.0% | 15.7% | 0.0% |
| states or implies a diagnosis | 10.7% | 1.6% | 0.0% | 0.0% |
| wrong or missing direction | 12.3% | 3.3% | 5.7% | 2.9% |
| leaves out a flagged result | 2.5% | 3.3% | 5.7% | 1.4% |

(Untuned columns are for the prompt with background.)

The untuned model's Turkish problem is behaviour, not knowledge: giving it the background barely helps (17% to 20%), because seven answers in ten tell the patient they are healthy. Fine-tuning removes that. The difference between v2 and v3 on Turkish is four reports out of 140 and is within noise.

## Why v3 exists: the rules do not measure correctness

v2 scored 95% on Turkish. Run on a real report, it then wrote that a low PDW "is usually a sign of a problem". The catalog says the opposite: with a normal platelet count it is usually not significant. None of the eleven rules can catch that, because they check how a thing is said, not whether it is true.

The cause was a design choice. Only the teacher was given the catalog's background; the student was expected to have absorbed it. A 4B model does not reliably recall the details of 58 analytes. From v3 on, the background for every flagged result is part of the student's prompt at training and at inference, and the API renders it from the same catalog. The model restates vetted text instead of recalling it.

On the same real report v3 writes "tek başına genellikle önemli değildir" and, in English, "usually not significant on its own".

Rule scores did not move between v2 and v3, which is the point: the improvement is of a kind these numbers cannot show. It was found by reading output, not by a metric.

## What this does and does not show

- The percentages measure rule compliance on synthetic reports. They do not measure medical accuracy, and nothing here has been reviewed by a clinician.
- Grounding limits what the model can get wrong to how it restates the background. It can still restate it badly, and it has no vetted text for combinations of results.
- The teacher's Turkish has occasional spelling and suffix errors ("kolesterolin"), and the student inherits some of them. Real output also shows loose phrasing, such as announcing two notable values and listing three.
- The teacher failed the rules five times in a row on 344 of 2,900 planned reports. 239 of those were reports with nothing flagged, where it kept reassuring the patient. All-normal reports are therefore under-represented (308 in the dataset).
- The rules are patterns. They miss paraphrases, and some reject acceptable sentences.

## Found by reading generated text

Each of these passed the rules that existed at the time:

- "ast" matched inside "fasting" and "waste"; "ALT" would have matched the Turkish "altında". Names are matched as whole words, acronyms case-sensitively.
- A sentence such as "low phosphorus can be linked to low vitamin D" counted as calling vitamin D low. A direction word now only describes an analyte when it follows its name.
- The teacher named hyperthyroidism for a low TSH. Conditions may only be named when the catalog names them for that result.
- An all-normal report got three paragraphs saying the patient was healthy and free of inflammation. 272 of the first 1,585 examples had some form of this and were removed; answers to all-normal reports are capped at 90 words.
- Training text built with the chat template put an empty think block before the answer (see `finetuned-text.md`).

## Reading real reports

Tried with one real report from a Turkish hospital laboratory: 38 printed rows, 30 recognised, 7 listed as unrecognised (platelet and immature-cell indices that are not in the catalog), 1 set aside because its printed range is on a different scale from the catalog's. The alkaline phosphatase row printed no range, so the catalog's adult range was used and the interface says so.

## Next

- Read a larger sample of v3 output by hand, Turkish first.
- A better Turkish teacher, or a Turkish proofreading pass over the dataset.
- More all-normal and borderline reports.
- Review of the catalog text by someone medically qualified.
