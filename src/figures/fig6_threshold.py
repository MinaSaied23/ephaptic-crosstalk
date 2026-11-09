"""Fig. 6 - Excitability of the C-fiber for brief, local inputs (data: e07_*).

Top row: strength-duration curves, voltage reached without firing, and the gain threshold
alpha* of the recorded ephaptic waveform.  Bottom row: space-time traces of replays of the
recorded waveform (NavC): at n = 25 with the gain the earlier span-only rule had accepted as
threshold (overshoots under single nodes that do not propagate), and at the gain threshold of
the propagation criterion for n = 25 and 50.  Dots: first crossing of 0 mV at each position.
"""
import os
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from style import plt, save, COL, ROOT

D = os.path.join(ROOT, "results", "data")
sd = pd.read_csv(os.path.join(D, "e07_strength_duration.csv"))
sf = pd.read_csv(os.path.join(D, "e07_safety_factor.csv"))
TR = np.load(os.path.join(D, "e07_replay_traces.npz"))

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
ORDER = list(NAMES)


def name(v):
    return NAMES.get(v, (v, "k", "-"))


def front_cv(tc_ms, z_mm):
    """Outward front velocity (m/s) over the outermost 1 mm, on the side(s) that meet the
    criterion's 0.05-5 m/s window (the first-crossing time at the inner point can belong to an
    earlier, local overshoot under a node, which makes the other side's estimate meaningless)."""
    ok = np.isfinite(tc_ms)
    idx = np.where(ok)[0]
    k = int(round(1.0 / (z_mm[1] - z_mm[0])))
    cvs = []
    for outer, inner in ((idx[-1], idx[-1] - k), (idx[0], idx[0] + k)):
        if 0 <= inner < len(tc_ms) and ok[inner] and tc_ms[outer] > tc_ms[inner]:
            cvs.append(abs(z_mm[outer] - z_mm[inner]) / (tc_ms[outer] - tc_ms[inner]))
    good = [c for c in cvs if 0.05 <= c <= 5.0]
    return max(good) if good else float("nan")


def letter(fig, ax, s):
    bb = ax.get_tightbbox(fig.canvas.get_renderer())
    inv = fig.transFigure.inverted()
    x0 = inv.transform((bb.x0, 0))[0]
    y1 = inv.transform((0, ax.get_window_extent().y1))[1]
    fig.text(x0 - 0.004, y1 + 0.012, s, fontsize=10, fontweight="bold", ha="right", va="bottom")


fig = plt.figure(figsize=(7.2, 5.6))
gs = GridSpec(3, 3, figure=fig, height_ratios=[1.0, 0.16, 1.0], hspace=0.55, wspace=0.62)
top = [fig.add_subplot(gs[0, j]) for j in range(3)]
bot = [fig.add_subplot(gs[2, j]) for j in range(3)]
pt = sd[sd["mode"] == "point"]

ax = top[0]
for v in ORDER:
    d = pt[pt.variant == v].sort_values("duration_ms")
    lab, c, ls = name(v)
    ax.plot(d.duration_ms, d.threshold * 1e9, ls=ls, color=c, marker="o", ms=2.5, label=lab)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("pulse duration (ms)"); ax.set_ylabel("threshold current (nA)")
ax.set_title("point injection, z = 5 mm", fontsize=8, pad=6)
ax.axvspan(0.07, 0.16, color="#f3e6f7", zorder=0)

ax = top[1]
for v in ORDER:
    d = pt[pt.variant == v].sort_values("duration_ms")
    lab, c, ls = name(v)
    ax.plot(d.duration_ms, d.v_peak_subthreshold_mV, ls=ls, color=c, marker="o", ms=2.5, label=lab)
ax.set_xscale("log")
ax.axhline(0.0, color="k", lw=0.5, ls=":")
ax.axvspan(0.07, 0.16, color="#f3e6f7", zorder=0)
ax.annotate("ephaptic\nFWHM", xy=(0.11, 0.62), xycoords=("data", "axes fraction"), xytext=(14, 10),
            textcoords="offset points", fontsize=6, ha="left", va="center", color=COL["ue"],
            arrowprops=dict(arrowstyle="-", color=COL["ue"], lw=0.6))
ax.set_xlabel("pulse duration (ms)"); ax.set_ylabel("peak V$_m$ 0.5 % below threshold (mV)", fontsize=7)
ax.set_title("voltage reached, no AP", fontsize=8, pad=6)

ax = top[2]
d0 = sf[sf.c_bias == 0]
for v in ORDER:
    d = d0[d0.variant == v].sort_values("n_abeta")
    lab, c, ls = name(v)
    ax.plot(d.n_abeta, d.alpha_star, ls=ls, color=c, marker="o", ms=2.5, label=lab)
ax.axhline(1.0, color="k", lw=0.6)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("synchronous Aβ fibers n"); ax.set_ylabel("α* (gain on recorded u$_e$)")
ax.set_title("gain threshold α*", fontsize=8, pad=6)
ax.axvspan(25, 130, color="#eeeeee", zorder=0)
ax.text(27, 0.8, "Aβ conduction\nfails in lesion", fontsize=5.5, color="#555555", va="top",
        transform=ax.get_xaxis_transform())
h, l = top[0].get_legend_handles_labels()
lax = fig.add_subplot(gs[1, :]); lax.axis("off")
lax.legend(h, l, loc="center", ncol=4, frameon=False, fontsize=6.5)

cases = [("n25_fixed", "n = 25, α = {a:.2f}\n(span-only rule: 'fires')"),
         ("n25_at", "n = 25, α* = {a:.1f}"),
         ("n50_at", "n = 50, α* = {a:.1f}")]
im = None
for ax, (key, title) in zip(bot, cases):
    t = TR[f"{key}__t"] * 1e3
    z = TR[f"{key}__z"] * 1e3
    v = TR[f"{key}__v"]
    a = float(TR[f"{key}__alpha"][0])
    im = ax.pcolormesh(z, t, v, cmap="RdBu_r", vmin=-90, vmax=90, shading="auto", rasterized=True)
    tc = TR[f"{key}__t_cross"] * 1e3
    zf = np.arange(tc.size) * (z[1] - z[0]) / 4.0
    ok = np.isfinite(tc)
    step = 1 if key == "n25_fixed" else 4
    ax.plot(zf[ok][::step], tc[ok][::step], ".", color="k", ms=1.6 if key != "n25_fixed" else 3)
    for x in (2.5, 7.5):
        ax.axvline(x, color="k", lw=0.5, ls="--")
    sp = bool(TR[f"{key}__spike"][0])
    span = float(TR[f"{key}__span_mm"][0])
    note = (f"propagates, {front_cv(tc, zf):.2f} m/s" if sp else f"overshoot span {span:.2f} mm,\nno outward front")
    ax.text(0.03, 0.97, note, transform=ax.transAxes, fontsize=5.8, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_ylim(0, 1.0 if key == "n25_fixed" else 29); ax.set_xlim(0, 10)
    ax.set_xlabel("z (mm)"); ax.set_ylabel("time (ms)")
    ax.set_title(title.format(a=a), fontsize=7.5, pad=6)
cb = fig.colorbar(im, ax=bot, fraction=0.025, pad=0.02)
cb.set_label("C-fiber V$_m$ (mV)", fontsize=7)
fig.canvas.draw()
for ax, s in zip(top + bot, "abcdef"):
    letter(fig, ax, s)
save(fig, "fig6_threshold.png")
