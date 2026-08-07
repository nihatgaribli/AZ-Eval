"""analyze.py üçün testlər."""

from __future__ import annotations

import json

import pytest

from src.analyze import (
    Run,
    RunKey,
    build_breakdown_table,
    build_main_table,
    build_modes_table,
    build_rq1_table,
    build_rq2_table,
    error_rows,
    extract_answer,
    gold_answers,
    load_runs,
    majority_baseline,
    markdown_table,
    score_run,
)
from src.metrics import LENIENT, MORPH, STRICT


def record(record_id, answer, answer_en, category="geography", variant="0", **extra):
    return {
        "id": record_id,
        "question_az": f"{record_id} sualı?",
        "question_en": f"{record_id} question?",
        "answer": answer,
        "answer_en": answer_en,
        "answer_aliases": [],
        "category": category,
        "source": "https://example.org",
        "provenance": "wikidata-template",
        "verified_by": "human",
        "notes": f"template=t;variant={variant}",
        **extra,
    }


DATASET = {
    "az-001": record("az-001", "Bakı", "Baku", answer_aliases=["Bakıda"]),
    "az-002": record("az-002", "Gəncə", "Ganja", category="history"),
    "az-003": record("az-003", "Şəki", "Sheki", category="history", variant="1"),
}


def make_run(model, language, predictions):
    return Run(
        key=RunKey(model, language),
        predictions=dict(predictions),
        raw=dict(predictions),
    )


# --------------------------------------------------------------------------
# Cavabın xam mətndən çıxarılması — metrikanı birbaşa dəyişən qat
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Paris", "Paris"),
        ("  Paris  ", "Paris"),
        ("Paris.", "Paris"),
        ("Cavab: Paris", "Paris"),
        ("cavab: Paris", "Paris"),
        ("Answer: Paris", "Paris"),
        ("The answer is Paris", "Paris"),
        ('"Paris"', "Paris"),
        ("«Bakı»", "Bakı"),
    ],
)
def test_extract_answer_strips_prefixes_and_punctuation(raw, expected):
    assert extract_answer(raw) == expected


def test_extract_answer_keeps_only_the_first_line():
    # Modellər cavabı yazıb sonrakı sətirlərdə izahat verir; izahatı saymaq
    # token F1-i süni şəkildə aşağı salardı.
    raw = "Bakı\n\nBakı Azərbaycanın paytaxtı və ən böyük şəhəridir."
    assert extract_answer(raw) == "Bakı"


def test_extract_answer_takes_the_first_sentence_when_too_long():
    raw = (
        "Fransanın paytaxtı Parisdir və bu şəhər ölkənin ən böyük "
        "yaşayış məntəqəsidir. İkinci cümlə."
    )
    result = extract_answer(raw, max_words=8)
    assert result.startswith("Fransanın paytaxtı Parisdir")
    assert "İkinci" not in result


def test_extract_answer_leaves_short_answers_untouched():
    assert extract_answer("Xəzər dənizi") == "Xəzər dənizi"


def test_extract_answer_handles_empty_and_whitespace():
    assert extract_answer("") == ""
    assert extract_answer("   \n  ") == ""
    assert extract_answer(None) == ""


def test_extract_answer_does_not_eat_a_real_answer_starting_with_a():
    # "A" prefiksi kimi görünən, amma əslində cavab olan mətn korlanmamalıdır.
    assert extract_answer("Almaniya") == "Almaniya"
    assert extract_answer("Au") == "Au"


def test_extract_answer_removes_a_closed_think_block():
    # Düşünmə modeli mühakiməni bitirib cavab veribsə, cavab götürülür.
    raw = "<think>\nİstifadəçi paytaxtı soruşur. Fransanın paytaxtı Parisdir.\n</think>\n\nParis"
    assert extract_answer(raw) == "Paris"


def test_extract_answer_treats_a_truncated_think_block_as_no_answer():
    """Kəsilmiş mühakimə = cavab yoxdur, səhv cavab deyil.

    Qwen3 kimi hibrid modellər susmadan düşünmə rejimində işləyir. Qısa cavab
    tapşırığında 24-32 token limiti mühakimənin ortasında bitir və model əsl
    cavaba çatmır. `"<think>"` sətrini cavab kimi saxlamaq xəta taksonomiyasını
    korlayardı — sətir "format" yox, "boş cavab" kateqoriyasına aiddir.
    """
    raw = "<think>\nOkay, the user is asking for the capital of France. I need to"
    assert extract_answer(raw) == ""


