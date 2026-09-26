import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base_dir = os.path.dirname(__file__)
phase2_dir = os.path.join(base_dir, 'phase2_nav18_nav19')
if phase2_dir not in sys.path:
    sys.path.insert(0, phase2_dir)

from navc_cable import run_navc_alone, estimate_cv
from coupled_navc_model import run_coupled_navc
from ephaptic_model import dz

# ---------------------------------------------------------------------------
# Physiological coupling parameter used uniformly across all Phase 2
# experiments (calibrated to produce 2–4 mV nodal extracellular perturbations
# consistent with volume-conductor estimates; Goldwyn & Rinzel, 2016).
KAPPA = 1.0e9   # m^-2  (lambda_e ≈ 32 µm)
# ---------------------------------------------------------------------------

def generate_fig3():
    plt.rcParams.update({
        'font.size': 9,
        'font.family': 'serif',
        'axes.labelsize': 10,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 8
    })

    # -----------------------------------------------------------------------
    # Panel (a): Nav1.8/Nav1.9 C-fiber isolated conduction (positive control)
    # -----------------------------------------------------------------------
    print("Running Nav1.8/Nav1.9 single-fiber simulation (40 ms window)...")
    dt = 2.5e-6
    T_control = 40.0e-3
    v_rec = run_navc_alone(T=T_control, stim_amp=2e-9, stim_dur=1e-3, dt=dt)
    cv = estimate_cv(v_rec, dz, dt, 100, 900)
    print(f"  Nav1.8/1.9 Conduction Velocity: {cv:.2f} m/s")

    t_control = np.arange(v_rec.shape[0]) * dt * 1e3

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # Panel (a): Positive control
    ax0 = axes[0]
    locs = [1, 3, 5, 7, 9]
    colors_c = plt.cm.viridis(np.linspace(0.1, 0.9, len(locs)))
    for z_mm, col in zip(locs, colors_c):
        idx = int(z_mm * 1e-3 / dz)
        ax0.plot(t_control, v_rec[:, idx] * 1e3, label=f'z={z_mm} mm', color=col, lw=1.5)

    ax0.set_title(f'(a) Nav1.8/1.9 C-fiber conduction (CV ≈ {cv:.2f} m/s)')
    ax0.set_xlabel('Time (ms)')
    ax0.set_ylabel('Membrane potential (mV)')
    ax0.set_xlim(0, 40.0)
    ax0.set_ylim(-80, 50)
    ax0.legend(loc='upper right', framealpha=0.9, fontsize=7.5)
    ax0.spines['top'].set_visible(False)
    ax0.spines['right'].set_visible(False)

    # -----------------------------------------------------------------------
    # Panel (b): Coupled C-fiber midpoint membrane potential over time
    # Showing subthreshold depolarization "humps" across n in [1, 5, 10, 25]
    # -----------------------------------------------------------------------
    ax1 = axes[1]
    ns_hump = [1, 5, 10, 25]
    colors_hump = plt.cm.coolwarm(np.linspace(0.1, 0.9, len(ns_hump)))
    
    print("\nRunning coupled C-fiber temporal traces for subthreshold humps...")
    t_hump = None
    for n_val, col in zip(ns_hump, colors_hump):
        res_hump = run_coupled_navc(
            w_cleft=20e-9,
            n_abeta=n_val,
            jitter_ms=0.0,
            kappa=KAPPA,
            T=4.0e-3,
            stim_amp=100e-9,
            stim_dur=0.2e-3
        )
        if t_hump is None:
            t_hump = np.arange(len(res_hump['v2_mid'])) * 1e-6 * 1e3
        v2_trace = res_hump['v2_mid'] * 1e3
        v_rest_actual = v2_trace[0]
        v_pk = v2_trace.max()
        dv = v_pk - v_rest_actual
        ax1.plot(t_hump, v2_trace, label=f'n={n_val} (peak: {v_pk:.1f} mV, +{dv:.1f} mV)', color=col, lw=1.6)

    ax1.axhline(-35.0, color='crimson', linestyle='--', lw=1.2, label='AP Threshold (-35 mV)')
    ax1.axhline(v_rest_actual, color='gray', linestyle=':', lw=1.2, label=f'Rest ({v_rest_actual:.1f} mV)')
    ax1.set_title('(b) Coupled C-fiber: subthreshold depolarization')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Midpoint potential $V_m$ (mV)')
    ax1.set_xlim(0, 4.0)
    ax1.set_ylim(-72, -30)
    ax1.legend(loc='upper right', framealpha=0.9, fontsize=7.5)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # -----------------------------------------------------------------------
    # Panel (c): Multi-fiber spatial summation trend (n in 1..25)
    # Fixed ylim logic so all data points and baseline are fully visible.
    # -----------------------------------------------------------------------
    ax2 = axes[2]
    ns = [1, 2, 3, 5, 8, 15, 25]
    peaks = []

    print(f"\nRunning multi-fiber sweep n={ns} at kappa={KAPPA:.1e} m^-2 ...")
    for n in ns:
        res = run_coupled_navc(
            w_cleft=20e-9,
            n_abeta=n,
            jitter_ms=0.0,
            kappa=KAPPA,
            T=3e-3,
            stim_amp=100e-9,
            stim_dur=0.2e-3
        )
        peak_mv = res['v2_mid'].max() * 1e3
        peaks.append(peak_mv)
        print(f"  n={n:3d} -> midpoint peak = {peak_mv:.2f} mV  (spiked={res['spiked']})")

    ns_arr = np.array(ns)
    peaks_arr = np.array(peaks)
    v_rest = v_rest_actual   # settled resting potential (mV)

    ax2.axhline(-35.0, color='crimson', linestyle='--', lw=1.2, label='AP Threshold (-35 mV)')
    ax2.axhline(v_rest, color='gray', linestyle=':', lw=1.2, label=f'Rest ({v_rest:.1f} mV)')
    ax2.plot(ns_arr, peaks_arr, marker='o', color='#1f4e78', lw=1.8, ms=6,
             label=f'Peak potential (κ = {KAPPA:.0e} m⁻²)')

    ax2.set_title('(c) Multi-fiber spatial summation')
    ax2.set_xlabel('Number of synchronized Aβ fibers (n)')
    ax2.set_ylabel('Peak C-fiber potential (mV)')
    ax2.set_xlim(0, 26)
    ax2.set_ylim(-72, -30)   # Cleanly accommodates rest (-66.8 mV), peaks (-65 to -56.3 mV), and threshold (-35 mV)
    ax2.legend(loc='lower right', framealpha=0.9, fontsize=7.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    out_dir = os.path.join(base_dir, '..', 'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig3_phase2_control.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"\nSaved {out_path}")
    print(f"\nFig 3b summary (kappa={KAPPA:.1e}):")
    for n, p in zip(ns, peaks):
        print(f"  n={n}: {p:.2f} mV")

if __name__ == '__main__':
    generate_fig3()
