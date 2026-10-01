"""
Run Temporal Summation Battery across frequencies [100, 200, 400] Hz and pulse counts [1, 2, 5, 10].
Evaluates inter-pulse recovery, residual baseline depolarization, gating accumulation,
and spike classification on the frozen production model.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from scipy.linalg import solve_banded

base_dir = os.path.dirname(os.path.abspath(__file__))
phase1_dir = os.path.join(base_dir, "phase1_classical_hh")
if phase1_dir not in sys.path:
    sys.path.insert(0, phase1_dir)

from ephaptic_model import *
from validate_single_fibers import build_implicit_operator
from spike_detector import build_fixed_node_geometry, classify_waveform

out_dir = os.path.join(base_dir, "..", "results", "convergence")
os.makedirs(out_dir, exist_ok=True)

def run_temporal_summation_sweep(
    w_cleft=20e-9,
    kappa=1.0e9,
    dz=10e-6,
    dt=2.5e-6,
    stim_amp=100e-9,
    stim_dur=0.2e-3
):
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

    def laplacian_neumann_local(x):
        d2x = np.zeros_like(x)
        d2x[1:-1] = (x[2:] - 2*x[1:-1] + x[:-2]) / dz**2
        d2x[0] = 2 * (x[1] - x[0]) / dz**2
        d2x[-1] = 2 * (x[-2] - x[-1]) / dz**2
        return d2x

    def build_poisson_op(kappa_val):
        A = np.zeros((3, N))
        A[1, :] = -2.0 / dz**2 - kappa_val
        A[0, 1:] = 1.0 / dz**2
        A[2, :-1] = 1.0 / dz**2
        A[0, 1] = 2.0 / dz**2
        A[2, -2] = 2.0 / dz**2
        return A

    freqs = [100, 200, 400]
    pulse_counts = [1, 2, 5, 10]
    n_abeta_conditions = [1, 25]

    results = []

    for n_abeta in n_abeta_conditions:
        sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
        kappa_eff = (kappa / r_e) / sum_inv_r
        A_poisson_eff = build_poisson_op(kappa_eff)

        for freq in freqs:
            interval_ms = 1000.0 / freq
            for npulses in pulse_counts:
                period = 1.0 / freq
                pulse_starts = [i * period for i in range(npulses)]
                train_duration = (npulses - 1) * period + stim_dur
                T = train_duration + 5e-3
                nsteps = int(round(T / dt))

                v1 = np.full(N, -80e-3)
                am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
                m1 = np.full(N, am1 / (am1 + bm1))
                h1 = np.full(N, ah1 / (ah1 + bh1))

                v2 = np.full(N, -65e-3)
                m2 = np.full(N, 0.05); h2 = np.full(N, 0.6); n2 = np.full(N, 0.32)

                mid_idx = N // 2
                v2_mid_trace = np.zeros(nsteps)
                v2_rec = np.zeros((nsteps, N))

                t0 = time.time()
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

                    v2_mid_trace[step] = v2[mid_idx]
                    v2_rec[step] = v2

                elapsed = time.time() - t0

                detect_res = classify_waveform(v2_rec, z, dt, fiber_type="c_fiber")
                
                v2_mid_mV = v2_mid_trace * 1e3
                v_rest = v2_mid_mV[0]
                max_v2_mid = np.max(v2_mid_mV)
                max_delta_v = max_v2_mid - v_rest

                pulse_baselines = []
                pulse_peaks = []
                for p_idx, ps in enumerate(pulse_starts):
                    step_start = int(round(ps / dt))
                    step_end = int(round((ps + period) / dt)) if p_idx < npulses - 1 else nsteps
                    base_val = v2_mid_mV[step_start]
                    peak_val = np.max(v2_mid_mV[step_start:step_end])
                    pulse_baselines.append(base_val)
                    pulse_peaks.append(peak_val)

                first_depol = pulse_peaks[0] - pulse_baselines[0]
                last_depol = pulse_peaks[-1] - pulse_baselines[-1]
                
                if npulses > 1:
                    inter_pulse_baselines = pulse_baselines[1:]
                    residual_depol = np.mean([b - v_rest for b in inter_pulse_baselines])
                    recovery_pct = (1.0 - (pulse_baselines[-1] - v_rest) / max(first_depol, 1e-6)) * 100.0
                    accumulates = bool((pulse_peaks[-1] > pulse_peaks[0] + 0.1) or (residual_depol > 0.5))
                else:
                    residual_depol = 0.0
                    recovery_pct = 100.0
                    accumulates = False

                results.append({
                    "n_abeta": n_abeta,
                    "freq_Hz": freq,
                    "interval_ms": interval_ms,
                    "n_pulses": npulses,
                    "train_duration_ms": train_duration * 1e3,
                    "sim_T_ms": T * 1e3,
                    "max_delta_v_mV": max_delta_v,
                    "v_rest_mV": v_rest,
                    "max_v2_mid_mV": max_v2_mid,
                    "first_pulse_delta_v_mV": first_depol,
                    "last_pulse_delta_v_mV": last_depol,
                    "residual_baseline_depol_mV": residual_depol,
                    "recovery_between_pulses_pct": recovery_pct,
                    "activation_accumulates": accumulates,
                    "c_classification": detect_res["classification"],
                    "c_spiked": detect_res["spiked"],
                    "runtime_s": elapsed
                })
                print(f"n={n_abeta:2d} | {freq:3d} Hz (dt={interval_ms:4.1f}ms) | {npulses:2d} pulses | max dV={max_delta_v:6.3f} mV | accum={accumulates!s:5s} | class={detect_res['classification']:24s} | spiked={detect_res['spiked']}")

    df_ts = pd.DataFrame(results)
    out_csv = os.path.join(out_dir, "phase2_temporal_summation.csv")
    df_ts.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")
    return df_ts

if __name__ == "__main__":
    print("Running Temporal Summation Battery on Frozen Production Model...")
    run_temporal_summation_sweep()
