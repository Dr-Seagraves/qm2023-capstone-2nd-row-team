"""Create a single PNG dashboard for the four memo figures.

The dashboard keeps the memo structure intact:
1. M2 rolling correlation and lag structure
2. M3v2 small vs large firm trends
3. M3v2 event study around the GFC and COVID shocks
4. M3v2 residual diagnostics

Figure 1 and Figure 4 are grouped from multiple source plots so the final
image reads like the memo rather than a flat contact sheet.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec


ROOT_DIR = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT_DIR / "results" / "figures"
OUTPUT_PATH = FIGURES_DIR / "memo_four_figure_dashboard.png"

FIGURE_1_ROLLING = FIGURES_DIR / "M2_05_rolling_correlation.png"
FIGURE_1_LAG = FIGURES_DIR / "M2_04_lagged_effects.png"
FIGURE_2_TRENDS = FIGURES_DIR / "m3v2_group_trends.png"
FIGURE_3_EVENT_STUDY = FIGURES_DIR / "m3v2_did_event_study.png"
FIGURE_4_FITTED = FIGURES_DIR / "m3v2_residuals_vs_fitted.png"
FIGURE_4_QQ = FIGURES_DIR / "m3v2_residuals_qq.png"
FIGURE_4_HIST = FIGURES_DIR / "m3v2_residuals_hist.png"


def load_image(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing figure asset: {path}")
    return plt.imread(path)


def show_image(ax, path: Path, title: str | None = None) -> None:
    ax.imshow(load_image(path))
    ax.set_axis_off()
    if title:
        ax.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=10)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "figure.facecolor": "white",
        }
    )

    fig = plt.figure(figsize=(24, 30), facecolor="white")
    outer = GridSpec(2, 2, figure=fig, wspace=0.08, hspace=0.16)

    # Figure 1: rolling correlation + lag structure.
    fig1 = GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[0, 0], hspace=0.18)
    ax1 = fig.add_subplot(fig1[0, 0])
    show_image(
        ax1,
        FIGURE_1_ROLLING,
        "Figure 1. M2 rolling correlation and lag structure",
    )
    ax1b = fig.add_subplot(fig1[1, 0])
    show_image(ax1b, FIGURE_1_LAG)

    # Figure 2: firm-size trends.
    ax2 = fig.add_subplot(outer[0, 1])
    show_image(
        ax2,
        FIGURE_2_TRENDS,
        "Figure 2. M3v2 small vs large firm trends",
    )

    # Figure 3: event study.
    ax3 = fig.add_subplot(outer[1, 0])
    show_image(
        ax3,
        FIGURE_3_EVENT_STUDY,
        "Figure 3. M3v2 event study around the GFC and COVID shocks",
    )

    # Figure 4: residual diagnostics grouped in one section.
    fig4 = GridSpecFromSubplotSpec(3, 1, subplot_spec=outer[1, 1], hspace=0.14)
    ax4 = fig.add_subplot(fig4[0, 0])
    show_image(
        ax4,
        FIGURE_4_FITTED,
        "Figure 4. M3v2 residual diagnostics",
    )
    ax4b = fig.add_subplot(fig4[1, 0])
    show_image(ax4b, FIGURE_4_QQ)
    ax4c = fig.add_subplot(fig4[2, 0])
    show_image(ax4c, FIGURE_4_HIST)

    fig.suptitle(
        "Memo Figure Dashboard",
        fontsize=20,
        fontweight="bold",
        y=0.995,
    )

    plt.savefig(OUTPUT_PATH, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()