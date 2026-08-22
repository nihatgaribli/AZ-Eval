"""AZ-Eval-in işləmə prinsipi: bir sxem, minimum mətn.

    python talk/diagram.py

ÖLÇÜ 1920x1080. Sxem iki sualı ayırır, çünki layihənin quruluşu da onları
ayırır:

  yuxarı zolaq  - dataset NECƏ QURULUR (mənbə, insan qapısı, dəst)
  aşağı zolaq   - ölçmə NECƏ APARILIR  (model, xam cavab, normalizasiya)

Bu ayrılıq təsadüfi deyil, layihənin əsas memarlıq qərarıdır: `run_eval`
metrika hesablamır, yalnız xam mətn yazır. Ona görə metrik qaydası dəyişəndə
modellər yenidən işlədilmir, yalnız `analyze` təkrarlanır. Sxemdə bu, xam
cavabın ayrıca düyün kimi dayanması ilə göstərilir.

MƏTN AZDIR: hər düyün bir söz. İzah şəklin işi deyil, danışanın işidir.
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
    Polygon,
    Rectangle,
)

HERE = Path(__file__).resolve().parent

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
MUTED = "#898781"
SURFACE = "#fcfcfb"
PANEL = "#f1f0ea"
HERO = "#fdeee8"
FONT = "Segoe UI"


def label(ax, x, y, text, size, color=INK, weight="normal", ha="center"):
    ax.text(x, y, text, fontsize=size, color=color, fontweight=weight,
            ha=ha, va="center", zorder=6, fontname=FONT)


def disc(ax, x, y, r, face=PANEL, ring=None):
    ax.add_patch(Circle((x, y), r, facecolor=face, edgecolor="none", zorder=1))
    if ring:
        ax.add_patch(Circle((x, y), r, facecolor="none", edgecolor=ring,
                            linewidth=2.4, zorder=2))


def arrow(ax, x0, y0, x1, y1, width=1.8):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=18, color=MUTED,
                                 linewidth=width, zorder=2))


# --------------------------------------------------------------------------
# İkonlar
# --------------------------------------------------------------------------


def icon_sources(ax, x, y):
    """İki mənbə: verilənlər bazası (Wikidata) və əl ilə yazılmış sual."""
    ax.add_patch(Rectangle((x - 0.60, y - 0.34), 0.48, 0.68,
                           facecolor=BLUE, edgecolor="none", zorder=3))
    ax.add_patch(Circle((x - 0.36, y - 0.34), 0.24, facecolor=BLUE,
                        edgecolor="none", zorder=2))
    ax.add_patch(Circle((x - 0.36, y + 0.34), 0.24, facecolor="#5b9ae4",
                        edgecolor="none", zorder=4))

    ax.add_patch(Polygon([[x + 0.20, y - 0.44], [x + 0.70, y + 0.32],
                          [x + 0.50, y + 0.46]],
                         closed=True, facecolor=ORANGE, edgecolor="none",
                         zorder=3))
    ax.add_patch(Polygon([[x + 0.20, y - 0.44], [x + 0.31, y - 0.26],
                          [x + 0.15, y - 0.31]],
                         closed=True, facecolor=INK_SOFT, edgecolor="none",
                         zorder=4))


def icon_gate(ax, x, y):
    """Qıf: namizədlər girir, azı çıxır. Rədd edilənlər yana tökülür."""
    ax.add_patch(Polygon([[x - 0.70, y + 0.54], [x + 0.70, y + 0.54],
                          [x + 0.15, y - 0.08], [x + 0.15, y - 0.58],
                          [x - 0.15, y - 0.58], [x - 0.15, y - 0.08]],
                         closed=True, facecolor=ORANGE, edgecolor="none",
                         zorder=3))
    for dx, dy, r in ((0.98, 0.28, 0.11), (1.16, -0.02, 0.09),
                      (0.90, -0.26, 0.07)):
        ax.add_patch(Circle((x + dx, y + dy), r, facecolor=MUTED,
                            edgecolor="none", zorder=3, alpha=0.7))


def icon_dataset(ax, x, y):
    """Paralel dəst: eyni sual iki dildə."""
    ax.add_patch(FancyBboxPatch((x - 0.70, y - 0.50), 1.40, 1.00,
                                boxstyle="round,pad=0,rounding_size=0.09",
                                facecolor="white", edgecolor=ORANGE,
                                linewidth=2.4, zorder=3))
    for dy, shade in ((0.21, ORANGE), (-0.21, BLUE)):
        ax.add_patch(Rectangle((x - 0.52, y + dy - 0.11), 1.04, 0.22,
                               facecolor=shade, alpha=0.20, edgecolor="none",
                               zorder=4))
        ax.add_patch(Rectangle((x - 0.52, y + dy - 0.11), 0.10, 0.22,
                               facecolor=shade, edgecolor="none", zorder=5))


def icon_model(ax, x, y):
    """Şəbəkə qlifi."""
    left = [(x - 0.48, y + d) for d in (0.46, 0.0, -0.46)]
    right = [(x + 0.48, y + d) for d in (0.25, -0.25)]
    for lx, ly in left:
        for rx, ry in right:
            ax.plot([lx, rx], [ly, ry], color=MUTED, linewidth=1.0,
                    alpha=0.5, zorder=2)
    for px, py in left + right:
        ax.add_patch(Circle((px, py), 0.14, facecolor=BLUE, edgecolor="none",
                            zorder=4))


def icon_raw(ax, x, y):
    """Xam cavab faylı. Toxunulmaz saxlanılır, ona görə ayrıca düyündür."""
    ax.add_patch(FancyBboxPatch((x - 0.44, y - 0.54), 0.88, 1.08,
                                boxstyle="round,pad=0,rounding_size=0.07",
                                facecolor="white", edgecolor=INK_SOFT,
                                linewidth=2.0, zorder=3))
    for i, w in enumerate((0.58, 0.48, 0.62, 0.40)):
        ax.add_patch(Rectangle((x - 0.30, y + 0.30 - i * 0.22), w, 0.085,
                               facecolor=MUTED, alpha=0.5, edgecolor="none",
                               zorder=4))


def node_label(ax, x, y, title, module, detail, above: bool):
    """Düyünün üç sətri: ad, modul, texniki fakt.

    Modul adı qəsdən göstərilir. Sxem yalnız anlayışları göstərsəydi, oxucu
    onu koda bağlaya bilməzdi; modul adı isə hər mərhələnin harada yaşadığını
    birbaşa deyir.
    """
    step = 0.34
    lines = [(title, 19, INK, "bold"), (module, 13, ORANGE, "normal"),
             (detail, 13, MUTED, "normal")]
    for i, (text, size, color, weight) in enumerate(lines):
        offset = (i * step) if not above else ((len(lines) - 1 - i) * step)
        label(ax, x, y + offset if above else y - offset, text, size, color, weight)


def ladder(ax, x0, y0, step_w=1.42, step_h=0.40):
    """Normalizasiya zənciri: hər pillə bir səth hadisəsini ayırır.

    Pillələrin hündürlüyü artır, çünki hər addım daha çox səhvi bağışlayır.
    Rəngin tündləşməsi eyni şeyi ikinci kanalda təkrarlayır: forma və ton
    birlikdə oxunur, tək kanala güvənmək lazım deyil.

    Hər pillənin altında onun NƏ ƏLAVƏ ETDİYİ yazılır. Ad tək başına ("MORPH")
    heç nə demir; "+ suffixes" isə pillənin ölçdüyü səth hadisəsini adlandırır.
    """
    steps = [("STRICT", "exact"), ("MORPH", "+ suffixes"),
             ("LENIENT", "+ diacritics"), ("TRANSLIT", "+ script")]
    shades = [0.30, 0.50, 0.72, 1.0]
    for i, ((name, adds), shade) in enumerate(zip(steps, shades)):
        x = x0 + i * step_w
        ax.add_patch(FancyBboxPatch((x, y0), step_w * 0.84, step_h * (i + 1),
                                    boxstyle="round,pad=0,rounding_size=0.07",
                                    facecolor=ORANGE, alpha=shade,
                                    edgecolor="none", zorder=3))
        cx = x + step_w * 0.42
        label(ax, cx, y0 - 0.30, name, 14, INK, "bold")
        label(ax, cx, y0 - 0.60, adds, 12, MUTED)


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

    ax.add_patch(Rectangle((1.05, 8.62), 0.95, 0.06, facecolor=BLUE,
                           edgecolor="none", zorder=3))
    label(ax, 1.05, 8.28, "AZ-Eval", 34, INK, "bold", ha="left")
    label(ax, 3.30, 8.28, "how a score is produced", 17, MUTED, ha="left")

    radius = 0.92

    # ---- Yuxarı zolaq: dataset necə qurulur -------------------------
    top = 5.95
    xs = [2.7, 6.3, 9.9]
    for x in xs:
        disc(ax, x, top, radius)
    disc(ax, xs[1], top, radius, face=HERO, ring=ORANGE)

    icon_sources(ax, xs[0], top)
    icon_gate(ax, xs[1], top)
    icon_dataset(ax, xs[2], top)

    for a, b in zip(xs, xs[1:]):
        arrow(ax, a + radius + 0.15, top, b - radius - 0.15, top)

    # Yuxarı zolağın etiketləri disklərin ÜSTÜNDƏDİR. Altda olsaydı, dəstdən
    # modelə enən birləşdirici xətt onların üstündən keçərdi; sxemdə kəsişən
    # xətt ən tez nəzərə çarpan səliqəsizlikdir.
    top_labels = [
        ("SOURCES", "harvest_wikidata.py", "24 SPARQL templates + hand-written"),
        ("HUMAN GATE", "review.py", "verified_by = human, or it never enters"),
        ("DATASET", "build_dataset.py", "356 parallel AZ / EN items"),
    ]
    for x, (title, module, detail) in zip(xs, top_labels):
        node_label(ax, x, top + radius + 0.42, title, module, detail, above=True)

    # ---- Aşağı zolaq: ölçmə necə aparılır ---------------------------
    bottom = 2.60
    mx = [2.7, 6.3]
    for x in mx:
        disc(ax, x, bottom, radius)
    icon_model(ax, mx[0], bottom)
    icon_raw(ax, mx[1], bottom)
    arrow(ax, mx[0] + radius + 0.15, bottom, mx[1] - radius - 0.15, bottom)
    bottom_labels = [
        ("MODEL", "run_eval.py", "greedy decoding, fixed seed"),
        ("RAW OUTPUT", "results/raw_outputs/", "text only, never scored in place"),
    ]
    for x, (title, module, detail) in zip(mx, bottom_labels):
        node_label(ax, x, bottom - radius - 0.42, title, module, detail, above=False)

    # Dəstdən modelə enən yol. Üfüqi hissə iki zolağın arasındakı boş zolaqdan
    # keçir: yuxarıda etiketlər disklərin üstünə köçürülüb, aşağıda isə
    # nərdivanın ən hündür pilləsi 3.65-ə çatır, ona görə 4.55 hər ikisindən
    # təmiz qalır.
    turn = 4.55
    ax.plot([xs[2], xs[2]], [top - radius - 0.15, turn], color=MUTED,
            linewidth=1.6, zorder=2)
    ax.plot([xs[2], mx[0]], [turn, turn], color=MUTED, linewidth=1.6, zorder=2)
    arrow(ax, mx[0], turn, mx[0], bottom + radius + 0.14, width=1.6)

    # Normalizasiya nərdivanı. Baza 2.00-dədir: ən hündür pillə 3.60-a çatır,
    # ona görə üstündəki etiket bloku 3.72-dən başlaya bilir və sütuna toxunmur.
    ladder(ax, 8.60, 2.00)
    arrow(ax, mx[1] + radius + 0.15, bottom, 8.42, bottom)
    label(ax, 11.28, 4.32, "NORMALIZATION", 19, INK, "bold")
    label(ax, 11.28, 4.02, "analyze.py", 13, ORANGE)
    label(ax, 11.28, 3.72, "each step isolates one surface phenomenon", 13, MUTED)

    # Statistika sətri nərdivanın ALTINDADIR, mərkəzdə yox: mərkəzdə qoyulanda
    # aşağı zolağın düyün etiketləri ilə üst-üstə düşürdü.
    label(ax, 11.28, 0.85, "paired bootstrap · permutation test · Holm correction",
          13, MUTED)

    fig.savefig(path, dpi=100, facecolor=SURFACE)
    plt.close(fig)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    target = HERE / "diagram_principle.png"
    build(target)
    print(f"{target.name}  ({target.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
