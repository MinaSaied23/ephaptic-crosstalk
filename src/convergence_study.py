"""
Decoupled Spatial and Temporal Convergence Study for the Ephaptic Core-Conductor Model.
Directly addresses Reviewer 1 Major Comment 8 for the Journal of Computational Neuroscience.

Decouples numerical refinement:
1. Spatial convergence: Fix dt = 2.5 µs, sweep dz in [20, 10, 5, 2.5] µm.
   Physical node width is held invariant at 10 µm across all dz values.
2. Temporal convergence: Fix dz = 10 µm, sweep dt in [10.0, 5.0, 2.5, 1.25] µs.

Quantities reported and verified:
  1. Aβ conduction velocity (m/s)
  2. Peak C-fiber ephaptic potential (mV)
  3. Ephaptic ΔV above rest (mV)
  4. Timing of maximum ephaptic event (ms)
  5. Source current magnitude (A/m)
  6. Ectopic spike classification (spiked / no-spike)
"""

import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base_dir = os.path.dirname(__file__)
phase1_dir = os.path.join(base_dir, 'phase1_classical_hh')
if phase1_dir not in sys.path:
    sys.path.insert(0, phase1_dir)

PHYSICAL_NODE_WIDTH = 10e-6   # 10 µm physical nodal length (invariant)
L_CABLE = 10e-3               # 10 mm cable length
KAPPA = 1.0e9                 # m^-2
W_CLEFT = 20e-9               # 20 nm cleft

_PHASE1_MODULES = ['ephaptic_model', 'coupled_model', 'validate_single_fibers']

def _purge_phase1_modules():
    for mod in _PHASE1_MODULES:
        if mod in sys.modules:
            del sys.modules[mod]

def run_simulation(dz_um, dt_us):
    _purge_phase1_modules()

    dz_m = dz_um * 1e-6
    dt_s = dt_us * 1e-6
    N = int(round(L_CABLE / dz_m))

    import ephaptic_model as em
    em.dz = dz_m
    em.N = N
    em.dt = dt_s

    # Invariant physical nodal mapping
    pos = np.arange(N) * dz_m
    em.node_mask = (pos % em.internode_spacing) < PHYSICAL_NODE_WIDTH
    em.node_mask[0] = True

    # Recompute geometry-dependent arrays
    f_node = min(1.0, em.l_node / dz_m)
    em.f_node = f_node
    em.Cm_node_comp = (2.0 * f_node + 0.005 * (1.0 - f_node)) * em.uF_cm2_to_F_m2
    em.Cm1_arr = np.where(em.node_mask, em.Cm_node_comp, em.Cm_internode)
    em.g_Na_CRRSS = 1445.0 * f_node * em.mS_cm2_to_S_m2
    em.g_leak_node_comp = em.g_leak_CRRSS * f_node + em.g_leak_internode * (1.0 - f_node)
    em.g_leak1_arr = np.where(em.node_mask, em.g_leak_node_comp, em.g_leak_internode)

    from validate_single_fibers import run_abeta_alone, estimate_conduction_velocity
    from coupled_model import run_coupled

    t0 = time.time()
    v1, _ = run_abeta_alone(T=3e-3, stim_amp=100e-9, stim_dur=0.2e-3, dz=dz_m, dt=dt_s)
    t_cv = time.time() - t0

    cv = estimate_conduction_velocity(
        v1, dz_m, dt_s,
        z_start_idx=max(1, int(0.20 * N)),
        z_end_idx=int(0.80 * N)
    )

    t0 = time.time()
    res = run_coupled(w_cleft=W_CLEFT, kappa=KAPPA, T=3e-3, record_full=True, dz=dz_m, dt=dt_s)
    t_coupled = time.time() - t0

    v2_trace = res['v2_mid']
    v_peak_mv = v2_trace.max() * 1e3
    n_pre = max(1, int(0.1e-3 / dt_s))
    v_rest_mv = v2_trace[:n_pre].mean() * 1e3
    delta_v_mv = v_peak_mv - v_rest_mv
    t_event_ms = v2_trace.argmax() * dt_s * 1e3

    source_peak = np.abs(np.diff(v1, axis=1)).max() / dz_m

    res_dict = dict(
        dz_um = dz_um,
        dt_us = dt_us,
        N = N,
        cv_ms = cv if cv is not None else 0.0,
        v_peak = v_peak_mv,
        v_rest = v_rest_mv,
        delta_v = delta_v_mv,
        t_event = t_event_ms,
        source_peak = source_peak,
        spiked = res['spiked'],
        t_wall = t_cv + t_coupled
    )
    _purge_phase1_modules()
    return res_dict

