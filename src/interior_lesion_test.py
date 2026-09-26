"""
Interior Lesion Test (Task 2.1)
Tests whether C-fiber excitation occurs via genuine ephaptic coupling inside an interior lesion
(z in [3, 7] mm) or was an artifact of direct current injection at the stimulation electrode (z = 0).

Protocol:
- Stimulation site (z = 0 to 2 mm): r_e is effectively zero (grounded bulk fluid, u_e = 0).
- Lesion zone (z = 3 to 7 mm): pathological cleft (w_cleft = 20-50 nm).
- Tests:
  1. Temporal summation at 800 Hz (train of 5, 10, 20 pulses).
  2. Multi-fiber bundle with n = 25 synchronized Aβ fibers.
- Tested across both Classical HH and Nav1.8/Nav1.9 C-fiber models.
"""

import os
import sys
import numpy as np
from scipy.linalg import solve_banded

# Paths
base_dir = os.path.dirname(__file__)
p1_dir = os.path.join(base_dir, 'phase1_classical_hh')
p2_dir = os.path.join(base_dir, 'phase2_nav18_nav19')

sys.path.insert(0, p1_dir)
import ephaptic_model as em1
from coupled_model import build_poisson_operator, laplacian_neumann

sys.path.insert(0, p2_dir)
import navc_cable
import nav_kinetics
from navc_cable import g_Na18, g_Na19, g_K_HH, g_leak_HH, E_leak_2, hh_k_rates
from nav_kinetics import nav_c_fiber_rates

