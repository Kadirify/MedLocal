# MedLocal Yol Haritası

Her faz bir branch'te yapılır, doğrulanır, sonra bir sonrakine geçilir. "Çıktı" sütunundaki şey yoksa faz bitmemiştir.

Durum: `[ ]` başlamadı · `[~]` sürüyor · `[x]` bitti

## Faz 0 — Ortam `[~]`

| İş | Çıktı |
|---|---|
| uv + Python 3.12, `training/pyproject.toml` | `uv sync` temiz çalışır |
| PyTorch (CUDA 12.8), Unsloth, transformers, peft, trl, datasets | `torch.cuda.is_available()` → True, GPU adı RTX 5070 |
| Ollama kurulumu | `ollama run` ile küçük bir model cevap verir |
| pnpm workspace iskeleti | `pnpm install` temiz çalışır |
| ruff, mypy, pytest, eslint, prettier ayarları | lint komutları boş repoda geçer |

Öğrenilecekler: sanal ortam mantığı, CUDA/PyTorch sürüm eşleşmesi, VRAM'i ne doldurur.

## Faz 1 — Baseline `[ ]`

| İş | Çıktı |
|---|---|
| PubMedQA test split'ini sabitle | `data/splits/pubmedqa.json` (id listesi) |
| Ham Qwen3-4B'yi test setinde ölç | `docs/results/baseline-text.md` |
| IU X-Ray test split'ini sabitle | `data/splits/iu-xray.json` |
| Ham Qwen3-VL-4B ve MedGemma-4B'yi ölç | `docs/results/baseline-vision.md` |

Öğrenilecekler: neden önce ölçüyoruz, train/val/test ayrımı, veri sızıntısı, accuracy / ROUGE / F1 ne anlatır ne anlatmaz.

## Faz 2 — Veri `[ ]`

| İş | Çıktı |
|---|---|
| `DatasetSource` portu + PubMedQA, MedMCQA implementasyonları | unit testli loader'lar |
| Chat formatına çevirici | örnek → `messages` dönüşümü, testli |
| Sentetik tahlil → açıklama veri seti üretimi | `data/synthetic/lab-explanations.jsonl` + üretim script'i |
| IU X-Ray görüntü + rapor eşleştirme, temizlik | vision eğitim seti |
| `data/README.md` | her veri setinin kaynağı ve lisansı |

Öğrenilecekler: chat template, tokenizasyon, veri kalitesinin model kalitesine etkisi, sentetik veri riskleri.

## Faz 3 — Metin modeli fine-tune `[ ]`

| İş | Çıktı |
|---|---|
| QLoRA trainer (config'ten beslenir) | `uv run medlocal train configs/text-qwen3-4b.yaml` |
| İlk eğitim + loss eğrisi | `training/runs/...` altında metrikler |
| 2–3 hiperparametre denemesi (rank, lr, epoch) | karşılaştırma tablosu |
| Test setinde ölçüm | `docs/results/finetuned-text.md`, baseline ile yan yana |

Öğrenilecekler: LoRA nedir, rank/alpha, 4-bit quantization, gradient accumulation, overfitting nasıl anlaşılır.

## Faz 4 — Görüntü modeli fine-tune `[ ]`

| İş | Çıktı |
|---|---|
| Vision trainer (aynı portlar, yeni implementasyon) | `configs/vision-qwen3vl-4b.yaml` ile eğitim |
| Test setinde ölçüm, MedGemma ile kıyas | `docs/results/finetuned-vision.md` |

Öğrenilecekler: vision encoder + dil modeli nasıl birleşir, hangi katmanlar eğitilir, görüntü ön işleme.

## Faz 5 — Dışa aktarma `[ ]`

| İş | Çıktı |
|---|---|
| LoRA adaptörünü taban modelle birleştir | merged safetensors |
| GGUF'a çevir, Q4_K_M quantize et | `models/*.gguf` (gitignored) |
| Vision model için `mmproj` dosyası | röntgen modeli Ollama'da görüntü alır |
| Ollama `Modelfile` (system prompt, template, parametreler) | `ollama create medlocal-lab` çalışır |
| Quantize modelin kalite kaybını ölç | fp16 vs Q4 tablosu |
| Hugging Face Hub'a adaptör + model kartı | yayın sahibi tarafından yapılır |

Öğrenilecekler: adaptör vs merged model, GGUF formatı, quantization seviyeleri ve bedeli, model kartı nasıl yazılır.

## Faz 6 — API (NestJS) `[ ]`

| İş | Çıktı |
|---|---|
| `shared/llm`: `TextGenerator`, `ImageDescriber` portları + Ollama adaptörü | entegrasyon testi |
| `lab-report` modülü: PDF parser, referans aralığı kuralları, kritik değerler, açıklama use case'i | domain unit testleri + e2e |
| `radiology` modülü: görüntü doğrulama, taslak use case'i | e2e |
| Streaming cevap, timeout, hata sözleşmesi | OpenAPI dokümanı |

## Faz 7 — Web (Next.js) `[ ]`

| İş | Çıktı |
|---|---|
| Tahlil yükleme + sonuç ekranı (değer, aralık, bayrak, açıklama) | çalışan akış |
| Röntgen yükleme + taslak ekranı | çalışan akış |
| Uyarı metni, model sürümü, TR/EN arayüz | her sonuç ekranında görünür |

## Faz 8 — Paketleme ve yayın `[ ]`

| İş | Çıktı |
|---|---|
| Docker Compose (api + web; Ollama host'ta) | tek komutla ayağa kalkar |
| README: mimari diyagram, sonuç tabloları, demo GIF | — |
| CI: lint + test (GitHub Actions) | yeşil rozet |
| LinkedIn yazı serisi taslakları | `docs/posts/` |

## Kapsam dışı

- Tanı, tedavi önerisi, ilaç dozu.
- Gerçek hasta verisi ve kimlik doğrulamalı veri setleri.
- 12 GB VRAM'e sığmayan modeller, bulut eğitimi.
- Göğüs röntgeni dışındaki modaliteler (ilk sürümde).
