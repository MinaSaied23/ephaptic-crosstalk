import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import *
from validate_single_fibers import build_implicit_operator
from coupled_model import build_poisson_operator, laplacian_neumann

def run_positive_control(stim_amp_c, w_cleft=200e-9, T=3e-3, stim_dur=0.5e-3, stim_loc_idx=500):
    """
    Same closed-loop two-fiber apparatus as all ephaptic experiments (coupling
    left ON, kappa=1e9), but the stimulus is injected directly into the
    C-fiber (axon 2) at the same location (z=L/2) used to monitor for ectopic
    spikes throughout the paper, instead of into the Abeta fiber. Confirms
    the C-fiber model is capable of firing and propagating in this exact
    apparatus; the Abeta fiber receives no stimulus and simply reports its
    (expected) quiescence throughout.
    """
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1 / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    Cm1_arr = np.where(node_mask, Cm, Cm_internode)
    g_leak1_arr = np.where(node_mask, g_leak_CRRSS, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)
    A_poisson = build_poisson_operator(dz, N)  # default kappa=1e9, matches main experiments

    v1 = np.full(N, -70e-3); m1 = np.full(N, 0.05); h1 = np.full(N, 0.6)
    v2 = np.full(N, -65e-3); m2 = np.full(N, 0.05); h2 = np.full(N, 0.6); n2 = np.full(N, 0.32)

    nsteps = int(T / dt)
    v2_full = np.zeros((nsteps, N))
    v1_mid = np.zeros(nsteps)

    for step in range(nsteps):
        am1, bm1, ah1, bh1 = crrss_rates(v1)
        m1 = np.clip(np.where(node_mask, m1 + dt*(am1*(1-m1) - bm1*m1), m1), 0, 1)
        h1 = np.clip(np.where(node_mask, h1 + dt*(ah1*(1-h1) - bh1*h1), h1), 0, 1)
        I_active1 = g_Na_CRRSS * m1**2 * h1 * (v1 - E_Na) + g_leak1_arr * (v1 - E_leak_1)
        I_passive1 = g_leak1_arr * (v1 - E_leak_1)
        I_ion1 = np.where(node_mask, I_active1, I_passive1)

        am2, bm2, ah2, bh2, an2, bn2 = hh_rates(v2)
        m2 = np.clip(m2 + dt*(am2*(1-m2) - bm2*m2), 0, 1)
        h2 = np.clip(h2 + dt*(ah2*(1-h2) - bh2*h2), 0, 1)
        n2 = np.clip(n2 + dt*(an2*(1-n2) - bn2*n2), 0, 1)
        I_ion2 = (g_Na_HH * m2**3 * h2 * (v2 - E_Na)
                  + g_K_HH * n2**4 * (v2 - E_K)
                  + g_leak_HH * (v2 - E_leak_2))

        I_total = np.pi * d1 * I_ion1 + np.pi * d2 * I_ion2
        B = r_e * I_total
        u_e = solve_banded((1, 1), A_poisson, B)
        d2ue = laplacian_neumann(u_e, dz)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        # Direct stimulus into the C-fiber only, at the standard monitoring site
        I_stim2 = np.zeros(N)
        if step * dt < stim_dur:
            I_stim2[stim_loc_idx] = stim_amp_c / (np.pi * d2 * dz)

        rhs1 = Cm1_arr / dt * v1 + (-I_ion1 + I_eph1)   # Abeta: no stimulus, coupling only
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt * v2 + (I_stim2 - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v2_full[step] = v2
        v1_mid[step] = v1[stim_loc_idx]

    return {"v2": v2_full, "v1_mid": v1_mid}

if __name__ == "__main__":
    print(f"{'I_stim (nA)':>12} {'peak V2 @ site (mV)':>20} {'fired':>7} {'propagated (+/-1mm)':>22}")
    for amp_nA in [0.1, 0.5, 1.0, 2.0, 5.0]:
        res = run_positive_control(stim_amp_c=amp_nA * 1e-9)
        site = 500
        peak_site = res["v2"][:, site].max() * 1e3
        fired = peak_site > 0
        # check propagation 1 mm to either side (100 compartments)
        peak_left = res["v2"][:, site-100].max() * 1e3
        peak_right = res["v2"][:, site+100].max() * 1e3
        propagated = (peak_left > 0) and (peak_right > 0)
        print(f"{amp_nA:12.2f} {peak_site:20.2f} {str(fired):>7} {str(propagated):>22}")

    # confirm the Abeta fiber (no stimulus) stayed quiescent throughout, as expected
    res_check = run_positive_control(stim_amp_c=2.0e-9)
    print(f"\nAbeta fiber (unstimulated) max V1 at site during run: {res_check['v1_mid'].max()*1e3:.2f} mV (should stay near rest -70 mV)")
