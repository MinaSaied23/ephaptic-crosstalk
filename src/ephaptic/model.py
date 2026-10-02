"""
Monolithic, implicit solver for the coupled Abeta / C-fiber / extracellular system.

Semi-discrete equations (per unit inner membrane area for the fibers, per unit
length for the extracellular compartment), with u_k = v_k + u_e:

    Cm1 dv1_j/dt = a1 L(v1_j + u_e) - I_ion1(v1_j) + I_stim,j      j = 1..K Abeta groups
    Cm2 dv2/dt   = a2 L(v2 + u_e)   - I_ion2(v2)   + I_bias
    0 = (1/r_e) L u_e - G_e u_e + sum_j (n/K) g1 L(v1_j + u_e) + g2 L(v2 + u_e) + i_stim/len
                                               (inside the shared compartment)
    u_e = 0                                    (grounded bulk, outside the compartment)

a_k = d_k / (4 rho_i), g_k = pi d_k a_k = 1 / r_i,k, G_e = kappa / r_e, and L is the
second-difference operator with sealed (mirror) ends.  All three fields are advanced
together by backward Euler, so the extracellular potential is never lagged.  Gates
use a Rush-Larsen step at the old potential; ionic currents are either explicit at
the updated gates ("explicit", matrix factorized once) or conductance-implicit
("implicit", matrix refactorized every step).  Both are first order in dt.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from scipy.linalg import lapack

from .params import AbetaParams, CleftParams, Protocol, HHParams, NavCParams, sleeve_area, ABETA_THRESHOLD
from .membranes import AbetaMembrane, make_c_membrane


# ----------------------------------------------------------------------------
# Banded storage helpers (LAPACK general band format)
# ----------------------------------------------------------------------------
class BandMatrix:
    def __init__(self, n, kl, ku):
        self.n, self.kl, self.ku = n, kl, ku
        self.ab = np.zeros((2 * kl + ku + 1, n))

    def add(self, rows, cols, vals):
        rows = np.asarray(rows); cols = np.asarray(cols)
        vals = np.broadcast_to(vals, rows.shape)
        np.add.at(self.ab, (self.kl + self.ku + rows - cols, cols), vals)

    def factor(self):
        lu, piv, info = lapack.dgbtrf(self.ab.copy(), self.kl, self.ku)
        if info != 0:
            raise np.linalg.LinAlgError(f"dgbtrf info={info}")
        return lu, piv

    def solve(self, lu_piv, b):
        lu, piv = lu_piv
        x, info = lapack.dgbtrs(lu, self.kl, self.ku, b, piv)
        if info != 0:
            raise np.linalg.LinAlgError(f"dgbtrs info={info}")
        return x

    def matvec(self, x):
        n, kl, ku = self.n, self.kl, self.ku
        y = np.zeros(n)
        for off in range(-kl, ku + 1):          # off = col - row
            row = kl + ku - off
            if off >= 0:
                y[: n - off] += self.ab[row, off:] * x[off:]
            else:
                y[-off:] += self.ab[row, : n + off] * x[: n + off]
        return y


def laplacian_stencil(N):
    """(rows, cols, weights) of the mirror-Neumann second difference (times dz^2)."""
    rows, cols, w = [], [], []
    for i in range(N):
        if i == 0:
            rows += [0, 0]; cols += [0, 1]; w += [-2.0, 2.0]
        elif i == N - 1:
            rows += [i, i]; cols += [i, i - 1]; w += [-2.0, 2.0]
        else:
            rows += [i, i, i]; cols += [i - 1, i, i + 1]; w += [1.0, -2.0, 1.0]
    return np.array(rows), np.array(cols), np.array(w)


def lap(x, dz):
    d = np.empty_like(x)
    d[..., 1:-1] = x[..., 2:] - 2 * x[..., 1:-1] + x[..., :-2]
    d[..., 0] = 2 * (x[..., 1] - x[..., 0])
    d[..., -1] = 2 * (x[..., -2] - x[..., -1])
    return d / dz ** 2


# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------
@dataclass
class Geometry:
    N: int
    dz: float
    z: np.ndarray
    cleft: np.ndarray          # bool mask of compartments inside the shared compartment
    r_e: float
    G_e: float
    A_e: float


def build_geometry(proto: Protocol, cleft: CleftParams, ab: AbetaParams, c_d: float) -> Geometry:
    N = int(round(proto.L / proto.dz))
    z = np.arange(N) * proto.dz
    if cleft.area_model == "fixed":
        A_e = cleft.A_e
    elif cleft.area_model == "per_fiber":
        A_e = proto.n_abeta * sleeve_area(ab.D_outer, cleft.w_sleeve) + sleeve_area(c_d, cleft.w_sleeve)
    else:
        raise ValueError(cleft.area_model)
    r_e = cleft.rho_e / A_e
    G_e = cleft.kappa / r_e
    if cleft.config == "full":
        mask = np.ones(N, dtype=bool)
    elif cleft.config == "lesion":
        mask = (z > cleft.lesion_start + 1e-12) & (z < cleft.lesion_end - 1e-12)
    else:
        raise ValueError(cleft.config)
    return Geometry(N, proto.dz, z, mask, r_e, G_e, A_e)


class CoupledModel:
    """Assembles and integrates the coupled system for one parameter configuration."""

    def __init__(self, c_params, proto: Protocol = Protocol(), cleft: CleftParams = CleftParams(),
                 ab: AbetaParams = AbetaParams()):
        self.cp, self.proto, self.clp, self.ab = c_params, proto, cleft, ab
        self.c_cable = c_params.cable
        self.geo = build_geometry(proto, cleft, ab, self.c_cable.d)
        N, dz = self.geo.N, self.geo.dz
        self.N, self.dz = N, dz
        self.K = proto.jitter_phases if proto.jitter > 0 else 1
        self.nvar = self.K + 2
        self.mem1 = AbetaMembrane(ab, self.geo.z, dz)
        self.mem2 = make_c_membrane(c_params, N)
        self.a1 = ab.d_axon / (4.0 * ab.rho_i)
        self.a2 = self.c_cable.d / (4.0 * self.c_cable.rho_i)
        self.g1 = math.pi * ab.d_axon * self.a1
        self.g2 = math.pi * self.c_cable.d * self.a2
        self.nk = proto.n_abeta / self.K
        self.Sigma = 1.0 / self.geo.r_e + proto.n_abeta * self.g1 + self.g2
        if proto.jitter > 0:
            self.offsets = np.linspace(0.0, proto.jitter, self.K)
        else:
            self.offsets = np.zeros(1)
        self._lap = laplacian_stencil(N)

    # index helpers -----------------------------------------------------
    def idx(self, var, i):
        return np.asarray(i) * self.nvar + var

    @property
    def iC(self):
        return self.K

    @property
    def iE(self):
        return self.K + 1

    def assemble(self, dt, G1=None, G2=None):
        """Band matrix of the backward-Euler step.  G1 (K,N) / G2 (N,) are ionic
        conductances added to the diagonal in the conductance-implicit scheme."""
        N, dz, K = self.N, self.dz, self.K
        nv = self.nvar
        n = N * nv
        kl = ku = 2 * nv - 1
        A = BandMatrix(n, kl, ku)
        lr, lc, lw = self._lap
        lw = lw / dz ** 2
        allN = np.arange(N)
        cleft = self.geo.cleft
        # Abeta groups
        for j in range(K):
            diag = self.mem1.Cm / dt + (0.0 if G1 is None else G1[j])
            A.add(self.idx(j, allN), self.idx(j, allN), diag)
            A.add(self.idx(j, lr), self.idx(j, lc), -self.a1 * lw)
            A.add(self.idx(j, lr), self.idx(self.iE, lc), -self.a1 * lw)
        # C-fiber
        diag = self.mem2.Cm / dt + (0.0 if G2 is None else G2)
        A.add(self.idx(self.iC, allN), self.idx(self.iC, allN), diag)
        A.add(self.idx(self.iC, lr), self.idx(self.iC, lc), -self.a2 * lw)
        A.add(self.idx(self.iC, lr), self.idx(self.iE, lc), -self.a2 * lw)
        # extracellular rows (scaled by 1/Sigma)
        inside = cleft[lr]
        r, c, w = lr[inside], lc[inside], lw[inside]
        S = self.Sigma
        A.add(self.idx(self.iE, r), self.idx(self.iE, c), w)          # Sigma L ue / Sigma
        A.add(self.idx(self.iE, allN[cleft]), self.idx(self.iE, allN[cleft]), -self.geo.G_e / S)
        for j in range(K):
            A.add(self.idx(self.iE, r), self.idx(j, c), self.nk * self.g1 * w / S)
        A.add(self.idx(self.iE, r), self.idx(self.iC, c), self.g2 * w / S)
        out = allN[~cleft]
        A.add(self.idx(self.iE, out), self.idx(self.iE, out), 1.0)
        return A

    # ------------------------------------------------------------------
    def stim_density(self):
        """Abeta stimulus current density (A/m^2) for the injected current at node 0."""
        amp = self.proto.stim_amp
        if amp is None:
            amp = self.proto.stim_factor * ABETA_THRESHOLD
        self.stim_amp_used = amp
        return amp / (math.pi * self.ab.d_axon * self.dz)

    def resting_state(self, tol=1e-12, max_iter=50):
        """Steady state of the coupled system without stimulus.

        The C-fiber is seeded at its space-clamped quiescent equilibrium (most
        hyperpolarized root of I_ion,ss(v) = bias, see c_fiber_equilibria) and the
        full system is then solved by Newton's method with steady-state gates."""
        N = self.N
        roots = c_fiber_equilibria(self.cp, self.proto.c_bias)
        v1 = np.full((self.K, N), self.ab.EL)
        v2 = np.full(N, roots[0]["v"])
        ue = np.zeros(N)
        big = 1.0e12   # pseudo-step: makes Cm/dt negligible, so the system is the exact
                       # steady-state Jacobian (D - a L) of the coupled problem
        h = 1e-7
        for it in range(max_iter):
            G1, J1 = self.mem1.steady_conductance(v1)
            G2, J2 = self.mem2.steady_conductance(v2)
            I1 = G1 * v1 - J1
            I2 = G2 * v2 - J2
            Gp1, Jp1 = self.mem1.steady_conductance(v1 + h)
            Gp2, Jp2 = self.mem2.steady_conductance(v2 + h)
            D1 = ((Gp1 * (v1 + h) - Jp1) - I1) / h          # dI_ss/dv
            D2 = ((Gp2 * (v2 + h) - Jp2) - I2) / h
            A = self.assemble(big, D1, D2)
            # Newton: D (v_new - v) + I(v) - bias - a L(...) = 0  ->  D v_new = D v - I + bias
            rhs = self._rhs(v1, v2, big, D1 * v1 - I1, D2 * v2 - I2, Istim=None,
                            bias=self.proto.c_bias, implicit=True)
            x = A.solve(A.factor(), rhs)
            nv1, nv2, nue = self._unpack(x)
            d = max(np.abs(nv1 - v1).max(), np.abs(nv2 - v2).max())
            v1, v2, ue = nv1, nv2, nue
            if d < tol:
                break
        self.rest_iterations = it + 1
        self.c_equilibria = roots
        return v1, v2, ue

    def _c_rest_guess(self):
        return -65.0e-3 if isinstance(self.cp, HHParams) else -66.8e-3

    def _unpack(self, x):
        X = x.reshape(self.N, self.nvar)
        return X[:, : self.K].T.copy(), X[:, self.iC].copy(), X[:, self.iE].copy()

    def _rhs(self, v1, v2, dt, J1, J2, Istim, bias, implicit, I1=None, I2=None, c_stim=None):
        N, nv = self.N, self.nvar
        R = np.zeros((N, nv))
        if implicit:
            R[:, : self.K] = (self.mem1.Cm / dt * v1 + J1).T
            R[:, self.iC] = self.mem2.Cm / dt * v2 + J2 + bias
        else:
            R[:, : self.K] = (self.mem1.Cm / dt * v1 - I1).T
            R[:, self.iC] = self.mem2.Cm / dt * v2 - I2 + bias
        if Istim is not None:
            R[:, : self.K] += Istim.T
            if self.clp.stim_current_returns_via_cleft:
                # injected current leaves through the membrane into the compartment
                src = (self.nk * Istim.sum(axis=0) * math.pi * self.ab.d_axon) / self.Sigma
                R[:, self.iE] -= np.where(self.geo.cleft, src, 0.0)
        if c_stim is not None:
            R[:, self.iC] += c_stim
            if self.clp.stim_current_returns_via_cleft:
                R[:, self.iE] -= np.where(self.geo.cleft, c_stim * math.pi * self.c_cable.d / self.Sigma, 0.0)
        R[~self.geo.cleft, self.iE] = 0.0
        return R.ravel()

    # ------------------------------------------------------------------
    def run(self, record=None, record_stride=1, state=None):
        """Integrate one protocol.  Returns a dict of summary metrics and recordings.

        record: iterable of names from {"v1", "v2", "ue"} to store full fields every
        record_stride steps.
        """
        P = self.proto
        dt, N, K = P.dt, self.N, self.K
        record = set(record or [])
        if state is None:
            v1, v2, ue = self.resting_state()
        else:
            v1, v2, ue = (s.copy() for s in state)
        v1_rest, v2_rest, ue_rest = v1.copy(), v2.copy(), ue.copy()
        g1 = self.mem1.init_gates(v1)
        g2 = self.mem2.init_gates(v2)
        I_dens = self.stim_density() if (P.stim_amp is None or P.stim_amp > 0) else 0.0
        if P.ionic not in ("explicit", "implicit", "implicit_c"):
            raise ValueError(P.ionic)
        impl1 = P.ionic == "implicit"                  # Abeta ionic current conductance-implicit
        impl2 = P.ionic in ("implicit", "implicit_c")  # C-fiber ionic current conductance-implicit
        implicit = impl1 or impl2
        A = self.assemble(dt)
        if implicit:
            # base matrix without ionic conductances; only its main diagonal changes per step
            allN = np.arange(N)
            d1_idx = np.concatenate([self.idx(j, allN) for j in range(K)])
            dC_idx = self.idx(self.iC, allN)
            drow = A.kl + A.ku
            ab_base = A.ab.copy()
        else:
            LU = A.factor()

        node_idx = self.mem1.node_idx
        z = self.geo.z
        nsteps = int(round(P.T / dt))
        thr_c = 0.0
        t_cross_c = np.full(N, np.nan)          # first crossing of 0 mV by the C-fiber
        t_cross_ab = np.full((K, node_idx.size), np.nan)   # Abeta nodes crossing -40 mV (interpolated)
        v2_max = v2.copy(); v2_min = v2.copy()
        ue_max = ue.copy(); ue_min = ue.copy()
        v1_max = v1.copy()
        rec = {k: [] for k in record}
        rec_t = []
        c_stim_dens = None
        if P.c_stim_amp:
            ic = int(round(P.c_stim_z / self.dz))
            c_stim_dens = np.zeros(N)
            c_stim_dens[ic] = P.c_stim_amp / (math.pi * self.c_cable.d * self.dz)
        t_end = nsteps * dt
        status = "completed"
        prev_v1n = v1[:, node_idx].copy()
        prev_v2 = v2.copy()
        last_stim_end = max(P.pulse_times) + self.offsets.max() + P.stim_dur
        for s in range(nsteps):
            t = s * dt
            tn = t + dt
            # stimulus during [t, t+dt): pulse active if onset <= t < onset + dur
            Istim = None
            if I_dens:
                Istim = np.zeros((K, N))
                for j in range(K):
                    for p0 in P.pulse_times:
                        on = p0 + self.offsets[j]
                        if on - 1e-12 <= t < on + P.stim_dur - 1e-12:
                            Istim[j, 0] = I_dens
                if not Istim.any():
                    Istim = None
            cs = c_stim_dens if (c_stim_dens is not None and t < P.c_stim_dur - 1e-12) else None
            g1 = self.mem1.step_gates(v1, g1, dt)
            g2 = self.mem2.step_gates(v2, g2, dt)
            G1, J1 = self.mem1.conductance(v1, g1)
            G2, J2 = self.mem2.conductance(v2, g2)
            if implicit:
                A.ab = ab_base.copy()
                if impl1:
                    A.ab[drow, d1_idx] += G1.ravel()
                if impl2:
                    A.ab[drow, dC_idx] += G2
                # implicit parts enter the right-hand side as +J, explicit parts as -(G v - J)
                R1 = J1 if impl1 else -(G1 * v1 - J1)
                R2 = J2 if impl2 else -(G2 * v2 - J2)
                rhs = self._rhs(v1, v2, dt, R1, R2, Istim, P.c_bias, True, c_stim=cs)
                x = A.solve(A.factor(), rhs)
            else:
                I1 = G1 * v1 - J1
                I2 = G2 * v2 - J2
                rhs = self._rhs(v1, v2, dt, None, None, Istim, P.c_bias, False, I1, I2, c_stim=cs)
                x = A.solve(LU, rhs)
            v1, v2, ue = self._unpack(x)
            # bookkeeping
            v1n = v1[:, node_idx]
            up = np.isnan(t_cross_ab) & (v1n >= -0.040) & (prev_v1n < -0.040)
            if up.any():
                frac = (-0.040 - prev_v1n[up]) / (v1n[up] - prev_v1n[up])
                t_cross_ab[up] = t + frac * dt
            prev_v1n = v1n.copy()
            upc = np.isnan(t_cross_c) & (v2 >= thr_c) & (prev_v2 < thr_c)
            if upc.any():
                frac = (thr_c - prev_v2[upc]) / (v2[upc] - prev_v2[upc])
                t_cross_c[upc] = t + frac * dt
            prev_v2 = v2.copy()
            np.maximum(v2_max, v2, out=v2_max); np.minimum(v2_min, v2, out=v2_min)
            np.maximum(ue_max, ue, out=ue_max); np.minimum(ue_min, ue, out=ue_min)
            np.maximum(v1_max, v1, out=v1_max)
            if record and (s % record_stride == 0):
                rec_t.append(tn)
                if "v1" in record:
                    rec["v1"].append(v1[K // 2].copy())
                if "v2" in record:
                    rec["v2"].append(v2.copy())
                if "ue" in record:
                    rec["ue"].append(ue.copy())
            if not np.all(np.isfinite(v2)):
                status = "diverged"; t_end = tn; break
            crossed = ~np.isnan(t_cross_c)
            if P.stop_on_spike and crossed.any():
                # stop only once the overshoot has spread far enough to be unambiguous
                span = z[crossed].max() - z[crossed].min()
                if span >= 7.0e-3:
                    status = "spike"; t_end = tn; break
            if tn >= max(P.quiet_after, last_stim_end + 2e-3) and not crossed.any():
                dev = max(np.abs(v2 - v2_rest).max(), np.abs(v1 - v1_rest).max())
                if dev < P.quiet_tol:
                    status = "quiescent"; t_end = tn; break

        out = dict(
            status=status, t_end=t_end, z=z, cleft=self.geo.cleft,
            v1_rest=v1_rest, v2_rest=v2_rest, ue_rest=ue_rest,
            v2_max=v2_max, v2_min=v2_min, ue_max=ue_max, ue_min=ue_min, v1_max=v1_max,
            t_cross_c=t_cross_c, t_cross_ab=t_cross_ab, node_z=z[node_idx],
            stim_amp=getattr(self, "stim_amp_used", P.stim_amp),
            r_e=self.geo.r_e, A_e=self.geo.A_e, G_e=self.geo.G_e, Sigma=self.Sigma,
            final_state=(v1, v2, ue),
        )
        if record:
            out["t"] = np.array(rec_t)
            for k in record:
                out[k] = np.array(rec[k])
        return out


# ----------------------------------------------------------------------------
# Abeta stimulation threshold (uncoupled fiber, same grid and dt)
# ----------------------------------------------------------------------------
_TH_CACHE = {}


def abeta_threshold(ab: AbetaParams, proto: Protocol, rtol=1e-3):
    """Smallest current (A) at node 0 (pulse proto.stim_dur) that makes the isolated
    Abeta fiber conduct to the last node.  Computed once per (dz, dt, dur)."""
    key = (ab, proto.dz, proto.dt, proto.stim_dur, proto.L)
    if key in _TH_CACHE:
        return _TH_CACHE[key]
    from .params import CleftParams, Protocol as _P, HHParams as _HH
    from dataclasses import replace

    def conducts(I):
        pr = replace(proto, stim_amp=I, n_abeta=1.0, jitter=0.0, T=3e-3, pulse_times=(0.0,),
                     c_bias=0.0, c_stim_amp=0.0, stop_on_spike=False, quiet_after=3e-3)
        m = CoupledModel(_HH(), pr, CleftParams(config="lesion", lesion_start=proto.L, lesion_end=proto.L), ab)
        r = m.run()
        return not np.isnan(r["t_cross_ab"][0, -1])
    lo, hi = 0.0, 1e-9
    while not conducts(hi):
        lo, hi = hi, hi * 2
    while (hi - lo) > rtol * hi:
        mid = 0.5 * (lo + hi)
        if conducts(mid):
            hi = mid
        else:
            lo = mid
    _TH_CACHE[key] = hi
    return hi


# ----------------------------------------------------------------------------
# Space-clamped equilibria of the C-fiber membrane
# ----------------------------------------------------------------------------
def c_fiber_equilibria(cp, bias=0.0, vmin=-0.120, vmax=0.060, npts=3601):
    """All equilibria of the space-clamped C-fiber membrane with a uniform bias current
    density (A/m^2), sorted from most hyperpolarized.  Each entry gives v and whether it
    is linearly stable (eigenvalues of the Jacobian of the membrane ODE system)."""
    from scipy.optimize import brentq
    from .membranes import make_c_membrane
    mem = make_c_membrane(cp, 1)

    def f(v):
        G, J = mem.steady_conductance(np.atleast_1d(v))
        return G * np.atleast_1d(v) - J - bias
    vs = np.linspace(vmin, vmax, npts)
    fv = f(vs)
    roots = []
    for i in np.where(np.sign(fv[:-1]) != np.sign(fv[1:]))[0]:
        r = brentq(lambda x: float(f(x)[0]), vs[i], vs[i + 1], xtol=1e-14)
        roots.append(dict(v=r, stable=_membrane_stable(mem, r)))
    if not roots:
        raise RuntimeError("no equilibrium found")
    return roots


def _membrane_stable(mem, v0, eps=1e-7):
    """Linear stability of the space-clamped membrane ODE at equilibrium v0."""
    v0 = np.array([v0])
    g0 = mem.init_gates(v0)[:, 0]
    x0 = np.concatenate([[v0[0]], g0])
    Cm = mem.Cm[0]

    def rhs(x):
        v = np.array([x[0]])
        g = x[1:].reshape(-1, 1)
        G, J = mem.conductance(v, g)
        dv = -(G[0] * v[0] - J[0]) / Cm
        dt = 1e-9
        g_new = mem.step_gates(v, g, dt)[:, 0]
        dg = (g_new - g[:, 0]) / dt
        return np.concatenate([[dv], dg])
    n = x0.size
    Jm = np.zeros((n, n))
    f0 = rhs(x0)
    for k in range(n):
        x = x0.copy(); x[k] += eps
        Jm[:, k] = (rhs(x) - f0) / eps
    return bool(np.all(np.linalg.eigvals(Jm).real < 0))


# ----------------------------------------------------------------------------
# Reproduction of the earlier (lagged) coupling scheme, for documentation only
# ----------------------------------------------------------------------------
def run_lagged(model: CoupledModel):
    """Integrate `model` (K = 1) with the scheme of the earlier version of the study:
    u_e^{n+1} is obtained from v^n alone and its second difference is fed back
    explicitly into backward-Euler cable steps.  Used only to quantify the
    time-step error of that scheme (Supplementary convergence study)."""
    from scipy.linalg import solve_banded
    if model.K != 1:
        raise ValueError("lagged scheme implemented for K = 1 only")
    P, N, dz, dt = model.proto, model.N, model.dz, model.proto.dt
    v1, v2, ue = model.resting_state()
    v1, v2 = v1[0].copy(), v2.copy()
    v2_rest = v2.copy()
    g1 = model.mem1.init_gates(v1)
    g2 = model.mem2.init_gates(v2)

    def cable(a, Cm):
        k = a / dz ** 2
        A = np.zeros((3, N)); A[1] = Cm / dt + 2 * k; A[0, 1:] = -k; A[2, :-1] = -k
        A[0, 1] = -2 * k; A[2, -2] = -2 * k
        return A
    A1, A2 = cable(model.a1, model.mem1.Cm), cable(model.a2, model.mem2.Cm)
    S = model.Sigma
    # extracellular operator: L ue - (G_e/S) ue = -(n g1 L v1 + g2 L v2)/S inside the compartment
    E = BandMatrix(N, 1, 1)
    lr, lc, lw = model._lap
    inside = model.geo.cleft[lr]
    E.add(lr[inside], lc[inside], lw[inside] / dz ** 2)
    cl = np.where(model.geo.cleft)[0]
    E.add(cl, cl, -model.geo.G_e / S)
    out = np.where(~model.geo.cleft)[0]
    E.add(out, out, 1.0)
    ELU = E.factor()
    I_dens = model.stim_density()
    nsteps = int(round(P.T / dt))
    v2_max = v2.copy()
    for s in range(nsteps):
        t = s * dt
        g1 = model.mem1.step_gates(v1, g1, dt)
        g2 = model.mem2.step_gates(v2, g2, dt)
        G1, J1 = model.mem1.conductance(v1, g1)
        G2, J2 = model.mem2.conductance(v2, g2)
        B = -(P.n_abeta * model.g1 * lap(v1, dz) + model.g2 * lap(v2, dz)) / S
        B[~model.geo.cleft] = 0.0
        ue = E.solve(ELU, B)
        d2ue = lap(ue, dz)
        Is = np.zeros(N)
        if any(p0 - 1e-12 <= t < p0 + P.stim_dur - 1e-12 for p0 in P.pulse_times):
            Is[0] = I_dens
        v1 = solve_banded((1, 1), A1, model.mem1.Cm / dt * v1 - (G1 * v1 - J1) + Is + model.a1 * d2ue)
        v2 = solve_banded((1, 1), A2, model.mem2.Cm / dt * v2 - (G2 * v2 - J2) + P.c_bias + model.a2 * d2ue)
        np.maximum(v2_max, v2, out=v2_max)
    return dict(z=model.geo.z, v2_rest=v2_rest, v2_max=v2_max, cleft=model.geo.cleft)
