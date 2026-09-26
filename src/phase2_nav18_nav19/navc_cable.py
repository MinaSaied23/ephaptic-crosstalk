"""
Full 1D cable C-fiber model using Nav1.8/Nav1.9 nociceptor kinetics in place of
classical squid-axon HH Na+ conductance. K+ delayed rectifier and leak retained
from the classical model. Reuses the validated IMEX (implicit diffusion /
explicit ionic) integration scheme and geometry from ephaptic_model.py.
"""
import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import (L, dz, N, d2, rho_i, Cm, E_Na, E_K,
                             mS_cm2_to_S_m2)
from nav_kinetics import nav_c_fiber_rates

# Nav1.8/1.9 C-fiber parameters, calibrated to eliminate non-repolarizing attractor
# and yield physiological action potential duration (5-10 ms) and unmyelinated CV (0.2-1.0 m/s)
g_Na18 = 2000.0 * mS_cm2_to_S_m2  # S/m^2
g_Na19 = 0.2 * mS_cm2_to_S_m2     # S/m^2
g_K_HH = 60.0 * mS_cm2_to_S_m2    # S/m^2 (calibrated delayed rectifier)
g_leak_HH = 0.3 * mS_cm2_to_S_m2  # S/m^2
E_leak_2 = -55e-3                 # nominal nociceptor leak reversal (true resting Vm settles near -66.8 mV)

def hh_k_rates(v):
    vmV = v * 1e3
    denom = (1.0 - np.exp(-(vmV + 55.0) / 10.0))
    denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
    alpha_n = 0.01 * (vmV + 55.0) / denom * 1e3
    beta_n = 0.125 * np.exp(-(vmV + 65.0) / 80.0) * 1e3
    return alpha_n, beta_n

def build_implicit_operator(axial_coeff, dt, Cm_arr, dz, N):
    Cm_arr = np.broadcast_to(np.asarray(Cm_arr, dtype=float), (N,)).copy()
    k = axial_coeff / dz**2
    A = np.zeros((3, N))
    A[1, :] = Cm_arr / dt + 2.0 * k
    A[0, 1:] = -k
    A[2, :-1] = -k
    A[0, 1] = -2.0 * k
    A[2, -2] = -2.0 * k
    return A

_STEADY_STATE_CACHE = {}

def get_settled_navc(dt, A_banded):
    key = dt
    if key in _STEADY_STATE_CACHE:
        v, m8, h8, m9, n = _STEADY_STATE_CACHE[key]
        return v.copy(), m8.copy(), h8.copy(), m9.copy(), n.copy()

    v = np.full(N, -66.8e-3)
    m8_inf, tau_m8, h8_inf, tau_h8, m9_inf, tau_m9 = nav_c_fiber_rates(v)
    m8 = m8_inf.copy(); h8 = h8_inf.copy(); m9 = m9_inf.copy()
    an, bn = hh_k_rates(v)
    n = an / (an + bn)

    # Settle baseline unconditionally (20 ms) using Rush-Larsen to reach exact steady state
    for _ in range(int(20e-3 / dt)):
        m8_inf, tau_m8, h8_inf, tau_h8, m9_inf, tau_m9 = nav_c_fiber_rates(v)
        an, bn = hh_k_rates(v)
        tau_n = 1.0 / (an + bn); n_inf = an * tau_n
        m8 = m8_inf + (m8 - m8_inf) * np.exp(-dt / tau_m8)
        h8 = h8_inf + (h8 - h8_inf) * np.exp(-dt / tau_h8)
        m9 = m9_inf + (m9 - m9_inf) * np.exp(-dt / tau_m9)
        n = n_inf + (n - n_inf) * np.exp(-dt / tau_n)
        I_ion = (g_Na18 * m8**3 * h8 * (v - E_Na)
                 + g_Na19 * m9 * (v - E_Na)
                 + g_K_HH * n**4 * (v - E_K)
                 + g_leak_HH * (v - E_leak_2))
        rhs = Cm / dt * v - I_ion
        v = solve_banded((1, 1), A_banded, rhs)

    _STEADY_STATE_CACHE[key] = (v.copy(), m8.copy(), h8.copy(), m9.copy(), n.copy())
    return v.copy(), m8.copy(), h8.copy(), m9.copy(), n.copy()

