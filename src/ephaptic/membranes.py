"""
Membrane objects used by the cable solver.

Each membrane exposes
    init_gates(v)               gates at steady state for potential v
    step_gates(v, gates, dt)    Rush-Larsen (exponential) gate update at fixed v
    conductance(v, gates)       (G, J) with I_ion = G * v - J  (G in S/m^2, J in A/m^2)
so that the solver can treat I_ion explicitly (I = G v - J at the old v) or
conductance-implicitly (G v^{n+1} - J).
"""
from __future__ import annotations

import numpy as np

from . import kinetics as K
from .params import AbetaParams, HHParams, NavCParams


def _rl(x, xinf, tau, dt):
    return xinf + (x - xinf) * np.exp(-dt / tau)


class AbetaMembrane:
    """CRRSS nodes (homogenized into the containing compartment) + passive myelin."""

    def __init__(self, p: AbetaParams, z: np.ndarray, dz: float):
        self.p = p
        N = z.size
        node_idx = []
        n_nodes = int(round((z[-1] + dz) / p.internode))
        for k in range(n_nodes):
            i = int(round(k * p.internode / dz))
            if i < N:
                node_idx.append(i)
        self.node_idx = np.array(node_idx, dtype=int)
        self.node_mask = np.zeros(N, dtype=bool)
        self.node_mask[self.node_idx] = True
        f = p.l_node / dz
        if f > 1.0 + 1e-12:
            raise ValueError("dz must be >= l_node")
        self.f_node = min(1.0, f)
        self.Cm = np.full(N, p.Cm_internode)
        self.Cm[self.node_idx] = self.f_node * p.Cm_node + (1 - self.f_node) * p.Cm_internode
        self.gL = np.full(N, p.gL_internode)
        self.gL[self.node_idx] = self.f_node * p.gL_node + (1 - self.f_node) * p.gL_internode
        self.gNa_node = self.f_node * p.gNa
        self.N = N

    # gates: array (2, ..., n_nodes): m, h at node compartments
    def init_gates(self, v):
        vn = v[..., self.node_idx]
        minf, _, hinf, _ = K.crrss_inf_tau(vn, self.p.phi)
        return np.stack([minf, hinf])

    def step_gates(self, v, g, dt):
        vn = v[..., self.node_idx]
        minf, tm, hinf, th = K.crrss_inf_tau(vn, self.p.phi)
        return np.stack([_rl(g[0], minf, tm, dt), _rl(g[1], hinf, th, dt)])

    def conductance(self, v, g):
        G = np.broadcast_to(self.gL, v.shape).copy()
        J = G * self.p.EL
        gna = self.gNa_node * g[0] ** 2 * g[1]
        G[..., self.node_idx] += gna
        J[..., self.node_idx] += gna * self.p.ENa
        return G, J

    def steady_conductance(self, v):
        return self.conductance(v, self.init_gates(v))


class HHMembrane:
    def __init__(self, p: HHParams, N: int):
        self.p = p
        self.N = N
        self.Cm = np.full(N, p.cable.Cm)

    def init_gates(self, v):
        minf, _, hinf, _, ninf, _ = K.hh_inf_tau(v, self.p.phi, self.p.gating_shift)
        return np.stack([minf, hinf, ninf])

    def step_gates(self, v, g, dt):
        minf, tm, hinf, th, ninf, tn = K.hh_inf_tau(v, self.p.phi, self.p.gating_shift)
        return np.stack([_rl(g[0], minf, tm, dt), _rl(g[1], hinf, th, dt), _rl(g[2], ninf, tn, dt)])

    def conductance(self, v, g):
        p = self.p
        gna = p.gNa * g[0] ** 3 * g[1]
        gk = p.gK * g[2] ** 4
        G = gna + gk + p.gL
        J = gna * p.ENa + gk * p.EK + p.gL * p.EL
        return G, J

    def steady_conductance(self, v):
        return self.conductance(v, self.init_gates(v))


class NavCMembrane:
    def __init__(self, p: NavCParams, N: int):
        self.p = p
        self.N = N
        self.Cm = np.full(N, p.cable.Cm)

    def init_gates(self, v):
        m8, h8, m9 = K.navc_inf(v, self.p)
        ninf, _ = K.navc_n_inf_tau(v, self.p)
        return np.stack([m8, h8, m9, ninf])

    def step_gates(self, v, g, dt):
        p = self.p
        m8, h8, m9 = K.navc_inf(v, p)
        ninf, tn = K.navc_n_inf_tau(v, p)
        return np.stack([_rl(g[0], m8, p.tau_m8, dt), _rl(g[1], h8, p.tau_h8, dt),
                         _rl(g[2], m9, p.tau_m9, dt), _rl(g[3], ninf, tn, dt)])

    def conductance(self, v, g):
        p = self.p
        g8 = p.g18 * g[0] ** 3 * g[1]
        g9 = p.g19 * g[2]
        gk = p.gK * g[3] ** 4
        G = g8 + g9 + gk + p.gL
        J = (g8 + g9) * p.ENa + gk * p.EK + p.gL * p.EL
        return G, J

    def steady_conductance(self, v):
        return self.conductance(v, self.init_gates(v))


def make_c_membrane(p, N):
    if isinstance(p, HHParams):
        return HHMembrane(p, N)
    if isinstance(p, NavCParams):
        return NavCMembrane(p, N)
    raise TypeError(f"unknown C-fiber parameter set {type(p)}")


def resting_potential(mem_factory, v0, tol=1e-12):
    """Space-clamped resting potential (root of I_ion with gates at steady state)."""
    from scipy.optimize import brentq
    mem = mem_factory(1)

    def f(v):
        G, J = mem.steady_conductance(np.array([v]))
        return float(G[0] * v - J[0])
    lo, hi = v0 - 0.02, v0 + 0.02
    return brentq(f, lo, hi, xtol=tol)
