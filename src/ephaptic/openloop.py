"""
Open-loop drive of an isolated C-fiber cable by a prescribed extracellular potential
u_e(z, t) (scaled by `alpha`), used to measure how far a recorded ephaptic drive is
from the C-fiber's excitation threshold.

Because the C-fiber contributes at most 1.6 % of the axial conductance of the shared
compartment (and far less at larger n), the closed-loop u_e is essentially unaffected by
the C-fiber's own response; alpha = 1 reproduces the closed-loop C-fiber response to
within 0.01 % (measured in E07, and asserted in tests/test_model.py).
"""
from __future__ import annotations

import math
import numpy as np

from .membranes import make_c_membrane
from .model import BandMatrix, laplacian_stencil, lap, c_fiber_equilibria


def run_c_driven(cp, ue_t, dt, dz, alpha=1.0, bias=0.0, T=None, I_point=None, z_point=None,
                 I_uniform=None, region=None, dur=None, stop_on_spike=True, ionic="explicit"):
    """Integrate the C-fiber with  Cm dv/dt = a L(v + alpha ue) - I_ion + bias + I_inj.

    ue_t:      array (nsteps_ue, N) of u_e at t = (s+1) dt, or None
    I_point:   point current (A) injected at z_point for `dur` seconds (strength-duration)
    I_uniform: current density (A/m^2) applied over `region` (bool mask) for `dur` seconds
    Returns dict(spike, v_max, v_rest, t_cross).
    """
    N = ue_t.shape[1] if ue_t is not None else int(round(10e-3 / dz))
    mem = make_c_membrane(cp, N)
    a = cp.cable.d / (4.0 * cp.cable.rho_i)
    v = np.full(N, c_fiber_equilibria(cp, bias)[0]["v"])
    v_rest = v.copy()
    g = mem.init_gates(v)
    A = BandMatrix(N, 1, 1)
    lr, lc, lw = laplacian_stencil(N)
    A.add(np.arange(N), np.arange(N), mem.Cm / dt)
    A.add(lr, lc, -a * lw / dz ** 2)
    LU = A.factor()
    ab_base = A.ab.copy()
    drow = A.kl + A.ku
    nsteps = int(round((T if T is not None else ue_t.shape[0] * dt) / dt))
    z = np.arange(N) * dz
    t_cross = np.full(N, np.nan)
    v_max = v.copy()
    inj = np.zeros(N)
    if I_point is not None:
        inj[int(round(z_point / dz))] = I_point / (math.pi * cp.cable.d * dz)
    if I_uniform is not None:
        inj[region] = I_uniform
    prev = v.copy()
    for s in range(nsteps):
        t = s * dt
        g = mem.step_gates(v, g, dt)
        G, J = mem.conductance(v, g)
        if ionic == "implicit":
            A.ab = ab_base.copy()
            A.ab[drow] += G
            LU = A.factor()
            rhs = mem.Cm / dt * v + J + bias
        else:
            rhs = mem.Cm / dt * v - (G * v - J) + bias
        if dur is not None and t < dur - 1e-12:
            rhs = rhs + inj
        if ue_t is not None and s < ue_t.shape[0]:
            rhs = rhs + a * alpha * lap(ue_t[s], dz)
        v = A.solve(LU, rhs)
        np.maximum(v_max, v, out=v_max)
        up = np.isnan(t_cross) & (v >= 0.0) & (prev < 0.0)
        t_cross[up] = t
        prev = v
        crossed = ~np.isnan(t_cross)
        if crossed.any():
            span = z[crossed].max() - z[crossed].min()
            if stop_on_spike and span >= 3e-3:
                break
        if (ue_t is None or s >= ue_t.shape[0]) and (dur is None or t > dur) and not crossed.any():
            if np.abs(v - v_rest).max() < 0.25e-3 and t > 2e-3:
                break
    crossed = ~np.isnan(t_cross)
    span = (z[crossed].max() - z[crossed].min()) if crossed.any() else 0.0
    return dict(spike=bool(span >= 3e-3), v_max=v_max, v_rest=v_rest, t_cross=t_cross, z=z)


def bisect_threshold(fn, lo, hi, rtol=5e-3, grow=2.0, hi_max=1e6):
    """Smallest x in (lo, hi] with fn(x) True, assuming monotonicity.  Returns (x, n_evals)
    or (nan, n) if no threshold below hi_max."""
    n = 0
    while not fn(hi):
        n += 1
        lo, hi = hi, hi * grow
        if hi > hi_max:
            return float("nan"), n
    while hi - lo > rtol * hi:
        mid = 0.5 * (lo + hi)
        n += 1
        if fn(mid):
            hi = mid
        else:
            lo = mid
    return hi, n
