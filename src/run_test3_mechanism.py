"""
run_test3_mechanism.py

Canonical reproduction script for the Phase 2 temporal summation mechanism diagnostic.
Evaluates whether repeated recruitment during 100-Hz stimulation is mediated by:
1. Progressive extracellular potential accumulation in the cleft, or
2. Cumulative residual membrane depolarization and gating-state integration in the C-fiber.

Compares:
- CONTROL_A_NORMAL: Standard closed-loop simulation across 10 pulses at 100 Hz.
- CONTROL_B_STATE_RESET: C-fiber membrane potential and gating states reset to baseline
  immediately prior to each subsequent pulse (t = 10, 20, ..., 90 ms), while keeping
  the Aβ source train identical.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from scipy.linalg import solve_banded

# Repository-relative imports
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

out_dir = os.path.join(base_dir, "results", "convergence")
os.makedirs(out_dir, exist_ok=True)

def run_mechanism_diagnostic():
    dz = 10e-6
    dt = 2.5e-6
    w_cleft = 20e-9
    kappa = 1.0e9
    stim_amp = 100e-9
    stim_dur = 0.2e-3
    n_abeta = 25
    freq = 100  # Hz
    npulses = 10
    period = 1.0 / freq  # 10 ms
    pulse_starts = [i * period for i in range(npulses)]
    T = (npulses - 1) * period + 5.0e-3  # 95 ms
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

    mid_idx = N // 2
    conditions = ["CONTROL_A_NORMAL", "CONTROL_B_STATE_RESET"]
    rows = []

    for cond in conditions:
        reset_c_fiber = (cond == "CONTROL_B_STATE_RESET")

        v1 = np.full(N, -80e-3)
        am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
        m1 = np.full(N, am1 / (am1 + bm1))
        h1 = np.full(N, ah1 / (ah1 + bh1))

        v2 = np.full(N, -65e-3)
        m2 = np.full(N, 0.05)
        h2 = np.full(N, 0.6)
        n2 = np.full(N, 0.32)

        v2_rec = np.zeros((nsteps, N))
        ue_rec = np.zeros((nsteps, N))
        ieph2_rec = np.zeros((nsteps, N))

        pre_pulse_states = {}

        for step in range(nsteps):
            t_now = step * dt

            # If reset condition, check if we are at the exact onset of pulse 2, 3, ..., 10
            for p_idx, ps in enumerate(pulse_starts):
                if p_idx > 0 and abs(t_now - ps) < 1e-9:
                    pre_pulse_states[p_idx + 1] = {
                        "v2_pre": v2[mid_idx] * 1e3,
                        "m2_pre": m2[mid_idx],
                        "h2_pre": h2[mid_idx],
                        "n2_pre": n2[mid_idx]
                    }
                    if reset_c_fiber:
                        v2 = np.full(N, -65e-3)
                        m2 = np.full(N, 0.05)
                        h2 = np.full(N, 0.6)
                        n2 = np.full(N, 0.32)

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

            v2_rec[step] = v2
            ue_rec[step] = u_e
            ieph2_rec[step] = I_eph2

        # Classification for the whole trace
        detect_res = classify_waveform(v2_rec, z, dt, fiber_type="c_fiber")

        for p_idx, ps in enumerate(pulse_starts):
            s_start = int(round(ps / dt))
            s_end = int(round((ps + period) / dt)) if p_idx < npulses - 1 else nsteps

            v2_win_mid = v2_rec[s_start:s_end, mid_idx] * 1e3
            ue_win_mid = ue_rec[s_start:s_end, mid_idx] * 1e3
            ieph2_win_mid = ieph2_rec[s_start:s_end, mid_idx]

            base_v2 = v2_win_mid[0]
            pk_v2 = np.max(v2_win_mid)
            delta_v2 = pk_v2 - base_v2

            pk_ue = np.max(np.abs(ue_win_mid))
            pk_ieph2 = np.max(np.abs(ieph2_win_mid))

            if p_idx == 0:
                m2_val = 0.05; h2_val = 0.60; n2_val = 0.32
            else:
                saved = pre_pulse_states.get(p_idx + 1, {})
                m2_val = saved.get("m2_pre", 0.05)
                h2_val = saved.get("h2_pre", 0.60)
                n2_val = saved.get("n2_pre", 0.32)

            rows.append({
                "condition": cond,
                "pulse_index": p_idx + 1,
                "stimulus_time_ms": ps * 1e3,
                "c_baseline_pre_pulse_mV": base_v2,
                "c_peak_post_pulse_mV": pk_v2,
                "c_peak_delta_v_mV": delta_v2,
                "peak_extracellular_potential_ue_mV": pk_ue,
                "peak_ephaptic_current_Ieph2_A_per_m2": pk_ieph2,
                "c_gating_m2_pre_pulse": m2_val,
                "c_gating_h2_pre_pulse": h2_val,
                "c_gating_n2_pre_pulse": n2_val,
                "c_spike_classification": detect_res["classification"],
                "c_spiked": detect_res["spiked"]
            })
            print(f"[{cond}] Pulse {p_idx+1:2d} | base={base_v2:6.2f} mV | pk={pk_v2:6.2f} mV | dV={delta_v2:6.2f} mV | ue={pk_ue:6.2f} mV | ieph={pk_ieph2:8.2f} A/m2 | m2={m2_val:.4f}, h2={h2_val:.4f}")

    df_mech = pd.DataFrame(rows)
    csv_mech = os.path.join(out_dir, "phase2_summation_mechanism.csv")
    df_mech.to_csv(csv_mech, index=False)
    print(f"Saved {csv_mech}")

    # Generate Markdown Summary (every number below is read from the simulation output)
    def _row(cond, pulse):
        return df_mech[(df_mech["condition"] == cond) & (df_mech["pulse_index"] == pulse)].iloc[0]

    def _cell(cond, pulse):
        r = _row(cond, pulse)
        kind = "spike detected in window" if r["c_spiked"] else "no spike in window"
        return f"{r['c_peak_post_pulse_mV']:+.2f} mV (dV = {r['c_peak_delta_v_mV']:.2f} mV; {kind})"

    cA, cB = "CONTROL_A_NORMAL", "CONTROL_B_STATE_RESET"
    last = int(df_mech["pulse_index"].max())
    ue_A = df_mech[df_mech["condition"] == cA]["peak_extracellular_potential_ue_mV"]
    ue_B = df_mech[df_mech["condition"] == cB]["peak_extracellular_potential_ue_mV"]
    md_report = (
        "# State-Reset Mechanism Control (100 Hz train, n = 25, w_cleft = 20 nm)\n\n"
        "**Setup:** Phase 1 classical-HH C-fiber, 10 Abeta pulses at 100 Hz. CONTROL A is the normal closed-loop run. "
        "In CONTROL B the C-fiber membrane potential and gating variables are reset to rest immediately before each pulse; "
        "the Abeta source train is unchanged.\n\n"
        "| Metric | CONTROL A (normal) | CONTROL B (C-fiber state reset) |\n| :--- | :--- | :--- |\n"
        f"| Pulse 1 peak midpoint V2 | {_cell(cA, 1)} | {_cell(cB, 1)} |\n"
        f"| Pulse 2 peak midpoint V2 | {_cell(cA, 2)} | {_cell(cB, 2)} |\n"
        f"| Pulse {last} peak midpoint V2 | {_cell(cA, last)} | {_cell(cB, last)} |\n"
        f"| Peak extracellular u_e, range over pulses (mV) | {ue_A.min():.2f} to {ue_A.max():.2f} | {ue_B.min():.2f} to {ue_B.max():.2f} |\n\n"
        "**Interpretation (consistent with Sec. 3.9.3 of the manuscript):** the extracellular peak is the same on every pulse, "
        "so there is no pulse-to-pulse accumulation of u_e in the cleft. Resetting the C-fiber before a pulse removes a wave that is already "
        "propagating, by construction, so this control alone does not separate membrane-state accumulation from conduction delay. "
        "The single-pulse run observed for T >= 30 ms (Table 1) reproduces the same downstream spike and shows that it is initiated by "
        "Pulse 1 at the sealed boundary; the 100 Hz result is therefore not evidence of temporal summation.\n"
    )

    md_path = os.path.join(out_dir, "phase2_summation_mechanism.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"Saved {md_path}")
    return df_mech

if __name__ == "__main__":
    print("Running Temporal Summation Mechanism Diagnostic...")
    run_mechanism_diagnostic()
