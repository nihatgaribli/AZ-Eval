"""Çıxışın iki əsas qrafiki.

    python talk/figures.py

12 dəqiqəlik çıxışda əsas nəticə BİR BAXIŞDA görünməlidir. Cədvəl dəqiqdir,
amma oxumaq vaxt aparır və zaldakı adam eyni anda həm oxuya, həm dinləyə
bilmir. Ona görə 7 və 8-ci slaydlar qrafikə çevrilir; dəqiqlik tələb edən
slaydlar (6 və 9) cədvəl olaraq qalır.

RƏNGLƏR sınaqdan keçirilib (dataviz validator, light rejim):
    slot 1 mavi #2a78d6, slot 2 narıncı #eb6834
    CVD ΔE 24.7 (hədəf ≥8), normal görmə ΔE 33.6 (hədəf ≥15) - hamısı PASS.
Rəngi dəyişsən, validatoru yenidən işlət - gözlə qiymətləndirmə.

FON ŞƏFFAFDIR ki, həm PowerPoint (ağ), həm Beamer (açıq boz) fonunda otursun.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


HERE = Path(__file__).resolve().parent

# Təsdiqlənmiş kateqorial palitra + mürəkkəb tokenləri
BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"

plt.rcParams.update(
    {
        "font.family": "Segoe UI",
        "font.size": 13,
        "axes.edgecolor": MUTED,
        "text.color": INK,
        "savefig.transparent": True,
    }
)


def _swatch(color: str):
    """Leqenda üçün açıq rəng nişanı.

    NİYƏ ƏL İLƏ QURULUR: matplotlib leqenda nişanını sütun obyektindən götürür.
    Sütunlar hər hansı səbəbdən dəyişdirilsə (məsələn əvvəlki versiyada
    yuvarlaqlaşdırma üçün gizlədilirdi), leqendada rəng ITIR və kimlik yalnız
    mövqe ilə qalır. Nişanı ayrıca qurmaq bu asılılığı kəsir.
    """
    return plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="none")


def negative_transfer(path: Path) -> None:
    """Qruplaşdırılmış sütun: model × dil.

    NİYƏ MƏHZ BU FORMA: tapıntı tək rəqəm deyil, ASİMMETRİYADIR - ingiliscə
    iki model demək olar eynidir, azərbaycanca isə uçurum var. Qruplaşdırılmış
    sütunda bu asimmetriya bir baxışda görünür; iki ayrı qrafikdə görünməz.
    """
    labels = ["Azerbaijani", "English"]
    base = [16.6, 30.6]
    tuned = [3.1, 29.5]

    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = [0, 1.15]
    width = 0.36
    gap = 0.02  # səthi boşluq - qonşu sütunlar bir-birinə yapışmır

    ax.bar([i - width / 2 - gap for i in x], base, width, color=BLUE, zorder=3)
    ax.bar([i + width / 2 + gap for i in x], tuned, width, color=ORANGE, zorder=3)

    # Birbaşa etiketlər: cəmi dörd sütun var, hamısını etiketləmək olar.
    for positions, values in (
        ([i - width / 2 - gap for i in x], base),
        ([i + width / 2 + gap for i in x], tuned),
    ):
        for pos, value in zip(positions, values):
            ax.text(pos, value + 0.9, f"{value}%", ha="center", va="bottom",
                    fontsize=14, fontweight="bold", color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=15, color=INK)
    ax.set_ylabel("Exact match (strict)", fontsize=12, color=INK_SOFT)
    ax.set_ylim(0, 36)
    ax.set_yticks([0, 10, 20, 30])
    ax.tick_params(axis="y", colors=MUTED, labelsize=11)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)

    ax.legend(
        [_swatch(BLUE), _swatch(ORANGE)],
        ["Qwen3-VL-4B-Instruct  (base)", "Qolda-AVL-5B  (Kazakh-tuned)"],
        frameon=False, fontsize=12, loc="upper left", labelcolor=INK_SOFT,
    )

    # Tapıntını qrafikin üstündə bir cümlə ilə göstər, dinləyici izahı
    # gözləmədən nəyə baxdığını bilsin.
    ax.annotate(
        "same in English  ·  3× apart in Azerbaijani",
        xy=(0.5, 1.04), xycoords="axes fraction", ha="center",
        fontsize=13, color=INK_SOFT,
    )

    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def script_counts(path: Path) -> None:
    """Yığılmış üfüqi sütun: 356 cavabın əlifba bölgüsü.

    NİYƏ YIĞILMIŞ: hər sətir eyni bütövdür (356 cavab), ona görə hissə-bütöv
    münasibəti mənalıdır. Dinləyici 326-nın 356-dan nə qədər olduğunu
    hesablamır - görür.
    """
    rows = [
        ("Qolda · Azerbaijani prompt", 326, 30),
        ("Qolda · Latin script demanded", 314, 42),
        ("Base model · same prompt", 1, 355),
        ("Qolda · English prompt", 0, 356),
    ]

    fig, ax = plt.subplots(figsize=(10, 4.2))
    y = list(range(len(rows)))[::-1]
    gap = 2  # cavab sayında 2 vahid - səthi boşluq, seqmentlər yapışmasın

    for position, (_, cyrillic, latin) in zip(y, rows):
        if cyrillic:
            ax.barh(position, cyrillic, color=ORANGE, height=0.52, zorder=3)
        ax.barh(position, latin, left=cyrillic + gap, color=BLUE,
                height=0.52, zorder=3)

    for position, (_, cyrillic, _latin) in zip(y, rows):
        if cyrillic >= 40:
            ax.text(cyrillic / 2, position, str(cyrillic), ha="center",
                    va="center", color="white", fontsize=15, fontweight="bold")
        else:
            ax.text(cyrillic + 8, position, str(cyrillic), ha="left",
                    va="center", color=ORANGE, fontsize=15, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([label for label, _, _ in rows], fontsize=13, color=INK)
    ax.set_xlim(0, 372)
    ax.set_xticks([0, 100, 200, 300, 356])
    ax.set_xticklabels(["0", "100", "200", "300", "356"], fontsize=11)
    ax.tick_params(axis="x", colors=MUTED)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("answers produced, out of 356", fontsize=12, color=INK_SOFT)
    ax.grid(axis="x", color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)

    # İki seriya var, ona görə leqenda MƏCBURİDİR: kimlik yalnız rənglə verilə
    # bilməz. Leqenda oxların XARİCİNDƏ, üstdə yerləşir; `loc="lower right"`
    # onu alt sütunun üstünə salırdı və məlumatı örtürdü.
    ax.legend(
        [_swatch(ORANGE), _swatch(BLUE)],
        ["Cyrillic", "Latin"],
        frameon=False, fontsize=12, ncol=2, labelcolor=INK_SOFT,
        loc="lower left", bbox_to_anchor=(0, 1.01),
    )

    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    targets = [
        (HERE / "fig_negative_transfer.png", negative_transfer),
        (HERE / "fig_script_counts.png", script_counts),
    ]
    for path, builder in targets:
        builder(path)
        print(f"{path.name}  ({path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
