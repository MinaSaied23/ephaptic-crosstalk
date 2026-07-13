import sys
sys.path.insert(0, '../phase1_classical_hh')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from validate_single_fibers import run_abeta_alone, run_cfiber_alone, estimate_conduction_velocity
from ephaptic_model import dz, dt, N

plt.rcParams.update({'font.size': 8, 'font.family': 'serif'})

v1 = run_abeta_alone(T=1e-3, stim_amp=100e-9, stim_dur=0.2e-3)
v2 = run_cfiber_alone(T=20e-3, stim_amp=1e-9, stim_dur=1e-3)

cv1 = estimate_conduction_velocity(v1, dz, dt, 100, 900)
cv2 = estimate_conduction_velocity(v2, dz, dt, 100, 900)

fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.6))

t1 = np.arange(v1.shape[0]) * dt * 1e3
node_positions_mm = [1, 3, 5, 7, 9]
node_indices = [int(p*1e-3/dz) for p in node_positions_mm]
colors1 = plt.cm.viridis(np.linspace(0.15, 0.9, len(node_indices)))
for idx, c, p in zip(node_indices, colors1, node_positions_mm):
    axes[0].plot(t1, v1[:, idx]*1e3, color=c, lw=1.1, label=f'z={p} mm')
axes[0].set_xlabel('Time (ms)')
axes[0].set_ylabel('Membrane potential (mV)')
axes[0].set_title(f'(a) A\u03b2 saltatory conduction, CV \u2248 {cv1:.1f} m/s', fontsize=8)
axes[0].legend(fontsize=6, loc='upper right', framealpha=0.9)
axes[0].set_xlim(0, 1.0)

t2 = np.arange(v2.shape[0]) * dt * 1e3
pos_mm2 = [1, 3, 5, 7, 9]
idx2 = [int(p*1e-3/dz) for p in pos_mm2]
colors2 = plt.cm.plasma(np.linspace(0.15, 0.85, len(idx2)))
for idx, c, p in zip(idx2, colors2, pos_mm2):
    axes[1].plot(t2, v2[:, idx]*1e3, color=c, lw=1.1, label=f'z={p} mm')
axes[1].set_xlabel('Time (ms)')
axes[1].set_ylabel('Membrane potential (mV)')
axes[1].set_title(f'(b) C-fiber continuous conduction, CV \u2248 {cv2:.2f} m/s', fontsize=8)
axes[1].legend(fontsize=6, loc='upper right', framealpha=0.9)
axes[1].set_xlim(0, 20)

for ax in axes:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('./fig1_validation.pdf', dpi=300, bbox_inches='tight')
print('Fig1 saved. CV1=', cv1, 'CV2=', cv2)