def test_extract_answer_handles_uppercase_think_tags():
    assert extract_answer("<THINK>mühakimə</THINK>\nBakı") == "Bakı"


def test_extract_answer_is_applied_identically_to_both_languages():
    # Fərqli tətbiq olunsaydı, ölçülən AZ/EN fərqinin bir hissəsi bu qatdan
    # gələrdi.
    assert extract_answer("Cavab: Bakı") == extract_answer("Answer: Bakı")


# --------------------------------------------------------------------------
# Qaçışların yüklənməsi
# --------------------------------------------------------------------------


def test_load_runs_groups_by_model_and_language(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(r, ensure_ascii=False)
            for r in [
                {"id": "az-001", "model": "m1", "language": "az", "raw_response": "Bakı"},
                {"id": "az-002", "model": "m1", "language": "az", "raw_response": "Gəncə"},
                {"id": "az-001", "model": "m1", "language": "en", "raw_response": "Baku"},
                {"id": "az-001", "model": "m2", "language": "az", "raw_response": "Şəki"},
            ]
        ),
        encoding="utf-8",
    )

    runs = load_runs(tmp_path)
    keys = {str(r.key) for r in runs}
    assert keys == {"m1 [az]", "m1 [en]", "m2 [az]"}
    assert next(r for r in runs if str(r.key) == "m1 [az]").ids == {"az-001", "az-002"}


