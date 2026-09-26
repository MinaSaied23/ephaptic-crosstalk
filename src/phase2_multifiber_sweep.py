import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.dirname(__file__)
phase2_dir = os.path.join(base_dir, 'phase2_nav18_nav19')
if phase2_dir not in sys.path:
    sys.path.insert(0, phase2_dir)
from coupled_navc_model import run_coupled_navc

# ---------------------------------------------------------------------------
# Coupling parameter — same value used across all Phase 2 experiments.
# Calibrated to produce 2–4 mV nodal extracellular perturbations consistent
# with volume-conductor estimates (Goldwyn & Rinzel, 2016).
# kappa = 1e9 m^-2 corresponds to a field decay space constant lambda_e ≈ 32 µm.
KAPPA = 1.0e9  # m^-2
# ---------------------------------------------------------------------------

def run_multifiber_sweep():
    # Multi-fiber bundle sweep across n in [1, 50] comparing synchronous vs jittered recruitment.
    ns = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50]
    jitter_vals = [0.0, 1.5]

    results = {j: [] for j in jitter_vals}

    for j in jitter_vals:
        print(f"\nRunning sweep with jitter_ms={j}, kappa={KAPPA:.1e} m^-2")
        for n in ns:
            res = run_coupled_navc(
                w_cleft=20e-9,
                n_abeta=n,
                jitter_ms=j,
                kappa=KAPPA,   # EXPLICIT — never relying on function default
                T=3e-3
            )
            spiked = res['spiked']
            v_peak = res['v2_mid'].max()
            results[j].append((n, spiked, v_peak))
            print(f"  n={n:3d} -> spiked: {spiked}, midpoint peak: {v_peak*1000:.2f} mV")

    # Plotting
    fig, ax = plt.subplots(figsize=(7, 5))
    for j in jitter_vals:
        res = np.array(results[j])
        n_vals = res[:, 0]
        spiked_vals = res[:, 1]

        threshold_idx = np.where(spiked_vals)[0]
        threshold_n = n_vals[threshold_idx[0]] if len(threshold_idx) > 0 else np.nan
        print(f"Jitter {j} ms threshold: n = {threshold_n}")

        label = f'Jitter = {j} ms' + ('' if np.isnan(threshold_n) else f'  (threshold n={threshold_n:.0f})')
        ax.plot(n_vals, res[:, 2] * 1000, marker='o', lw=1.8, label=label)

    ax.axhline(-35.0, color='crimson', linestyle='--', lw=1.2, label='Nav1.8 Threshold (-35 mV)')
    ax.axhline(0, color='darkred', linestyle=':', lw=1.0, label='Overshoot (0 mV)')
    ax.axhline(-66.82, color='gray', linestyle=':', lw=1.2, label='Unperturbed rest (-66.8 mV)')
    ax.set_xlabel('Number of Synchronized A\u03b2 Fibers (n)')
    ax.set_ylabel('Peak C-Fiber Midpoint Voltage (mV)')
    ax.set_title(f'Multi-Fiber Bundle Crosstalk: Synchronous vs Jittered\n'
                 f'($w_{{\\mathrm{{cleft}}}}$ = 20 nm, $\\kappa$ = {KAPPA:.0e} m$^{{-2}}$)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    out_dir = os.path.join(base_dir, '..', 'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'phase2_multifiber_sweep.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"\nSaved {out_path}")

if __name__ == "__main__":
    run_multifiber_sweep()
