"""
Run Phase 1 Multi-Fiber Sweep Experiment across n_abeta in [1, 50].
Records downstream C-fiber ephaptic perturbation, Aβ conduction velocity,
effective decay lengths, and spike detection classifications.
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

def run_multifiber_experiment(
    n_list=[1, 2, 5, 10, 15, 20, 25, 30, 40, 50],
    w_cleft=20e-9,
    kappa=1.0e9,
    dz=10e-6,
    dt=2.5e-6,
    T=6e-3,
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

    nsteps = int(round(T / dt))
    results = []

    for n_abeta in n_list:
        sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
        kappa_eff = (kappa / r_e) / sum_inv_r
        lambda_eff_um = 1.0 / np.sqrt(kappa_eff) * 1e6
        A_poisson_eff = build_poisson_op(kappa_eff)

        v1 = np.full(N, -80e-3)
        am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
        m1 = np.full(N, am1 / (am1 + bm1))
        h1 = np.full(N, ah1 / (ah1 + bh1))

        v2 = np.full(N, -65e-3)
        m2 = np.full(N, 0.05); h2 = np.full(N, 0.6); n2 = np.full(N, 0.32)

        v1_rec = np.zeros((nsteps, N))
        v2_rec = np.zeros((nsteps, N))
        ue_max_global = 0.0
        max_d2v1_global = 0.0

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
            if t_now < stim_dur:
                I_stim1[0] = stim_amp / (np.pi * d1_axon * dz)

            d2v1 = laplacian_neumann_local(v1)
            d2v2 = laplacian_neumann_local(v2)
            max_d2v1_global = max(max_d2v1_global, np.max(np.abs(d2v1)))

            B = - (n_abeta * inv_r1 * d2v1 + inv_r2 * d2v2) / sum_inv_r
            u_e = solve_banded((1, 1), A_poisson_eff, B)
            ue_max_global = max(ue_max_global, np.max(np.abs(u_e)))

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

        # C-fiber spike classification
        detect_res = classify_waveform(v2_rec, z, dt, fiber_type="c_fiber")

        # Downstream C-fiber peak and timing (3 mm to 8 mm)
        idx_down = np.where((z >= 3.0e-3 - 1e-9) & (z <= 8.0e-3 + 1e-9))[0]
        v2_down = v2_rec[:, idx_down] * 1e3 # mV
        v2_max = np.max(v2_down)
        v2_base = np.mean(v2_down[0, :])
        delta_v2 = v2_max - v2_base
        max_step, max_col = np.unravel_index(np.argmax(v2_down), v2_down.shape)
        t_max_peak_ms = max_step * dt * 1e3
        z_max_peak_mm = z[idx_down[max_col]] * 1e3

        # C-fiber midpoint (z = 5 mm, node N//2) peak potential, as used in Table 4
        mid_trace_mV = v2_rec[:, N // 2] * 1e3
        mid_peak_mV = float(np.max(mid_trace_mV))
        mid_delta_mV = mid_peak_mV - float(mid_trace_mV[0])

        # Aβ waveform metrics
        idx_4mm = np.argmin(np.abs(z - 4.0e-3))
        idx_8mm = np.argmin(np.abs(z - 8.0e-3))
        pk_4mm = np.max(v1_rec[:, idx_4mm]) * 1e3
        amp_4mm = pk_4mm - (-80.0)
        t_dv_4 = np.argmax(np.diff(v1_rec[:, idx_4mm])) * dt
        t_dv_8 = np.argmax(np.diff(v1_rec[:, idx_8mm])) * dt
        cv_abeta = (z[idx_8mm] - z[idx_4mm]) / (t_dv_8 - t_dv_4) if t_dv_8 > t_dv_4 else np.nan

        results.append({
            "n_abeta": n_abeta,
            "w_cleft_nm": w_cleft * 1e9,
            "c_ephaptic_delta_v_mV": delta_v2,
            "c_peak_t_ms": t_max_peak_ms,
            "c_peak_z_mm": z_max_peak_mm,
            "c_classification": detect_res["classification"],
            "c_propagated_ap": detect_res["spiked"],
            "c_mid_peak_v2_mV": mid_peak_mV,
            "c_mid_delta_v_mV": mid_delta_mV,
            "abeta_cv_mps": cv_abeta,
            "abeta_ap_amp_mV": amp_4mm,
            "abeta_pk_4mm_mV": pk_4mm,
            "kappa_eff_m2": kappa_eff,
            "lambda_eff_um": lambda_eff_um,
            "peak_ue_mV": ue_max_global * 1e3,
            "max_d2v1_V_per_m2": max_d2v1_global,
            "source_summary": f"Abeta AP propagating at {cv_abeta:.1f} m/s, peak d2V/dz2={max_d2v1_global:.2e} V/m2",
            "runtime_s": elapsed
        })
        print(f"n={n_abeta:2d} | C dV={delta_v2:6.3f} mV at z={z_max_peak_mm:4.1f}mm, t={t_max_peak_ms:4.2f}ms | class={detect_res['classification']:24s} | spiked={detect_res['spiked']!s:5s} | ue_pk={ue_max_global*1e3:5.2f} mV")

    return pd.DataFrame(results)

if __name__ == "__main__":
    print("Testing Multi-Fiber Sweep on Frozen Production Model (w_cleft=20 nm)...")
    df_mf = run_multifiber_experiment()
    df_mf.to_csv(os.path.join(out_dir, "phase2_multifiber.csv"), index=False)
    print("Saved phase2_multifiber.csv")
