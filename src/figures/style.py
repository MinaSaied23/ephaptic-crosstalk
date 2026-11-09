"""Shared figure style."""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
FIG = os.path.join(ROOT, "results", "figures")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, "experiments"))

COL = {"HH": "#1f5fa8", "NavC": "#c0392b", "grey": "#7f7f7f", "abeta": "#2c7d3a", "ue": "#7b3fa0"}

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "lines.linewidth": 1.2, "font.family": "DejaVu Sans",
})


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    p = os.path.join(FIG, name)
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


def panel_letters(fig, axs, letters, dy=0.035):
    """Panel letters placed left of each panel's tick and axis labels (no overlap with them)."""
    fig.canvas.draw()
    inv = fig.transFigure.inverted()
    r = fig.canvas.get_renderer()
    for ax, s in zip(axs, letters):
        x0 = inv.transform((ax.get_tightbbox(r).x0, 0))[0]
        y1 = inv.transform((0, ax.get_window_extent().y1))[1]
        fig.text(x0 - 0.012, y1 + dy, s, fontsize=10, fontweight="bold", ha="right", va="bottom")


def panel(ax, letter):
    ax.text(-0.14, 1.04, letter, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom")
