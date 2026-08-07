"""Xam cavabları bala çevirir, cədvəlləri və xəta nümunəsini hazırlayır.

    python -m src.analyze

Bu modul modelə MÜRACİƏT ETMİR — yalnız `results/raw_outputs/` altındakı xam
faylları oxuyur. Ona görə metrikanı, cavab çıxarma qaydasını və ya normalizasiya
rejimini dəyişib istənilən qədər təkrar işlətmək olar; heç bir GPU saatı yenidən
xərclənmir. Bu ayrılıq brief-in 7-ci bölməsinin tələbidir.

İstehsal etdiyi cədvəllər:

  1. `main.md`      — model × dil × metrika, hər xana `62.4% ± 3.1` formatında
  2. `modes.md`     — STRICT / MORPH / LENIENT yan-yana (RQ3-ün kəmiyyət cavabı)
  3. `rq1.md`       — AZ vs EN cütləşdirilmiş fərq, CI və p qiyməti
  4. `rq2.md`       — modellərarası cütləşdirilmiş müqayisə (Qolda transfer sualı)
  5. `breakdown.md` — kateqoriya və sual variantı üzrə kəsim
  6. `errors.csv`   — əl ilə etiketlənmək üçün təbəqələndirilmiş səhv nümunəsi
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.build_dataset import load_jsonl
from src.metrics import (
    LENIENT,
    MODES,
    STRICT,
    NormalizationConfig,
    bootstrap_ci,
    compare_paired,
    format_ci,
    holm_correction,
    normalize,
    score_example,
)

__all__ = [
    "extract_answer",
    "RunKey",
    "Run",
    "load_runs",
    "run_label",
    "gold_answers",
    "score_run",
    "markdown_table",
    "build_main_table",
    "build_modes_table",
    "build_rq1_table",
    "build_rq2_table",
    "build_breakdown_table",
    "error_rows",
]


# --------------------------------------------------------------------------
# Cavabın xam mətndən çıxarılması
# --------------------------------------------------------------------------

#: Modellərin cavabdan əvvəl yazdığı adi prefikslər. İki ailə var:
#:
#:   etiket formalı  — "Cavab:", "Answer:", "A -"   (ayırıcı TƏLƏB OLUNUR)
#:   cümlə formalı   — "The answer is", "Cavab budur"
#:
#: Etiket ailəsində ayırıcının tələb olunması vacibdir: onsuz `a` qaydası
#: "Almaniya" və "Au" kimi həqiqi cavabların başını yeyərdi.
_ANSWER_PREFIXES = re.compile(
    r"^\s*(?:"
    r"(?:cavab|cavabı|answer|a)\s*[:\-—]"
    r"|the answer is\b"
    r"|cavab budur\b"
    r")\s*",
    re.IGNORECASE,
)

#: "Fransanın paytaxtı Parisdir." kimi tam cümlə cavablarında son nöqtə.
_TRAILING_PUNCT = re.compile(r"[.!?,;:]+\s*$")

#: Düşünmə modellərinin gizli mühakimə bloku.
_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_UNCLOSED_THINK = re.compile(r"<think>.*", re.DOTALL | re.IGNORECASE)

#: Markdown vurğusu — modellər cavabı tez-tez qalın yazır: "**Berlin**dır".
#: Ulduzlar normalizasiyada durğu işarəsi kimi silinmir (Unicode kateqoriyası
#: `Po` deyil, `Sm`/`Po` qarışığıdır) və EM-i sındırır.
_MARKDOWN_EMPHASIS = re.compile(r"(\*{1,3}|_{1,3}|`+)")


def extract_answer(raw_response: str, max_words: int = 12) -> str:
    """Modelin xam mətnindən qısa cavabı çıxarır.

    Bu qat metrikanı birbaşa dəyişir, ona görə qaydaları açıq saxlamaq lazımdır:

    1. `<think>...</think>` blokları silinir (düşünmə modelləri). Blok
       bağlanmayıbsa — yəni generasiya mühakimənin ortasında kəsilibsə — model
       cavaba ümumiyyətlə çatmayıb, ona görə nəticə BOŞ sayılır. `"<think>"`
       sətrini cavab kimi saxlamaq xəta taksonomiyasını korlayardı: sətir
       "səhv cavab" yox, "cavab yoxdur" kateqoriyasına aiddir.
    2. Yalnız BİRİNCİ sətir götürülür. Modellər çox vaxt cavabı yazıb sonrakı
       sətirlərdə izahat verir; izahatı saymaq token F1-i süni şəkildə aşağı salır.
    3. "Cavab:" / "Answer:" prefiksləri atılır.
    4. Dırnaqlar və sondakı durğu işarəsi təmizlenir.
    5. Nəticə `max_words` sözdən uzundursa, ilk cümlə götürülür — model
       təlimata baxmayaraq abzas yazıbsa, ilk cümlə adətən cavabı daşıyır.

    Qayda hər iki dilə EYNİ tətbiq olunur. Fərqli tətbiq olunsaydı, ölçülən
    AZ/EN fərqinin bir hissəsi bu qatdan gələrdi.

    Xam cavab diskdə toxunulmaz qalır — qayda dəyişsə, yalnız bu modul yenidən
    işlədilir, modellər yox.
    """
    text = (raw_response or "").strip()
    if not text:
        return ""

    text = _THINK_BLOCK.sub(" ", text)
    text = _UNCLOSED_THINK.sub("", text)   # kəsilmiş mühakimə -> cavab yoxdur
    text = text.strip()
    if not text:
        return ""

    text = text.splitlines()[0].strip()
    text = _ANSWER_PREFIXES.sub("", text, count=1)
    text = _MARKDOWN_EMPHASIS.sub("", text)
    text = text.strip().strip('"“”«»\'')

    if len(text.split()) > max_words:
        first_sentence = re.split(r"(?<=[.!?])\s+", text)[0]
        text = first_sentence

    return _TRAILING_PUNCT.sub("", text).strip()


# --------------------------------------------------------------------------
# Qaçışların yüklənməsi
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RunKey:
    """Bir qaçışın kimliyi: model + dil + prompt üslubu.

    Prompt üslubu açarın hissəsidir, yoxsa eyni modelin iki fərqli promptla
    qaçışı BİR qaçış kimi birləşər və əlifba nəzarəti mənasını itirər.
    Standart üslub adda göstərilmir ki, mövcud cədvəllər dəyişməsin.
    """

    model: str
    language: str
    prompt_style: str = "default"

    def __str__(self) -> str:
        suffix = "" if self.prompt_style == "default" else f" ({self.prompt_style})"
        return f"{self.model}{suffix} [{self.language}]"


@dataclass
class Run:
    """Bir modelin bir dildəki qaçışı: id -> çıxarılmış cavab."""

    key: RunKey
    predictions: dict[str, str]
    raw: dict[str, str]

    @property
    def ids(self) -> set[str]:
        return set(self.predictions)


def load_runs(raw_dir: Path, max_words: int = 12) -> list[Run]:
    """`results/raw_outputs/*.jsonl` fayllarını oxuyur.

    Fayl adına yox, sətirlərin içindəki `model`/`language` sahələrinə güvənir —
    fayl əl ilə adı dəyişdirilsə də nəticə düzgün qalır.
    """
    grouped: dict[RunKey, dict[str, dict[str, str]]] = defaultdict(
        lambda: {"pred": {}, "raw": {}}
    )

    for path in sorted(raw_dir.glob("*.jsonl")):
        for _, row in load_jsonl(path):
            if not isinstance(row, dict):
                continue
            key = RunKey(
                row.get("model", path.stem),
                row.get("language", "az"),
                row.get("prompt_style", "default"),
            )
            record_id = row.get("id")
            if not isinstance(record_id, str):
                continue
            raw = row.get("raw_response", "")
            grouped[key]["raw"][record_id] = raw
            grouped[key]["pred"][record_id] = extract_answer(raw, max_words=max_words)

    return [
        Run(key=key, predictions=data["pred"], raw=data["raw"])
        for key, data in sorted(grouped.items(), key=lambda kv: str(kv[0]))
    ]


def gold_answers(record: dict[str, Any], language: str) -> list[str]:
    """Bir sətrin qəbul edilən cavabları.

    AZ tərəfdə `answer_aliases` da daxil edilir (hallanmış formalar), EN tərəfdə
    yalnız `answer_en` — ingilis dilində hallanma yoxdur, alias generasiyası da
    yoxdur. Bu asimmetriya QƏSDƏNdir və hesabatda göstərilməlidir: AZ tərəfə bir
    az əlverişlidir, yəni ölçülən AZ/EN fərqi əsl fərqin AŞAĞI həddidir.
    """
    azerbaijani = str(record.get("answer", ""))
    english = str(record.get("answer_en", ""))

    if language == "az":
        return [azerbaijani, *(record.get("answer_aliases") or [])]

    # İngilis etalonu AZ-dən UZUNDURSA, ayrı-ayrı sözləri də qəbul edilir.
    #
    # Wikidata etiket konvensiyaları iki dildə fərqlidir və asimmetriya hər iki
    # istiqamətdə baş verir. AZ tərəfin uzun olduğu hal `build_dataset
    # .equivalence_aliases` ilə datasetdə həll olunur; burada TƏRSİ tutulur:
    #
    #     AZ "futbolçu"  vs  EN "association football player"
    #     AZ "Şimalda"   vs  EN "In the North"
    #
    # Model ingiliscə "footballer" və ya "North" desə, faktiki olaraq doğrudur,
    # amma exact match sıfır verər — halbuki azərbaycanca qarşılığı bal alır.
    # Düzəliş olmasa, ölçülən AZ/EN fərqinin bir hissəsi dildən yox, etiket
    # konvensiyasından gələr.
    english_words = english.split()
    if len(english_words) > max(1, len(azerbaijani.split())):
        return [english, *english_words]
    return [english]


def score_run(
    run: Run,
    dataset: dict[str, dict[str, Any]],
    mode: NormalizationConfig,
    ids: Sequence[str] | None = None,
) -> dict[str, dict[str, float]]:
    """Qaçışı bal cədvəlinə çevirir: id -> {"em": ..., "f1": ...}."""
    target_ids = list(ids) if ids is not None else sorted(run.ids & set(dataset))
    return {
        record_id: score_example(
            run.predictions.get(record_id, ""),
            gold_answers(dataset[record_id], run.key.language),
            mode,
        )
        for record_id in target_ids
    }


def run_label(key: "RunKey") -> str:
    """Cədvəl üçün qaçış adı: model + (standartdan fərqlidirsə) prompt üslubu.

    Dil ayrıca sütundadır, ona görə `str(key)`-dən fərqli olaraq bura salınmır.
    Prompt üslubu MÜTLƏQ görünməlidir: əlifba nəzarəti qaçışı əsas qaçışla eyni
    modeldəndir və etiketsiz cədvəldə iki fərqləndirilməyən sətir kimi görünür.
    """
    suffix = "" if key.prompt_style == "default" else f" ({key.prompt_style})"
    return f"{key.model}{suffix}"


def _column(scores: dict[str, dict[str, float]], metric: str, ids: Sequence[str]):
    return [scores[i][metric] for i in ids]


# --------------------------------------------------------------------------
# Bazalar
# --------------------------------------------------------------------------


def majority_baseline(
    dataset: dict[str, dict[str, Any]], ids: Sequence[str], language: str
) -> float:
    """"Həmişə ən çox rast gəlinən cavabı de" strategiyasının balı.

    Modelin balı bu rəqəmdən yuxarı deyilsə, model heç nə öyrənməyib —
    sadəcə paylanmanı təkrarlayır. Avtomatik yığılmış datasetlərdə bu, real
    risqdir, ona görə hər cədvəldə göstərilir.
    """
    counts: dict[str, int] = defaultdict(int)
    for record_id in ids:
        counts[normalize(gold_answers(dataset[record_id], language)[0], STRICT)] += 1
    if not counts:
        return 0.0
    return max(counts.values()) / len(ids)


# --------------------------------------------------------------------------
# Cədvəl qurucuları
# --------------------------------------------------------------------------


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    body = [list(map(str, row)) for row in rows]
    widths = [
        max(len(str(headers[i])), *(len(r[i]) for r in body)) if body else len(headers[i])
        for i in range(len(headers))
    ]
    line = lambda cells: "| " + " | ".join(
        str(c).ljust(widths[i]) for i, c in enumerate(cells)
    ) + " |"
    sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    return "\n".join([line(headers), sep, *(line(r) for r in body)])


def build_main_table(
    runs: Sequence[Run], dataset: dict[str, dict[str, Any]], seed: int = 0
) -> str:
    """Model × dil × metrika, STRICT rejimdə (əsas, ən müdafiə olunan rəqəm)."""
    rows = []
    for run in runs:
        ids = sorted(run.ids & set(dataset))
        if not ids:
            continue
        scores = score_run(run, dataset, STRICT, ids)
        em = bootstrap_ci(_column(scores, "em", ids), seed=seed)
        f1 = bootstrap_ci(_column(scores, "f1", ids), seed=seed)
        rows.append(
            [
                run_label(run.key),
                run.key.language.upper(),
                len(ids),
                format_ci(em),
                format_ci(f1),
                f"{100 * majority_baseline(dataset, ids, run.key.language):.1f}%",
            ]
        )
    return markdown_table(
        ["Model", "Dil", "N", "EM (STRICT)", "Token F1 (STRICT)", "Əksəriyyət bazası"],
        rows,
    )


def build_modes_table(
    runs: Sequence[Run], dataset: dict[str, dict[str, Any]], seed: int = 0
) -> str:
    """Üç normalizasiya rejimi yan-yana — RQ3-ün kəmiyyət cavabı.

    STRICT -> MORPH morfologiyadan, MORPH -> LENIENT diakritikadan,
    LENIENT -> TRANSLIT isə YAZI SİSTEMİNDƏN gələn xəta payını verir.

    Sonuncu sütun layihənin əsas tapıntısını ölçür: qazax dilinə köklənmiş model
    azərbaycan sualına kiril əlifbası ilə düzgün cavab verir. Onun balı
    transliterasiyadan sonra kəskin qalxırsa, bu, biliyin transfer olunduğunu,
    yazı sisteminin isə olunmadığını göstərir.
    """
    rows = []
    for run in runs:
        ids = sorted(run.ids & set(dataset))
        if not ids:
            continue
        means = {}
        for mode in MODES:
            scores = score_run(run, dataset, mode, ids)
            means[mode.name] = 100 * sum(_column(scores, "em", ids)) / len(ids)
        rows.append(
            [
                run_label(run.key),
                run.key.language.upper(),
                f"{means['strict']:.1f}%",
                f"{means['morph']:.1f}%",
                f"{means['lenient']:.1f}%",
                f"{means['translit']:.1f}%",
                f"+{means['morph'] - means['strict']:.1f}pp",
                f"+{means['lenient'] - means['morph']:.1f}pp",
                f"+{means['translit'] - means['lenient']:.1f}pp",
            ]
        )
    return markdown_table(
        [
            "Model", "Dil", "STRICT", "MORPH", "LENIENT", "TRANSLIT",
            "morfologiya", "diakritika", "yazı sistemi",
        ],
        rows,
    )


#: NƏZARƏT qatı: modelin ingiliscə nümayişkaranə bildiyi faktlar.
#:
#: RQ2-nin təmiz ölçüsü buradadır. Azərbaycana xas suallarda hər iki model
#: uğursuz olur (bilik yoxluğu), ona görə onlar fərqi SEYRƏLDİR və ümumi rəqəm
#: effekti olduğundan kiçik göstərir. Nəzarət qatında isə ingilis balları
#: üst-üstə düşür, yəni ümumi qabiliyyət fərqi istisna olunur və azərbaycanca
#: qalan fərq yalnız dilə aid ola bilər.
CONTROL_CATEGORIES: frozenset[str] = frozenset({"world", "science"})


def _paired(
    run_a: Run,
    run_b: Run,
    dataset: dict[str, dict[str, Any]],
    mode: NormalizationConfig,
    metric: str,
    seed: int,
    categories: frozenset[str] | None = None,
):
    ids = sorted(run_a.ids & run_b.ids & set(dataset))
    if categories is not None:
        ids = [i for i in ids if dataset[i].get("category") in categories]
    if not ids:
        return None, []
    a = _column(score_run(run_a, dataset, mode, ids), metric, ids)
    b = _column(score_run(run_b, dataset, mode, ids), metric, ids)
    return compare_paired(a, b, seed=seed), ids


def _table_with_holm(headers: Sequence[str], rows: list[list[Any]]) -> str:
    """Xam p sütununu düzəldilmiş p ilə birlikdə verir.

    Sətirlərin sondan əvvəlki elementi XAM `p` (float), sonuncusu isə xam
    həddə görə "bəli/xeyr" olmalıdır. Funksiya cədvəldəki bütün testləri bir
    ailə sayır, Holm düzəlişini tətbiq edir və nəticəni əlavə sütun kimi verir.

    Xam p qiyməti də saxlanılır — gizlətmək düzəlişin təsirini görünməz edərdi.
    """
    raw_p = [row[-2] for row in rows]
    adjusted = holm_correction(raw_p)

    out = []
    for row, p_adj in zip(rows, adjusted, strict=True):
        out.append(
            [*row[:-2], f"{row[-2]:.4f}", f"{p_adj:.4f}", "bəli" if p_adj < 0.05 else "xeyr"]
        )
    return markdown_table([*headers, "p", "p (Holm)", "Mənalı"], out)


def build_rq1_table(
    runs: Sequence[Run], dataset: dict[str, dict[str, Any]], seed: int = 0
) -> str:
    """RQ1: eyni modelin EN və AZ balları arasındakı cütləşdirilmiş fərq."""
    # Açar model + prompt üslubudur. Yalnız modelə görə qruplaşdırsaq, əlifba
    # nəzarəti qaçışı əsas qaçışı SƏSSİZCƏ əvəz edər və cədvəl yanlış cütləri
    # müqayisə edərdi.
    by_model: dict[str, dict[str, Run]] = defaultdict(dict)
    for run in runs:
        by_model[run_label(run.key)][run.key.language] = run

    rows = []
    for model, langs in sorted(by_model.items()):
        if "az" not in langs or "en" not in langs:
            continue
        for mode in MODES:
            result, ids = _paired(langs["en"], langs["az"], dataset, mode, "em", seed)
            if result is None:
                continue
            rows.append(
                [
                    model,
                    mode.name,
                    len(ids),
                    f"{100 * result.mean_b:.1f}%",
                    f"{100 * result.mean_a:.1f}%",
                    f"{100 * result.diff:.1f}pp",
                    f"[{100 * result.diff_low:.1f}, {100 * result.diff_high:.1f}]",
                    result.p_value,
                    "bəli" if result.significant else "xeyr",
                ]
            )
    if not rows:
        return "_AZ və EN qaçışı olan model yoxdur._"
    return _table_with_holm(
        ["Model", "Rejim", "N", "AZ EM", "EN EM", "Fərq", "95% CI"], rows
    )


def build_rq2_table(
    runs: Sequence[Run],
    dataset: dict[str, dict[str, Any]],
    language: str = "az",
    seed: int = 0,
) -> str:
    """RQ2: modellərarası cütləşdirilmiş müqayisə (qazax modelinin transferi).

    DİQQƏT — hesabatda mütləq qeyd olunmalıdır: "Qolda AZ-də zəifdir" nəticəsi
    tək başına "türk dilləri arasında transfer yoxdur" demək DEYİL. Zəiflik
    qazax fine-tune-undan yox, modelin bazasından gələ bilər. Bu suala cavab
    vermək üçün Qolda-nın BAZA modeli də ölçülməli və bu cədvələ salınmalıdır.

    Müqayisə BÜTÜN rejimlərdə verilir, çünki yalnız STRICT-ə baxmaq nəticəni
    tərsinə çevirə bilər: kirillə cavab verən model STRICT-də zəif, TRANSLIT-də
    güclü görünür. Bir rejimli cədvəl bu fərqi gizlədərdi.
    """
    same_language = [r for r in runs if r.key.language == language]
    rows = []
    for i, run_a in enumerate(same_language):
        for run_b in same_language[i + 1 :]:
            for mode in MODES:
                result, ids = _paired(run_a, run_b, dataset, mode, "em", seed)
                if result is None:
                    continue
                rows.append(
                    [
                        run_label(run_a.key),
                        run_label(run_b.key),
                        mode.name,
                        len(ids),
                        f"{100 * result.mean_a:.1f}%",
                        f"{100 * result.mean_b:.1f}%",
                        f"{100 * result.diff:.1f}pp",
                        result.p_value,
                        "bəli" if result.significant else "xeyr",
                    ]
                )
    if not rows:
        return f"_`{language}` dilində müqayisə üçün ən azı iki model lazımdır._"
    return _table_with_holm(
        ["Model A", "Model B", "Rejim", "N", "A EM", "B EM", "Fərq"], rows
    )


def build_control_table(
    runs: Sequence[Run],
    dataset: dict[str, dict[str, Any]],
    seed: int = 0,
) -> str:
    """RQ2, yalnız NƏZARƏT qatında — işin ən təmiz ölçüsü.

    Ümumi RQ2 rəqəmi Azərbaycana xas suallarla seyrəlir: orada hər iki model
    uğursuzdur, ona görə aralarındakı fərq kiçilir. Bu cədvəl ölçünü yalnız
    modelin ingiliscə bildiyi faktlarla aparır.

    İNGİLİS sətri təsadüfi əlavə deyil, TƏLƏBDİR: o, "bəlkə qazax modeli sadəcə
    zəifdir?" etirazına cavabdır. İngilis balları statistik olaraq fərqlənmirsə,
    azərbaycanca qalan fərq ümumi qabiliyyətdən gələ bilməz.
    """
    rows: list[list[Any]] = []
    for language in ("en", "az"):
        same = [r for r in runs if r.key.language == language]
        for i, run_a in enumerate(same):
            for run_b in same[i + 1 :]:
                for mode in MODES:
                    if language == "en" and mode is not STRICT:
                        continue  # ingilis tərəfdə rejimlərin təsiri sıfırdır
                    result, ids = _paired(
                        run_a, run_b, dataset, mode, "em", seed, CONTROL_CATEGORIES
                    )
                    if result is None:
                        continue
                    rows.append(
                        [
                            language.upper(),
                            run_label(run_a.key),
                            run_label(run_b.key),
                            mode.name,
                            len(ids),
                            f"{100 * result.mean_a:.1f}%",
                            f"{100 * result.mean_b:.1f}%",
                            f"{100 * result.diff:.1f}pp",
                            result.p_value,
                            "bəli" if result.significant else "xeyr",
                        ]
                    )
    if not rows:
        return "_Nəzarət qatı boşdur._"
    return _table_with_holm(
        ["Dil", "Model A", "Model B", "Rejim", "N", "A EM", "B EM", "Fərq"], rows
    )


def _group_key(record: dict[str, Any], dimension: str) -> str:
    """Kəsim ölçüsü: `category`, `variant` və ya `template`.

    `template` kəsimi ən vacibidir: dataset iki hissədən ibarətdir — universal
    NƏZARƏT faktları (Fransanın paytaxtı; model onları ingiliscə mütləq bilir)
    və AZƏRBAYCANA XAS məzmun (Təzəpir məscidinin memarı). İki qrupdakı AZ/EN
    fərqini müqayisə etmək məqalənin əsas müşahidəsidir: nəzarət qrupunda fərq
    təmiz dil emalı problemidir, AZ məzmununda isə üstünə bilik boşluğu gəlir.
    """
    if dimension == "category":
        return str(record.get("category", "—"))

    marker = "template=" if dimension == "template" else "variant="
    notes = str(record.get("notes", ""))
    return notes.split(marker)[1].split(";")[0] if marker in notes else "—"


def build_breakdown_table(
    runs: Sequence[Run],
    dataset: dict[str, dict[str, Any]],
    dimension: str = "category",
    seed: int = 0,
) -> str:
    """Kateqoriya və ya sual variantı üzrə kəsim.

    Variant kəsimi ayrıca dəyərlidir: eyni faktı fərqli quruluşda soruşduqda bal
    kəskin dəyişirsə, ölçdüyümüz şeyin bir hissəsi bilik yox, qəlibə tanışlıqdır.
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for record_id, record in dataset.items():
        groups[_group_key(record, dimension)].append(record_id)

    header = ["Qrup", "N"] + [str(r.key) for r in runs]
    rows = []
    for group, group_ids in sorted(groups.items()):
        row: list[Any] = [group, len(group_ids)]
        for run in runs:
            ids = sorted(set(group_ids) & run.ids)
            if not ids:
                row.append("—")
                continue
            scores = score_run(run, dataset, STRICT, ids)
            row.append(f"{100 * sum(_column(scores, 'em', ids)) / len(ids):.1f}%")
        rows.append(row)
    return markdown_table(header, rows)


