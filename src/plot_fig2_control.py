import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base_dir = os.path.dirname(__file__)
phase1_dir = os.path.join(base_dir, 'phase1_classical_hh')
if phase1_dir not in sys.path:
    sys.path.insert(0, phase1_dir)

from validate_single_fibers import run_abeta_alone, run_cfiber_alone, estimate_conduction_velocity
from ephaptic_model import dz, dt

def generate_fig2():
    plt.rcParams.update({
        'font.size': 9,
        'font.family': 'serif',
        'axes.labelsize': 10,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 8
    })

    print("Running Aβ single-fiber simulation...")
    # 2 nA, 0.2 ms: threshold-level drive used for all uncoupled Aβ validation
    # (Table 5, convergence battery, Crank-Nicolson audit). The 100 nA drive used in
    # the coupled bundle runs saturates node 0 (> +780 mV) and is not a positive control.
    v1, _ = run_abeta_alone(T=5.0e-3, stim_amp=2e-9, stim_dur=0.2e-3)
    # A-beta CV: maximum upstroke rate (dV/dt) between z = 4 mm and z = 8 mm,
    # the same metric used in the manuscript and convergence study (41.03 m/s)
    dv1 = np.diff(v1, axis=0) / dt
    i4, i8 = int(round(4.0e-3 / dz)), int(round(8.0e-3 / dz))
    cv1 = (i8 - i4) * dz / ((np.argmax(dv1[:, i8]) - np.argmax(dv1[:, i4])) * dt)
    print(f"  Aβ Conduction Velocity: {cv1:.2f} m/s")

    print("Running C-fiber single-fiber simulation...")
    v2, _ = run_cfiber_alone(T=40.0e-3, stim_amp=1e-9, stim_dur=1e-3)
    cv2 = estimate_conduction_velocity(v2, dz, dt, 100, 900)
    print(f"  C-fiber Conduction Velocity: {cv2:.2f} m/s")

    t1 = np.arange(v1.shape[0]) * dt * 1e3
    t2 = np.arange(v2.shape[0]) * dt * 1e3

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Panel (a): Aβ saltatory conduction
    ax = axes[0]
    locs = [1, 3, 5, 7, 9]
    colors_abeta = plt.cm.viridis(np.linspace(0.1, 0.9, len(locs)))
    for z_mm, col in zip(locs, colors_abeta):
        idx = int(z_mm * 1e-3 / dz)
        ax.plot(t1, v1[:, idx] * 1e3, label=f'z={z_mm} mm', color=col, lw=1.6)

    ax.set_title(f'(a) Aβ saltatory conduction, CV ≈ {cv1:.1f} m/s')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Membrane potential (mV)')
    ax.set_xlim(0, 1.5)
    ax.set_ylim(-85, 25)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Panel (b): C-fiber continuous conduction
    ax = axes[1]
    colors_c = plt.cm.plasma(np.linspace(0.1, 0.9, len(locs)))
    for z_mm, col in zip(locs, colors_c):
        idx = int(z_mm * 1e-3 / dz)
        ax.plot(t2, v2[:, idx] * 1e3, label=f'z={z_mm} mm', color=col, lw=1.6)

    ax.set_title(f'(b) C-fiber continuous conduction, CV ≈ {cv2:.2f} m/s')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Membrane potential (mV)')
    ax.set_xlim(0, 40.0)
    ax.set_ylim(-85, 45)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out_dir = os.path.join(base_dir, '..', 'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig2_phase1_control.png')
    plt.savefig(out_path, dpi=300)
    print(f"Successfully generated clean {out_path}")

if __name__ == '__main__':
    generate_fig2()
