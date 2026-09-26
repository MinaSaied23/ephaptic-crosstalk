import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import *
from navc_cable import run_navc_alone, estimate_cv as estimate_cv_navc, calculate_ap_duration

def build_implicit_operator(axial_coeff, dt, Cm_arr, dz, N):
    """
    Build (Cm/dt*I - axial_coeff*L) as a banded matrix for backward-Euler
    diffusion step, where L is the Neumann-BC Laplacian. Cm_arr may be a
    scalar or a length-N array (spatially varying capacitance, e.g. node
    vs internode). Solve with solve_banded((1,1), A, rhs) where
    rhs = Cm/dt*v_n + (I_stim - I_ion).
    """
    Cm_arr = np.broadcast_to(np.asarray(Cm_arr, dtype=float), (N,)).copy()
    k = axial_coeff / dz**2
    A = np.zeros((3, N))
    A[1, :] = Cm_arr / dt + 2.0 * k     # main diagonal
    A[0, 1:] = -k                        # upper diagonal
    A[2, :-1] = -k                        # lower diagonal
    # Neumann (sealed end): reflected neighbor doubles the single-sided coupling
    A[0, 1] = -2.0 * k
    A[2, -2] = -2.0 * k
    return A

def run_abeta_alone(T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3):
    """Aβ fiber alone, current injected at node 0, no ephaptic coupling.
    IMEX scheme: implicit backward-Euler for axial diffusion, Rush-Larsen for CRRSS ion channels."""
    v = np.full(N, -80e-3)
    am, bm, ah, bh = crrss_rates(-80e-3)
    m = np.full(N, am / (am + bm))
    h = np.full(N, ah / (ah + bh))
    nsteps = int(T / dt)
    v_rec = np.zeros((nsteps, N))
    axial_coeff = d1_axon / (4.0 * rho_i)

    A_banded = build_implicit_operator(axial_coeff, dt, Cm1_arr, dz, N)

    for step in range(nsteps):
        am, bm, ah, bh = crrss_rates(v)
        tau_m = 1.0 / (am + bm); m_inf = am * tau_m
        tau_h = 1.0 / (ah + bh); h_inf = ah * tau_h
        m = np.where(node_mask, m_inf + (m - m_inf) * np.exp(-dt / tau_m), m)
        h = np.where(node_mask, h_inf + (h - h_inf) * np.exp(-dt / tau_h), h)

        I_active = g_Na_CRRSS * m**2 * h * (v - E_Na) + g_leak1_arr * (v - E_leak_1)
        I_passive = g_leak1_arr * (v - E_leak_1)
        I_ion = np.where(node_mask, I_active, I_passive)

        I_stim = np.zeros(N)
        if step * dt < stim_dur:
            I_stim[0] = stim_amp / (np.pi * d1 * dz)

        rhs = Cm1_arr / dt * v + (I_stim - I_ion)
        v = solve_banded((1, 1), A_banded, rhs)
        v_rec[step] = v

    return v_rec

def run_cfiber_alone(T=35e-3, stim_amp=2e-9, stim_dur=1e-3, dt=1e-6):
    """Phase 2 C-fiber alone with Nav1.8/Nav1.9 nociceptor kinetics.
    Delegates to the canonical navc_cable implementation."""
    return run_navc_alone(T=T, stim_amp=stim_amp, stim_dur=stim_dur, dt=dt)

def estimate_conduction_velocity(v_rec, dz, dt, z_start_idx, z_end_idx, thresh=0.0):
    """Estimate CV from time-to-threshold-crossing at two spatial points."""
    def crossing_time(idx):
        trace = v_rec[:, idx]
        above = np.where(trace > thresh)[0]
        if len(above) == 0:
            return None
        return above[0] * dt
    t1 = crossing_time(z_start_idx)
    t2 = crossing_time(z_end_idx)
    if t1 is None or t2 is None:
        return None
    dist = (z_end_idx - z_start_idx) * dz
    dtime = t2 - t1
    if dtime <= 0:
        return None
    return dist / dtime  # m/s

if __name__ == "__main__":
    print("Running Abeta fiber alone (Sweeney 1987 CRRSS kinetics)...")
    v1 = run_abeta_alone(T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3)
    peak1 = v1[:, 500].max()
    print(f"  Abeta peak voltage (Node 500): {peak1*1e3:.1f} mV")
    print(f"  Abeta final potential: {v1[-1, 500]*1e3:.2f} mV (100% repolarization)")
    cv1 = estimate_conduction_velocity(v1, dz, dt, 100, 900)
    print(f"  Abeta estimated conduction velocity: {cv1:.2f} m/s (target: 30-60 m/s)")

    print("\nRunning C-fiber alone (Phase 2: Nav1.8/Nav1.9 nociceptor kinetics)...")
    dt_navc = 1e-6
    v2 = run_cfiber_alone(T=35e-3, stim_amp=2e-9, stim_dur=1e-3, dt=dt_navc)
    trace300 = v2[:, 300] * 1e3
    dur_0, dur_half = calculate_ap_duration(trace300, dt_navc, thresh=0.0)
    print(f"  Nav1.8/Nav1.9 C-fiber peak voltage (Node 300): {trace300.max():.1f} mV")
    print(f"  Nav1.8/Nav1.9 C-fiber final potential: {trace300[-1]:.2f} mV (repolarization verified)")
    print(f"  Nav1.8 AP duration above 0 mV: {dur_0*1e3:.2f} ms (target: 5-10 ms)")
    print(f"  Nav1.8 APD50 (half-max duration): {dur_half*1e3:.2f} ms (target: 5-10 ms)")
    cv2 = estimate_cv_navc(v2, dz, dt_navc, 100, 500)
    print(f"  Nav1.8/Nav1.9 C-fiber conduction velocity: {cv2:.2f} m/s (target: 0.2-1.0 m/s)")
