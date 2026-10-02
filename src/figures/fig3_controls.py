"""Fig. 3 - Uncoupled positive controls (data: e13_waveforms.npz, e01_*.csv)."""
import os
import numpy as np
import pandas as pd
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
W = np.load(os.path.join(D, "e13_waveforms.npz"))
ab = pd.read_csv(os.path.join(D, "e01_abeta_control.csv")).iloc[0]
cc = pd.read_csv(os.path.join(D, "e01_cfiber_controls.csv")).set_index("variant")

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.3))
ax = axs[0]
t = W["ctrl_abeta__t"] * 1e3
v = W["ctrl_abeta__v1"]
z = W["ctrl_abeta__z"][::200]
cmap = plt.get_cmap("Greens")
for j in range(1, v.shape[1]):
    ax.plot(t, v[:, j], color=cmap(0.35 + 0.6 * j / v.shape[1]), lw=0.9)
ax.set_xlim(0, 0.6); ax.set_xlabel("time (ms)"); ax.set_ylabel("V$_m$ (mV)")
ax.set_title(f"Aβ, nodes z = 1–9 mm\n{ab.stim_nA:.2f} nA (2× threshold): CV {ab.cv_4_8mm_m_s:.1f} m/s", fontsize=7.5)
panel(ax, "a")

for ax, kind, key, letter in ((axs[1], "HH", "HH_phi1_gNa120", "b"), (axs[2], "NavC", "NavC_tm8_1.5ms_g18_2000", "c")):
    t = W[f"ctrl_{kind}__t"] * 1e3
    v = W[f"ctrl_{kind}__v2"]
    cm = plt.get_cmap("Blues" if kind == "HH" else "Reds")
    for j in range(1, v.shape[1]):
        ax.plot(t, v[:, j], color=cm(0.35 + 0.6 * j / v.shape[1]), lw=0.9)
    r = cc.loc[key]
    name = "HH C-fiber (6.3 °C)" if kind == "HH" else "Nav1.8/1.9 C-fiber"
    ax.set_title(f"{name}, z = 1–9 mm\nCV {r.cv_m_s:.2f} m/s, rest {r.rest_mV:.2f} mV", fontsize=7.5)
    ax.set_xlabel("time (ms)")
    ax.set_xlim(0, 30)
    panel(ax, letter)
fig.tight_layout()
save(fig, "fig3_controls.png")
