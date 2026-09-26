import numpy as np
from scipy.linalg import solve_banded
from ephaptic_model import *
from spike_detector import build_fixed_node_geometry

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

def run_abeta_alone(T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3, dz=10e-6, dt=2.5e-6):
    """Aβ fiber alone, current injected at node 0, no ephaptic coupling.
    IMEX scheme: implicit backward-Euler for axial diffusion, Rush-Larsen for CRRSS ion channels."""
    N, z, node_mask, f_node = build_fixed_node_geometry(dz=dz)
    Cm_node_comp = (2.0 * f_node + 0.005 * (1.0 - f_node)) * uF_cm2_to_F_m2
    Cm_internode = 0.005 * uF_cm2_to_F_m2
    Cm1_arr = np.where(node_mask, Cm_node_comp, Cm_internode)
    g_Na_CRRSS_eff = 1445.0 * f_node * mS_cm2_to_S_m2
    g_leak_CRRSS = 128.0 * mS_cm2_to_S_m2
    g_leak_internode = 0.006 * mS_cm2_to_S_m2
    g_leak_node_comp = g_leak_CRRSS * f_node + g_leak_internode * (1.0 - f_node)
    g_leak1_arr = np.where(node_mask, g_leak_node_comp, g_leak_internode)

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

        I_active = g_Na_CRRSS_eff * m**2 * h * (v - E_Na) + g_leak1_arr * (v - E_leak_1)
        I_passive = g_leak1_arr * (v - E_leak_1)
        I_ion = np.where(node_mask, I_active, I_passive)

        I_stim = np.zeros(N)
        if step * dt < stim_dur:
            # Stimulus normalization uses d1_axon to match the inner-axon reference area of the 1D cable PDE
            I_stim[0] = stim_amp / (np.pi * d1_axon * dz)

        rhs = Cm1_arr / dt * v + (I_stim - I_ion)
        v = solve_banded((1, 1), A_banded, rhs)
        v_rec[step] = v

    return v_rec, z

def run_cfiber_alone(T=20e-3, stim_amp=1e-9, stim_dur=1e-3, dz=10e-6, dt=2.5e-6):
    """C-fiber alone, current injected at z=0, no ephaptic coupling. IMEX scheme."""
    N, z, node_mask, f_node = build_fixed_node_geometry(dz=dz)
    v = np.full(N, -65e-3)
    m = np.full(N, 0.05)
    h = np.full(N, 0.6)
    n = np.full(N, 0.32)
    nsteps = int(T / dt)
    v_rec = np.zeros((nsteps, N))
    axial_coeff = d2 / (4.0 * rho_i)
    A_banded = build_implicit_operator(axial_coeff, dt, Cm, dz, N)

    for step in range(nsteps):
        am, bm, ah, bh, an, bn = hh_rates(v)
        m += dt * (am * (1 - m) - bm * m)
        h += dt * (ah * (1 - h) - bh * h)
        n += dt * (an * (1 - n) - bn * n)
        m, h, n = np.clip(m, 0, 1), np.clip(h, 0, 1), np.clip(n, 0, 1)

        I_ion = (g_Na_HH * m**3 * h * (v - E_Na)
                 + g_K_HH * n**4 * (v - E_K)
                 + g_leak_HH * (v - E_leak_2))

        I_stim = np.zeros(N)
        if step * dt < stim_dur:
            I_stim[0] = stim_amp / (np.pi * d2 * dz)

        rhs = Cm / dt * v + (I_stim - I_ion)
        v = solve_banded((1, 1), A_banded, rhs)
        v_rec[step] = v

    return v_rec, z

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
    print("Running Abeta fiber alone...")
    v1, _ = run_abeta_alone()
    peak = v1[:, 500].max()
    print(f"  Abeta peak voltage (propagated at Node 500): {peak*1e3:.1f} mV (expect spike well above 0 mV if firing)")
    cv1 = estimate_conduction_velocity(v1, dz, dt, 100, 900)
    print(f"  Abeta estimated conduction velocity: {cv1:.2f} m/s (expect ~30-60 m/s for myelinated 10um fiber)")

    print("Running C-fiber alone...")
    v2, _ = run_cfiber_alone()
    peak2 = v2.max()
    print(f"  C-fiber peak voltage: {peak2*1e3:.1f} mV")
    cv2 = estimate_conduction_velocity(v2, dz, dt, 50, 900)
    print(f"  C-fiber estimated conduction velocity: {cv2} m/s (expect ~0.5-1.0 m/s)")
