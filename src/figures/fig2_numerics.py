"""Fig. 2 - Numerical verification (data: e02_*.csv; n = 100 from e15_convergence_extremes.csv)."""
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT
import os

D = os.path.join(ROOT, "results", "data")
lag = pd.read_csv(os.path.join(D, "e02_lagged_vs_monolithic.csv"))
ref = pd.read_csv(os.path.join(D, "e02_refinement.csv"))
_e15 = os.path.join(D, "e15_convergence_extremes.csv")
ext = pd.read_csv(_e15) if os.path.exists(_e15) else None
C100 = "#e6862e"

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
if ext is not None:     # the baseline maximum, n = 100 (E15), refined to dt = 0.1 us
    for kind, mk in (("NavC", "s"), ("HH", "o")):
        d = ext[(ext.case == "n_sweep_max") & (ext.model == kind) & (ext.dz_um == 5.0)].sort_values("dt_us")
        base = d[d.dt_us == d.dt_us.min()].dv_lesion_mV.values[0]
        ax.plot(d.dt_us, 100 * (d.dv_lesion_mV - base) / base, marker=mk, ms=3, color=C100,
                ls="-" if kind == "NavC" else ":")
ax.axvline(1.0, color=COL["grey"], lw=0.6, ls="--")
ax.set_xscale("log"); ax.invert_xaxis()
ax.set_xlabel("Δt (µs)  [Δz = 5 µm]"); ax.set_ylabel("deviation from finest Δt (%)")
ax.set_title("Production configuration:\ntime-step refinement", fontsize=8)
panel(ax, "b")

ax = axs[2]
for kind, mk in (("NavC", "s"), ("HH", "o")):
    for n, c in cols.items():
        d = ref[(ref.model == kind) & (ref.n_abeta == n) & (ref.dt_us == 1.0) & (ref.ionic == "explicit")].sort_values("dz_um")
        base = d[d.dz_um == d.dz_um.min()].dv_lesion_mV.values[0]
        ax.plot(d.dz_um, 100 * (d.dv_lesion_mV - base) / base, marker=mk, ms=3, color=c,
                ls="-" if kind == "NavC" else ":")
if ext is not None:
    for kind, mk in (("NavC", "s"), ("HH", "o")):
        d = ext[(ext.case == "n_sweep_max") & (ext.model == kind) & (ext.dt_us == 1.0)].sort_values("dz_um")
        base = d[d.dz_um == d.dz_um.min()].dv_lesion_mV.values[0]
        ax.plot(d.dz_um, 100 * (d.dv_lesion_mV - base) / base, marker=mk, ms=3, color=C100,
                ls="-" if kind == "NavC" else ":")
ax.axvline(5.0, color=COL["grey"], lw=0.6, ls="--")
ax.set_xscale("log"); ax.invert_xaxis()
ax.set_xlabel("Δz (µm)  [Δt = 1 µs]"); ax.set_ylabel("deviation from Δz = 1.25 µm (%)")
ax.set_title("Production configuration:\ngrid refinement", fontsize=8)
panel(ax, "c")
if ext is not None:
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=c, marker="s", ms=3, label=f"n = {n}") for n, c in cols.items()]
    h += [Line2D([], [], color=C100, marker="s", ms=3, label="n = 100")]
    h += [Line2D([], [], color="k", ls="-", label="NavC"), Line2D([], [], color="k", ls=":", label="HH")]
    axs[2].legend(handles=h, frameon=False, fontsize=5.5, loc="lower left", ncol=2)
fig.tight_layout()
save(fig, "fig2_numerics.png")