# --------------------------------------------------------------------------
# Xəta taksonomiyası üçün nümunə
# --------------------------------------------------------------------------


def error_rows(
    run: Run,
    dataset: dict[str, dict[str, Any]],
    sample_size: int = 100,
    seed: int = 0,
) -> list[dict[str, Any]]:
    """Səhv cavabların kateqoriya üzrə TƏBƏQƏLƏNDİRİLMİŞ nümunəsi.

    Təbəqələndirmə vacibdir: sadə təsadüfi nümunə ən böyük kateqoriyanı üstün
    göstərir və xəta taksonomiyası əyilir.

    `error_type` sütunu QƏSDƏN boş qalır — RQ3-ün cavabı əl ilə etiketlənməlidir.
    Sütun adları brief-in 6-cı bölməsindəki kateqoriyalara uyğundur.
    """
    ids = sorted(run.ids & set(dataset))
    strict = score_run(run, dataset, STRICT, ids)
    lenient = score_run(run, dataset, LENIENT, ids)

    wrong = [i for i in ids if strict[i]["em"] == 0.0]
    by_category: dict[str, list[str]] = defaultdict(list)
    for record_id in wrong:
        by_category[str(dataset[record_id].get("category", "—"))].append(record_id)

    rng = random.Random(seed)
    per_group = max(1, sample_size // max(1, len(by_category)))
    chosen: list[str] = []
    for group_ids in by_category.values():
        pool = sorted(group_ids)
        rng.shuffle(pool)
        chosen.extend(pool[:per_group])

    # Kvota bütün yerləri doldurmayıbsa, qalanı ümumi hovuzdan tamamlanır.
    if len(chosen) < min(sample_size, len(wrong)):
        remaining = sorted(set(wrong) - set(chosen))
        rng.shuffle(remaining)
        chosen.extend(remaining[: sample_size - len(chosen)])

    chosen = sorted(chosen)[:sample_size]

    return [
        {
            "id": record_id,
            "category": dataset[record_id].get("category", ""),
            "variant": _group_key(dataset[record_id], "variant"),
            "question": dataset[record_id].get(
                "question_az" if run.key.language == "az" else "question_en", ""
            ),
            "gold": gold_answers(dataset[record_id], run.key.language)[0],
            "prediction": run.predictions.get(record_id, ""),
            "raw_response": run.raw.get(record_id, ""),
            "em_lenient": lenient[record_id]["em"],
            "f1_strict": round(strict[record_id]["f1"], 3),
            # Əl ilə doldurulur: diakritika | morfologiya | faktual |
            # format | boş cavab | digər
            "error_type": "",
        }
        for record_id in chosen
    ]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="analyze", description="Xam cavabları cədvəllərə çevirir"
    )
    parser.add_argument("--dataset", type=Path, default=Path("data/az_eval_v0.jsonl"))
    parser.add_argument("--raw-dir", type=Path, default=Path("results/raw_outputs"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--error-sample", type=int, default=100)
    parser.add_argument("--max-answer-words", type=int, default=12)
    args = parser.parse_args(argv)

    dataset = {
        r["id"]: r
        for _, r in load_jsonl(args.dataset)
        if isinstance(r, dict) and isinstance(r.get("id"), str)
    }
    if not dataset:
        print(f"Dataset boşdur: {args.dataset}", file=sys.stderr)
        return 1

    runs = load_runs(args.raw_dir, max_words=args.max_answer_words)
    if not runs:
        print(f"Qaçış tapılmadı: {args.raw_dir}", file=sys.stderr)
        return 1

    print(f"{len(dataset)} sətir, {len(runs)} qaçış\n")
    for run in runs:
        missing = set(dataset) - run.ids
        if missing:
            print(f"  DİQQƏT: {run.key} — {len(missing)} sətir üçün cavab yoxdur")

    tables = {
        "main.md": ("Əsas nəticələr (STRICT)", build_main_table(runs, dataset, args.seed)),
        "modes.md": (
            "Normalizasiya rejimləri — RQ3 dekompozisiyası",
            build_modes_table(runs, dataset, args.seed),
        ),
        "rq1.md": ("RQ1 — AZ vs EN", build_rq1_table(runs, dataset, args.seed)),
        "rq2.md": (
            "RQ2 — modellərarası müqayisə (AZ)",
            build_rq2_table(runs, dataset, "az", args.seed),
        ),
        "control.md": (
            "RQ2 nəzarət qatında (world + science) — ən təmiz ölçü",
            build_control_table(runs, dataset, args.seed),
        ),
        "breakdown.md": (
            "Kateqoriya üzrə kəsim",
            build_breakdown_table(runs, dataset, "category", args.seed)
            + "\n\n### Sual variantı üzrə kəsim\n\n"
            + build_breakdown_table(runs, dataset, "variant", args.seed),
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for filename, (title, table) in tables.items():
        (args.out_dir / filename).write_text(
            f"# {title}\n\n{table}\n", encoding="utf-8"
        )
        print(f"\n## {title}\n\n{table}")

    # Xəta nümunəsi — hər AZ qaçışı üçün ayrıca fayl.
    for run in runs:
        if run.key.language != "az":
            continue
        rows = error_rows(run, dataset, args.error_sample, args.seed)
        if not rows:
            continue
        safe = run.key.model.replace("/", "__").replace(":", "_")
        path = args.out_dir / f"errors__{safe}.csv"
        with open(path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n{len(rows)} səhv cavab -> {path}")
        print("  `error_type` sütununu əl ilə doldur (RQ3).")

    print(f"\nCədvəllər: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