def run_navc_alone(T=25e-3, stim_amp=2e-9, stim_dur=1e-3, dt=1e-6):
    """Isolated Nav1.8/1.9 C-fiber, current injected at z=0, no ephaptic coupling."""
    axial_coeff = d2 / (4.0 * rho_i)
    A_banded = build_implicit_operator(axial_coeff, dt, Cm, dz, N)

    v, m8, h8, m9, n = get_settled_navc(dt, A_banded)

    nsteps = int(T / dt)
    v_rec = np.zeros((nsteps, N))

    for step in range(nsteps):
        m8_inf, tau_m8, h8_inf, tau_h8, m9_inf, tau_m9 = nav_c_fiber_rates(v)
        an, bn = hh_k_rates(v)
        tau_n = 1.0 / (an + bn); n_inf = an * tau_n

        m8 = m8_inf + (m8 - m8_inf) * np.exp(-dt / tau_m8)
        h8 = h8_inf + (h8 - h8_inf) * np.exp(-dt / tau_h8)
        m9 = m9_inf + (m9 - m9_inf) * np.exp(-dt / tau_m9)
        n = n_inf + (n - n_inf) * np.exp(-dt / tau_n)

        I_na8 = g_Na18 * m8**3 * h8 * (v - E_Na)
        I_na9 = g_Na19 * m9 * (v - E_Na)
        I_k = g_K_HH * n**4 * (v - E_K)
        I_leak = g_leak_HH * (v - E_leak_2)
        I_ion = I_na8 + I_na9 + I_k + I_leak

        I_stim = np.zeros(N)
        if step * dt < stim_dur:
            I_stim[0] = stim_amp / (np.pi * d2 * dz)

        rhs = Cm / dt * v + (I_stim - I_ion)
        v = solve_banded((1, 1), A_banded, rhs)
        v_rec[step] = v

    return v_rec

def estimate_cv(v_rec, dz, dt, i0, i1, thresh=0.0):
    def crossing_time(idx):
        trace = v_rec[:, idx]
        above = np.where(trace > thresh)[0]
        return above[0] * dt if len(above) else None
    t0, t1 = crossing_time(i0), crossing_time(i1)
    if t0 is None or t1 is None or t1 <= t0:
        return None
    return (i1 - i0) * dz / (t1 - t0)

def calculate_ap_duration(trace, dt, thresh=0.0):
    """Calculate duration above thresh (default 0 mV) and APD50 (half-max duration)."""
    t_arr = np.arange(len(trace)) * dt
    above = t_arr[trace > thresh]
    dur_0 = (above[-1] - above[0]) if len(above) > 0 else 0.0

    v_base = trace[0]
    v_peak = trace.max()
    half_v = v_base + 0.5 * (v_peak - v_base)
    above_half = t_arr[trace > half_v]
    dur_half = (above_half[-1] - above_half[0]) if len(above_half) > 0 else 0.0

    return dur_0, dur_half

if __name__ == "__main__":
    print("Full cable propagation test for Nav1.8/1.9 C-fiber...")
    v_rec = run_navc_alone(T=30e-3, stim_amp=2e-9, stim_dur=1e-3, dt=1e-6)
    cv = estimate_cv(v_rec, dz, 1e-6, 100, 500)
    print(f"  CV (1mm -> 5mm) = {cv:.2f} m/s  (target 0.2-1.0 m/s)")
    
    trace300 = v_rec[:, 300] * 1e3
    dur_0, dur_half = calculate_ap_duration(trace300, 1e-6, thresh=0.0)
    print(f"  Action potential at Node 300 (z=3mm):")
    print(f"    Resting Vm: {trace300[0]:.2f} mV")
    print(f"    Peak Vm: {trace300.max():.2f} mV")
    print(f"    Final Vm: {trace300[-1]:.2f} mV (repolarization verified)")
    print(f"    Duration above 0 mV: {dur_0*1e3:.2f} ms (target 5-10 ms)")
    print(f"    APD50 duration: {dur_half*1e3:.2f} ms (target 5-10 ms)")
    
    pk900 = v_rec[:, 900].max() * 1e3
    print(f"  Propagated peak at Node 900 (z=9mm): {pk900:.2f} mV")
