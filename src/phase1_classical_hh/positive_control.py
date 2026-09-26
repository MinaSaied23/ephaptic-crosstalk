import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import *
from validate_single_fibers import build_implicit_operator
from coupled_model import build_poisson_operator, laplacian_neumann

from spike_detector import build_fixed_node_geometry, classify_waveform

def run_positive_control(stim_amp_c, w_cleft=200e-9, T=20e-3, stim_dur=0.5e-3, stim_loc_idx=0, dz=10e-6, dt=2.5e-6):
    """
    Same closed-loop two-fiber apparatus as all ephaptic experiments (coupling
    left ON, kappa=1e9), but the stimulus is injected directly into the
    C-fiber (axon 2) at z=0 (or specified stim_loc_idx). Confirms the C-fiber
    model is capable of firing and propagating in this exact apparatus; the
    Abeta fiber receives no stimulus and simply reports its (expected) quiescence.
    """
    N_val, z_val, node_mask_val, f_node_val = build_fixed_node_geometry(dz=dz)
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    Cm_node_comp_val = (2.0 * f_node_val + 0.005 * (1.0 - f_node_val)) * uF_cm2_to_F_m2
    Cm1_arr_val = np.where(node_mask_val, Cm_node_comp_val, Cm_internode)

    g_Na_val = 1445.0 * f_node_val * mS_cm2_to_S_m2
    g_leak_node_val = (128.0 * f_node_val + 0.006 * (1.0 - f_node_val)) * mS_cm2_to_S_m2
    g_leak1_arr_val = np.where(node_mask_val, g_leak_node_val, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr_val, dz, N_val)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N_val)

    v1 = np.full(N_val, -80e-3)
    am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
    m1 = np.full(N_val, am1 / (am1 + bm1))
    h1 = np.full(N_val, ah1 / (ah1 + bh1))
    v2 = np.full(N_val, -65e-3); m2 = np.full(N_val, 0.05); h2 = np.full(N_val, 0.6); n2 = np.full(N_val, 0.32)

    nsteps = int(round(T / dt))
    v2_full = np.zeros((nsteps, N_val))
    v1_mid = np.zeros(nsteps)
    mid_idx = N_val // 2

    # Pre-calculate algebraic elimination constants
    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e
    sum_inv_r = inv_re + inv_r1 + inv_r2
    kappa_eff = (1e9 / r_e) / sum_inv_r  # positive_control hardcoded kappa=1e9
    A_poisson_eff = build_poisson_operator(dz, N_val, kappa=kappa_eff)

    for step in range(nsteps):
        am1, bm1, ah1, bh1 = crrss_rates(v1)
        tau_m1 = 1.0 / (am1 + bm1); m1_inf = am1 * tau_m1
        tau_h1 = 1.0 / (ah1 + bh1); h1_inf = ah1 * tau_h1
        m1 = np.where(node_mask_val, m1_inf + (m1 - m1_inf) * np.exp(-dt / tau_m1), m1)
        h1 = np.where(node_mask_val, h1_inf + (h1 - h1_inf) * np.exp(-dt / tau_h1), h1)
        I_active1 = g_Na_val * m1**2 * h1 * (v1 - E_Na) + g_leak1_arr_val * (v1 - E_leak_1)
        I_passive1 = g_leak1_arr_val * (v1 - E_leak_1)
        I_ion1 = np.where(node_mask_val, I_active1, I_passive1)

        am2, bm2, ah2, bh2, an2, bn2 = hh_rates(v2)
        m2 = np.clip(m2 + dt*(am2*(1-m2) - bm2*m2), 0, 1)
        h2 = np.clip(h2 + dt*(ah2*(1-h2) - bh2*h2), 0, 1)
        n2 = np.clip(n2 + dt*(an2*(1-n2) - bn2*n2), 0, 1)
        I_ion2 = (g_Na_HH * m2**3 * h2 * (v2 - E_Na)
                  + g_K_HH * n2**4 * (v2 - E_K)
                  + g_leak_HH * (v2 - E_leak_2))

        I_stim2 = np.zeros(N_val)
        if step * dt < stim_dur:
            I_stim2[stim_loc_idx] = stim_amp_c / (np.pi * d2 * dz)

        # Algebraic elimination of capacitive current for unconditional stability
        d2v1 = laplacian_neumann(v1, dz)
        d2v2 = laplacian_neumann(v2, dz)
        
        B = - (inv_r1 * d2v1 + inv_r2 * d2v2) / sum_inv_r
        u_e = solve_banded((1, 1), A_poisson_eff, B)
        d2ue = laplacian_neumann(u_e, dz)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        rhs1 = Cm1_arr_val / dt * v1 + (-I_ion1 + I_eph1)   # Abeta: no stimulus, coupling only
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt * v2 + (I_stim2 - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v2_full[step] = v2
        v1_mid[step] = v1[mid_idx]

    detect_res = classify_waveform(v2_full, z_val, dt, fiber_type="c_fiber")
    return {
        "v2": v2_full,
        "v1_mid": v1_mid,
        "classification": detect_res["classification"],
        "spiked": detect_res["spiked"],
        "cv": detect_res["cv"],
        "ephaptic_delta_v": detect_res["delta_v"]
    }

if __name__ == "__main__":
    print(f"{'I_stim (nA)':>12} {'peak V2 (mV)':>16} {'fired':>7} {'classification':>30} {'CV (m/s)':>10}")
    for amp_nA in [0.1, 0.5, 1.0, 2.0, 5.0]:
        res = run_positive_control(stim_amp_c=amp_nA * 1e-9)
        peak_v2 = res["v2"][:, 400:].max() * 1e3
        fired = res["spiked"]
        cv_str = f"{res['cv']:.2f}" if res['cv'] is not None else "N/A"
        print(f"{amp_nA:12.2f} {peak_v2:16.2f} {str(fired):>7} {res['classification']:>30} {cv_str:>10}")

    # confirm the Abeta fiber (no stimulus) stayed quiescent throughout, as expected
    res_check = run_positive_control(stim_amp_c=2.0e-9)
    print(f"\nAbeta fiber (unstimulated) max V1 at midpoint during run: {res_check['v1_mid'].max()*1e3:.2f} mV (should stay near rest -80 mV)")
