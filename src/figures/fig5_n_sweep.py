"""Fig. 5 - Dependence on the number of synchronous Abeta fibers sharing the compartment
(equivalently, on the extracellular cross-section per fiber).  Data: e03, e04."""
import os
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT
from ephaptic.params import A_REF, equivalent_gap

D = os.path.join(ROOT, "results", "data")
n3 = pd.read_csv(os.path.join(D, "e03_n_sweep.csv"))
g4 = pd.read_csv(os.path.join(D, "e04_geometry.csv"))

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5))
ax = axs[0]
d = n3[n3.model == "NavC"].sort_values("n_abeta")
h = n3[n3.model == "HH"].sort_values("n_abeta")
ax.plot(d.n_abeta, d.dv_lesion_mV, "-o", ms=3, color=COL["NavC"], label="NavC")
ax.plot(h.n_abeta, h.dv_lesion_mV, "o", ms=4.5, mfc="none", color=COL["HH"], label="HH")
ax.plot(d.n_abeta, d.hyp_lesion_mV, ":", color=COL["NavC"], lw=1)
fail = d[~d.ab_conducts.astype(bool)].n_abeta.min()
ax.axvspan(fail, 480, color="#eeeeee", zorder=0)
ax.text(fail * 1.15, -12, "Aβ fails\nin lesion", fontsize=6.5, color="#555555")
ax.axhline(0, color="k", lw=0.5)
ax.set_xscale("log"); ax.set_xlim(0.8, 400); ax.set_ylim(-35, 32)
ax.set_xlabel("synchronous Aβ fibers n")
ax.set_ylabel("C-fiber ΔV in lesion (mV)")
ax.legend(frameon=False, loc="upper left", fontsize=6.5)
ax.text(1.0, -31, "dotted: hyperpolarization", fontsize=6, color="#555555")
top = ax.twiny()
top.set_xscale("log"); top.set_xlim(ax.get_xlim())
ticks = [1, 5, 25, 100]
top.set_xticks(ticks); top.set_xticklabels([f"{equivalent_gap(A_REF / n) * 1e9:.0f}" for n in ticks], fontsize=6)
top.minorticks_off()
top.set_xlabel("w$_{eq}$ (nm)", fontsize=7)
top.spines["top"].set_visible(True)
panel(ax, "a")

ax = axs[1]
for kind in ("NavC", "HH"):
    d = n3[n3.model == kind].sort_values("n_abeta")
    ax.plot(d.n_abeta, d.ab_cv_lesion, "-o", ms=3, color=COL[kind] if kind == "NavC" else COL["abeta"])
    break
ax.set_xscale("log"); ax.set_xlim(0.8, 400)
ax.set_xlabel("n"); ax.set_ylabel("Aβ CV in lesion, nodes 3→7 mm (m/s)")
ax.axvspan(fail, 480, color="#eeeeee", zorder=0)
ax.set_ylim(0, 42)
panel(ax, "b")

ax = axs[2]
for kind, mk in (("NavC", "s"), ("HH", "o")):
    for n, ls in ((1, ":"), (10, "--"), (100, "-")):
        d = g4[(g4.model == kind) & (g4.closure == "per_fiber") & (g4.n_abeta == n)].sort_values("w_nm")
        if kind == "NavC":
            ax.plot(d.w_nm, d.dv_lesion_mV, ls=ls, marker=mk, ms=2.5, color=COL[kind], label=f"own sleeve, n = {n}")
    d = n3[n3.model == kind]
    if kind == "NavC":
        ax.plot(d.w_eq_nm, d.dv_lesion_mV, "x", ms=4, color="k", label="shared 16.4 µm², n fibers\n(plotted at w$_{eq}$)")
ax.set_xscale("log")
ax.set_xlabel("periaxonal gap w (nm)"); ax.set_ylabel("C-fiber peak ΔV (mV)")
ax.set_ylim(0, 32)
ax.legend(frameon=False, fontsize=5.8, loc="upper right")
panel(ax, "c")
fig.tight_layout()
save(fig, "fig5_n_sweep.png")
