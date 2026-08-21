"""Üfüqi sxem: AZ-Eval insanla dil modeli arasında harada durur.

    python talk/story.py

ÖLÇÜ 1920x1080 (16:9). Üfüqi format həm Instagram paylaşımı, həm LinkedIn,
həm də slayda əlavə üçün işləyir.

DİZAYN QAYDASI: mətn az, şəkil çox. Hər mərhələ çəkilmiş ikonla göstərilir,
altında bir-iki söz. Telefonda 3-5 saniyə baxılır, ona görə oxunacaq cümlə
qoymaq mənasızdır: forma özü danışmalıdır.

KOORDİNAT SİSTEMİ: oxlar 16x9 vahidə qurulub və `aspect="equal"` təyin edilib.
Bunsuz `transAxes` işlədəndə dairələr ellipsə çevrilir, çünki kətan kvadrat
deyil.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import (  # noqa: E402
    Circle,
    FancyArrowPatch,
    FancyBboxPatch,
    Rectangle,
    Wedge,
)

HERE = Path(__file__).resolve().parent

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
MUTED = "#898781"
SURFACE = "#fcfcfb"
PANEL = "#f1f0ea"

FONT = "Segoe UI"

#: Sxemin şaquli mərkəzi. Bütün ikonlar bu xəttdə oturur.
ROW = 4.55


def _label(ax, x, y, text, size, color=INK, weight="normal"):
    ax.text(x, y, text, fontsize=size, color=color, fontweight=weight,
            ha="center", va="center", zorder=5, fontname=FONT)


#: AZ-Eval diskinin açıq narıncı fonu. Digər mərhələlərdən ayırır.
HERO_PANEL = "#fdeee8"


def _disc(ax, x, y, radius, facecolor=PANEL, ring=None):
    """İkonun altındakı disk.

    `ring` verilsə, kənarına nazik həlqə çəkilir. Bu, yalnız AZ-Eval üçündür:
    sxem dörd mərhələ göstərir, amma paylaşımın mövzusu onlardan BİRİDİR və
    baxan adam hansının layihə olduğunu bir anda görməlidir.
    """
    ax.add_patch(Circle((x, y), radius, facecolor=facecolor,
                        edgecolor="none", zorder=1))
    if ring:
        ax.add_patch(Circle((x, y), radius, facecolor="none",
                            edgecolor=ring, linewidth=2.6, zorder=2))


def _icon_human(ax, x, y, color):
    """İnsan qlifi: baş və çiyin.

    Baş ilə çiyin ARASINDA boşluq lazımdır. Əvvəlki versiyada ikisi birləşirdi
    və nəticə insana yox, tağa oxşayırdı. Çiyin də nazik qövs yox, dolu
    yarımdairədir: nazik qövs bu ölçüdə tanınmır.
    """
    ax.add_patch(Circle((x, y + 0.46), 0.30, facecolor=color,
                        edgecolor="none", zorder=3))
    ax.add_patch(Wedge((x, y - 0.52), 0.66, 0, 180,
                       facecolor=color, edgecolor="none", zorder=3))


def _icon_dataset(ax, x, y, color, scale=1.0):
    """Paralel dataset: iki sıra, biri AZ, biri EN."""
    width, height = 1.56 * scale, 1.24 * scale
    ax.add_patch(FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0,rounding_size=0.10",
        facecolor="white", edgecolor=color, linewidth=2.8, zorder=3,
    ))
    for index, (offset, tag) in enumerate(((0.26, "AZ"), (-0.26, "EN"))):
        shade = color if index == 0 else MUTED
        row_y = y + offset * scale
        ax.add_patch(Rectangle(
            (x - 0.58 * scale, row_y - 0.12 * scale), 1.16 * scale, 0.24 * scale,
            facecolor=shade, alpha=0.18, edgecolor="none", zorder=4,
        ))
        ax.text(x - 0.50 * scale, row_y, tag, fontsize=13 * scale, color=shade,
                fontweight="bold", ha="left", va="center", zorder=5,
                fontname=FONT)


def _icon_model(ax, x, y, color):
    """Şəbəkə qlifi: iki sütun düyün və aralarındakı bağlar."""
    left_nodes = [(x - 0.55, y + dy) for dy in (0.55, 0.0, -0.55)]
    right_nodes = [(x + 0.55, y + dy) for dy in (0.30, -0.30)]
    for lx, ly in left_nodes:
        for rx, ry in right_nodes:
            ax.plot([lx, rx], [ly, ry], color=MUTED, linewidth=1.0,
                    alpha=0.55, zorder=2)
    for px, py in left_nodes + right_nodes:
        ax.add_patch(Circle((px, py), 0.16, facecolor=color,
                            edgecolor="none", zorder=4))


def _icon_gap(ax, x, y, color_ok, color_bad):
    """Ölçmə qlifi: iki sütun, biri hündür, biri alçaq."""
    ax.add_patch(FancyBboxPatch(
        (x - 0.62, y - 0.62), 0.44, 1.20,
        boxstyle="round,pad=0,rounding_size=0.08",
        facecolor=color_ok, edgecolor="none", zorder=3,
    ))
    ax.add_patch(FancyBboxPatch(
        (x + 0.18, y - 0.62), 0.44, 0.40,
        boxstyle="round,pad=0,rounding_size=0.08",
        facecolor=color_bad, edgecolor="none", zorder=3,
    ))


def _arrow(ax, x_from, x_to, y):
    ax.add_patch(FancyArrowPatch(
        (x_from, y), (x_to, y),
        arrowstyle="-|>", mutation_scale=20,
        color=MUTED, linewidth=1.8, zorder=2,
    ))


def build(path: Path) -> None:
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(SURFACE)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)

    # --- Başlıq ---------------------------------------------------------
    ax.add_patch(Rectangle((1.15, 7.95), 1.05, 0.075, facecolor=BLUE,
                           edgecolor="none", zorder=3))
    ax.text(1.15, 7.45, "AZ-Eval", fontsize=52, color=INK, fontweight="bold",
            ha="left", va="center", zorder=5, fontname=FONT)
    ax.text(1.15, 6.85, "What happens between an Azerbaijani speaker "
            "and a language model", fontsize=21, color=INK_SOFT,
            ha="left", va="center", zorder=5, fontname=FONT)

    # --- Mərhələlər -----------------------------------------------------
    columns = [2.25, 6.05, 9.95, 13.55]
    # AZ-Eval diski böyükdür. Sxem dörd mərhələ göstərir, amma paylaşımın
    # mövzusu ikincisidir; ölçü fərqi bunu izahsız bildirir.
    radii = [1.10, 1.62, 1.10, 1.10]

    _disc(ax, columns[0], ROW, radii[0])
    _disc(ax, columns[1], ROW, radii[1], facecolor=HERO_PANEL, ring=ORANGE)
    _disc(ax, columns[2], ROW, radii[2])
    _disc(ax, columns[3], ROW, radii[3])

    _icon_human(ax, columns[0], ROW, BLUE)
    _icon_dataset(ax, columns[1], ROW, ORANGE, scale=1.30)
    _icon_model(ax, columns[2], ROW, BLUE)
    _icon_gap(ax, columns[3], ROW, BLUE, ORANGE)

    captions = [
        ("Human", "asks in Azerbaijani", False),
        ("AZ-Eval", "356 parallel items,\nevery one verified by hand", True),
        ("Language model", "answers under\nidentical prompts", False),
        ("The gap", "English holds,\nAzerbaijani collapses", False),
    ]
    for x, radius, (name, detail, hero) in zip(columns, radii, captions):
        _label(ax, x, ROW - 2.30, name, 30 if hero else 24,
               ORANGE if hero else INK, "bold")
        ax.text(x, ROW - 3.00, detail, fontsize=19 if hero else 17,
                color=INK_SOFT if hero else MUTED,
                ha="center", va="center", zorder=5, fontname=FONT,
                linespacing=1.5)

    # Oxlar disklərin arasında qalır, üstünə düşmür. Radius fərqli olduğu
    # üçün hər ox öz qonşularının ölçüsünə görə hesablanır.
    for index in range(len(columns) - 1):
        _arrow(ax,
               columns[index] + radii[index] + 0.20,
               columns[index + 1] - radii[index + 1] - 0.20,
               ROW)

    fig.savefig(path, dpi=100, facecolor=SURFACE)
    plt.close(fig)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    target = HERE / "story_instagram.png"
    build(target)
    print(f"{target.name}  ({target.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
