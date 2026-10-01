"""
plot_convergence_figure.py

Fig. 4 of the manuscript: spatial (top row) and temporal (bottom row) refinement.
Reads results/convergence/spatial_convergence.csv and temporal_convergence_final.csv
(written by run_convergence_battery.py) and writes results/figures/fig_convergence_analysis.png.

Usage:
    python src/plot_convergence_figure.py
"""

import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator

_SRC = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC)
CONV = os.path.join(_ROOT, "results", "convergence")
OUT = os.path.join(_ROOT, "results", "figures", "fig_convergence_analysis.png")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {k: np.array([float(r[k]) if r[k].replace('.', '', 1).replace('-', '', 1).replace('e', '', 1).replace('+', '', 1).isdigit() else np.nan
                         for r in rows]) for k in rows[0].keys()}


def richardson(dt, f):
    """Richardson estimate from the three finest dyadic steps (0.5, 0.25, 0.125 us)."""
    idx = [int(np.where(np.isclose(dt, x))[0][0]) for x in (0.5, 0.25, 0.125)]
    a, b, c = (f[i] for i in idx)
    p = np.log2((b - a) / (c - b))
    return p, c + (c - b) / (2.0 ** p - 1.0), c + (c - b)


def logx(ax, ticks, label):
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FixedFormatter([f"{t:g}" for t in ticks]))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel(label)
    ax.grid(True, linestyle="--", alpha=0.6)


def main():
    sp = read_csv(os.path.join(CONV, "spatial_convergence.csv"))
    tp = read_csv(os.path.join(CONV, "temporal_convergence_final.csv"))
    w = sp["w_cleft_nm"][0]

    dz, dt = sp["dz_um"], tp["dt_us"]
    # labelled ticks (every grid point is still plotted; 1.25 and 0.625 are left unlabelled to avoid overlap)
    dz_ticks = [1.0, 2.5, 5.0, 10.0, 20.0]
    dt_ticks = [0.125, 0.25, 0.5, 1.25, 2.5, 5.0]
    p, rich, first = richardson(dt, tp["c25_delta_v_mV"])

    fig, ax = plt.subplots(2, 3, figsize=(14, 8))

    # --- top row: spatial refinement at dt = 2.5 us
    a = ax[0, 0]
    a.plot(dz, sp["abeta_cv_mps"], "o-", color="navy", lw=2)
    a.set_ylim(39.0, 43.0)
    a.set_ylabel("Conduction Velocity (m/s)")
    a.set_title(r"A$\beta$ Conduction Velocity vs. $\Delta z$")
    logx(a, dz_ticks, r"Spatial grid $\Delta z$ ($\mu$m)")

    a = ax[0, 1]
    a.plot(dz, sp["abeta_amp_4mm_mV"], "s-", color="crimson", lw=2, label="4 mm")
    a.plot(dz, sp["abeta_amp_8mm_mV"], "^-", color="darkorange", lw=2, label="8 mm (boundary)")
    a.set_ylim(80.0, 85.0)
    a.set_ylabel("Action Potential Amplitude (mV)")
    a.set_title(r"A$\beta$ AP Amplitude vs. $\Delta z$")
    a.legend(loc="center right")
    logx(a, dz_ticks, r"Spatial grid $\Delta z$ ($\mu$m)")

    a = ax[0, 2]
    a.plot(dz, sp["c1_delta_v_mV"], "o-", color="teal", lw=2, label="n = 1")
    a.plot(dz, sp["c25_delta_v_mV"], "D-", color="purple", lw=2, label="n = 25")
    a.set_ylim(0.0, 7.0)
    a.set_ylabel(r"C-fiber Ephaptic $\Delta V$ (mV)")
    a.set_title(rf"Coupled C-fiber Ephaptic $\Delta V$ vs. $\Delta z$" "\n" rf"($w_{{\mathrm{{cleft}}}}$ = {w:g} nm)")
    a.legend(loc="center right")
    logx(a, dz_ticks, r"Spatial grid $\Delta z$ ($\mu$m)")

    # --- bottom row: temporal refinement at dz = 10 um
    a = ax[1, 0]
    a.plot(dt, tp["abeta_cv_mps"], "o-", color="navy", lw=2)
    a.set_ylabel("Conduction Velocity (m/s)")
    a.set_title(r"A$\beta$ Conduction Velocity vs. $\Delta t$")
    logx(a, dt_ticks, r"Temporal step $\Delta t$ ($\mu$s)")

    a = ax[1, 1]
    a.plot(dt, tp["abeta_amp_4mm_mV"], "s-", color="crimson", lw=2)
    a.set_ylabel("Action Potential Amplitude at 4 mm (mV)")
    a.set_title(r"A$\beta$ AP Amplitude vs. $\Delta t$")
    logx(a, dt_ticks, r"Temporal step $\Delta t$ ($\mu$s)")

    a = ax[1, 2]
    a.plot(dt, tp["c1_delta_v_mV"], "o-", color="teal", lw=2, label="n = 1")
    a.plot(dt, tp["c25_delta_v_mV"], "D-", color="purple", lw=2, label="n = 25")
    a.axhline(rich, color="gray", ls="--", lw=1.2,
              label=rf"Richardson estimate, n = 25 ($p\approx{p:.2f}$): {rich:.1f} mV")
    a.set_ylabel(r"C-fiber Ephaptic $\Delta V$ (mV)")
    a.set_title(rf"Coupled C-fiber Ephaptic $\Delta V$ vs. $\Delta t$" "\n" rf"($w_{{\mathrm{{cleft}}}}$ = {w:g} nm)")
    a.set_ylim(0.0, 21.0)
    a.legend(loc="upper right", fontsize=8)
    logx(a, dt_ticks, r"Temporal step $\Delta t$ ($\mu$s)")

    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=300)
    print(f"Saved {OUT}  (Richardson: p = {p:.3f}, estimate = {rich:.2f} mV, first-order = {first:.2f} mV)")


if __name__ == "__main__":
    main()