def test_load_runs_applies_answer_extraction(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text(
        json.dumps(
            {"id": "az-001", "model": "m", "language": "az", "raw_response": "Cavab: Bakı."},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    run = load_runs(tmp_path)[0]
    assert run.predictions["az-001"] == "Bakı"
    assert run.raw["az-001"] == "Cavab: Bakı."   # xam mətn toxunulmaz qalır


def test_load_runs_on_empty_directory(tmp_path):
    assert load_runs(tmp_path) == []


# --------------------------------------------------------------------------
# Etalon cavablar
# --------------------------------------------------------------------------


def test_azerbaijani_golds_include_generated_aliases():
    golds = gold_answers(DATASET["az-001"], "az")
    assert golds == ["Bakı", "Bakıda"]


def test_english_golds_have_no_aliases():
    # İngilis dilində hallanma yoxdur; bu asimmetriya qəsdəndir və ölçülən
    # AZ/EN fərqini əsl fərqin aşağı həddinə çevirir.
    assert gold_answers(DATASET["az-001"], "en") == ["Baku"]


def test_alias_credits_an_inflected_prediction():
    run = make_run("m", "az", {"az-001": "Bakıda"})
    scores = score_run(run, DATASET, STRICT)
    assert scores["az-001"]["em"] == 1.0


# --------------------------------------------------------------------------
# Ballandırma
# --------------------------------------------------------------------------


def test_score_run_covers_every_shared_id():
    run = make_run("m", "az", {"az-001": "Bakı", "az-002": "Gəncə", "az-003": "Şəki"})
    assert set(score_run(run, DATASET, STRICT)) == set(DATASET)


def test_missing_prediction_scores_zero_not_skipped():
    # Cavabı olmayan sətri atmaq balı süni yüksəldərdi.
    run = make_run("m", "az", {"az-001": "Bakı"})
    scores = score_run(run, DATASET, STRICT, ids=list(DATASET))
    assert scores["az-002"]["em"] == 0.0
    assert len(scores) == 3


def test_modes_are_ordered_from_strict_to_lenient():
    run = make_run("m", "az", {"az-002": "Gence"})   # diakritiksiz
    strict = score_run(run, DATASET, STRICT, ["az-002"])["az-002"]["em"]
    lenient = score_run(run, DATASET, LENIENT, ["az-002"])["az-002"]["em"]
    assert strict == 0.0 and lenient == 1.0


# --------------------------------------------------------------------------
# Əksəriyyət bazası
# --------------------------------------------------------------------------


def test_majority_baseline_on_a_balanced_dataset():
    assert majority_baseline(DATASET, list(DATASET), "az") == pytest.approx(1 / 3)


def test_majority_baseline_exposes_a_skewed_dataset():
    skewed = {f"az-{i:03d}": record(f"az-{i:03d}", "Bakı", "Baku") for i in range(1, 9)}
    skewed["az-009"] = record("az-009", "Gəncə", "Ganja")
    assert majority_baseline(skewed, list(skewed), "az") == pytest.approx(8 / 9)


# --------------------------------------------------------------------------
# Cədvəllər
# --------------------------------------------------------------------------


def test_markdown_table_has_a_separator_row():
    text = markdown_table(["A", "B"], [[1, 2], [3, 4]])
    lines = text.splitlines()
    assert lines[0].startswith("| A")
    assert set(lines[1]) <= {"|", "-"}
    assert len(lines) == 4


def test_main_table_lists_every_run_with_a_confidence_interval():
    runs = [
        make_run("m1", "az", {"az-001": "Bakı", "az-002": "səhv", "az-003": "Şəki"}),
        make_run("m1", "en", {"az-001": "Baku", "az-002": "Ganja", "az-003": "Sheki"}),
    ]
    table = build_main_table(runs, DATASET)
    assert "m1" in table and "AZ" in table and "EN" in table
    assert "±" in table                      # çılpaq faiz göstərilmir
    assert "Əksəriyyət bazası" in table


def test_modes_table_decomposes_the_error():
    # "Gence" yalnız LENIENT rejimdə tutulur -> diakritika sütunu artmalıdır.
    run = make_run("m", "az", {"az-001": "Bakı", "az-002": "Gence", "az-003": "Şəki"})
    table = build_modes_table([run], DATASET)
    assert "morfologiya" in table and "diakritika" in table
    assert "+33.3pp" in table


def test_rq1_table_reports_the_paired_gap():
    runs = [
        make_run("m", "az", {"az-001": "səhv", "az-002": "səhv", "az-003": "Şəki"}),
        make_run("m", "en", {"az-001": "Baku", "az-002": "Ganja", "az-003": "Sheki"}),
    ]
    table = build_rq1_table(runs, DATASET)
    assert "Fərq" in table and "95% CI" in table and "p" in table
    assert "strict" in table and "lenient" in table


def test_rq1_table_needs_both_languages():
    table = build_rq1_table([make_run("m", "az", {"az-001": "Bakı"})], DATASET)
    assert "yoxdur" in table


def test_rq2_table_compares_models_within_one_language():
    runs = [
        make_run("qolda", "az", {"az-001": "Bakı", "az-002": "səhv"}),
        make_run("qwen", "az", {"az-001": "Bakı", "az-002": "Gəncə"}),
    ]
    table = build_rq2_table(runs, DATASET, "az")
    assert "qolda" in table and "qwen" in table


def test_rq2_table_needs_two_models():
    table = build_rq2_table([make_run("m", "az", {"az-001": "Bakı"})], DATASET, "az")
    assert "iki model" in table


def test_breakdown_by_category():
    run = make_run("m", "az", {"az-001": "Bakı", "az-002": "səhv", "az-003": "Şəki"})
    table = build_breakdown_table([run], DATASET, "category")
    assert "geography" in table and "history" in table


def test_breakdown_by_question_variant():
    # Eyni faktı fərqli quruluşda soruşduqda bal kəskin dəyişirsə, ölçdüyümüz
    # şeyin bir hissəsi bilik yox, qəlibə tanışlıqdır.
    run = make_run("m", "az", {"az-001": "Bakı", "az-002": "Gəncə", "az-003": "səhv"})
    table = build_breakdown_table([run], DATASET, "variant")
    lines = [ln for ln in table.splitlines() if ln.startswith("| 0") or ln.startswith("| 1")]
    assert len(lines) == 2


# --------------------------------------------------------------------------
# Xəta nümunəsi
# --------------------------------------------------------------------------


def test_error_rows_contain_only_wrong_answers():
    run = make_run("m", "az", {"az-001": "Bakı", "az-002": "səhv", "az-003": "səhv"})
    rows = error_rows(run, DATASET)
    assert {r["id"] for r in rows} == {"az-002", "az-003"}


def test_error_rows_leave_the_label_column_empty():
    run = make_run("m", "az", {"az-001": "səhv", "az-002": "səhv", "az-003": "səhv"})
    for row in error_rows(run, DATASET):
        assert row["error_type"] == ""          # RQ3 əl ilə etiketlənir
        assert row["gold"] and row["question"]
        assert "raw_response" in row


def test_error_rows_keep_the_lenient_score_for_diagnosis():
    # Diakritika səbəbli səhvi ayırd etmək üçün LENIENT balı lazımdır.
    run = make_run("m", "az", {"az-002": "Gence"})
    row = error_rows(run, DATASET)[0]
    assert row["em_lenient"] == 1.0            # yalnız diakritika fərqi


def test_error_sample_is_stratified_across_categories():
    dataset = {}
    for i in range(1, 41):
        category = "geography" if i <= 30 else "history"
        dataset[f"az-{i:03d}"] = record(f"az-{i:03d}", f"cavab{i}", f"answer{i}", category)
    run = make_run("m", "az", {k: "səhv" for k in dataset})

    rows = error_rows(run, dataset, sample_size=10, seed=0)
    counts = {"geography": 0, "history": 0}
    for row in rows:
        counts[row["category"]] += 1
    # Sadə təsadüfi nümunə ~7/3 verərdi; təbəqələndirmə balanslaşdırır.
    assert counts["history"] >= 4


def test_error_sample_is_reproducible():
    dataset = {
        f"az-{i:03d}": record(f"az-{i:03d}", f"cavab{i}", f"answer{i}")
        for i in range(1, 31)
    }
    run = make_run("m", "az", {k: "səhv" for k in dataset})
    a = [r["id"] for r in error_rows(run, dataset, 10, seed=5)]
    b = [r["id"] for r in error_rows(run, dataset, 10, seed=5)]
    assert a == b


def test_error_sample_respects_the_size_limit():
    dataset = {
        f"az-{i:03d}": record(f"az-{i:03d}", f"cavab{i}", f"answer{i}")
        for i in range(1, 51)
    }
    run = make_run("m", "az", {k: "səhv" for k in dataset})
    assert len(error_rows(run, dataset, sample_size=12, seed=0)) == 12


def test_error_rows_empty_when_everything_is_correct():
    run = make_run("m", "az", {"az-001": "Bakı", "az-002": "Gəncə", "az-003": "Şəki"})
    assert error_rows(run, DATASET) == []


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("**Berlin**", "Berlin"),
        ("*Paris*", "Paris"),
        ("`Au`", "Au"),
        ("__Bakı__", "Bakı"),
    ],
)
def test_extract_answer_strips_markdown_emphasis(raw, expected):
    # Modellər cavabı tez-tez qalın yazır; ulduzlar normalizasiyada silinmir
    # və exact match-i sındırır.
    assert extract_answer(raw) == expected


def test_breakdown_by_template_separates_control_from_local_content():
    """Datasetin iki hissəsi ayrıca ölçülə bilməlidir.

    Universal nəzarət faktlarında (Fransanın paytaxtı) AZ/EN fərqi təmiz dil
    emalı problemidir; Azərbaycana xas məzmunda üstünə bilik boşluğu gəlir.
    İki rəqəmin müqayisəsi məqalənin əsas müşahidəsidir.
    """
    dataset = {
        "az-001": record("az-001", "Paris", "Paris", notes="template=country_capital;variant=0"),
        "az-002": record("az-002", "Kür", "Kura", notes="template=river_mouth;variant=0"),
    }
    run = make_run("m", "az", {"az-001": "Paris", "az-002": "səhv"})
    table = build_breakdown_table([run], dataset, "template")
    assert "country_capital" in table and "river_mouth" in table


def test_prompt_style_separates_runs_of_the_same_model(tmp_path):
    """Eyni modelin iki promptla qaçışı BİR qaçış kimi birləşməməlidir.

    Birləşsəydi, əlifba nəzarəti mənasını itirərdi: nəzarət qaçışının cavabları
    əsas qaçışın cavabları ilə qarışardı.
    """
    path = tmp_path / "run.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(r, ensure_ascii=False)
            for r in [
                {"id": "az-001", "model": "m", "language": "az",
                 "prompt_style": "default", "raw_response": "Париж"},
                {"id": "az-001", "model": "m", "language": "az",
                 "prompt_style": "script", "raw_response": "Paris"},
            ]
        ),
        encoding="utf-8",
    )
    runs = load_runs(tmp_path)
    assert len(runs) == 2
    assert {str(r.key) for r in runs} == {"m [az]", "m (script) [az]"}


