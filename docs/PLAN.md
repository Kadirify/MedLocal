# MedLocal Yol Haritası

Kapsam: **sadece tahlil açıklama.** Röntgen tarafı 2026-09-19'da kapsamdan çıkarıldı; baseline ölçümleri ve kodu git geçmişinde (`feat/vision-baseline`) duruyor.

Her faz bir branch'te yapılır, doğrulanır, sonra bir sonrakine geçilir. "Çıktı" sütunundaki şey yoksa faz bitmemiştir.

Durum: `[ ]` başlamadı · `[~]` sürüyor · `[x]` bitti

## Faz 0 — Ortam `[x]`

| İş | Çıktı |
|---|---|
| uv + Python 3.12, PyTorch (CUDA 12.8), Unsloth, transformers, peft, trl | `uv run medlocal doctor` → RTX 5070, sm_120 |
| Ollama | modeller HTTP API üzerinden %100 GPU'da cevap verir |
| ruff, mypy, pytest | lint komutları geçer |

## Faz 1 — Hattı bir benchmark ile kurmak `[x]`

PubMedQA burada ürün değil, hattın doğru çalıştığını kanıtlayan ölçü çubuğu.

| İş | Çıktı |
|---|---|
| Resmi test split'i, baseline ölçümü | `docs/results/baseline-text.md` — accuracy 0.596 |
| QLoRA trainer, iki deney | `docs/results/finetuned-text.md` — accuracy 0.764 |
| Adaptör birleştirme → GGUF → Ollama, eşdeğerlik ölçümü | `medlocal-pubmedqa:q8_0`, Ollama'da 0.766 |

Öğrenilenler: baseline'ın önemi, macro F1, veri dengesizliği, chat template tuzağı, gradient accumulation, adaptör/merge/GGUF.

Açık kalan: "maybe" sınıfı (F1 0). Ürünü etkilemediği için ertelendi.

## Faz 2 — Tahlil verisi `[x]`

| İş | Çıktı |
|---|---|
| Analit kataloğu: aralıklar, kritik eşikler, doğrulanmış arka plan metni ✔ | `reference/analytes.yaml` (28 analit, 8 panel) |
| Deterministik bayraklama ✔ | `labs/report.py`, sınır değer testleri |
| Sentetik rapor üretici (seed'li, kritik değerlerden uzak) ✔ | `labs/synthetic.py` |
| Açıklama güvenlik kontrolleri ✔ | `labs/explanation_checks.py` — 7 kural |
| Öğretmen modelle veri seti üretimi ✔ | `data/synthetic/lab-explanations.jsonl` (976 / 99 / 149) |
| Elle kalite incelemesi ✔ (kısmi) | üç kontrol hatası bulundu ve düzeltildi, bkz. `docs/results/lab-explainer.md` |

Öğrenilecekler: distillation, sentetik veri riskleri, kural tabanlı filtreleme, öğretmene "kopya kâğıdı" vermek.

## Faz 3 — Tahlil açıklama modeli `[~]`

| İş | Çıktı |
|---|---|
| Üretim tabanlı değerlendirme: kural geçme oranı, öğretmenle ROUGE-L, uzunluk ✔ | `medlocal evaluate-explanations` |
| Ham Qwen3-4B baseline ✔ | kural geçme oranı 0.779 |
| QLoRA eğitimi, erken durdurma ✔ | adaptör, doğrulama loss'u 0.295 |
| Test ölçümü ✔ | `docs/results/lab-explainer.md` — 0.779 → 0.940 |
| Kuraldan geçemeyen 9 çıktının ve rastgele 30 çıktının elle okunması | notlar |
| Zor vakalar: hepsi normal, tek sınır değer, 5+ bayrak | ayrı tablo |

## Faz 4 — Dışa aktarma `[~]`

| İş | Çıktı |
|---|---|
| Birleştir → Q8_0 GGUF → Modelfile ✔ | `medlocal-lab:q8_0` Ollama'da, API bunu kullanıyor |
| Ollama üzerinden aynı test ✔ | 0.946 |
| (İsteğe bağlı) Q4_K_M, `llama-quantize` ile | boyut / kalite tablosu |
| Hugging Face Hub'a adaptör + model kartı | yayın sahibi tarafından yapılır |

## Faz 5 — API (NestJS) `[~]`

| İş | Çıktı |
|---|---|
| pnpm workspace, eslint, prettier ✔ | `pnpm install` ve lint temiz |
| `shared/llm`: `TextGenerator` portu + Ollama adaptörü (streaming, timeout) ✔ | entegrasyon testi |
| `lab-report` domain: `LabReport`, `ReferenceRange`, bayraklama, kritik değerler ✔ | Python tarafıyla aynı sınır değer testleri |
| Katalog okuyucu (`reference/analytes.yaml`) ✔ | `ReferenceRangeRepository` |
| PDF parser: metin tabanlı PDF ✔, gerçek e-Nabız / özel lab çıktılarıyla deneme | örnek PDF'lerle testler |
| `ExplainLabReport` use case, eğitimdeki prompt formatıyla birebir ✔ | e2e test, OpenAPI |

## Faz 6 — Web (Next.js) `[~]`

| İş | Çıktı |
|---|---|
| PDF yükleme, sonuç tablosu (değer, aralık, bayrak) ✔ | çalışan akış |
| Açıklamanın akarak gelmesi, kritik değer uyarısı ✔ | — |
| Uyarı metni, model sürümü, TR/EN arayüz | her sonuç ekranında |

## Faz 7 — Türkçe `[x]`

| İş | Çıktı |
|---|---|
| Türkçe açıklama verisi, Türkçe kontroller ✔ | tek veri seti, yarısı Türkçe |
| İki dilli tek model ✔ | `medlocal-lab:v3-q8_0`; sonuçlar `docs/results/lab-explainer.md` |
| Katalog notlarının modele kullanım anında verilmesi (v3) ✔ | gerçek raporda bulunan bilgi hatası üzerine |

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
- Görüntüleme (röntgen, MR, BT).
- 12 GB VRAM'e sığmayan modellerin eğitimi, bulut eğitimi.
