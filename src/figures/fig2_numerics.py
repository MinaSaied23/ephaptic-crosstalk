"""Fig. 2 - Numerical verification (data: e02_*.csv)."""
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT
import os

D = os.path.join(ROOT, "results", "data")
lag = pd.read_csv(os.path.join(D, "e02_lagged_vs_monolithic.csv"))
ref = pd.read_csv(os.path.join(D, "e02_refinement.csv"))

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4))
ax = axs[0]
cols = {1: "#444444", 10: "#1f77b4", 25: "#d62728", 50: "#9467bd"}
for n, c in cols.items():
    for scheme, ls, mk in (("lagged", "--", "o"), ("monolithic", "-", "s")):
        d = lag[(lag.n_abeta == n) & (lag.scheme == scheme)].sort_values("dt_us")
        ax.plot(d.dt_us, d.dv_downstream_mV, ls=ls, marker=mk, ms=3, color=c,
                label=f"n = {n}" if scheme == "monolithic" else None)
ax.set_xscale("log"); ax.invert_xaxis()
ax.set_xlabel("Δt (µs)"); ax.set_ylabel("C-fiber ΔV, z = 3–8 mm (mV)")
ax.set_title("Earlier geometry: lagged (--) vs\nmonolithic (—) coupling", fontsize=8)
ax.legend(frameon=False, loc="center left")
panel(ax, "a")

ax = axs[1]
for kind, mk in (("NavC", "s"), ("HH", "o")):
    for n, c in cols.items():
        d = ref[(ref.model == kind) & (ref.n_abeta == n) & (ref.dz_um == 5.0) & (ref.ionic == "explicit")].sort_values("dt_us")
        base = d[d.dt_us == d.dt_us.min()].dv_lesion_mV.values[0]
        ax.plot(d.dt_us, 100 * (d.dv_lesion_mV - base) / base, marker=mk, ms=3, color=c,
                ls="-" if kind == "NavC" else ":", label=None)
ax.axvline(1.0, color=COL["grey"], lw=0.6, ls="--")
ax.set_xscale("log"); ax.invert_xaxis()
ax.set_xlabel("Δt (µs)  [Δz = 5 µm]"); ax.set_ylabel("deviation from Δt = 0.125 µs (%)")
ax.set_title("Production configuration:\ntime-step refinement", fontsize=8)
panel(ax, "b")

ax = axs[2]
for kind, mk in (("NavC", "s"), ("HH", "o")):
    for n, c in cols.items():
        d = ref[(ref.model == kind) & (ref.n_abeta == n) & (ref.dt_us == 1.0) & (ref.ionic == "explicit")].sort_values("dz_um")
        base = d[d.dz_um == d.dz_um.min()].dv_lesion_mV.values[0]
        ax.plot(d.dz_um, 100 * (d.dv_lesion_mV - base) / base, marker=mk, ms=3, color=c,
                ls="-" if kind == "NavC" else ":")
ax.axvline(5.0, color=COL["grey"], lw=0.6, ls="--")
ax.set_xscale("log"); ax.invert_xaxis()
ax.set_xlabel("Δz (µm)  [Δt = 1 µs]"); ax.set_ylabel("deviation from Δz = 1.25 µm (%)")
ax.set_title("Production configuration:\ngrid refinement", fontsize=8)
panel(ax, "c")
fig.tight_layout()
save(fig, "fig2_numerics.png")
