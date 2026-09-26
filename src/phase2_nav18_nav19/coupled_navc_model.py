import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import (dz, N, d1, d2, rho_i, Cm, Cm_internode, Cm1_arr,
                             E_Na, E_K, E_leak_1, g_Na_CRRSS, g_leak_CRRSS,
                             g_leak_internode, g_leak1_arr, node_mask, crrss_rates,
                             r_e_from_cleft, d1_axon)
from navc_cable import g_Na18, g_Na19, g_K_HH, g_leak_HH, E_leak_2, hh_k_rates, build_implicit_operator
from nav_kinetics import nav_c_fiber_rates

DT = 1e-6  # finer timestep required for Nav1.8/1.9 stability

def build_poisson_operator(dz, N, kappa=1.0e9):
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

_STEADY_STATE_CACHE = {}

def get_settled_c_fiber(sens_bias, dt, A2, Cm):
    key = (round(sens_bias, 6), dt)
    if key in _STEADY_STATE_CACHE:
        v2, m8, h8, m9, n = _STEADY_STATE_CACHE[key]
        return v2.copy(), m8.copy(), h8.copy(), m9.copy(), n.copy()

    v2 = np.full(N, -66.8e-3)
    m8_inf, tau_m8, h8_inf, tau_h8, m9_inf, tau_m9 = nav_c_fiber_rates(v2)
    m8 = m8_inf.copy(); h8 = h8_inf.copy(); m9 = m9_inf.copy()
    an, bn = hh_k_rates(v2)
    n = an / (an + bn)

    # Settle baseline unconditionally (20 ms) using Rush-Larsen
    for _ in range(int(20e-3 / dt)):
        m8i, tm8, h8i, th8, m9i, tm9 = nav_c_fiber_rates(v2)
        an, bn = hh_k_rates(v2)
        tau_n = 1.0 / (an + bn); ni = an * tau_n
        m8 = m8i + (m8 - m8i) * np.exp(-dt / tm8)
        h8 = h8i + (h8 - h8i) * np.exp(-dt / th8)
        m9 = m9i + (m9 - m9i) * np.exp(-dt / tm9)
        n = ni + (n - ni) * np.exp(-dt / tau_n)
        I_ion2 = (g_Na18 * m8**3 * h8 * (v2 - E_Na)
                  + g_Na19 * m9 * (v2 - E_Na)
                  + g_K_HH * n**4 * (v2 - E_K)
                  + g_leak_HH * (v2 - E_leak_2))
        rhs2 = Cm / dt * v2 + (sens_bias - I_ion2)
        v2 = solve_banded((1, 1), A2, rhs2)

    _STEADY_STATE_CACHE[key] = (v2.copy(), m8.copy(), h8.copy(), m9.copy(), n.copy())
    return v2.copy(), m8.copy(), h8.copy(), m9.copy(), n.copy()

