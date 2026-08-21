# AZ-Eval

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22050776.svg)](https://doi.org/10.5281/zenodo.22050776)
[![tests](https://github.com/nihatgaribli/AZ-Eval/actions/workflows/tests.yml/badge.svg)](https://github.com/nihatgaribli/AZ-Eval/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Code license: MIT](https://img.shields.io/badge/code%20license-MIT-green.svg)](LICENSE)
[![Data license: CC BY 4.0](https://img.shields.io/badge/data%20license-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)

An open parallel Azerbaijani–English benchmark for evaluating multilingual language
models, together with the evaluation pipeline that produced it.

> **Headline finding.** Fine-tuning on Kazakh, the closest well-resourced Turkic
> relative of Azerbaijani, produces *negative* transfer: `issai/Qolda-AVL-5B` scores
> **3.1%** exact match on Azerbaijani against **16.6%** for its own base model
> `Qwen/Qwen3-VL-4B-Instruct` (Holm-corrected *p* = 0.0024). On the items both models
> demonstrably know in English the two are **indistinguishable in English** (59.4% vs
> 59.4%, *p* = 1.0000) yet **35.4 points apart in Azerbaijani**, so the loss cannot be a
> general capability difference. The mechanism is largely orthographic — **326 of 356**
> Azerbaijani answers come back in Cyrillic, several in Kazakh outright, against **1 of
> 356** for the base model. Transliteration recovers most of the deficit but not all of
> it: the model keeps much of the knowledge and loses the script.

Azerbaijani is a Turkic language written in Latin script. To our knowledge no open
parallel evaluation set for it existed before this one.

*(Azərbaycanca sənədləşdirmə: [README.az.md](README.az.md))*

---

## Results

All comparisons are paired over *n* = 356 items, reported with percentile bootstrap
confidence intervals (1000 resamples, fixed seed), assessed by a sign-flipping
permutation test, and corrected for multiplicity with the Holm procedure.
Majority-class baseline: **1.1%**.

### Azerbaijani vs English (exact match, strict normalization)

| Model | AZ | EN | Gap | *p* (Holm) |
|---|---|---|---|---|
| `Qwen/Qwen3-1.7B` | 5.9% | 23.6% | 17.7 pt | 0.0016 |
| `Qwen/Qwen3-VL-4B-Instruct` | 16.6% | 30.6% | 14.0 pt | 0.0016 |
| `issai/Qolda-AVL-5B` | 3.1% | 29.5% | 26.4 pt | 0.0016 |

### Kazakh-tuned model vs its own base

| Normalization | Base | Kazakh-tuned | Gap | *p* (Holm) |
|---|---|---|---|---|
| `STRICT` | 16.6% | 3.1% | 13.5 pt | **0.0024** |
| `TRANSLIT` | 18.0% | 12.1% | 5.9 pt | **0.0364** |

Transliteration removes **56%** of the deficit. The remainder stays significant, so
script is the largest single cause but not the only one.

### The same comparison on the control stratum

The 96 `world` and `science` items are facts every model demonstrably knows in English.
Restricting to them removes the Azerbaijan-specific questions that neither model can
answer, and the contrast sharpens:

| Language | Base | Kazakh-tuned | Gap | *p* (Holm) |
|---|---|---|---|---|
| **English** | 59.4% | 59.4% | **0.0 pt** | 1.0000 |
| Azerbaijani, `STRICT` | 45.8% | 10.4% | **35.4 pt** | **0.0030** |
| Azerbaijani, `TRANSLIT` | 46.9% | 33.3% | 13.5 pt | 0.2831 |

The English row is the point. The two models are statistically **indistinguishable** in
English, so the 35.4-point Azerbaijani gap cannot come from a general capability
difference. Transliteration recovers 62% of it.

The aggregate table above is reported as primary anyway: at *n* = 96 within a 30-test
family the transliterated row does not survive Holm correction, and only the full sample
has the power to show that the post-transliteration residual is non-zero. The two tables
answer different questions — how large is the effect, and is anything left after
transliteration. Table: [`results/tables/control.md`](results/tables/control.md).

### Script of the produced answers (Azerbaijani prompts)

| Run | Cyrillic | Latin | Empty |
|---|---|---|---|
| `Qolda-AVL-5B` | **326** | 30 | 0 |
| `Qolda-AVL-5B`, Latin script explicitly requested | **314** | 42 | 0 |
| `Qwen3-VL-4B-Instruct` (base) | **1** | 355 | 0 |
| `Qolda-AVL-5B`, English prompts | 0 | 356 | 0 |

Demanding the Latin alphabet in the prompt moves 12 of 326 answers. The behaviour is
not a prompting artifact.

### Where the gap is widest: mathematics

| Category | *n* | Qwen3-1.7B | Qwen3-VL-4B | Qolda-AVL-5B |
|---|---|---|---|---|
| `mathematics` | 28 | 0.0% / 7.1% | 3.6% / 25.0% | 3.6% / 28.6% |
| `world` | 45 | 24.4% / 57.8% | 51.1% / 57.8% | 0.0% / 60.0% |
| `history` | 45 | 0.0% / 0.0% | 4.4% / 0.0% | 0.0% / 2.2% |

*(AZ / EN, exact match, strict.)* On `mathematics` the two larger models answer about a
quarter of the questions correctly in English and **one in twenty-eight** in Azerbaijani
— a 21 to 25 point collapse, the widest of any category. This is not ignorance:
`history`, where the models genuinely do not know the answers, sits near zero in *both*
languages. Mathematics is where knowledge is present and the language blocks it.

Full tables: [`results/tables/`](results/tables/). Raw model outputs:
[`results/raw_outputs/`](results/raw_outputs/).

---

## The dataset

`data/az_eval_v0.jsonl` — 356 human-verified short-answer items, each stated in parallel
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

- **255 hand-written items** plus **101 from templated Wikidata harvesting**
  (8 fact templates × 4 syntactic variants, assigned round-robin so that phrasing is
  not confounded with item difficulty)
- Categories: culture 68, geography 60, language 59, science 51, world 45, history 45,
  mathematics 28
- `answer_aliases` are produced by a rule-based Azerbaijani inflection generator
  (vowel harmony, case, possessive and copular suffixes), so an inflected but correct
  answer is not penalized
- `verified_by` is a **gate**, not metadata: `build` refuses to admit any row that is
  not `human`

`mathematics` is deliberately kept apart from `science`. Azerbaijani mathematical
vocabulary is heavily borrowed (`triqonometriya`, `inteqral`, `funksional analiz`) and
therefore sits closer to Latin orthography than general science vocabulary does; merged
into one column it would dilute the writing-system effect this benchmark is built to
measure.

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

In practice the writing-system column is **+0.0 points for six of eight runs** and jumps
to **+9.0** and **+8.1** for exactly two — the Kazakh-tuned model on Azerbaijani, with
and without an explicit request for Latin script. That is how the mechanism was
isolated. Morphology contributes at most +1.1 points anywhere, diacritics at most +0.6.

---

## Install and run

```bash
pip install -r requirements.txt
python -m pytest                    # 517 tests

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
| `tests/` | 517 tests |

---

## Data construction and AI use

Items come from two routes. **255 were written by hand** by a native Azerbaijani
speaker. The remaining **101 were generated automatically from Wikidata** using eight
templated SPARQL queries, each rendered in four syntactic variants. Accepted-answer sets
were expanded by a rule-based morphological generator.

**No large language model was used to author, translate, or answer any dataset item.**
Every item, hand-written or harvested, was reviewed by a human annotator through the
included review interface; only items marked `verified_by = human` enter the released
dataset, and rejected items are retained in the raw files so that the acceptance rate
stays auditable.

Where an item asserts a fact about a person, institution or date, the claim was checked
against the cited source before acceptance. Candidates that the source did not support
were dropped rather than adjusted.

An AI coding assistant was used while developing the pipeline. All reported numbers are
produced by this code from this data and reproduce with a fixed seed.

---

## Excluded topics

Items whose gold answer depends on a politically contested position are excluded, so
that every reference answer in the benchmark is one a neutral source would state without
qualification.

Most rejected candidates are retained in `data/raw/` with `verified_by: "rejected"` and a
note recording the reason, so that the acceptance rate stays auditable. Items excluded on
political grounds are the exception: they are removed from the raw files as well, at the
author's decision, and are therefore not recoverable from this repository. Six items were
removed under this rule.

This is a scope decision about answer stability, not about coverage: a benchmark is only
useful if its gold answers are uncontested, and disputed place names or historical claims
fail that test regardless of which position one takes.

## Known limitations

- **n = 356.** Confidence intervals are ±2–5 points. Every comparison reported above
  survives Holm correction.
- **One model pair.** The controlled comparison rests on `Qolda-AVL-5B` against its own
  base. The 9B/8B pair did not fit in 8 GB of VRAM.
- **Two knowledge regimes are mixed, on purpose.** `world` and `science` items are facts
  every model demonstrably knows in English, so failure in Azerbaijani is a
  language-processing failure. `history` items are Azerbaijan-specific and score near
  zero in *both* languages (≤ 4.4% AZ, ≤ 2.2% EN) — that is ignorance, not a script
  problem, and it should not be read as a language result. The categories are kept
  separate precisely so the distinction stays visible instead of averaging away.
- **Suffix stripping is a heuristic, not a morphological analyzer.** Its documented
  failures are asserted in `tests/test_metrics.py::test_known_stripping_limitations`
  rather than hidden.

## Citing

Archived on Zenodo; the badge above resolves to the latest version. To cite the exact
revision behind the reported numbers — v0.1.0, *n* = 356 — use the version DOI
[10.5281/zenodo.22050777](https://doi.org/10.5281/zenodo.22050777).
Machine-readable metadata is in [CITATION.cff](CITATION.cff).

```bibtex
@dataset{garibli_2026_azeval,
  author    = {Garibli, Nihat},
  title     = {AZ-Eval: a parallel Azerbaijani--English benchmark},
  year      = {2026},
  publisher = {Zenodo},
  version   = {v0.1.0},
  doi       = {10.5281/zenodo.22050777},
  url       = {https://doi.org/10.5281/zenodo.22050777}
}
```

## License

Code: MIT. Dataset: CC BY 4.0. See [LICENSE](LICENSE) and [LICENSE-DATA](LICENSE-DATA).