def test_tables_label_the_prompt_style():
    from src.analyze import run_label

    assert run_label(RunKey("m", "az")) == "m"
    assert run_label(RunKey("m", "az", "script")) == "m (script)"


def test_rq1_keeps_prompt_styles_apart():
    """Eyni model, iki prompt — RQ1 cədvəlində iki ayrı sətir olmalıdır.

    Yalnız modelə görə qruplaşdırsaq, nəzarət qaçışı əsas qaçışı səssizcə əvəz
    edər və cədvəl yanlış cütləri müqayisə edərdi.
    """
    runs = [
        make_run("m", "az", {"az-001": "Bakı"}),
        make_run("m", "en", {"az-001": "Baku"}),
        Run(key=RunKey("m", "az", "script"), predictions={"az-001": "səhv"}, raw={}),
        Run(key=RunKey("m", "en", "script"), predictions={"az-001": "Baku"}, raw={}),
    ]
    table = build_rq1_table(runs, DATASET)
    assert "m (script)" in table
    assert len([ln for ln in table.splitlines() if ln.startswith("| m ")]) > 0


def test_rq2_labels_the_prompt_style_too():
    """RQ2 cədvəlində nəzarət qaçışı ayrıca adlanmalıdır.

    Adlanmasa, cədvəldə iki eyni adlı, fərqli p qiymətli sətir cütü görünür və
    oxucu hansının nəzarət qaçışı olduğunu bilmir.
    """
    runs = [
        make_run("a", "az", {"az-001": "Bakı"}),
        Run(key=RunKey("b", "az", "script"), predictions={"az-001": "səhv"}, raw={}),
    ]
    table = build_rq2_table(runs, DATASET, "az")
    assert "b (script)" in table


