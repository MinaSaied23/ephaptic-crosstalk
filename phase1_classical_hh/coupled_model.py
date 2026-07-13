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

def run_coupled(w_cleft, T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3, record_full=False,
                 sens_bias=0.0, stim_freq=None, n_pulses=1):
    """
    Run the closed-loop coupled Aβ/C-fiber ephaptic model.
    Stimulus injected at Aβ node 0 (z=0).

    sens_bias: persistent depolarizing current density (A/m^2) applied
    uniformly along the C-fiber, representing peripheral sensitization by
    inflammatory mediators that partially depolarize the nociceptor,
    without on its own being suprathreshold.

    stim_freq, n_pulses: if stim_freq is set and n_pulses>1, deliver
    n_pulses identical stimulus pulses (each stim_amp/stim_dur) at node 0,
    spaced 1/stim_freq apart, mimicking repetitive mechanical stimulation
    (e.g. brushing, vibration) rather than a single static touch.
    """
    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1 / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    Cm1_arr = np.where(node_mask, Cm, Cm_internode)
    g_leak1_arr = np.where(node_mask, g_leak_CRRSS, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt, Cm1_arr, dz, N)
    A2 = build_implicit_operator(axial2, dt, Cm, dz, N)
    A_poisson = build_poisson_operator(dz, N)

    v1 = np.full(N, -70e-3)
    m1 = np.full(N, 0.05)
    h1 = np.full(N, 0.6)

    v2 = np.full(N, -65e-3)
    m2 = np.full(N, 0.05)
    h2 = np.full(N, 0.6)
    n2 = np.full(N, 0.32)

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

    nsteps = int(T / dt)
    mid = N // 2

    v2_mid_trace = np.zeros(nsteps)
    v1_rec = np.zeros((nsteps, N)) if record_full else None
    v2_rec = np.zeros((nsteps, N)) if record_full else None

    for step in range(nsteps):
        t_now = step * dt

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

        I_total = np.pi * d1 * I_ion1 + np.pi * d2 * I_ion2   # A/m
        B = r_e * I_total
        u_e = solve_banded((1, 1), A_poisson, B)
        d2ue = laplacian_neumann(u_e, dz)

        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        I_stim1 = np.zeros(N)
        for ps in pulse_starts:
            if ps <= t_now < ps + stim_dur:
                I_stim1[0] = stim_amp / (np.pi * d1 * dz)
                break

        rhs1 = Cm1_arr / dt * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt * v2 + (sens_bias - I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)

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
    print("Smoke test: train stimulus, mild sensitization...")
    res = run_coupled(w_cleft=200e-9, T=3e-3, stim_amp=100e-9, stim_dur=0.2e-3,
                       sens_bias=0.5, stim_freq=200.0, n_pulses=5, record_full=True)
    print(f"  spiked (midpoint)={res['spiked']}, any spike away from injection={(res['v2'][:,200:800]>0).any()}")
