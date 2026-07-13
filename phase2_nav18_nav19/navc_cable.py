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

# Nav1.8/1.9 C-fiber parameters, tuned via point-neuron rheobase testing and
# cable propagation-safety-factor testing (see tuning notes: classical-HH-scale
# conductances failed to propagate continuously given Nav1.8's slow activation
# time constant; g_Na18 was increased until full-length propagation was achieved
# and confirmed numerically stable at dt=1us)
g_Na18 = 2000.0 * mS_cm2_to_S_m2  # S/m^2
g_Na19 = 0.2 * mS_cm2_to_S_m2     # S/m^2
g_K_HH = 36.0 * mS_cm2_to_S_m2    # S/m^2 (unchanged, classical delayed rectifier)
g_leak_HH = 0.3 * mS_cm2_to_S_m2  # S/m^2 (unchanged)
E_leak_2 = -55e-3                 # nominal nociceptor leak reversal (true resting Vm settles near -65mV; see validation notes)

def hh_k_rates(v):
    vmV = v * 1e3
    def safe_div(num, denom):
        denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
        return num / denom
    alpha_n = safe_div(0.01 * (vmV + 55.0), (1.0 - np.exp(-(vmV + 55.0) / 10.0))) * 1e3
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

def run_navc_alone(T=20e-3, stim_amp=1e-9, stim_dur=1e-3, dt=5e-6):
    """Isolated Nav1.8/1.9 C-fiber, current injected at z=0, no ephaptic coupling."""
    axial_coeff = d2 / (4.0 * rho_i)
    A_banded = build_implicit_operator(axial_coeff, dt, Cm, dz, N)

    v = np.full(N, E_leak_2)
    m8 = np.full(N, 0.02); h8 = np.full(N, 0.9); m9 = np.full(N, 0.05); n = np.full(N, 0.3)
    nsteps = int(T / dt)
    v_rec = np.zeros((nsteps, N))

    for step in range(nsteps):
        m8_inf, tau_m8, h8_inf, tau_h8, m9_inf, tau_m9 = nav_c_fiber_rates(v)
        m8 = m8 + dt * (m8_inf - m8) / tau_m8
        h8 = h8 + dt * (h8_inf - h8) / tau_h8
        m9 = m9 + dt * (m9_inf - m9) / tau_m9
        an, bn = hh_k_rates(v)
        n = n + dt * (an * (1 - n) - bn * n)

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

if __name__ == "__main__":
    print("Rheobase check (point-like: single node, short pulse)...")
    for amp in [0.5e-9, 1e-9, 2e-9, 5e-9]:
        v_rec = run_navc_alone(T=15e-3, stim_amp=amp, stim_dur=1e-3)
        peak = v_rec[:, 0].max() * 1e3
        print(f"  stim={amp*1e9:.1f} nA -> peak at z=0: {peak:.1f} mV")

    print("\nFull cable propagation test...")
    v_rec = run_navc_alone(T=25e-3, stim_amp=2e-9, stim_dur=1e-3)
    cv = estimate_cv(v_rec, dz, 5e-6, 100, 900)
    print(f"  CV (node@1mm -> node@9mm) = {cv} m/s  (target 0.5-1.0 m/s)")
    for z_mm, idx in [(1,100),(3,300),(5,500),(7,700),(9,900)]:
        print(f"  z={z_mm}mm peak={v_rec[:,idx].max()*1e3:.1f} mV")
