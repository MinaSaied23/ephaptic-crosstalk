"""Fig. 7 - Sensitivity maps (data: e05_kappa, e06_kinetics, e10_bias)."""
import os
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
k5 = pd.read_csv(os.path.join(D, "e05_kappa.csv"))
k6 = pd.read_csv(os.path.join(D, "e06_kinetics.csv"))
b10 = pd.read_csv(os.path.join(D, "e10_bias.csv"))

fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7), gridspec_kw=dict(width_ratios=[1.15, 1.25, 1.0]))

# (a) kappa x n map, NavC
ax = axs[0]
d = k5[k5.model == "NavC"]
P = d.pivot_table(index="kappa", columns="n_abeta", values="dv_lesion_mV")
C = d.pivot_table(index="kappa", columns="n_abeta", values="ab_conducts", aggfunc="first").astype(bool)
S = d.pivot_table(index="kappa", columns="n_abeta", values="c_spike", aggfunc="first").astype(bool)
im = ax.imshow(P.values, origin="lower", aspect="auto", cmap="viridis", vmin=0, vmax=35)
for i in range(P.shape[0]):
    for j in range(P.shape[1]):
        ax.text(j, i, f"{P.values[i, j]:.0f}", ha="center", va="center", fontsize=5.5,
                color="w" if P.values[i, j] < 22 else "k")
        if not C.values[i, j]:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, hatch="////", ec="#ffffff55", lw=0))
        if S.values[i, j]:
            ax.plot(j, i, "r*", ms=8)
ax.set_xticks(range(P.shape[1])); ax.set_xticklabels(P.columns)
ax.set_yticks(range(P.shape[0])); ax.set_yticklabels([f"{k:.0e}".replace("e+0", "e") for k in P.index], fontsize=6)
ax.set_xlabel("n"); ax.set_ylabel("κ (m$^{-2}$)")
ax.set_title("NavC: peak ΔV (mV)\nhatched: Aβ conduction fails in lesion", fontsize=7.5, pad=8)
fig.colorbar(im, ax=ax, fraction=0.05)
panel(ax, "a")

# (b) kinetics x n map at kappa = 1e9: max dV or spike
ax = axs[1]
d = k6[k6.kappa == 1e9].copy()
order = [("HH_temperature", 6.3), ("HH_temperature", 15.0), ("HH_temperature", 25.0),
         ("HH_gscale", 5.0), ("HH_gscale", 10.0),
         ("HH_speed", 2.0), ("HH_speed", 3.0), ("HH_speed", 4.0), ("HH_speed", 5.0), ("HH_speed", 7.0), ("HH_speed", 10.0),
         ("NavC_tau_m8", 1.5), ("NavC_tau_m8", 0.2), ("NavC_tau_m8", 0.05),
         ("NavC_speed", 2.0), ("NavC_speed", 5.0), ("NavC_speed", 10.0)]
labels = {"HH_temperature": "HH {v:g} °C", "HH_gscale": "HH g×{v:g}", "HH_speed": "HH rates&g×{v:g}",
          "NavC_tau_m8": "NavC τm8 {v:g} ms", "NavC_speed": "NavC τ/{v:g}, g×{v:g}"}
ns = sorted(d.n_abeta.unique())
M = np.full((len(order), len(ns)), np.nan); SP = np.zeros_like(M, dtype=bool)
for i, (fam, v) in enumerate(order):
    for j, n in enumerate(ns):
        r = d[(d.family == fam) & (np.isclose(d.value, v)) & (d.n_abeta == n)]
        if len(r):
            M[i, j] = r.dv_lesion_mV.values[0]; SP[i, j] = bool(r.c_spike.values[0])
Mp = np.where(SP, np.nan, M)
im = ax.imshow(Mp, origin="lower", aspect="auto", cmap="viridis", vmin=0, vmax=35)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        if SP[i, j]:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#d62728"))
ax.set_xticks(range(len(ns))); ax.set_xticklabels(ns, fontsize=5.5, rotation=90)
ax.set_yticks(range(len(order))); ax.set_yticklabels([labels[f].format(v=v) for f, v in order], fontsize=5.5)
ax.set_xlabel("n")
ax.set_title("kinetic variants (κ = 10$^9$ m$^{-2}$)\nsame colour scale as (a); red: propagating C-fiber AP", fontsize=7.5, pad=8)
panel(ax, "b")

# (c) bias
ax = axs[2]
for kind, mk in (("NavC", "s"), ("HH", "o")):
    d = b10[(b10.model == kind) & (b10.control != "no_stimulus")]
    for n, ls in ((1, ":"), (25, "-"), (100, "--")):
        dd = d[d.n_abeta == n].sort_values("bias_A_m2")
        ax.plot(dd.bias_A_m2, dd.v2_peak_lesion_mV, ls=ls, marker=mk, ms=2.5, color=COL[kind],
                label=f"{kind}, n = {n}")
        sp = dd[dd.c_spike.astype(bool)]
        ax.plot(sp.bias_A_m2, sp.v2_peak_lesion_mV, "r*", ms=7)
ax.set_xscale("symlog", linthresh=0.01)
ax.set_xlabel("C-fiber bias (A m$^{-2}$)"); ax.set_ylabel("peak C-fiber V$_m$ in lesion (mV)")
ax.set_title("sensitized C-fiber\n(no propagating AP in any run)", fontsize=7.5, pad=8)
ax.legend(frameon=False, fontsize=5.5, ncol=1)
panel(ax, "c")
fig.tight_layout()
save(fig, "fig7_sensitivity.png")