@pytest.mark.parametrize(
    ("answer_az", "answer_en", "should_accept"),
    [
        ("futbolçu", "association football player", "player"),
        ("Şimalda", "In the North", "North"),
        ("Armududa", "In armudu glass", "armudu"),
    ],
)
def test_english_golds_accept_their_head_words_when_longer(answer_az, answer_en, should_accept):
    """Etiket konvensiyası asimmetriyası hər iki istiqamətdə tutulmalıdır.

    AZ tərəfin uzun olduğu hal datasetdə alias ilə həll olunur; burada tərsi —
    ingilis etalonu uzundursa, ayrı-ayrı sözləri də qəbul edilir. Əks halda
    ölçülən fərqin bir hissəsi dildən yox, konvensiyadan gələr.

    MƏHDUDİYYƏT: bölmə yalnız MÖVCUD sözləri verir, yeni söz düzəltmir. Model
    "association football player" əvəzinə "footballer" desə, bal almır — bu,
    morfoloji törəmədir və qayda əsaslı bölmə onu tuta bilmir.
    """
    row = {"answer": answer_az, "answer_en": answer_en, "answer_aliases": []}
    assert should_accept in gold_answers(row, "en")


def test_english_head_word_split_does_not_invent_derived_forms():
    # Sənədləşdirilmiş məhdudiyyət: "footballer" tutulmur.
    row = {"answer": "futbolçu", "answer_en": "association football player",
           "answer_aliases": []}
    assert "footballer" not in gold_answers(row, "en")


def test_english_gold_stays_single_when_not_longer():
    row = {"answer": "Bakı", "answer_en": "Baku", "answer_aliases": []}
    assert gold_answers(row, "en") == ["Baku"]


def test_english_head_words_do_not_leak_into_azerbaijani():
    row = {"answer": "futbolçu", "answer_en": "association football player",
           "answer_aliases": ["futbolçunun"]}
    assert gold_answers(row, "az") == ["futbolçu", "futbolçunun"]
