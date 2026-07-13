import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import (dz, N, d1, d2, rho_i, Cm, Cm_internode,
                             E_Na, E_K, E_leak_1, g_Na_CRRSS, g_leak_CRRSS,
                             g_leak_internode, node_mask, crrss_rates,
                             r_e_from_cleft)
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

def run_coupled_navc(w_cleft, T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3, record_full=False,
                      sens_bias=0.0, stim_freq=None, n_pulses=1, dt=DT, kappa=1.0e9,
                      n_abeta=1):
    """Coupled Abeta (CRRSS) / C-fiber (Nav1.8/1.9) ephaptic model.

    n_abeta: number of identical, synchronously-firing Abeta fibers assumed to
    surround the C-fiber within the same shared extracellular compartment
    (spatial summation / multi-fiber bundle test). By symmetry (identical
    kinetics, identical stimulus, identical coupling to the shared field),
    all n_abeta fibers evolve identically, so a single Abeta cable is
    simulated and its ionic-current contribution to the shared extracellular
    source term I_total is scaled by n_abeta. Each fiber's own self-dynamics
    (and the ephaptic feedback it individually receives) are unaffected by
    n_abeta, consistent with the symmetric-copy assumption.
    """
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1 / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    Cm1_arr = np.where(node_mask, Cm, Cm_internode)
    g_leak1_arr = np.where(node_mask, g_leak_CRRSS, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)
    A_poisson = build_poisson_operator(dz, N, kappa=kappa)

    v1 = np.full(N, -70e-3)
    m1 = np.full(N, 0.05); h1 = np.full(N, 0.6)

    v2 = np.full(N, E_leak_2)
    m8 = np.full(N, 0.02); h8 = np.full(N, 0.9); m9 = np.full(N, 0.05); n = np.full(N, 0.3)

    if sens_bias != 0.0:
        for _ in range(int(6e-3 / dt)):
            m8i, tm8, h8i, th8, m9i, tm9 = nav_c_fiber_rates(v2)
            m8 = m8 + dt*(m8i-m8)/tm8; h8 = h8 + dt*(h8i-h8)/th8; m9 = m9 + dt*(m9i-m9)/tm9
            an, bn = hh_k_rates(v2); n = n + dt*(an*(1-n)-bn*n)
            I_ion2 = g_Na18*m8**3*h8*(v2-E_Na) + g_Na19*m9*(v2-E_Na) + g_K_HH*n**4*(v2-E_K) + g_leak_HH*(v2-E_leak_2)
            rhs2 = Cm/dt*v2 + (sens_bias - I_ion2)
            v2 = solve_banded((1,1), A2, rhs2)

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

    for step in range(nsteps):
        t_now = step * dt

        am1, bm1, ah1, bh1 = crrss_rates(v1)
        m1 = np.clip(np.where(node_mask, m1+dt*(am1*(1-m1)-bm1*m1), m1), 0, 1)
        h1 = np.clip(np.where(node_mask, h1+dt*(ah1*(1-h1)-bh1*h1), h1), 0, 1)
        I_active1 = g_Na_CRRSS*m1**2*h1*(v1-E_Na) + g_leak1_arr*(v1-E_leak_1)
        I_passive1 = g_leak1_arr*(v1-E_leak_1)
        I_ion1 = np.where(node_mask, I_active1, I_passive1)

        m8i, tm8, h8i, th8, m9i, tm9 = nav_c_fiber_rates(v2)
        m8 = m8 + dt*(m8i-m8)/tm8
        h8 = h8 + dt*(h8i-h8)/th8
        m9 = m9 + dt*(m9i-m9)/tm9
        an, bn = hh_k_rates(v2)
        n = n + dt*(an*(1-n)-bn*n)
        I_ion2 = g_Na18*m8**3*h8*(v2-E_Na) + g_Na19*m9*(v2-E_Na) + g_K_HH*n**4*(v2-E_K) + g_leak_HH*(v2-E_leak_2)

        I_total = n_abeta * np.pi*d1*I_ion1 + np.pi*d2*I_ion2
        B = r_e * I_total
        u_e = solve_banded((1,1), A_poisson, B)
        d2ue = laplacian_neumann(u_e, dz)
        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        I_stim1 = np.zeros(N)
        for ps in pulse_starts:
            if ps <= t_now < ps + stim_dur:
                I_stim1[0] = stim_amp / (np.pi*d1*dz)
                break

        rhs1 = Cm1_arr/dt*v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1,1), A1, rhs1)
        rhs2 = Cm/dt*v2 + (sens_bias - I_ion2 + I_eph2)
        v2 = solve_banded((1,1), A2, rhs2)

        v2_mid_trace[step] = v2[mid]
        if record_full:
            v1_rec[step] = v1
            v2_rec[step] = v2

    result = {"v2_mid": v2_mid_trace, "spiked": v2_mid_trace.max() > 0.0}
    if record_full:
        result["v1"] = v1_rec
        result["v2"] = v2_rec
    return result

if __name__ == "__main__":
    print("Smoke test at w_cleft=200nm, no sensitization, dt=1us...")
    res = run_coupled_navc(w_cleft=200e-9, T=1.5e-3)
    print(f"  peak={res['v2_mid'].max()*1e3:.2f} mV, spiked={res['spiked']}")
