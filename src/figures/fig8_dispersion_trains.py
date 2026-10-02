"""Fig. 8 - Temporal dispersion and repetitive trains (data: e08_jitter, e09_trains)."""
import os
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
j8 = pd.read_csv(os.path.join(D, "e08_jitter.csv"))
t9 = pd.read_csv(os.path.join(D, "e09_trains.csv"))

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4))
ax = axs[0]
for n, c in ((10, "#1f77b4"), (25, "#d62728"), (50, "#9467bd")):
    d = j8[(j8.model == "NavC") & (j8.n_abeta == n)].sort_values("jitter_ms")
    ax.plot(d.jitter_ms, d.dv_lesion_mV, "-o", ms=3, color=c, label=f"n = {n}")
h = j8[(j8.model == "HH") & (j8.n_abeta == 25)].sort_values("jitter_ms")
ax.plot(h.jitter_ms, h.dv_lesion_mV, "s", ms=5, mfc="none", color="k", label="HH, n = 25")
ax.set_xlabel("dispersion window W (ms)"); ax.set_ylabel("C-fiber peak ΔV (mV)")
ax.legend(frameon=False, fontsize=6.5)
panel(ax, "a")

ax = axs[1]
for n, c in ((10, "#1f77b4"), (25, "#d62728"), (50, "#9467bd")):
    d = j8[(j8.model == "NavC") & (j8.n_abeta == n)].sort_values("jitter_ms")
    base = d[d.jitter_ms == 0].dv_lesion_mV.values[0]
    ax.plot(d.jitter_ms, 100 * (1 - d.dv_lesion_mV / base), "-o", ms=3, color=c, label=f"n = {n}")
ax.axhline(0, color="#888888", lw=0.5)
ax.set_xlabel("dispersion window W (ms)"); ax.set_ylabel("attenuation vs synchronous (%)")
# at n = 50 the synchronous volley blocks its own Abeta APs, so a small dispersion increases
# the response: the attenuation starts negative and the axis has to show it
ax.set_ylim(-25, 100)
panel(ax, "b")

ax = axs[2]
pcols = [c for c in t9.columns if c.startswith("dv_pulse")]
for (kind, n), d in t9[t9.n_abeta.isin([10, 25])].groupby(["model", "n_abeta"]):
    if kind != "NavC":
        continue
    for f, c in zip((50, 100, 200, 400), ("#bbbbbb", "#888888", "#444444", "#000000")):
        r = d[d.freq_Hz == f]
        if len(r):
            ax.plot(range(1, len(pcols) + 1), r[pcols].values[0], marker="o", ms=2.5, color=c,
                    ls="-" if n == 25 else "--", label=f"{f} Hz" if n == 25 else None)
ax.set_xlabel("pulse number"); ax.set_ylabel("peak ΔV in pulse window (mV)")
ax.set_title("NavC trains: n = 25 (—), n = 10 (--)", fontsize=8)
ax.legend(frameon=False, fontsize=6)
panel(ax, "c")
fig.tight_layout()
save(fig, "fig8_dispersion_trains.png")
