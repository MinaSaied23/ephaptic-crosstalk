"""
Open-loop drive of an isolated C-fiber cable by a prescribed extracellular potential
u_e(z, t) (scaled by `alpha`), or by an intracellular current pulse, used to measure how far
a recorded ephaptic drive is from the C-fiber's excitation threshold.

The recorded u_e comes from the coupled simulation and therefore already contains the
C-fiber's own contribution to the compartment current.  Replaying it at alpha = 1
reproduces the coupled C-fiber response; that checks the open-loop C-fiber calculation for
the recorded waveform, not the effect of the C-fiber on u_e.  The latter is measured
separately by recomputing u_e with the C-fiber left out of the compartment equation
(CleftParams(c_fiber_loads_compartment=False), experiment E07).

Every run is classified with the same propagation criterion as the coupled simulations
(ephaptic.metrics.c_spike_info: an overshoot of 0 mV spanning at least 3 mm whose front moves
outward at 0.05-5 m/s over the outermost 1 mm on either side), with the same interpolated
crossing times, and runs continue until the overshoot has spread over 7 mm, until the fiber
is back at rest after the drive, or until the end of the run.
"""
from __future__ import annotations

import math
import numpy as np

from .membranes import make_c_membrane
from .metrics import c_spike_info
from .model import BandMatrix, laplacian_stencil, lap, c_fiber_equilibria

#: an overshoot spread over this length is unambiguous; the coupled runs stop there too
STOP_SPAN = 7.0e-3


def run_c_driven(cp, ue_t, dt, dz, alpha=1.0, bias=0.0, T=None, I_point=None, z_point=None,
                 I_uniform=None, region=None, dur=None, stop_on_spike=True, ionic="explicit",
                 quiet_after=4.0e-3, quiet_tol=0.25e-3, record_stride=0):
    """Integrate the C-fiber with  Cm dv/dt = a L(v + alpha ue) - I_ion + bias + I_inj.

    ue_t:      array (nsteps_ue, N) of u_e at t = (s+1) dt, or None
    I_point:   point current (A) injected at z_point for `dur` seconds (strength-duration)
    I_uniform: current density (A/m^2) applied over `region` (bool mask) for `dur` seconds
    stop_on_spike: stop once the overshoot has spread over 7 mm (as in the coupled runs)
    quiet_after, quiet_tol: stop once the whole fiber is back within quiet_tol of rest, no
               earlier than quiet_after and 2 ms after the drive ends
    record_stride: if > 0, store v(z, t) every record_stride steps (key "v", times "t")

    Returns dict(spike, c_span_mm, c_cv, c_init_z_mm, c_init_t_ms, c_overshoot, v_max, v_rest,
    t_cross, z, status, t_end[, t, v]).  `spike` is the propagation criterion of the
    coupled simulations (metrics.c_spike_info).
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
    drive_end = max(ue_t.shape[0] * dt if ue_t is not None else 0.0, dur or 0.0)
    t_quiet = max(quiet_after, drive_end + 2e-3)
    rec_t, rec_v = [], []
    prev = v.copy()
    status, t_end = "completed", nsteps * dt
    for s in range(nsteps):
        t = s * dt
        tn = t + dt
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
        # first upward crossing of 0 mV, interpolated within the step (as in CoupledModel.run)
        up = np.isnan(t_cross) & (v >= 0.0) & (prev < 0.0)
        if up.any():
            t_cross[up] = t + (0.0 - prev[up]) / (v[up] - prev[up]) * dt
        prev = v
        if record_stride and s % record_stride == 0:
            rec_t.append(tn)
            rec_v.append(v.copy())
        if not np.all(np.isfinite(v)):
            status, t_end = "diverged", tn
            break
        crossed = ~np.isnan(t_cross)
        if stop_on_spike and crossed.any() and z[crossed].max() - z[crossed].min() >= STOP_SPAN:
            status, t_end = "spike", tn
            break
        # Back at rest after the drive: nothing further can happen.  Unlike the coupled runs,
        # this also ends runs whose overshoots did not propagate (their crossing times, and so
        # their classification, are already fixed), which shortens the threshold searches.
        if tn >= t_quiet and np.abs(v - v_rest).max() < quiet_tol:
            status, t_end = "quiescent", tn
            break
    info = c_spike_info(dict(z=z, t_cross_c=t_cross))
    out = dict(spike=info["c_spike"], v_max=v_max, v_rest=v_rest, t_cross=t_cross, z=z,
               status=status, t_end=t_end, **{k: info[k] for k in
                                               ("c_overshoot", "c_span_mm", "c_cv", "c_init_z_mm", "c_init_t_ms")})
    if record_stride:
        out["t"] = np.array(rec_t)
        out["v"] = np.array(rec_v)
    return out


def scan_threshold(fn, x0, factor=1.2, x_max=1e6, rtol=5e-3, n_above=3):
    """Smallest x >= x0 with fn(x) True, found without assuming monotonicity outside the final
    bracket.

    fn is evaluated on the geometric grid x0, x0*factor, x0*factor^2, ... up to the first x
    that fires (or x_max); the threshold is then bisected (to rtol) between that point and the
    last grid point that did not fire, so the search interval is the first one on the grid in
    which firing appears.  `n_above` further grid points above the threshold are also
    evaluated, to show that firing persists.

    Returns dict(threshold, lo, hi, n_evals, fires_at_x0, scan, above, monotone), where
    `scan` lists (x, fired) on the grid up to the first firing point, `above` the checks above
    it, and `monotone` is True when no grid point below the bracket fired and every point
    above it fired.  threshold is nan if nothing fired up to x_max (x0 itself is returned when
    fn(x0) already fires).
    """
    scan, n = [], 0
    x, prev = x0, None
    while x <= x_max * (1 + 1e-12):
        f = bool(fn(x)); n += 1
        scan.append((x, f))
        if f:
            break
        prev = x
        x *= factor
    res = dict(threshold=float("nan"), lo=prev, hi=None, n_evals=n, fires_at_x0=scan[0][1],
               scan=scan, above=[], monotone=True)
    if not scan[-1][1]:
        return res
    hi = scan[-1][0]
    if prev is None:                      # fires at the lower limit itself
        res.update(threshold=hi, hi=hi)
    else:
        lo = prev
        while hi - lo > rtol * hi:
            mid = 0.5 * (lo + hi)
            n += 1
            if fn(mid):
                hi = mid
            else:
                lo = mid
        res.update(threshold=hi, lo=lo, hi=hi)
    above = []
    xa = scan[-1][0]
    for _ in range(n_above):
        xa *= factor
        if xa > x_max * (1 + 1e-12):
            break
        above.append((xa, bool(fn(xa)))); n += 1
    res.update(n_evals=n, above=above,
               monotone=all(f for _, f in above) and not any(f for _, f in scan[:-1]))
    return res
