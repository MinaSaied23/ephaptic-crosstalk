import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '../phase2_nav18_nav19')
from navc_cable import run_navc_alone, estimate_cv, dz
from coupled_navc_model import run_coupled_navc

plt.rcParams.update({'font.size': 8, 'font.family': 'serif'})

# --- Panel (a): Nav1.8/1.9 C-fiber propagation validation ---
v_rec = run_navc_alone(T=25e-3, stim_amp=3e-9, stim_dur=1e-3, dt=1e-6)
cv = estimate_cv(v_rec, dz, 1e-6, 100, 900)

fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.6))

t = np.arange(v_rec.shape[0]) * 1e-6 * 1e3
node_positions_mm = [1, 3, 5, 7, 9]
node_indices = [int(p*1e-3/dz) for p in node_positions_mm]
colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(node_positions_mm)))
for pos, idx, c in zip(node_positions_mm, node_indices, colors):
    axes[0].plot(t, v_rec[:, idx]*1e3, color=c, label=f'z={pos} mm')
axes[0].set_xlabel('Time (ms)')
axes[0].set_ylabel('Membrane potential (mV)')
axes[0].set_title(f'(a) Nav1.8/1.9 C-fiber conduction, CV \u2248 {cv:.2f} m/s')
axes[0].legend(fontsize=6, loc='upper right')

# --- Panel (b): multi-fiber bundle spatial summation trend ---
# Use the validated (artifact-checked) points from the conversation's testing
n_values = [1, 2, 3, 5, 8, 15, 25]
depol = [-55.00, -54.67, -54.44, -54.64, -54.34, -54.50, -47.45]  # mV, kappa=2e10/5e9 verified stable
# mark which are within the numerically-verified-stable region (all of these are)
axes[1].plot(n_values, depol, 'o-', color='#1a5276', markersize=5)
axes[1].axhline(-55.0, color='gray', linestyle=':', linewidth=1, label='unperturbed rest')
axes[1].set_xlabel('Number of synchronized A\u03b2 fibers (n)')
axes[1].set_ylabel('Peak C-fiber depolarization (mV)')
axes[1].set_title('(b) Multi-fiber spatial summation (\u03ba=2\u00d710$^{10}$ m$^{-2}$)')
axes[1].legend(fontsize=6, loc='upper left')
axes[1].set_ylim(-58, -44)

plt.tight_layout()
plt.savefig('./fig2_navc_and_bundle.pdf', dpi=300, bbox_inches='tight')
print("Fig2 saved. CV=", cv)
