"""
audit_reference_solver.py

Independent reference check of the production Abeta (CRRSS) cable solver
(Sec. 2.4.3 of the manuscript).

Production solver (phase1_classical_hh/validate_single_fibers.py):
    backward-Euler axial diffusion (IMEX), Rush-Larsen gate update using the
    voltage at the start of the step, ionic current explicit.

Reference solver (this file):
    Crank-Nicolson axial diffusion (second order in time), ionic and stimulus
    currents explicit at step n, and a Rush-Larsen gate update that uses the
    midpoint voltage 0.5*(v_n + v_{n+1}).

The reference differs from production in the time integration of the axial
term and in the voltage used for the gates. It shares the membrane model,
geometry and explicit treatment of the ionic current with production, so it
checks the numerical integration of the Abeta cable only. It is not a full
reference solver for the coupled multi-fiber system.

Usage (from the repository root or from src/):
    python src/audit_reference_solver.py
"""

import os
import sys

import numpy as np
from scipy.linalg import solve_banded

_SRC = os.path.dirname(os.path.abspath(__file__))
_P1 = os.path.join(_SRC, "phase1_classical_hh")
if _P1 not in sys.path:
    sys.path.insert(0, _P1)

from ephaptic_model import (  # noqa: E402
    crrss_rates, E_Na, E_leak_1, d1_axon, rho_i,
    uF_cm2_to_F_m2, mS_cm2_to_S_m2, Cm_internode, g_leak_internode,
)
from spike_detector import build_fixed_node_geometry  # noqa: E402
from validate_single_fibers import run_abeta_alone  # noqa: E402


def run_crank_nicolson_reference(dz=10e-6, dt=2.5e-6, T=6e-3,
                                 stim_amp=2e-9, stim_dur=0.2e-3):
    """Isolated Abeta fiber, current injected at node 0."""
    N, z, node_mask, f_node = build_fixed_node_geometry(dz=dz)

    Cm_node = (2.0 * f_node + 0.005 * (1.0 - f_node)) * uF_cm2_to_F_m2
    Cm = np.where(node_mask, Cm_node, Cm_internode)
    g_Na = 1445.0 * f_node * mS_cm2_to_S_m2
    g_leak_node = (128.0 * f_node + 0.006 * (1.0 - f_node)) * mS_cm2_to_S_m2
    g_leak = np.where(node_mask, g_leak_node, g_leak_internode)

    axial_coeff = d1_axon / (4.0 * rho_i)
    k = axial_coeff / dz**2

    # (Cm/dt - 0.5*axial_coeff*L) v^{n+1} = Cm/dt*v^n + 0.5*axial_coeff*L v^n + I_stim - I_ion
    A = np.zeros((3, N))
    A[1, :] = Cm / dt + k
    A[0, 1:] = -0.5 * k
    A[2, :-1] = -0.5 * k
    A[0, 1] = -k          # sealed end (Neumann): reflected neighbor
    A[2, -2] = -k

    def laplacian_neumann(x):
        d2 = np.zeros_like(x)
        d2[1:-1] = (x[2:] - 2.0 * x[1:-1] + x[:-2]) / dz**2
        d2[0] = 2.0 * (x[1] - x[0]) / dz**2
        d2[-1] = 2.0 * (x[-2] - x[-1]) / dz**2
        return d2

    def rush_larsen(v_gate, m, h):
        am, bm, ah, bh = crrss_rates(v_gate)
        tau_m = 1.0 / (am + bm)
        tau_h = 1.0 / (ah + bh)
        m_new = am * tau_m + (m - am * tau_m) * np.exp(-dt / tau_m)
        h_new = ah * tau_h + (h - ah * tau_h) * np.exp(-dt / tau_h)
        return np.where(node_mask, m_new, m), np.where(node_mask, h_new, h)

    v = np.full(N, -80e-3)
    am, bm, ah, bh = crrss_rates(-80e-3)
    m = np.full(N, am / (am + bm))
    h = np.full(N, ah / (ah + bh))

    nsteps = int(round(T / dt))
    v_rec = np.zeros((nsteps, N))

    for step in range(nsteps):
        I_leak = g_leak * (v - E_leak_1)
        I_ion = np.where(node_mask, g_Na * m**2 * h * (v - E_Na) + I_leak, I_leak)

        I_stim = np.zeros(N)
        if step * dt < stim_dur:
            I_stim[0] = stim_amp / (np.pi * d1_axon * dz)

        rhs = Cm / dt * v + 0.5 * axial_coeff * laplacian_neumann(v) + I_stim - I_ion
        v_next = solve_banded((1, 1), A, rhs)

        m, h = rush_larsen(0.5 * (v + v_next), m, h)
        v = v_next
        v_rec[step] = v

    return v_rec, z


def waveform_metrics(v_rec, z, dt):
    """CV from maximum upstroke dV/dt between z = 4 mm and z = 8 mm; peak at z = 4 mm."""
    i4 = int(np.argmin(np.abs(z - 4.0e-3)))
    i8 = int(np.argmin(np.abs(z - 8.0e-3)))
    t4 = np.argmax(np.diff(v_rec[:, i4])) * dt
    t8 = np.argmax(np.diff(v_rec[:, i8])) * dt
    cv = (z[i8] - z[i4]) / (t8 - t4) if t8 > t4 else float("nan")
    peak_mV = v_rec[:, i4].max() * 1e3
    return {"cv": cv, "peak_mV": peak_mV, "excursion_mV": peak_mV + 80.0}


if __name__ == "__main__":
    dz, dt, T, amp = 10e-6, 0.625e-6, 6e-3, 2e-9
    print(f"Reference solver comparison: dz = {dz*1e6:.0f} um, dt = {dt*1e6:.3f} us, "
          f"stimulus {amp*1e9:.0f} nA / 0.2 ms at node 0")

    v_prod, z = run_abeta_alone(T=T, stim_amp=amp, stim_dur=0.2e-3, dz=dz, dt=dt)
    v_ref, _ = run_crank_nicolson_reference(dz=dz, dt=dt, T=T, stim_amp=amp)
    p = waveform_metrics(v_prod, z, dt)
    r = waveform_metrics(v_ref, z, dt)

    print(f"\n{'Metric':30s} {'Production IMEX':>16s} {'Crank-Nicolson':>16s} {'Rel. diff (%)':>14s}")
    print("-" * 80)
    for label, key in [("Conduction velocity (m/s)", "cv"),
                       ("AP excursion at 4 mm (mV)", "excursion_mV")]:
        rel = 100.0 * abs(p[key] - r[key]) / abs(p[key])
        print(f"{label:30s} {p[key]:16.3f} {r[key]:16.3f} {rel:14.2f}")