def run_coupled_navc(w_cleft, T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3, record_full=False,
                      sens_bias=0.0, stim_freq=None, n_pulses=1, dt=DT, kappa=1.0e9,
                      n_abeta=1.0, jitter_ms=0.0):
    """Coupled Abeta (CRRSS) / C-fiber (Nav1.8/1.9) ephaptic model.

    n_abeta: number of identical, synchronously-firing Abeta fibers assumed to
    surround the C-fiber within the same shared extracellular compartment
    (spatial summation / multi-fiber bundle test).
    """
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)

    K = 21 if jitter_ms > 0.0 else 1
    jitter_offsets = np.linspace(-jitter_ms*1e-3/2, jitter_ms*1e-3/2, K) if K > 1 else [0.0]

    v1 = np.full((K, N), -80e-3)
    am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
    m1 = np.full((K, N), am1 / (am1 + bm1))
    h1 = np.full((K, N), ah1 / (ah1 + bh1))

    v2, m8, h8, m9, n = get_settled_c_fiber(sens_bias, dt, A2, Cm)

    if stim_freq is not None and n_pulses > 1:
        period = 1.0 / stim_freq
        pulse_starts = [i * period for i in range(n_pulses)]
    else:
        pulse_starts = [0.0]

    nsteps = int(T / dt)
    mid = N // 2
    v2_mid_trace = np.zeros(nsteps)
    v1_rec = np.zeros((nsteps, N)) if record_full else None
    v2_rec = np.zeros((nsteps, N)) if record_full else None

    v2_global_max = -np.inf

    # Pre-calculate algebraic elimination constants
    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e
    sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
    kappa_eff = (kappa / r_e) / sum_inv_r
    A_poisson_eff = build_poisson_operator(dz, N, kappa=kappa_eff)

    for step in range(nsteps):
        t_now = step * dt

        am1, bm1, ah1, bh1 = crrss_rates(v1)
        tau_m1 = 1.0 / (am1 + bm1); m1_inf = am1 * tau_m1
        tau_h1 = 1.0 / (ah1 + bh1); h1_inf = ah1 * tau_h1
        m1 = np.where(node_mask, m1_inf + (m1 - m1_inf) * np.exp(-dt / tau_m1), m1)
        h1 = np.where(node_mask, h1_inf + (h1 - h1_inf) * np.exp(-dt / tau_h1), h1)

        I_active1 = g_Na_CRRSS * m1**2 * h1 * (v1 - E_Na) + g_leak1_arr * (v1 - E_leak_1)
        I_passive1 = g_leak1_arr * (v1 - E_leak_1)
        I_ion1 = np.where(node_mask, I_active1, I_passive1)

        m8i, tm8, h8i, th8, m9i, tm9 = nav_c_fiber_rates(v2)
        an, bn = hh_k_rates(v2)
        tau_n = 1.0 / (an + bn); ni = an * tau_n
        m8 = m8i + (m8 - m8i) * np.exp(-dt / tm8)
        h8 = h8i + (h8 - h8i) * np.exp(-dt / th8)
        m9 = m9i + (m9 - m9i) * np.exp(-dt / tm9)
        n = ni + (n - ni) * np.exp(-dt / tau_n)
        I_ion2 = (g_Na18 * m8**3 * h8 * (v2 - E_Na)
                  + g_Na19 * m9 * (v2 - E_Na)
                  + g_K_HH * n**4 * (v2 - E_K)
                  + g_leak_HH * (v2 - E_leak_2))

        I_stim1 = np.zeros((K, N))
        for ps in pulse_starts:
            for k in range(K):
                # Shift pulse start if jittering so earliest pulse is never negative
                t_start = ps + jitter_offsets[k] + (jitter_ms * 1e-3 / 2.0 if jitter_ms > 0 else 0.0)
                if t_start <= t_now < t_start + stim_dur:
                    I_stim1[k, 0] = stim_amp / (np.pi * d1 * dz)

        # Calculate d2v for the average Abeta fiber and the C-fiber
        d2v1_mean = np.mean(laplacian_neumann(v1.T, dz), axis=1)  # (N,)
        d2v2 = laplacian_neumann(v2, dz)

        B = - (n_abeta * inv_r1 * d2v1_mean + inv_r2 * d2v2) / sum_inv_r
        u_e = solve_banded((1, 1), A_poisson_eff, B)
        d2ue = laplacian_neumann(u_e, dz)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        # rhs1: (K,N); Cm1_arr (N,) and I_eph1 (N,) broadcast to (K,N).
        rhs1 = Cm1_arr / dt * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1.T).T
        rhs2 = Cm / dt * v2 + (sens_bias - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v2_mid_trace[step] = v2[mid]
        v2_global_max = max(v2_global_max, np.max(v2[100:]))
        if record_full:
            v1_rec[step] = v1[K // 2]
            v2_rec[step] = v2

    result = {"v2_mid": v2_mid_trace, "spiked": v2_global_max > 0.0}
    if record_full:
        result["v1"] = v1_rec
        result["v2"] = v2_rec
    return result

if __name__ == "__main__":
    print("Smoke test at w_cleft=200nm, no sensitization, dt=1us...")
    res = run_coupled_navc(w_cleft=200e-9, T=2e-3)
    print(f"  peak={res['v2_mid'].max()*1e3:.2f} mV, spiked={res['spiked']}")