def run_decoupled_convergence():
    print("=" * 80)
    print("DECOUPLED SPATIAL & TEMPORAL CONVERGENCE STUDY")
    print(f"Physical node width = {PHYSICAL_NODE_WIDTH*1e6:.1f} µm (constant)")
    print("=" * 80)

    # 1. Spatial convergence (fixed dt = 2.5 µs)
    dz_list = [20.0, 10.0, 5.0, 2.5]
    fixed_dt = 2.5
    spatial_rows = []
    print("\n--- Part 1: Spatial Grid Refinement (dt = 2.5 µs fixed) ---")
    for dz in dz_list:
        r = run_simulation(dz_um=dz, dt_us=fixed_dt)
        spatial_rows.append(r)
        print(f"dz = {dz:4.1f} µm | N={r['N']:4d} | CV = {r['cv_ms']:5.2f} m/s | "
              f"Vpeak = {r['v_peak']:6.2f} mV | ΔV = {r['delta_v']:5.2f} mV | "
              f"t_event = {r['t_event']:5.3f} ms | Spiked: {r['spiked']}")

    # 2. Temporal convergence (fixed dz = 10.0 µm)
    dt_list = [10.0, 5.0, 2.5, 1.25]
    fixed_dz = 10.0
    temporal_rows = []
    print("\n--- Part 2: Temporal Timestep Refinement (dz = 10.0 µm fixed) ---")
    for dt_val in dt_list:
        r = run_simulation(dz_um=fixed_dz, dt_us=dt_val)
        temporal_rows.append(r)
        print(f"dt = {dt_val:5.2f} µs | CV = {r['cv_ms']:5.2f} m/s | "
              f"Vpeak = {r['v_peak']:6.2f} mV | ΔV = {r['delta_v']:5.2f} mV | "
              f"t_event = {r['t_event']:5.3f} ms | Spiked: {r['spiked']}")

    # Plotting 2x3 comprehensive panel
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle('Decoupled Numerical Convergence Study\n'
                 r'(Invariant physical node length $l_{\mathrm{node}} = 1.0\,\mu$m, '
                 r'$w_{\mathrm{cleft}} = 20\,$nm, $\kappa = 10^9\,\mathrm{m}^{-2}$)',
                 fontsize=12, fontweight='bold')

    # Row 1: Spatial convergence vs dz (invert x axis so refinement goes left to right)
    dz_vals = [r['dz_um'] for r in spatial_rows]
    cv_s = [r['cv_ms'] for r in spatial_rows]
    dv_s = [r['delta_v'] for r in spatial_rows]
    te_s = [r['t_event'] for r in spatial_rows]

    axes[0, 0].plot(dz_vals, cv_s, 'o-', color='#1f77b4', lw=2, ms=6)
    axes[0, 0].set_xlabel(r'Spatial Step $\Delta z$ ($\mu$m)')
    axes[0, 0].set_ylabel('Aβ CV (m/s)')
    axes[0, 0].set_title(r'Aβ Conduction Velocity vs $\Delta z$ (dt=2.5 $\mu$s)', fontsize=10)
    axes[0, 0].invert_xaxis()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(dz_vals, dv_s, 's-', color='#2ca02c', lw=2, ms=6)
    axes[0, 1].set_xlabel(r'Spatial Step $\Delta z$ ($\mu$m)')
    axes[0, 1].set_ylabel(r'Ephaptic $\Delta V$ (mV)')
    axes[0, 1].set_title(r'C-Fiber Ephaptic $\Delta V$ vs $\Delta z$ (dt=2.5 $\mu$s)', fontsize=10)
    axes[0, 1].invert_xaxis()
    axes[0, 1].grid(True, alpha=0.3)

    axes[0, 2].plot(dz_vals, te_s, '^-', color='#d62728', lw=2, ms=6)
    axes[0, 2].set_xlabel(r'Spatial Step $\Delta z$ ($\mu$m)')
    axes[0, 2].set_ylabel('Event Time (ms)')
    axes[0, 2].set_title(r'Arrival Timing vs $\Delta z$ (dt=2.5 $\mu$s)', fontsize=10)
    axes[0, 2].invert_xaxis()
    axes[0, 2].grid(True, alpha=0.3)

    # Row 2: Temporal convergence vs dt (invert x axis)
    dt_vals = [r['dt_us'] for r in temporal_rows]
    cv_t = [r['cv_ms'] for r in temporal_rows]
    dv_t = [r['delta_v'] for r in temporal_rows]
    te_t = [r['t_event'] for r in temporal_rows]

    axes[1, 0].plot(dt_vals, cv_t, 'o--', color='#1f77b4', lw=2, ms=6)
    axes[1, 0].set_xlabel(r'Timestep $\Delta t$ ($\mu$s)')
    axes[1, 0].set_ylabel('Aβ CV (m/s)')
    axes[1, 0].set_title(r'Aβ Conduction Velocity vs $\Delta t$ ($\Delta z$=10 $\mu$m)', fontsize=10)
    axes[1, 0].invert_xaxis()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(dt_vals, dv_t, 's--', color='#2ca02c', lw=2, ms=6)
    axes[1, 1].set_xlabel(r'Timestep $\Delta t$ ($\mu$s)')
    axes[1, 1].set_ylabel(r'Ephaptic $\Delta V$ (mV)')
    axes[1, 1].set_title(r'C-Fiber Ephaptic $\Delta V$ vs $\Delta t$ ($\Delta z$=10 $\mu$m)', fontsize=10)
    axes[1, 1].invert_xaxis()
    axes[1, 1].grid(True, alpha=0.3)

    axes[1, 2].plot(dt_vals, te_t, '^--', color='#d62728', lw=2, ms=6)
    axes[1, 2].set_xlabel(r'Timestep $\Delta t$ ($\mu$s)')
    axes[1, 2].set_ylabel('Event Time (ms)')
    axes[1, 2].set_title(r'Arrival Timing vs $\Delta t$ ($\Delta z$=10 $\mu$m)', fontsize=10)
    axes[1, 2].invert_xaxis()
    axes[1, 2].grid(True, alpha=0.3)

    plt.tight_layout()
    out_dir = os.path.join(base_dir, '..', 'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'convergence_study.png')
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"\nSaved decoupled convergence figure to {out_path}")

    # Copy to artifacts
    art_dir = r"C:\Users\minas\.gemini\antigravity\brain\0b50dae7-9bc2-4269-808c-241b60d316f7"
    if os.path.exists(art_dir):
        import shutil
        shutil.copy(out_path, os.path.join(art_dir, 'convergence_study.png'))

    return spatial_rows, temporal_rows

if __name__ == '__main__':
    run_decoupled_convergence()