def run_interior_lesion_phase1(w_cleft=20e-9, T=15e-3, stim_amp=100e-9, stim_dur=0.2e-3,
                               stim_freq=800.0, n_pulses=10, sens_bias=0.0,
                               lesion_z_start=3e-3, lesion_z_end=7e-3,
                               ground_z=2e-3, kappa=1.0e9, method='dirichlet'):
    """
    Classical HH C-fiber coupled to CRRSS Aβ with interior lesion coupling.
    """
    dz = em1.dz
    N = em1.N
    dt = em1.dt
    d1_axon = em1.d1_axon
    d1 = em1.d1
    d2 = em1.d2
    rho_i = em1.rho_i
    Cm1_arr = em1.Cm1_arr
    Cm = em1.Cm
    node_mask = em1.node_mask
    E_Na = em1.E_Na
    E_K = em1.E_K
    E_leak_1 = em1.E_leak_1
    E_leak_2 = em1.E_leak_2
    g_Na_CRRSS = em1.g_Na_CRRSS
    g_leak1_arr = em1.g_leak1_arr
    g_Na_HH = em1.g_Na_HH
    g_K_HH_val = em1.g_K_HH
    g_leak_HH_val = em1.g_leak_HH
    r_e = em1.r_e_from_cleft(w_cleft)

    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    from validate_single_fibers import build_implicit_operator
    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)

    i_start = int(round(lesion_z_start / dz)) # 300
    i_end = int(round(lesion_z_end / dz))     # 700
    i_ground = int(round(ground_z / dz))      # 200

    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e
    sum_inv_r = inv_re + inv_r1 + inv_r2
    kappa_eff = (kappa / r_e) / sum_inv_r

    if method == 'dirichlet':
        # Solve u_e only on interior of lesion (i_start+1 to i_end-1) with u_e=0 at boundaries
        M = (i_end - 1) - (i_start + 1) + 1
        A_poiss_dir = np.zeros((3, M))
        A_poiss_dir[1, :] = -2.0 / dz**2 - kappa_eff
        A_poiss_dir[0, 1:] = 1.0 / dz**2
        A_poiss_dir[2, :-1] = 1.0 / dz**2
    else:
        # Smooth mask m(z)
        z = np.arange(N) * dz
        mask = np.zeros(N)
        for i in range(N):
            zi = z[i]
            if zi < ground_z:
                mask[i] = 0.0
            elif zi < lesion_z_start:
                mask[i] = 0.5 * (1.0 - np.cos(np.pi * (zi - ground_z) / (lesion_z_start - ground_z)))
            elif zi <= lesion_z_end:
                mask[i] = 1.0
            elif zi <= 8e-3:
                mask[i] = 0.5 * (1.0 + np.cos(np.pi * (zi - lesion_z_end) / (8e-3 - lesion_z_end)))
            else:
                mask[i] = 0.0
        A_poisson_full = build_poisson_operator(dz, N, kappa=kappa_eff)

    v1 = np.full(N, -80e-3)
    am1, bm1, ah1, bh1 = em1.crrss_rates(-80e-3)
    m1 = np.full(N, am1 / (am1 + bm1))
    h1 = np.full(N, ah1 / (ah1 + bh1))

    v2 = np.full(N, -65e-3)
    m2 = np.full(N, 0.05)
    h2 = np.full(N, 0.6)
    n2 = np.full(N, 0.32)

    if stim_freq is not None and n_pulses > 1:
        period = 1.0 / stim_freq
        pulse_starts = [i * period for i in range(n_pulses)]
    else:
        pulse_starts = [0.0]

    nsteps = int(T / dt)
    v2_rec = np.zeros((nsteps, N))
    u_e_rec = np.zeros((nsteps, N))

    for step in range(nsteps):
        t_now = step * dt

        am1, bm1, ah1, bh1 = em1.crrss_rates(v1)
        tau_m1 = 1.0 / (am1 + bm1); m1_inf = am1 * tau_m1
        tau_h1 = 1.0 / (ah1 + bh1); h1_inf = ah1 * tau_h1
        m1 = np.where(node_mask, m1_inf + (m1 - m1_inf) * np.exp(-dt / tau_m1), m1)
        h1 = np.where(node_mask, h1_inf + (h1 - h1_inf) * np.exp(-dt / tau_h1), h1)
        I_active1 = g_Na_CRRSS * m1**2 * h1 * (v1 - E_Na) + g_leak1_arr * (v1 - E_leak_1)
        I_passive1 = g_leak1_arr * (v1 - E_leak_1)
        I_ion1 = np.where(node_mask, I_active1, I_passive1)

        am2, bm2, ah2, bh2, an2, bn2 = em1.hh_rates(v2)
        m2 = np.clip(m2 + dt * (am2 * (1 - m2) - bm2 * m2), 0, 1)
        h2 = np.clip(h2 + dt * (ah2 * (1 - h2) - bh2 * h2), 0, 1)
        n2 = np.clip(n2 + dt * (an2 * (1 - n2) - bn2 * n2), 0, 1)
        I_ion2 = (g_Na_HH * m2**3 * h2 * (v2 - E_Na)
                  + g_K_HH_val * n2**4 * (v2 - E_K)
                  + g_leak_HH_val * (v2 - E_leak_2))

        I_stim1 = np.zeros(N)
        for ps in pulse_starts:
            if ps <= t_now < ps + stim_dur:
                I_stim1[0] = stim_amp / (np.pi * d1 * dz)
                break

        d2v1 = laplacian_neumann(v1, dz)
        d2v2 = laplacian_neumann(v2, dz)

        u_e = np.zeros(N)
        if method == 'dirichlet':
            B_sub = - (inv_r1 * d2v1[i_start+1:i_end] + inv_r2 * d2v2[i_start+1:i_end]) / sum_inv_r
            u_e_sub = solve_banded((1, 1), A_poiss_dir, B_sub)
            u_e[i_start+1:i_end] = u_e_sub
        else:
            B_masked = - mask * (inv_r1 * d2v1 + inv_r2 * d2v2) / sum_inv_r
            u_e = solve_banded((1, 1), A_poisson_full, B_masked) * mask

        d2ue = laplacian_neumann(u_e, dz)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        rhs1 = Cm1_arr / dt * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt * v2 + (sens_bias - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v2_rec[step] = v2
        u_e_rec[step] = u_e

    return {"v2": v2_rec, "u_e": u_e_rec, "dz": dz, "dt": dt}

def run_interior_lesion_phase2(w_cleft=20e-9, T=10e-3, stim_amp=100e-9, stim_dur=0.2e-3,
                               stim_freq=None, n_pulses=1, n_abeta=25.0, jitter_ms=0.0,
                               sens_bias=0.0, lesion_z_start=3e-3, lesion_z_end=7e-3,
                               ground_z=2e-3, kappa=1.0e9, dt=1e-6, method='dirichlet'):
    """
    Phase 2 Nav1.8/Nav1.9 C-fiber coupled to n_abeta CRRSS Aβ fibers with interior lesion coupling.
    """
    dz = em1.dz
    N = em1.N
    d1_axon = em1.d1_axon
    d1 = em1.d1
    d2 = em1.d2
    rho_i = em1.rho_i
    Cm1_arr = em1.Cm1_arr
    Cm = em1.Cm
    node_mask = em1.node_mask
    E_Na = em1.E_Na
    E_K = em1.E_K
    E_leak_1 = em1.E_leak_1
    g_Na_CRRSS = em1.g_Na_CRRSS
    g_leak1_arr = em1.g_leak1_arr
    r_e = em1.r_e_from_cleft(w_cleft)

    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    from navc_cable import build_implicit_operator, get_settled_navc
    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)

    i_start = int(round(lesion_z_start / dz)) # 300
    i_end = int(round(lesion_z_end / dz))     # 700
    i_ground = int(round(ground_z / dz))      # 200

    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e
    sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
    kappa_eff = (kappa / r_e) / sum_inv_r

    if method == 'dirichlet':
        M = (i_end - 1) - (i_start + 1) + 1
        A_poiss_dir = np.zeros((3, M))
        A_poiss_dir[1, :] = -2.0 / dz**2 - kappa_eff
        A_poiss_dir[0, 1:] = 1.0 / dz**2
        A_poiss_dir[2, :-1] = 1.0 / dz**2
    else:
        z = np.arange(N) * dz
        mask = np.zeros(N)
        for i in range(N):
            zi = z[i]
            if zi < ground_z:
                mask[i] = 0.0
            elif zi < lesion_z_start:
                mask[i] = 0.5 * (1.0 - np.cos(np.pi * (zi - ground_z) / (lesion_z_start - ground_z)))
            elif zi <= lesion_z_end:
                mask[i] = 1.0
            elif zi <= 8e-3:
                mask[i] = 0.5 * (1.0 + np.cos(np.pi * (zi - lesion_z_end) / (8e-3 - lesion_z_end)))
            else:
                mask[i] = 0.0
        A_poisson_full = build_poisson_operator(dz, N, kappa=kappa_eff)

    K = 21 if jitter_ms > 0.0 else 1
    jitter_offsets = np.linspace(-jitter_ms*1e-3/2, jitter_ms*1e-3/2, K) if K > 1 else [0.0]

    v1 = np.full((K, N), -80e-3)
    am1, bm1, ah1, bh1 = em1.crrss_rates(-80e-3)
    m1 = np.full((K, N), am1 / (am1 + bm1))
    h1 = np.full((K, N), ah1 / (ah1 + bh1))

    from coupled_navc_model import get_settled_c_fiber
    v2, m8, h8, m9, n = get_settled_c_fiber(sens_bias, dt, A2, Cm)

    if stim_freq is not None and n_pulses > 1:
        period = 1.0 / stim_freq
        pulse_starts = [i * period for i in range(n_pulses)]
    else:
        pulse_starts = [0.0]

    nsteps = int(T / dt)
    v2_rec = np.zeros((nsteps, N))
    u_e_rec = np.zeros((nsteps, N))

    for step in range(nsteps):
        t_now = step * dt

        am1, bm1, ah1, bh1 = em1.crrss_rates(v1)
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
                t_start = ps + jitter_offsets[k] + (jitter_ms * 1e-3 / 2.0 if jitter_ms > 0 else 0.0)
                if t_start <= t_now < t_start + stim_dur:
                    I_stim1[k, 0] = stim_amp / (np.pi * d1 * dz)

        d2v1_mean = np.mean(laplacian_neumann(v1.T, dz), axis=1)
        d2v2 = laplacian_neumann(v2, dz)

        u_e = np.zeros(N)
        if method == 'dirichlet':
            B_sub = - (n_abeta * inv_r1 * d2v1_mean[i_start+1:i_end] + inv_r2 * d2v2[i_start+1:i_end]) / sum_inv_r
            u_e_sub = solve_banded((1, 1), A_poiss_dir, B_sub)
            u_e[i_start+1:i_end] = u_e_sub
        else:
            B_masked = - mask * (n_abeta * inv_r1 * d2v1_mean + inv_r2 * d2v2) / sum_inv_r
            u_e = solve_banded((1, 1), A_poisson_full, B_masked) * mask

        d2ue = laplacian_neumann(u_e, dz)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        rhs1 = Cm1_arr / dt * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1.T).T

        rhs2 = Cm / dt * v2 + (sens_bias - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

        v2_rec[step] = v2
        u_e_rec[step] = u_e

    return {"v2": v2_rec, "u_e": u_e_rec, "dz": dz, "dt": dt}
