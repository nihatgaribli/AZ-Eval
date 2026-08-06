"""Wikidata-dan paralel AZ/EN sual-cavab qaralamalarının yığılması.

Niyə Wikidata: faktlar (subyekt, xassə, dəyər) üçlüyü kimi saxlanılır və
etiketlər HƏM Azərbaycan, HƏM ingilis dilində mövcuddur. Yəni AZ/EN cütü
tərcümə ilə deyil, konstruksiya ilə alınır — RQ1-in müqayisəsi tərcümə
keyfiyyətindən asılı olmur. Bu, maşın tərcüməsindən keyfiyyətcə fərqli mövqedir.

Çıxan sətirlər QARALAMADIR: `verified_by="pending"`. Yekun datasetə yalnız
`src/review.py` ilə əl yoxlamasından keçdikdən sonra düşür.

--------------------------------------------------------------------------
FİLTRLƏR — niyə hər biri lazımdır

Sadəlövh şablonlaşdırma sınıq benchmark verir. Aşağıdakı filtrlər empirik
olaraq tapılmış üç tələyə qarşıdır:

1. `--max-per-answer` (CAVAB KVOTASI). "Azərbaycanlı şəxs -> doğum yeri"
   sorğusunda nəticələrin böyük əksəriyyəti "Bakı" çıxır. Kvotasız datasetdə
   heç nə bilməyən model 60-70% alır. Bu, ən vacib filtrdir.
2. TƏKDƏYƏRLİLİK. Wikidata-da əhali kimi xassələr illər üzrə bir neçə dəyər
   saxlayır (bir şəhər üçün 5 fərqli rəqəm). Belə subyekt tamamilə atılır —
   birmənalı etalon cavab olmayan sual qiymətləndirməyə yaramır.
3. TARİXİ/LƏĞV OLUNMUŞ obyektlər. Doğum yeri "SSRİ" olan sətirlər faktiki
   olaraq doğrudur, amma müasir modeldən gözlənilən cavab deyil və xəta
   taksonomiyasını çirkləndirir.

Əlavə olaraq: tanınırlıq həddi (sitelink sayı), 1-3 sözlük cavab, mötərizəli
dəqiqləşdirmə etiketlərinin atılması, cavabın subyektlə üst-üstə düşməməsi.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.build_dataset import contains_token_sequence, write_jsonl
from src.metrics import STRICT, normalize, tokenize
from src.morphology import aliases_for, az_capitalize, genitive, locative

__all__ = [
    "FactTemplate",
    "TEMPLATES",
    "SparqlError",
    "run_sparql",
    "harvest_template",
    "apply_filters",
    "to_records",
]

ENDPOINT = "https://query.wikidata.org/sparql"

#: Wikimedia siyasəti aydın User-Agent tələb edir; anonim sorğular bloklanır.
USER_AGENT = (
    "az-eval/0.1 (Azerbaijani LLM evaluation benchmark; academic research) "
    "python-urllib"
)

#: Doğum yeri / yerləşmə cavabı kimi qəbul edilməyən tarixi qurumlar.
BLOCKED_ANSWERS: frozenset[str] = frozenset(
    {
        "ssri", "sovet ittifaqı", "sovet sosialist respublikaları ittifaqı",
        "rusiya imperiyası", "azərbaycan sovet sosialist respublikası",
        "zaqafqaziya sfsr", "rsfsr", "osmanlı imperiyası", "iran",
    }
)


#: İngilis mətnində praktiki olaraq rast gəlinməyən hərflər. İki qəsdən buraxılma:
#:
#: 1. `ö`, `ü`, `ç` YOXDUR — ingilis dilində işlənən alman/fransız alınmalarında
#:    (Zürich, São, façade) qanuni şəkildə görünürlər.
#: 2. Azərbaycan NÖQTƏSİZ BAŞ `I` hərfi YOXDUR, çünki o, ASCII `I` ilə eyni
#:    Unicode koddur (U+0049) — fərqləndirici əlamət ola bilməz. Siyahıya
#:    salınsaydı, tərkibində baş `I` olan bütün ingilis etiketləri atılardı:
#:    India, Italy, Israel, Iran, Iceland. Nöqtəli `İ` (U+0130) isə fərqlidir
#:    və həqiqətən ingilis dilində olmur.
NON_ENGLISH_LETTERS = frozenset("əğışƏĞŞİ")

#: Azərbaycan əlifbasına xas bütün hərflər (eyni etiket yoxlaması üçün).
#: Baş `I` burada da yoxdur — eyni səbəbdən.
AZ_LETTERS = frozenset("əğıöşüçƏĞİÖŞÜÇ")


class SparqlError(RuntimeError):
    """SPARQL sorğusu təkrarlardan sonra da uğursuz oldu."""


def _is_really_english(label_en: str, label_az: str) -> bool:
    """İngilis etiketinin həqiqətən ingilis olub-olmadığını yoxlayır.

    Wikidata-da ingilis etiketi tez-tez sadəcə yerli adın kopyasıdır:
    "Diana Hacıyeva", "Aşağı Tala", "Şıxmahmud". Belə sətir RQ1-i zədələyir —
    ingilis şərti azərbaycanca mətnlə çirklənirsə, AZ/EN müqayisəsi artıq iki
    dilin müqayisəsi olmur.

    İki əlamət:
      1. Etiketdə `ə`, `ğ`, `ı`, `ş` var — bunlar ingilis mətnində olmur.
      2. Etiket AZ variantı ilə eynidir VƏ Azərbaycan hərfi daşıyır — yəni
         tərcümə edilməyib, sadəcə köçürülüb. ("Zürich" birinci şərtdən keçir,
         ikincidən də keçir, çünki AZ variantı "Sürix"dir.)
    """
    if NON_ENGLISH_LETTERS & set(label_en):
        return False
    return not (label_en == label_az and AZ_LETTERS & set(label_en))


# --------------------------------------------------------------------------
# Şablon reyestri
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class QuestionVariant:
    """Eyni faktı soruşan bir cüt sual — AZ və EN.

    AZ mətnində üç yer tutucu işlənə bilər:
        {subject}      adlıq hal    — "Fransa"
        {subject_gen}  yiyəlik hal  — "Fransanın"
        {subject_loc}  yerlik hal   — "Fransada"
    EN mətnində yalnız `{subject}`.

    Cütlük TƏLƏBDİR: AZ variantı ilə EN variantı eyni quruluşda olmalıdır.
    Əks halda AZ tərəf çətin, EN tərəf asan qəlibə düşür və ölçülən fərqin bir
    hissəsi dildən yox, sual quruluşundan gəlir — RQ1 çirklənir.
    """

    az: str
    en: str


@dataclass(frozen=True)
class FactTemplate:
    """Bir fakt tipi: SPARQL sorğusu + bir neçə sual quruluşu.

    SPARQL sorğusu bu dəyişənləri qaytarmalıdır:
        ?subj ?subjAz ?subjEn ?ans ?ansAz ?ansEn ?links
    `?links` — subyektin sitelink sayı (tanınırlıq ölçüsü).

    Niyə bir yox, bir neçə variant: bütün suallar eyni qəlibdə olsa, benchmark
    modelin biliyini yox, həmin bir qəlibə tanışlığını ölçür. Variantlar
    sətirlərə növbə ilə paylanır (bax `to_records`), ona görə hər variant
    tanınırlıq spektrinin hər yerindən subyekt alır.
    """

    name: str
    category: str
    sparql: str
    variants: tuple[QuestionVariant, ...]
    difficulty: str = "medium"

    def render(
        self, subject_az: str, subject_en: str, variant_index: int = 0
    ) -> tuple[str, str, int]:
        """Qaytarır: (AZ sual, EN sual, işlənən variantın nömrəsi)."""
        index = variant_index % len(self.variants)
        variant = self.variants[index]
        forms = {
            "subject": subject_az,
            "subject_gen": genitive(subject_az),
            "subject_loc": locative(subject_az),
        }
        english = variant.en.format(subject=subject_en)
        # Bəzi variantlarda subyekt cümlənin əvvəlindədir ("{subject} is
        # represented by..."), Wikidata etiketi isə kiçik hərflə gələ bilər
        # ("silver"). İngilis üçün adi `upper()` kifayətdir — nöqtəli `i`
        # problemi yalnız Azərbaycan mətnində var.
        english = english[:1].upper() + english[1:]
        return (
            az_capitalize(variant.az.format(**forms)),
            english,
            index,
        )


def _query(
    body: str,
    limit: int,
    literal_answer: bool = False,
    single_value_filter: str = "",
    min_sitelinks: int = 8,
) -> str:
    """Şablon sorğusunun ümumi karkası.

    `literal_answer=True` — cavab Wikidata obyekti deyil, hərfi dəyərdir
    (kimyəvi simvol "Fe", il "1923"). Belə dəyərlərin dil etiketi olmur, ona
    görə cavaba `lang(...)="az"` filtri TƏTBİQ EDİLMİR — edilsəydi, sorğu
    həmişə boş qayıdardı, çünki etiketsiz literal üçün `lang()` boş sətir verir.

    `single_value_filter` — TƏKDƏYƏRLİLİK yoxlaması, SPARQL səviyyəsində.
    Bunu Python tərəfdə etmək YETƏRLİ DEYİL: orada yalnız gətirilən pəncərə
    görünür, ona görə subyektin digər dəyərləri `LIMIT`-dən kənarda qalsa,
    çoxdəyərli subyekt təkdəyərli kimi keçir. Real nümunə: ABŞ-ın `P37`
    (rəsmi dil) xassəsi çoxdəyərlidir, amma pəncərəyə yalnız biri düşdü və
    "ABŞ-ın rəsmi dili -> ispan dili" kimi FAKTİKİ OLARAQ YANLIŞ etalon
    yarandı. `FILTER NOT EXISTS` bütün qrafa baxdığı üçün bu boşluğu bağlayır.
    """
    answer_filter = (
        "" if literal_answer else '\n  FILTER(lang(?ansAz)="az") FILTER(lang(?ansEn)="en")'
    )
    single_value = f"\n{single_value_filter}" if single_value_filter else ""
    return f"""SELECT ?subj ?subjAz ?subjEn ?ans ?ansAz ?ansEn ?links WHERE {{
{body}{single_value}
  ?subj wikibase:sitelinks ?links .
  FILTER(?links >= {min_sitelinks})
  FILTER(lang(?subjAz)="az") FILTER(lang(?subjEn)="en"){answer_filter}
}} LIMIT {limit}"""


def _only_one(prop: str) -> str:
    """`?subj` üçün `prop` xassəsinin yeganə dəyəri `?ans` olsun."""
    return f"  FILTER NOT EXISTS {{ ?subj wdt:{prop} ?otherValue . FILTER(?otherValue != ?ans) }}"


#: Şablonlar qəsdən CAVAB MÜXTƏLİFLİYİ yüksək olanlara meyllidir. Doğum yeri
#: tipli şablonlar ("hamı Bakıda doğulub") kvota ilə cilovlanır; paytaxt, il və
#: kimyəvi simvol tipli şablonlarda isə skew təbii olaraq aşağıdır.
TEMPLATES: tuple[FactTemplate, ...] = (
    FactTemplate(
        name="country_capital",
        category="geography",
        sparql=_query(
            """  ?subj wdt:P31 wd:Q6256 ; wdt:P36 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            600,
            single_value_filter=_only_one("P36"),
        ),
        variants=(
            QuestionVariant(
                "{subject_gen} paytaxtı hansı şəhərdir?",
                "What is the capital city of {subject}?",
            ),
            QuestionVariant(
                "Hansı şəhər {subject_gen} paytaxtıdır?",
                "Which city is the capital of {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} paytaxtının adı nədir?",
                "What is the name of the capital of {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} paytaxtını yaz.",
                "Name the capital city of {subject}.",
            ),
        ),
        difficulty="easy",
    ),
    FactTemplate(
        name="country_currency",
        category="geography",
        sparql=_query(
            """  ?subj wdt:P31 wd:Q6256 ; wdt:P38 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            600,
            single_value_filter=_only_one("P38"),
        ),
        variants=(
            QuestionVariant(
                "{subject_gen} pul vahidi nədir?",
                "What is the currency of {subject}?",
            ),
            QuestionVariant(
                "{subject_loc} hansı pul vahidi işlənir?",
                "Which currency is used in {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} rəsmi valyutası necə adlanır?",
                "What is the official currency of {subject} called?",
            ),
            QuestionVariant(
                "{subject_gen} pul vahidinin adını yaz.",
                "Name the currency of {subject}.",
            ),
        ),
    ),
    FactTemplate(
        name="element_symbol",
        category="science",
        sparql=_query(
            """  ?subj wdt:P31 wd:Q11344 ; wdt:P246 ?symbol ; rdfs:label ?subjAz, ?subjEn .
  BIND(?symbol AS ?ansAz) BIND(?symbol AS ?ansEn) BIND(?subj AS ?ans)""",
            300,
            literal_answer=True,
            single_value_filter=(
                "  FILTER NOT EXISTS { ?subj wdt:P246 ?otherSymbol . "
                "FILTER(?otherSymbol != ?symbol) }"
            ),
        ),
        variants=(
            QuestionVariant(
                "{subject} elementinin kimyəvi simvolu nədir?",
                "What is the chemical symbol of {subject}?",
            ),
            QuestionVariant(
                "Kimyada {subject} hansı simvolla işarə olunur?",
                "In chemistry, which symbol represents {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} kimyəvi işarəsi nədir?",
                "{subject} is represented by which chemical symbol?",
            ),
            QuestionVariant(
                "{subject} elementinin simvolunu yaz.",
                "Write the chemical symbol of {subject}.",
            ),
        ),
    ),
    FactTemplate(
        name="person_birth_year",
        category="history",
        sparql=_query(
            """  ?subj wdt:P27 wd:Q227 ; wdt:P569 ?dob ; rdfs:label ?subjAz, ?subjEn .
  BIND(STR(YEAR(?dob)) AS ?ansAz) BIND(?ansAz AS ?ansEn) BIND(?subj AS ?ans)""",
            600,
            literal_answer=True,
            single_value_filter=(
                "  FILTER NOT EXISTS { ?subj wdt:P569 ?otherDob . "
                "FILTER(YEAR(?otherDob) != YEAR(?dob)) }"
            ),
        ),
        variants=(
            QuestionVariant(
                "{subject} hansı ildə anadan olub?",
                "In which year was {subject} born?",
            ),
            QuestionVariant(
                "{subject} neçənci ildə doğulub?",
                "What year was {subject} born?",
            ),
            QuestionVariant(
                "{subject_gen} doğum ili hansıdır?",
                "What is {subject}'s year of birth?",
            ),
            QuestionVariant(
                "{subject_gen} anadan olduğu ili yaz.",
                "Give the birth year of {subject}.",
            ),
        ),
    ),
    FactTemplate(
        name="person_birthplace",
        category="culture",
        sparql=_query(
            """  ?subj wdt:P27 wd:Q227 ; wdt:P19 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            800,
            single_value_filter=_only_one("P19"),
        ),
        variants=(
            QuestionVariant(
                "{subject} harada anadan olub?",
                "Where was {subject} born?",
            ),
            QuestionVariant(
                "{subject_gen} doğulduğu yer haradır?",
                "What is {subject}'s birthplace?",
            ),
            QuestionVariant(
                "{subject} hansı yaşayış məntəqəsində dünyaya gəlib?",
                "In which settlement was {subject} born?",
            ),
            QuestionVariant(
                "{subject_gen} doğum yerini yaz.",
                "Name the birthplace of {subject}.",
            ),
        ),
    ),
    # Bu iki şablon QƏSDƏN cavabı AZƏRBAYCAN SÖZÜ olan faktları hədəfləyir.
    #
    # Səbəb: yuxarıdakı şablonların cavabları əsasən beynəlxalq yazılışlardır
    # (Paris, Au, 1961) və Azərbaycan diakritiki daşımır. Belə datasetdə RQ3-ün
    # diakritika ölçüsü ölçülə bilmir — MORPH->LENIENT fərqi həmişə sıfır çıxır,
    # çünki qatlanacaq hərf yoxdur. Peşə adları ("müğənni", "siyasətçi",
    # "televiziya aparıcısı") və dil adları ("fransız dili") bu boşluğu doldurur.
    FactTemplate(
        name="person_occupation",
        category="culture",
        sparql=_query(
            """  ?subj wdt:P27 wd:Q227 ; wdt:P106 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            900,
            single_value_filter=_only_one("P106"),
        ),
        variants=(
            QuestionVariant(
                "{subject_gen} peşəsi nədir?",
                "What is {subject}'s occupation?",
            ),
            QuestionVariant(
                "{subject} hansı peşə ilə tanınır?",
                "Which occupation is {subject} known for?",
            ),
            QuestionVariant(
                "{subject_gen} əsas fəaliyyət sahəsi nədir?",
                "What is {subject}'s main field of activity?",
            ),
            QuestionVariant(
                "{subject_gen} peşəsini yaz.",
                "Name the occupation of {subject}.",
            ),
        ),
    ),
    FactTemplate(
        name="country_official_language",
        category="language",
        sparql=_query(
            """  ?subj wdt:P31 wd:Q6256 ; wdt:P37 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            500,
            single_value_filter=_only_one("P37"),
        ),
        variants=(
            QuestionVariant(
                "{subject_gen} rəsmi dili hansıdır?",
                "What is the official language of {subject}?",
            ),
            QuestionVariant(
                "{subject_loc} hansı dil rəsmi dildir?",
                "Which language is official in {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} dövlət dili necə adlanır?",
                "What is the state language of {subject} called?",
            ),
            QuestionVariant(
                "{subject_gen} rəsmi dilini yaz.",
                "Name the official language of {subject}.",
            ),
        ),
    ),
    FactTemplate(
        name="language_writing_system",
        category="language",
        sparql=_query(
            """  ?subj wdt:P31 wd:Q34770 ; wdt:P282 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            400,
            single_value_filter=_only_one("P282"),
        ),
        # "əlifba" deyil, "yazı sistemi" — Çin və Khmer yazısı əlifba deyil,
        # ona görə "hansı əlifba" sualı bu sətirlərdə faktiki olaraq yanlışdır.
        variants=(
            QuestionVariant(
                "{subject} hansı yazı sistemi ilə yazılır?",
                "Which writing system is {subject} written in?",
            ),
            QuestionVariant(
                "{subject} üçün hansı yazı sistemindən istifadə olunur?",
                "Which writing system is used for {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} yazı sistemi hansıdır?",
                "What is the writing system of {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} yazı sistemini yaz.",
                "Name the writing system used for {subject}.",
            ),
        ),
    ),
    # ----------------------------------------------------------------------
    # AZƏRBAYCANA XAS MƏZMUN
    #
    # Yuxarıdakı şablonlar universal faktları soruşur (Fransanın paytaxtı,
    # kimyəvi simvollar). Onların işi RQ1 üçün NƏZARƏT qrupu olmaqdır: model bu
    # faktları ingiliscə mütləq bilir, ona görə azərbaycanca uğursuzluq bilik
    # çatışmazlığı yox, dil emalı problemidir.
    #
    # Amma nəzarət qrupu tək başına dataset ola bilməz. Üç səbəb:
    #   1. Tavan effekti — "Fransanın paytaxtı" bütün modellər üçün asandır,
    #      ayırdetmə gücü qalmır.
    #   2. ISSAI-nin metodologiyası genişlənmir — onların `kz-history-queries`
    #      dəsti QAZAX tarixi haqqındadır; ekvivalent AZ məzmunu tələb edir.
    #   3. RQ2 ölçülməz qalır — qazax fine-tune-unun Paris haqqında suala təsiri
    #      yoxdur. Transfer yalnız regional/türk məzmununda görünə bilər.
    #
    # Aşağıdakı şablonlar məhz bu boşluğu doldurur: memarlıq irsi, çay şəbəkəsi,
    # milli incəsənət, xalq musiqi alətləri.
    FactTemplate(
        name="monument_architect",
        category="history",
        sparql=_query(
            """  ?subj wdt:P17 wd:Q227 ; wdt:P84 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            600,
            single_value_filter=_only_one("P84"),
        ),
        variants=(
            QuestionVariant(
                "{subject_gen} memarı kimdir?",
                "Who is the architect of {subject}?",
            ),
            QuestionVariant(
                "{subject} kimin layihəsidir?",
                "Whose design is {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} layihəsini kim hazırlayıb?",
                "Who designed {subject}?",
            ),
            QuestionVariant(
                "{subject_gen} memarının adını yaz.",
                "Name the architect of {subject}.",
            ),
        ),
    ),
    FactTemplate(
        name="river_mouth",
        category="geography",
        sparql=_query(
            """  ?subj wdt:P17 wd:Q227 ; wdt:P403 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            500,
            single_value_filter=_only_one("P403"),
        ),
        variants=(
            QuestionVariant(
                "{subject} hara tökülür?",
                "Where does {subject} flow into?",
            ),
            QuestionVariant(
                "{subject_gen} mənsəbi haradır?",
                "What is the mouth of {subject}?",
            ),
            QuestionVariant(
                "{subject} hansı su hövzəsinə qovuşur?",
                "Which body of water does {subject} join?",
            ),
            QuestionVariant(
                "{subject_gen} töküldüyü yeri yaz.",
                "Name where {subject} flows into.",
            ),
        ),
    ),
    FactTemplate(
        name="artwork_creator",
        category="culture",
        sparql=_query(
            """  ?subj wdt:P170 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans wdt:P27 wd:Q227 ; rdfs:label ?ansAz, ?ansEn .""",
            600,
            single_value_filter=_only_one("P170"),
            # Milli incəsənət əsərləri nadir hallarda 8 sitelink toplayır;
            # ümumi hədd bu şablonu tamamilə boşaldırdı.
            min_sitelinks=2,
        ),
        variants=(
            QuestionVariant(
                "«{subject}» əsərinin müəllifi kimdir?",
                "Who is the author of \"{subject}\"?",
            ),
            QuestionVariant(
                "«{subject}» əsərini kim yaradıb?",
                "Who created \"{subject}\"?",
            ),
            QuestionVariant(
                "«{subject}» kimin əsəridir?",
                "Whose work is \"{subject}\"?",
            ),
            QuestionVariant(
                "«{subject}» əsərinin müəllifini yaz.",
                "Name the author of \"{subject}\".",
            ),
        ),
    ),
    FactTemplate(
        name="musician_instrument",
        category="culture",
        sparql=_query(
            """  ?subj wdt:P27 wd:Q227 ; wdt:P1303 ?ans ; rdfs:label ?subjAz, ?subjEn .
  ?ans rdfs:label ?ansAz, ?ansEn .""",
            700,
            single_value_filter=_only_one("P1303"),
        ),
        variants=(
            QuestionVariant(
                "{subject} hansı musiqi alətində ifa edir?",
                "Which musical instrument does {subject} play?",
            ),
            QuestionVariant(
                "{subject_gen} ifa etdiyi alət hansıdır?",
                "What instrument does {subject} perform on?",
            ),
            QuestionVariant(
                "{subject} hansı alətin ifaçısıdır?",
                "{subject} is a performer of which instrument?",
            ),
            QuestionVariant(
                "{subject_gen} musiqi alətini yaz.",
                "Name the instrument {subject} plays.",
            ),
        ),
    ),
)


# --------------------------------------------------------------------------
# Şəbəkə
# --------------------------------------------------------------------------


def run_sparql(query: str, retries: int = 4, timeout: int = 90) -> list[dict[str, Any]]:
    """SPARQL sorğusunu icra edir, 502/429 hallarında eksponensial gözləyir.

    Wikidata endpoint-i ağır sorğularda müntəzəm olaraq 502 qaytarır — bu,
    sorğunun səhv olduğu demək deyil, sadəcə vaxt limitinə dəyməsidir.
    """
    url = f"{ENDPOINT}?format=json&query={urllib.parse.quote(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)["results"]["bindings"]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries - 1:
                delay = 2 ** (attempt + 1)
                print(f"    sorğu uğursuz ({exc}); {delay}s sonra təkrar...", flush=True)
                time.sleep(delay)

    raise SparqlError(f"{retries} cəhddən sonra uğursuz: {last_error}")


# --------------------------------------------------------------------------
# Filtrlər
# --------------------------------------------------------------------------


@dataclass
class FilterStats:
    """Hansı filtrin neçə sətri atdığı — hesabatda verilməlidir."""

    fetched: int = 0
    multi_valued: int = 0
    blocked_answer: int = 0
    bad_label: int = 0
    en_label_not_english: int = 0
    answer_too_long: int = 0
    answer_equals_subject: int = 0
    answer_inside_subject: int = 0
    over_quota: int = 0
    kept: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "gətirildi": self.fetched,
            "çoxdəyərli_subyekt": self.multi_valued,
            "bloklanmış_cavab": self.blocked_answer,
            "yararsız_etiket": self.bad_label,
            "EN_ingilis_deyil": self.en_label_not_english,
            "cavab_çox_uzun": self.answer_too_long,
            "cavab=subyekt": self.answer_equals_subject,
            "cavab_sualda": self.answer_inside_subject,
            "kvotadan_kənar": self.over_quota,
            "saxlanıldı": self.kept,
        }


def _value(binding: dict[str, Any], key: str) -> str:
    return binding.get(key, {}).get("value", "").strip()


def _label_is_usable(label: str) -> bool:
    """Mötərizəli dəqiqləşdirmə, boş və ya Q-id şəklində etiketlər yaramır."""
    if not label or "(" in label or ")" in label:
        return False
    if label.startswith("Q") and label[1:].isdigit():
        return False
    return len(label) <= 60


def apply_filters(
    bindings: Sequence[dict[str, Any]],
    max_per_answer: int = 3,
    max_answer_words: int = 3,
) -> tuple[list[dict[str, Any]], FilterStats]:
    """Xam SPARQL nəticələrini süzgəcdən keçirir.

    Ardıcıllıq vacibdir: əvvəlcə təkdəyərlilik (subyekt səviyyəsində), sonra
    sətir səviyyəli yoxlamalar, ən sonda kvota — kvota keyfiyyətli sətirlər
    arasından seçsin deyə.
    """
    stats = FilterStats(fetched=len(bindings))

    # 1. Təkdəyərlilik: bir subyektin bir neçə fərqli cavabı varsa, atılır.
    by_subject: dict[str, set[str]] = defaultdict(set)
    for binding in bindings:
        by_subject[_value(binding, "subj")].add(_value(binding, "ansAz"))
    ambiguous = {s for s, answers in by_subject.items() if len(answers) > 1}

    candidates: list[dict[str, Any]] = []
    seen_subjects: set[str] = set()

    for binding in bindings:
        subject_uri = _value(binding, "subj")
        if subject_uri in ambiguous:
            stats.multi_valued += 1
            continue
        if subject_uri in seen_subjects:
            continue  # eyni subyektin təkrar sətri
        seen_subjects.add(subject_uri)

        subject_az = _value(binding, "subjAz")
        subject_en = _value(binding, "subjEn")
        answer_az = _value(binding, "ansAz")
        answer_en = _value(binding, "ansEn")

        if not all(map(_label_is_usable, (subject_az, subject_en, answer_az, answer_en))):
            stats.bad_label += 1
            continue
        if not _is_really_english(subject_en, subject_az) or not _is_really_english(
            answer_en, answer_az
        ):
            stats.en_label_not_english += 1
            continue
        if normalize(answer_az, STRICT) in BLOCKED_ANSWERS:
            stats.blocked_answer += 1
            continue
        if len(answer_az.split()) > max_answer_words:
            stats.answer_too_long += 1
            continue
        if normalize(answer_az, STRICT) == normalize(subject_az, STRICT):
            stats.answer_equals_subject += 1
            continue
        # Cavab subyektin adının içində keçirsə, sual bilik tələb etmir:
        # "Astara rayonunun inzibati mərkəzi hansıdır?" -> "Astara". Modelin
        # cavabı sualdan köçürməsi kifayətdir, ona görə sətir ölçmə üçün
        # yararsızdır.
        subject_tokens = tokenize(subject_az, STRICT)
        answer_tokens = tokenize(answer_az, STRICT)
        if answer_tokens and contains_token_sequence(subject_tokens, answer_tokens):
            stats.answer_inside_subject += 1
            continue

        candidates.append(
            {
                "subject_uri": subject_uri,
                "subject_az": subject_az,
                "subject_en": subject_en,
                "answer_az": answer_az,
                "answer_en": answer_en,
                "links": int(_value(binding, "links") or 0),
            }
        )

    # 2. Cavab kvotası — skew-ə qarşı əsas müdafiə.
    # Determinist seçim: tanınırlığa görə azalan, sonra URI-yə görə.
    candidates.sort(key=lambda c: (-c["links"], c["subject_uri"]))
    per_answer: Counter[str] = Counter()
    kept: list[dict[str, Any]] = []

    for candidate in candidates:
        key = normalize(candidate["answer_az"], STRICT)
        if per_answer[key] >= max_per_answer:
            stats.over_quota += 1
            continue
        per_answer[key] += 1
        kept.append(candidate)

    stats.kept = len(kept)
    return kept, stats


def to_records(
    template: FactTemplate,
    candidates: Iterable[dict[str, Any]],
    start_id: int = 1,
) -> list[dict[str, Any]]:
    """Süzülmüş namizədləri dataset sxeminə uyğun sətirlərə çevirir.

    Sual variantları NÖVBƏ İLƏ paylanır (variant = sıra nömrəsi % variant sayı).
    Namizədlər tanınırlığa görə sıralandığı üçün növbə ilə paylama hər variantın
    həm məşhur, həm az tanınan subyektlərdən pay almasını təmin edir — variantla
    çətinlik arasında süni korrelyasiya yaranmır.

    İşlənən variantın nömrəsi `notes` sahəsinə yazılır ki, xəta təhlilində
    "sual quruluşu nəticəyə təsir edirmi?" sualına cavab verilə bilsin.
    """
    records: list[dict[str, Any]] = []
    for offset, candidate in enumerate(candidates):
        question_az, question_en, variant = template.render(
            candidate["subject_az"], candidate["subject_en"], variant_index=offset
        )
        answer = candidate["answer_az"]
        records.append(
            {
                "id": f"az-{start_id + offset:03d}",
                "question_az": question_az,
                "question_en": question_en,
                "answer": answer,
                "answer_en": candidate["answer_en"],
                "answer_aliases": aliases_for(answer),
                "category": template.category,
                "source": candidate["subject_uri"].replace(
                    "http://www.wikidata.org/entity/", "https://www.wikidata.org/wiki/"
                ),
                "difficulty": template.difficulty,
                "provenance": "wikidata-template",
                "verified_by": "pending",
                "notes": f"template={template.name};variant={variant}",
            }
        )
    return records


def harvest_template(
    template: FactTemplate, max_per_answer: int = 3
) -> tuple[list[dict[str, Any]], FilterStats]:
    """Bir şablonu icra edib süzülmüş namizədləri qaytarır."""
    bindings = run_sparql(template.sparql)
    return apply_filters(bindings, max_per_answer=max_per_answer)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="harvest_wikidata",
        description="Wikidata-dan paralel AZ/EN sual qaralamaları yığır",
    )
    parser.add_argument("--out", type=Path, default=Path("data/raw/wikidata.jsonl"))
    parser.add_argument(
        "--templates",
        nargs="*",
        default=None,
        help=f"seçilmiş şablonlar (default: hamısı). Mövcud: {[t.name for t in TEMPLATES]}",
    )
    parser.add_argument(
        "--max-per-answer",
        type=int,
        default=3,
        help="eyni cavab dəyəri üçün maksimum sual sayı (skew müdafiəsi)",
    )
    parser.add_argument(
        "--per-template", type=int, default=25, help="şablon başına saxlanılacaq sətir"
    )
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument(
        "--dry-run", action="store_true", help="fayla yazma, yalnız statistika göstər"
    )
    args = parser.parse_args(argv)

    selected = [t for t in TEMPLATES if not args.templates or t.name in args.templates]
    if not selected:
        print("Uyğun şablon tapılmadı.", file=sys.stderr)
        return 1

    all_records: list[dict[str, Any]] = []
    next_id = args.start_id

    for template in selected:
        print(f"\n== {template.name} ({template.category})")
        try:
            candidates, stats = harvest_template(
                template, max_per_answer=args.max_per_answer
            )
        except SparqlError as exc:
            print(f"   ATLANDI: {exc}", file=sys.stderr)
            continue

        candidates = candidates[: args.per_template]
        records = to_records(template, candidates, start_id=next_id)
        next_id += len(records)
        all_records.extend(records)

        print("   " + "  ".join(f"{k}={v}" for k, v in stats.as_dict().items()))
        print(f"   götürüldü: {len(records)}")
        for record in records[:3]:
            print(f"     · {record['question_az']}  ->  {record['answer']}")

    if not all_records:
        print("\nHeç bir sətir yığılmadı.", file=sys.stderr)
        return 1

    answers = Counter(normalize(r["answer"], STRICT) for r in all_records)
    top_answer, top_count = answers.most_common(1)[0]
    baseline = 100 * top_count / len(all_records)

    print(f"\n{'=' * 60}")
    print(f"Cəmi: {len(all_records)} qaralama sətir")
    print(f"Fərqli cavab: {len(answers)}")
    print(f"Əksəriyyət bazası: {baseline:.1f}%  (ən çox cavab: {top_answer!r})")
    if baseline > 15:
        print("  XƏBƏRDARLIQ: baza yüksəkdir — --max-per-answer azaldılmalıdır.")

    if args.dry_run:
        print("\n(dry-run: fayl yazılmadı)")
        return 0

    write_jsonl(args.out, all_records)
    print(f"\nYazıldı -> {args.out}")
    print(f"Növbəti addım: python -m src.review {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
