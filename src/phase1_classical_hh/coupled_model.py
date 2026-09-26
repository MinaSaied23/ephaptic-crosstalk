import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import *
from validate_single_fibers import build_implicit_operator

def build_poisson_operator(dz, N, kappa=1.0e9):
    """
    Banded matrix for d^2(u_e)/dz^2 - kappa*u_e = r_e * I_total(z), Neumann BCs.
    kappa is a small regularization representing weak leakage of the
    restricted cleft's extracellular potential to the surrounding bulk
    tissue beyond the simulated segment (pure-Neumann Poisson is otherwise
    singular). Tuned so a realistic single-node Na current produces a
    field of a few mV (decay length ~30 um at this kappa).
    """
    A = np.zeros((3, N))
    A[1, :] = -2.0 / dz**2 - kappa
    A[0, 1:] = 1.0 / dz**2
    A[2, :-1] = 1.0 / dz**2
    A[0, 1] = 2.0 / dz**2
    A[2, -2] = 2.0 / dz**2
    return A

def laplacian_neumann(x, dz):
    d2x = np.zeros_like(x)
    d2x[1:-1] = (x[2:] - 2*x[1:-1] + x[:-2]) / dz**2
    d2x[0] = 2 * (x[1] - x[0]) / dz**2
    d2x[-1] = 2 * (x[-2] - x[-1]) / dz**2
    return d2x

from spike_detector import build_fixed_node_geometry, classify_waveform

def run_coupled(w_cleft, kappa=1.0e9, T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3, record_full=False,
                 sens_bias=0.0, stim_freq=None, n_pulses=1, n_abeta=1, dz=10e-6, dt=2.5e-6):
    """
    Run the closed-loop coupled Aβ/C-fiber ephaptic model.
    Stimulus injected at Aβ node 0 (z=0).

    sens_bias: persistent depolarizing current density (A/m^2) applied
    uniformly along the C-fiber, representing peripheral sensitization.

    n_abeta: number of representative synchronous Aβ fibers (source-scaling approximation).
    dz, dt: spatial and temporal discretization steps.
    """
    N_val, z_val, node_mask_val, f_node_val = build_fixed_node_geometry(dz=dz)
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    # Dynamic fixed-node homogenization across arbitrary dz
    Cm_node_comp_val = (2.0 * f_node_val + 0.005 * (1.0 - f_node_val)) * uF_cm2_to_F_m2
    Cm1_arr_val = np.where(node_mask_val, Cm_node_comp_val, Cm_internode)
    
    g_Na_val = 1445.0 * f_node_val * mS_cm2_to_S_m2
    g_leak_node_val = (128.0 * f_node_val + 0.006 * (1.0 - f_node_val)) * mS_cm2_to_S_m2
    g_leak1_arr_val = np.where(node_mask_val, g_leak_node_val, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr_val, dz, N_val)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N_val)

    # Pre-calculate algebraic elimination constants with n_abeta scaling
    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e
    sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
    kappa_eff = (kappa / r_e) / sum_inv_r
    A_poisson_eff = build_poisson_operator(dz, N_val, kappa=kappa_eff)

    v1 = np.full(N_val, -80e-3)
    am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
    m1 = np.full(N_val, am1 / (am1 + bm1))
    h1 = np.full(N_val, ah1 / (ah1 + bh1))

    v2 = np.full(N_val, -65e-3)
    m2 = np.full(N_val, 0.05)
    h2 = np.full(N_val, 0.6)
    n2 = np.full(N_val, 0.32)

    if sens_bias != 0.0:
        for _ in range(int(6e-3 / dt)):  # 6 ms settling
            am2, bm2, ah2, bh2, an2, bn2 = hh_rates(v2)
            m2 = np.clip(m2 + dt*(am2*(1-m2) - bm2*m2), 0, 1)
            h2 = np.clip(h2 + dt*(ah2*(1-h2) - bh2*h2), 0, 1)
            n2 = np.clip(n2 + dt*(an2*(1-n2) - bn2*n2), 0, 1)
            I_ion2 = (g_Na_HH * m2**3 * h2 * (v2 - E_Na)
                      + g_K_HH * n2**4 * (v2 - E_K)
                      + g_leak_HH * (v2 - E_leak_2))
            rhs2 = Cm / dt * v2 + (sens_bias - I_ion2)
            v2 = solve_banded((1, 1), A2, rhs2)

    if stim_freq is not None and n_pulses > 1:
        period = 1.0 / stim_freq
        pulse_starts = [i * period for i in range(n_pulses)]
    else:
        pulse_starts = [0.0]

    nsteps = int(round(T / dt))
    mid = N_val // 2

    v2_mid_trace = np.zeros(nsteps)
    v1_rec = np.zeros((nsteps, N_val)) if record_full else None
    v2_rec = np.zeros((nsteps, N_val))  # Always record full v2 for unified spatiotemporal classification

    for step in range(nsteps):
        t_now = step * dt

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

        I_stim1 = np.zeros(N_val)
        for ps in pulse_starts:
            if ps <= t_now < ps + stim_dur:
                I_stim1[0] = stim_amp / (np.pi * d1_axon * dz)
                break

        # Algebraic elimination of capacitive current for unconditional stability
        d2v1 = laplacian_neumann(v1, dz)
        d2v2 = laplacian_neumann(v2, dz)
        
        B = - (n_abeta * inv_r1 * d2v1 + inv_r2 * d2v2) / sum_inv_r
        u_e = solve_banded((1, 1), A_poisson_eff, B)
        d2ue = laplacian_neumann(u_e, dz)

        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        rhs1 = Cm1_arr_val / dt * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt * v2 + (sens_bias - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v2_mid_trace[step] = v2[mid]
        v2_rec[step] = v2
        if record_full:
            v1_rec[step] = v1

    # Standardized evaluation via unified detector
    detect_res = classify_waveform(v2_rec, z_val, dt, fiber_type="c_fiber")

    result = {
        "v2_mid": v2_mid_trace,
        "classification": detect_res["classification"],
        "spiked": detect_res["spiked"],
        "ephaptic_delta_v": detect_res["delta_v"],
        "v2_max_downstream": detect_res["v_max"],
        "c_base": detect_res["v_base"]
    }
    if record_full:
        result["v1"] = v1_rec
        result["v2"] = v2_rec
    return result

if __name__ == "__main__":
    print("Smoke test: train stimulus, mild sensitization...")
    res = run_coupled(w_cleft=200e-9, T=3e-3, stim_amp=100e-9, stim_dur=0.2e-3,
                       sens_bias=0.5, stim_freq=200.0, n_pulses=5, record_full=True)
    print(f"  classification={res['classification']}, spiked={res['spiked']}, delta_v={res['ephaptic_delta_v']:.2f} mV")

