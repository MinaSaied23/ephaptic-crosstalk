"""Fig. 6 - Excitability of the C-fiber for brief, local inputs (data: e07_*.csv)."""
import os
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
sd = pd.read_csv(os.path.join(D, "e07_strength_duration.csv"))
sf = pd.read_csv(os.path.join(D, "e07_safety_factor.csv"))

NAMES = {
    "HH_phi1_gNa120": ("HH 6.3 °C", COL["HH"], "-"),
    "HH_phi7.8_gNa120": ("HH 25 °C", COL["HH"], "--"),
    "HH_phi1_gNa600": ("HH, g × 5", "#5aa0e0", ":"),
    "HH_phi5_gNa600": ("HH, rates & g × 5", "#2ca02c", "-."),
    "HH_phi10_gNa1200": ("HH, rates & g × 10", "#2ca02c", "-"),
    "NavC_tm8_1.5ms_g18_2000": ("NavC τm8 1.5 ms", COL["NavC"], "-"),
    "NavC_tm8_0.05ms_g18_2000": ("NavC τm8 0.05 ms", COL["NavC"], "--"),
    "NavC_tm8_0.15ms_g18_20000": ("NavC, τ's / 10 & g × 10", "#e377c2", "-"),
}


def name(v):
    return NAMES.get(v, (v, "k", "-"))


fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5))
ax = axs[0]
for v, d in sd[sd["mode"] == "point"].groupby("variant"):
    lab, c, ls = name(v)
    d = d.sort_values("duration_ms")
    ax.plot(d.duration_ms, d.threshold * 1e9, ls=ls, color=c, marker="o", ms=2.5, label=lab)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("pulse duration (ms)"); ax.set_ylabel("threshold current (nA)")
ax.set_title("point injection, z = 5 mm", fontsize=8, pad=10)
ax.axvspan(0.07, 0.16, color="#f3e6f7", zorder=0)
panel(ax, "a")

ax = axs[1]
for v, d in sd[sd["mode"] == "point"].groupby("variant"):
    lab, c, ls = name(v)
    d = d.sort_values("duration_ms")
    ax.plot(d.duration_ms, d.v_peak_subthreshold_mV, ls=ls, color=c, marker="o", ms=2.5, label=lab)
ax.set_xscale("log")
ax.axvspan(0.07, 0.16, color="#f3e6f7", zorder=0)
ax.annotate("ephaptic\nFWHM", xy=(0.11, 0.62), xycoords=("data", "axes fraction"), xytext=(14, 10),
            textcoords="offset points", fontsize=6, ha="left", va="center", color=COL["ue"],
            arrowprops=dict(arrowstyle="-", color=COL["ue"], lw=0.6))
ax.set_xlabel("pulse duration (ms)"); ax.set_ylabel("peak V$_m$, 0.5 % below threshold (mV)")
ax.set_title("voltage reached without firing", fontsize=8, pad=10)
panel(ax, "b")

ax = axs[2]
d0 = sf[sf.c_bias == 0]
for v, d in d0.groupby("variant"):
    lab, c, ls = name(v)
    d = d.sort_values("n_abeta")
    ax.plot(d.n_abeta, d.alpha_star, ls=ls, color=c, marker="o", ms=2.5, label=lab)
ax.axhline(1.0, color="k", lw=0.6)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("synchronous Aβ fibers n"); ax.set_ylabel("α* (gain on u$_e$ needed to fire)")
ax.set_title("ephaptic safety factor", fontsize=8, pad=10)
ax.axvspan(25, 130, color="#eeeeee", zorder=0)
ax.text(26, 22, "Aβ conduction\nfails in lesion", fontsize=5.5, color="#555555", va="top")
panel(ax, "c")
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.12))
fig.tight_layout()
save(fig, "fig6_threshold.png")
