"""
reproduce_pulse2_canonical.py
Fresh standalone simulation of the 100 Hz, 2-pulse, n=25 condition with T >= 35 ms.
Directly verifies C-fiber propagation, peak voltages, and coupled Abeta CV.
"""

import os
import sys
import time
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
p1_dir = os.path.join(base_dir, 'src', 'phase1_classical_hh')
if p1_dir not in sys.path:
    sys.path.insert(0, p1_dir)

from ephaptic_model import (
    d1_axon, d2, rho_i, r_e_from_cleft, Cm, Cm_internode, uF_cm2_to_F_m2,
    mS_cm2_to_S_m2, crrss_rates, hh_rates, E_Na, E_K, E_leak_1, E_leak_2,
    g_Na_HH, g_K_HH, g_leak_HH, g_leak_internode
)
from validate_single_fibers import build_implicit_operator
from spike_detector import build_fixed_node_geometry, classify_waveform
from scipy.linalg import solve_banded

def main():
    print("=" * 80)
    print("SIMULATING 2 PULSES AT 100 Hz (n=25, w_cleft=20 nm, T=40 ms)...", flush=True)
    print("=" * 80, flush=True)
    t0 = time.time()

    dz = 10e-6
    dt = 2.5e-6
    w_cleft = 20e-9
    kappa = 1.0e9
    stim_amp = 100e-9
    stim_dur = 0.2e-3
    n_abeta = 25
    period = 10.0e-3 # 100 Hz
    pulse_starts = [0.0, period]
    T = 40.0e-3 # 40 ms >= 35 ms observation window
    nsteps = int(round(T / dt))

    N, z, node_mask, f_node = build_fixed_node_geometry(dz=dz)
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    Cm_node_comp = (2.0 * f_node + 0.005 * (1.0 - f_node)) * uF_cm2_to_F_m2
    Cm1_arr = np.where(node_mask, Cm_node_comp, Cm_internode)

    g_Na_val = 1445.0 * f_node * mS_cm2_to_S_m2
    g_leak_node_val = (128.0 * f_node + 0.006 * (1.0 - f_node)) * mS_cm2_to_S_m2
    g_leak1_arr = np.where(node_mask, g_leak_node_val, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)

    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e

    sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
    kappa_eff = (kappa / r_e) / sum_inv_r

    A_poisson_eff = np.zeros((3, N))
    A_poisson_eff[1, :] = -2.0 / dz**2 - kappa_eff
    A_poisson_eff[0, 1:] = 1.0 / dz**2
    A_poisson_eff[2, :-1] = 1.0 / dz**2
    A_poisson_eff[0, 1] = 2.0 / dz**2
    A_poisson_eff[2, -2] = 2.0 / dz**2

    def laplacian_neumann_local(x):
        d2x = np.zeros_like(x)
        d2x[1:-1] = (x[2:] - 2*x[1:-1] + x[:-2]) / dz**2
        d2x[0] = 2 * (x[1] - x[0]) / dz**2
        d2x[-1] = 2 * (x[-2] - x[-1]) / dz**2
        return d2x

    v1 = np.full(N, -80e-3)
    am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
    m1 = np.full(N, am1 / (am1 + bm1))
    h1 = np.full(N, ah1 / (ah1 + bh1))

    v2 = np.full(N, -65e-3)
    m2 = np.full(N, 0.05)
    h2 = np.full(N, 0.6)
    n2 = np.full(N, 0.32)

    v1_rec = np.zeros((nsteps, N))
    v2_rec = np.zeros((nsteps, N))

    for step in range(nsteps):
        t_now = step * dt

        am1, bm1, ah1, bh1 = crrss_rates(v1)
        tau_m1 = 1.0 / (am1 + bm1); m1_inf = am1 * tau_m1
        tau_h1 = 1.0 / (ah1 + bh1); h1_inf = ah1 * tau_h1
        m1 = np.where(node_mask, m1_inf + (m1 - m1_inf) * np.exp(-dt / tau_m1), m1)
        h1 = np.where(node_mask, h1_inf + (h1 - h1_inf) * np.exp(-dt / tau_h1), h1)
        I_active1 = g_Na_val * m1**2 * h1 * (v1 - E_Na) + g_leak1_arr * (v1 - E_leak_1)
        I_passive1 = g_leak1_arr * (v1 - E_leak_1)
        I_ion1 = np.where(node_mask, I_active1, I_passive1)

        am2, bm2, ah2, bh2, an2, bn2 = hh_rates(v2)
        m2 = np.clip(m2 + dt*(am2*(1-m2) - bm2*m2), 0, 1)
        h2 = np.clip(h2 + dt*(ah2*(1-h2) - bh2*h2), 0, 1)
        n2 = np.clip(n2 + dt*(an2*(1-n2) - bn2*n2), 0, 1)
        I_ion2 = (g_Na_HH * m2**3 * h2 * (v2 - E_Na)
                  + g_K_HH * n2**4 * (v2 - E_K)
                  + g_leak_HH * (v2 - E_leak_2))

        I_stim1 = np.zeros(N)
        for ps in pulse_starts:
            if ps <= t_now < ps + stim_dur:
                I_stim1[0] = stim_amp / (np.pi * d1_axon * dz)
                break

        d2v1 = laplacian_neumann_local(v1)
        d2v2 = laplacian_neumann_local(v2)

        B = - (n_abeta * inv_r1 * d2v1 + inv_r2 * d2v2) / sum_inv_r
        u_e = solve_banded((1, 1), A_poisson_eff, B)

        d2ue = laplacian_neumann_local(u_e)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        rhs1 = Cm1_arr / dt * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt * v2 + (- I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v1_rec[step] = v1
        v2_rec[step] = v2

    elapsed = time.time() - t0
    print(f"Simulation completed in {elapsed:.2f} s", flush=True)

    # Classification
    detect_res = classify_waveform(v2_rec, z, dt, fiber_type="c_fiber")
    
    # Peak voltages
    mid_idx = N // 2
    idx_8mm = int(round(8.0e-3 / dz))
    idx_4mm = int(round(4.0e-3 / dz))
    v2_mid_max = np.max(v2_rec[:, mid_idx]) * 1e3
    v2_8mm_max = np.max(v2_rec[:, idx_8mm]) * 1e3
    v2_rest = v2_rec[0, mid_idx] * 1e3
    delta_v_mid = v2_mid_max - v2_rest

    # Coupled Abeta CV calculation (continuous max dV/dt metric)
    dv1_dt = np.diff(v1_rec, axis=0) / dt
    t_up_4mm = np.argmax(dv1_dt[:, idx_4mm]) * dt
    t_up_8mm = np.argmax(dv1_dt[:, idx_8mm]) * dt
    cv_abeta = (8.0e-3 - 4.0e-3) / (t_up_8mm - t_up_4mm)

    # Discrete peak latency calculation for comparison (argmax(V1))
    t_pk_4mm = np.argmax(v1_rec[:, idx_4mm]) * dt
    t_pk_8mm = np.argmax(v1_rec[:, idx_8mm]) * dt
    cv_abeta_discrete = (8.0e-3 - 4.0e-3) / (t_pk_8mm - t_pk_4mm)

    print("\n" + "=" * 80)
    print("SIMULATION RESULTS:")
    print("=" * 80)
    print(f"  Classification            : {detect_res['classification']}")
    print(f"  Spiked (propagated AP)    : {detect_res['spiked']}")
    print(f"  Midpoint peak (V2, 5 mm)  : {v2_mid_max:+.3f} mV")
    print(f"  Downstream peak (V2, 8 mm): {v2_8mm_max:+.3f} mV")
    print(f"  Midpoint Delta V          : {delta_v_mid:.3f} mV")
    print(f"  Coupled Abeta CV (max dV/dt): {cv_abeta:.2f} m/s")
    print(f"  Coupled Abeta CV (argmax V1): {cv_abeta_discrete:.2f} m/s")
    print("=" * 80)

if __name__ == "__main__":
    main()
