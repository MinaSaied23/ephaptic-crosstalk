"""Fig. S3 - Abeta gating, action-potential waveform and recovery (data: e14_*)."""
import os
import pandas as pd
from style import plt, save, COL, panel, ROOT

D = os.path.join(ROOT, "results", "data")
g = pd.read_csv(os.path.join(D, "e14_abeta_gates.csv"))
tr = pd.read_csv(os.path.join(D, "e14_abeta_ap_trace.csv"))
pp = pd.read_csv(os.path.join(D, "e14_abeta_paired_pulse.csv")).sort_values("isi_ms")

fig, axs = plt.subplots(1, 4, figsize=(7.4, 2.1))

ax = axs[0]
ax.plot(g.v_mV, g.m_inf, "-", color="#1f77b4", label="m$_\\infty$")
ax.plot(g.v_mV, g.h_inf, "-", color="#d62728", label="h$_\\infty$")
ax.set_xlabel("membrane potential (mV)"); ax.set_ylabel("steady state")
ax.set_ylim(-0.03, 1.03)
ax.legend(frameon=False, fontsize=7)
panel(ax, "a")

ax = axs[1]
ax.plot(g.v_mV, g.tau_m_ms * 1e3, "-", color="#1f77b4", label="τ$_m$")
ax.plot(g.v_mV, g.tau_h_ms * 1e3, "-", color="#d62728", label="τ$_h$")
ax.set_xlabel("membrane potential (mV)"); ax.set_ylabel("time constant (µs)")
ax.legend(frameon=False, fontsize=7)
panel(ax, "b")

ax = axs[2]
ax.plot(tr.t_ms, tr.v_node_mV, "-", color=COL.get("abeta", "#2ca02c"))
ax.axhline(tr.v_node_mV.iloc[0], color="#999999", lw=0.5, ls=":")
ax.set_xlabel("time (ms)"); ax.set_ylabel("V$_m$ at z = 5 mm (mV)")
ax.set_xlim(0, 2.0)
panel(ax, "c")

ax = axs[3]
ok = pp[pp.second_conducts]
no = pp[~pp.second_conducts]
ax.plot(ok.isi_ms, ok.peak2_mV, "-o", ms=3.5, color="#d62728", label="2nd AP conducts")
ax.plot(no.isi_ms, no.peak2_mV, "x", ms=5, color="#777777", label="blocked")
ax.axhline(pp.peak1_mV.iloc[0], color="#999999", lw=0.5, ls=":")
ax.set_xlabel("interpulse interval (ms)"); ax.set_ylabel("2nd AP peak at z = 8 mm (mV)")
ax.set_xscale("log")
ax.legend(frameon=False, fontsize=6.5, loc="lower right")
panel(ax, "d")

fig.tight_layout()
save(fig, "figS3_membrane_verification.png")
