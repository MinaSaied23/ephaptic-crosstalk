"""Fig. S3 - Lesion length and stimulus strength (data: e12_lesion_stimulus)."""
import os
import pandas as pd
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
d = pd.read_csv(os.path.join(D, "e12_lesion_stimulus.csv"))
d = d[d.model == "NavC"]

fig, axs = plt.subplots(1, 2, figsize=(5.4, 2.3))
NS = ((1, "#1f77b4"), (10, "#2ca02c"), (25, "#d62728"), (50, "#9467bd"))

ax = axs[0]
for n, c in NS:
    q = d[(d.study == "lesion_length") & (d.n_abeta == n)].sort_values("lesion_mm")
    if len(q):
        ax.plot(q.lesion_mm, q.dv_lesion_mV, "-o", ms=3, color=c, label=f"n = {n}")
        blocked = q[~q.ab_conducts.astype(bool)]
        ax.plot(blocked.lesion_mm, blocked.dv_lesion_mV, "x", ms=6, color="k")
ax.set_xlabel("lesion length (mm)"); ax.set_ylabel("C-fiber peak ΔV (mV)")
ax.legend(frameon=False, fontsize=6.5)
panel(ax, "a")

ax = axs[1]
for n, c in NS:
    q = d[(d.study == "stimulus") & (d.n_abeta == n)].sort_values("stim_factor")
    if len(q):
        ax.plot(q.stim_factor, q.dv_lesion_mV, "-o", ms=3, color=c, label=f"n = {n}")
        blocked = q[~q.ab_conducts.astype(bool)]
        ax.plot(blocked.stim_factor, blocked.dv_lesion_mV, "x", ms=6, color="k")
ax.set_xlabel("Aβ stimulus (× threshold)"); ax.set_ylabel("C-fiber peak ΔV (mV)")
ax.set_xscale("log")
ax.set_title("× : Aβ AP blocked in lesion", fontsize=7)
panel(ax, "b")

fig.tight_layout()
save(fig, "figS3_lesion_stimulus.png")
