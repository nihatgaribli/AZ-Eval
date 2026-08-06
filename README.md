# AZ-Eval

An open parallel Azerbaijani–English benchmark for evaluating multilingual language
models, together with the evaluation pipeline that produced it.

> **Headline finding.** Fine-tuning on Kazakh, the closest well-resourced Turkic
> relative of Azerbaijani, produces *negative* transfer: `issai/Qolda-AVL-5B` scores
> **9.4%** exact match on Azerbaijani against **26.0%** for its own base model
> `Qwen/Qwen3-VL-4B-Instruct` (Holm-corrected *p* = 0.0042). The mechanism is
> orthographic — **82 of 96** Azerbaijani answers come back in Cyrillic, several in
> Kazakh outright, against **1 of 96** for the base model. After transliteration the
> deficit halves and is no longer significant: the model keeps the knowledge and loses
> the script.

Azerbaijani is a Turkic language written in Latin script. To our knowledge no open
parallel evaluation set for it existed before this one.

*(Azərbaycanca sənədləşdirmə: [README.az.md](README.az.md))*

---

## Results

All comparisons are paired, reported with percentile bootstrap confidence intervals
(1000 resamples, fixed seed), assessed by a sign-flipping permutation test, and
corrected for multiplicity with the Holm procedure. Majority-class baseline: **2.1%**.

### Azerbaijani vs English (exact match, strict normalization)

| Model | AZ | EN | Gap | *p* |
|---|---|---|---|---|
| `Qwen/Qwen3-1.7B` | 10.4% | 45.8% | 35.4 pt | 0.0001 |
| `Qwen/Qwen3-VL-4B-Instruct` | 26.0% | 51.0% | 25.0 pt | 0.0001 |
| `issai/Qolda-AVL-5B` | 9.4% | 50.0% | 40.6 pt | 0.0001 |

### Kazakh-tuned model vs its own base

| Normalization | Base | Kazakh-tuned | *p* (Holm) |
|---|---|---|---|
| `STRICT` | 26.0% | 9.4% | **0.0042** |
| `TRANSLIT` | 28.1% | 19.8% | 1.0000 |

### Script of the produced answers (Azerbaijani prompts)

| Run | Cyrillic | Latin | Empty |
|---|---|---|---|
| `Qolda-AVL-5B` | **82** | 9 | 5 |
| `Qolda-AVL-5B`, Latin script explicitly requested | **79** | 10 | 7 |
| `Qwen3-VL-4B-Instruct` (base) | **1** | 84 | 11 |
| `Qolda-AVL-5B`, English prompts | 0 | 85 | 11 |

Full tables: [`results/tables/`](results/tables/). Raw model outputs (768 rows):
[`results/raw_outputs/`](results/raw_outputs/).

---

## The dataset

`data/az_eval_v0.jsonl` — 96 human-verified short-answer items, each stated in parallel
Azerbaijani and English.

```json
{"id": "az-001",
 "question_az": "Fransanın paytaxtı hansı şəhərdir?",
 "question_en": "What is the capital city of France?",
 "answer": "Paris", "answer_en": "Paris",
 "answer_aliases": ["Parisdə", "Parisdən", "Parisə", "Parisin", "Parisdir"],
 "category": "geography", "source": "https://www.wikidata.org/wiki/Q142",
 "difficulty": "easy", "provenance": "wikidata-template",
 "verified_by": "human", "notes": "template=country_capital;variant=0"}
```

- **8 fact templates × 4 syntactic variants** = 32 question frames, assigned round-robin
  so that phrasing is not confounded with item difficulty
- Categories: geography 24, culture 24, language 24, history 12, science 12
- `answer_aliases` are produced by a rule-based Azerbaijani inflection generator
  (vowel harmony, case, possessive and copular suffixes), so an inflected but correct
  answer is not penalized
- `verified_by` is a **gate**, not metadata: `build` refuses to admit any row that is
  not `human`

