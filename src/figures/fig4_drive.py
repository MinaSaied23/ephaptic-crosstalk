"""Fig. 4 - Anatomy of the ephaptic drive (NavC, production configuration).
Data: e13_waveforms.npz."""
import os
import numpy as np
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
W = np.load(os.path.join(D, "e13_waveforms.npz"))
key = "NavC_n10"
z = W[f"{key}__z"] * 1e3
tm = W[f"{key}__t_map"] * 1e3
ue = W[f"{key}__ue_map"]
dv = W[f"{key}__dv_map"]
t = W[f"{key}__t"] * 1e3
dv_peak = W[f"{key}__dv_peak"]
zp = W[f"{key}__peak_z_mm"][0]
tp = W[f"{key}__peak_t_ms"][0]

fig = plt.figure(figsize=(7.2, 4.6))
gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.42)

ax = fig.add_subplot(gs[0, 0])
lim = np.abs(ue).max()
im = ax.pcolormesh(z, tm, ue, cmap="PuOr_r", shading="auto", vmin=-lim, vmax=lim, rasterized=True)
ax.set_xlabel("z (mm)"); ax.set_ylabel("time (ms)"); ax.set_title("u$_e$ (mV), n = 10", fontsize=8)
fig.colorbar(im, ax=ax, fraction=0.05)
ax.axvline(2.5, color="k", lw=0.5, ls="--"); ax.axvline(7.5, color="k", lw=0.5, ls="--")
panel(ax, "a")

ax = fig.add_subplot(gs[0, 1])
lim = np.abs(dv).max()
im = ax.pcolormesh(z, tm, dv, cmap="RdBu_r", shading="auto", vmin=-lim, vmax=lim, rasterized=True)
ax.set_xlabel("z (mm)"); ax.set_title("C-fiber ΔV (mV), n = 10", fontsize=8)
fig.colorbar(im, ax=ax, fraction=0.05)
ax.axvline(2.5, color="k", lw=0.5, ls="--"); ax.axvline(7.5, color="k", lw=0.5, ls="--")
panel(ax, "b")

ax = fig.add_subplot(gs[0, 2])
ax.plot(z, W[f"{key}__dv_profile"], color=COL["NavC"], label="C-fiber ΔV")
ax.plot(z, -W[f"{key}__ue_profile"], color=COL["ue"], ls="--", label="−u$_e$")
ax.set_xlim(zp - 1.2, zp + 1.2); ax.axhline(0, color="k", lw=0.4)
ax.set_xlabel("z (mm)"); ax.set_ylabel("mV")
ax.set_title(f"profile at t = {tp:.3f} ms", fontsize=8)
ax.legend(frameon=False, fontsize=6.5)
panel(ax, "c")

ax = fig.add_subplot(gs[1, 0])
for n, c in ((1, "#888888"), (10, "#1f77b4"), (25, "#d62728")):
    kk = f"NavC_n{n}"
    ax.plot(W[f"{kk}__t"] * 1e3, W[f"{kk}__dv_peak"], color=c,
            label=f"n = {n} (z = {W[f'{kk}__peak_z_mm'][0]:.2f} mm)")
ax.set_xlim(0, 1.0); ax.axhline(0, color="k", lw=0.4)
ax.set_xlabel("time (ms)"); ax.set_ylabel("C-fiber ΔV at peak site (mV)")
ax.legend(frameon=False, fontsize=6)
panel(ax, "d")

ax = fig.add_subplot(gs[1, 1])
half = dv_peak.max() / 2
above = t[dv_peak >= half]
ax.plot(t, dv_peak, color=COL["NavC"])
ax.axhline(half, color=COL["grey"], lw=0.5, ls=":")
ax.set_xlim(tp - 0.4, tp + 0.6)
ax.set_xlabel("time (ms)"); ax.set_ylabel("ΔV (mV)")
ax.set_title(f"n = 10: FWHM {1e3 * (above.max() - above.min()):.0f} µs", fontsize=8)
panel(ax, "e")

ax = fig.add_subplot(gs[1, 2])
nz = W[f"{key}__node_z_mm"]
j = int(np.argmin(np.abs(nz - zp)))
ax.plot(t, W[f"{key}__v1_nodes"][:, j], color=COL["abeta"])
ax2 = ax.twinx()
ax2.plot(t, dv_peak, color=COL["NavC"], lw=1)
ax2.spines["right"].set_visible(True)
ax.set_xlim(0, 1.0); ax.set_xlabel("time (ms)")
ax.set_ylabel(f"Aβ V$_m$ at z = {nz[j]:.0f} mm (mV)", color=COL["abeta"])
ax2.set_ylabel("C-fiber ΔV (mV)", color=COL["NavC"])
panel(ax, "f")
save(fig, "fig4_drive.png")
