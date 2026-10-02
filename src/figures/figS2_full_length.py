"""Fig. S2 - Earlier full-length geometry: stimulus-site artifact (data: e11) and
Fig. S3 - lesion length and stimulus strength (data: e12)."""
import os
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
f11 = pd.read_csv(os.path.join(D, "e11_full_length.csv"))
f12 = pd.read_csv(os.path.join(D, "e12_lesion_stimulus.csv"))

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5))
d = f11[np.isclose(f11.kappa, 1e9)]
stims = sorted(d.stim_nA.unique())
cols = dict(zip(stims, ("#999999", "#6baed6", "#2171b5", "#08306b")))
for ax, ret, letter in ((axs[0], "returned", "a"), (axs[1], "omitted", "b")):
    dd = d[(d.model == "NavC") & (d.electrode_current == ret)]
    for stim in stims:
        q = dd[np.isclose(dd.stim_nA, stim)].sort_values("n_abeta")
        ax.plot(q.n_abeta, q.ue_abs_max_mV, "-o", ms=3, color=cols[stim], label=f"{stim:.3g} nA")
        sp = q[q.c_spike.astype(bool)]
        ax.plot(sp.n_abeta, sp.ue_abs_max_mV, "r*", ms=8)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("n"); ax.set_ylabel("max |u$_e$| (mV)")
    ax.set_title(f"electrode current {ret}\n(* = propagating C-fiber AP)", fontsize=7.5)
    panel(ax, letter)
axs[0].legend(frameon=False, fontsize=6, title="Aβ stimulus", title_fontsize=6)
ax = axs[2]
for ret, ls in (("returned", "-"), ("omitted", "--")):
    dd = d[(d.model == "NavC") & (d.electrode_current == ret)]
    for stim in stims:
        q = dd[np.isclose(dd.stim_nA, stim)].sort_values("n_abeta")
        ax.plot(q.n_abeta, q.abeta_node0_peak_mV, ls=ls, marker="o", ms=2.5, color=cols[stim])
ax.set_xscale("log"); ax.set_yscale("symlog", linthresh=100)
ax.set_xlabel("n"); ax.set_ylabel("Aβ node-0 peak V$_m$ (mV)")
ax.set_title("electrode-site Aβ membrane\n(solid: returned, dashed: omitted)", fontsize=7.5)
panel(ax, "c")
fig.tight_layout()
save(fig, "figS2_full_length.png")

fig, axs = plt.subplots(1, 2, figsize=(5.4, 2.4))
for ax, study, col, letter, xl in ((axs[0], "lesion_length", "lesion_mm", "a", "lesion length (mm)"),
                                   (axs[1], "stimulus", "stim_factor", "b", "stimulus (× threshold)")):
    d = f12[(f12.study == study) & (f12.model == "NavC")]
    if study == "stimulus":
        base = f12[(f12.study == "lesion_length") & (f12.model == "NavC") & np.isclose(f12.lesion_mm, 5.0)].copy()
        base["stim_factor"] = 2.0
        d = pd.concat([d, base])
    for n, c in ((1, "#888888"), (10, "#1f77b4"), (25, "#d62728"), (50, "#9467bd"), (100, "#2ca02c")):
        dd = d[d.n_abeta == n].sort_values(col)
        ax.plot(dd[col], dd.dv_lesion_mV, "-o", ms=2.5, color=c, label=f"n = {n}")
        sp = dd[dd.c_spike.astype(bool)]
        ax.plot(sp[col], sp.dv_lesion_mV, "r*", ms=7)
    ax.set_xlabel(xl); ax.set_ylabel("NavC peak ΔV in lesion (mV)")
    if study == "stimulus":
        ax.set_xscale("log")
    panel(ax, letter)
axs[0].legend(frameon=False, fontsize=6)
fig.tight_layout()
save(fig, "figS3_lesion_stimulus.png")