A further 45 Azerbaijan-specific items (architectural heritage, river systems, national
art) are drafted in `data/raw/az_content.jsonl` and awaiting verification.

---

## Why four normalizations

Azerbaijani is agglutinative, and models trained on other scripts may answer in the
wrong alphabet. A single exact-match number therefore conflates *knowing* with
*writing*. Scores are computed along a chain of increasingly permissive normalizations:

```text
STRICT  ──▶  MORPH  ──▶  LENIENT  ──▶  TRANSLIT
             suffix       diacritic     Cyrillic→Latin
             stripping    folding       transliteration
```

Each stage adds exactly one transformation, applied symmetrically to prediction and
reference. The score increment across a stage is therefore an attribution of error mass
to that single surface phenomenon.

In practice the writing-system column is zero for seven of eight runs and jumps
**+10.4 points** for exactly one — the Kazakh-tuned model on Azerbaijani. That is how
the mechanism was isolated.

---

## Install and run

```bash
pip install -r requirements.txt
python -m pytest                    # 467 tests

# harvest draft items from Wikidata (parallel AZ/EN by construction)
python -m src.harvest_wikidata --per-template 12 --max-per-answer 2

# human verification in a local browser UI: A accept / R reject / S skip
python -m src.review data/raw/wikidata.jsonl

# build the dataset (only verified_by=human passes)
python -m src.build_dataset build

# evaluate; add --load-in-4bit on small GPUs
python -m src.run_eval --model Qwen/Qwen3-1.7B --language az
python -m src.run_eval --model Qwen/Qwen3-1.7B --language en

# score and produce tables
python -m src.analyze
```

`run_eval` computes no metrics. It writes raw model text to `results/raw_outputs/` and
nothing else, so the scoring rules can be changed and `analyze` rerun without spending
another GPU-hour.

---

## Layout

| Path | Contents |
|---|---|
| `src/harvest_wikidata.py` | Templated SPARQL harvesting with quality filters |
| `src/review.py` | Local browser UI for human verification |
| `src/build_dataset.py` | Schema validation, alias filling, dataset assembly |
| `src/morphology.py` | Rule-based Azerbaijani inflection generation |
| `src/metrics.py` | Normalizations, EM, token F1, bootstrap, paired tests, Holm |
| `src/run_eval.py` | Model runs; raw outputs only |
| `src/analyze.py` | Scoring, tables, stratified error sample |
| `tests/` | 467 tests |

---

## Data construction and AI use

Candidate items were generated automatically from Wikidata using eight templated SPARQL
queries, each rendered in four syntactic variants; accepted-answer sets were expanded by
a rule-based morphological generator. **No large language model was used to author,
translate, or answer any dataset item.** Every candidate was then reviewed by a human
annotator through the included review interface; only items marked `verified_by =
human` enter the released dataset, and rejected items are retained in the raw files so
that the acceptance rate stays auditable.

An AI coding assistant was used while developing the pipeline. All reported numbers are
produced by this code from this data and reproduce with a fixed seed.

---

## Known limitations

- **n = 96.** Confidence intervals are ±6–10 points. The transliterated comparison sits
  at *p* = 0.12 and is likely underpowered.
- **One model pair.** The controlled comparison rests on `Qolda-AVL-5B` against its own
  base. The 9B/8B pair did not fit in 8 GB of VRAM.
- **Verified items are universal facts.** This is deliberate: RQ1 needs facts the model
  demonstrably knows in English, so that failure in Azerbaijani is a language-processing
  failure rather than ignorance. Azerbaijan-specific items are drafted but not yet
  verified.
- **Suffix stripping is a heuristic, not a morphological analyzer.** Its documented
  failures are asserted in `tests/test_metrics.py::test_known_stripping_limitations`
  rather than hidden.

## License

Code: MIT. Dataset: CC BY 4.0. See [LICENSE](LICENSE) and [LICENSE-DATA](LICENSE-DATA).
