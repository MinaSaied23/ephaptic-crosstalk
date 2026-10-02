"""E02 - Numerical verification.

(a) Time-step and grid refinement of the coupled endpoints (production configuration:
    focal lesion, 2x-threshold stimulus) for both C-fiber models and n = 1, 10, 25, 50,
    with the explicit-ionic and conductance-implicit variants of the monolithic scheme.
(b) Current balance: the physical Kirchhoff residual of the extracellular compartment,
    evaluated from the updated potentials and membrane currents, for the monolithic scheme.
(c) The lagged scheme vs the monolithic scheme in the extended-compartment
    geometry and parameters (100 nA stimulus, HH E_Na = +35.64 mV), as a function of dt.

Outputs: e02_refinement.csv, e02_kcl.csv, e02_lagged_vs_monolithic.csv
"""
import math
import numpy as np

import common
from ephaptic import CoupledModel, Protocol, CleftParams, HHParams, NavCParams
from ephaptic.model import run_lagged, lap
from ephaptic.metrics import summarize

MODELS = {"HH": HHParams(), "NavC": NavCParams()}


def refine_job(a):
    kind, n, dt, dz, ionic = a
    pr = Protocol(n_abeta=n, dt=dt, dz=dz, T=8e-3, ionic=ionic)
    s = summarize(CoupledModel(MODELS[kind], pr).run())
    return dict(model=kind, n_abeta=n, dt_us=dt * 1e6, dz_um=dz * 1e6, ionic=ionic,
                dv_lesion_mV=s["dv_lesion_mV"], dv_mid_mV=s["dv_mid_mV"],
                v2_peak_lesion_mV=s["v2_peak_lesion_mV"], ab_conducts=s["ab_conducts"],
                ab_cv_lesion=s["ab_cv_lesion"], ue_min_mV=s["ue_min_mV"], c_spike=s["c_spike"])


def kcl_job(a):
    """Max over space-time of |(1/r_e) L ue - G_e ue + sum_k n_k i_m,k| inside the compartment,
    with i_m,k = pi d_k (Cm dv/dt + I_ion - I_stim) computed from the updated state."""
    kind, n, dt = a
    pr = Protocol(n_abeta=n, dt=dt, T=1.5e-3, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(MODELS[kind], pr)
    r = m.run(record=["v1", "v2", "ue"], record_stride=1)
    v1, v2, ue = r["v1"], r["v2"], r["ue"]
    cl = m.geo.cleft
    worst, src_peak = 0.0, 0.0
    g1 = m.mem1.init_gates(r["v1_rest"][0]); g2 = m.mem2.init_gates(r["v2_rest"])
    v1p, v2p = r["v1_rest"][0], r["v2_rest"]
    for s in range(v1.shape[0]):
        g1 = m.mem1.step_gates(v1p, g1, dt); g2 = m.mem2.step_gates(v2p, g2, dt)
        G1, J1 = m.mem1.conductance(v1p, g1); G2, J2 = m.mem2.conductance(v2p, g2)
        # membrane current = capacitive + ionic (the electrode current enters the core at z = 0,
        # outside the compartment, and leaves through the membrane as part of these terms)
        im1 = math.pi * m.ab.d_axon * (m.mem1.Cm * (v1[s] - v1p) / dt + (G1 * v1p - J1))
        im2 = math.pi * m.c_cable.d * (m.mem2.Cm * (v2[s] - v2p) / dt + (G2 * v2p - J2))
        R = lap(ue[s], m.dz) / m.geo.r_e - m.geo.G_e * ue[s] + pr.n_abeta * im1 + im2
        worst = max(worst, np.abs(R[cl]).max())
        src_peak = max(src_peak, np.abs(pr.n_abeta * im1[cl]).max())
        v1p, v2p = v1[s], v2[s]
    return dict(model=kind, n_abeta=n, dt_us=dt * 1e6, max_abs_R_phys_A_per_m=worst,
                peak_source_A_per_m=src_peak, relative=worst / src_peak)


def lagged_job(a):
    scheme, n, dt = a
    hh = HHParams(ENa=35.64e-3)
    cl = CleftParams(config="full", stim_current_returns_via_cleft=False)
    pr = Protocol(n_abeta=n, dt=dt, dz=10e-6, T=1.5e-3, stim_amp=100e-9, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(hh, pr, cl)
    r = run_lagged(m) if scheme == "lagged" else m.run()
    z = r["z"]
    w = (z >= 3e-3 - 1e-9) & (z <= 8e-3 + 1e-9)
    return dict(scheme=scheme, n_abeta=n, dt_us=dt * 1e6,
                dv_downstream_mV=((r["v2_max"] - r["v2_rest"])[w]).max() * 1e3)


if __name__ == "__main__":
    jobs = []
    for kind in MODELS:
        for n in (1, 10, 25, 50):
            for dt in (2e-6, 1e-6, 0.5e-6, 0.25e-6, 0.125e-6):
                jobs.append((kind, n, dt, 5e-6, "explicit"))
            for dt in (1e-6, 0.25e-6):
                jobs.append((kind, n, dt, 5e-6, "implicit"))
            for dz in (20e-6, 10e-6, 2.5e-6, 1.25e-6):
                jobs.append((kind, n, 1e-6, dz, "explicit"))
    common.write_csv("e02_refinement.csv", common.pmap(refine_job, jobs))
    kjobs = [(k, n, dt) for k in MODELS for n in (1, 25) for dt in (1e-6, 0.25e-6)]
    common.write_csv("e02_kcl.csv", common.pmap(kcl_job, kjobs))
    ljobs = [(s, n, dt) for s in ("lagged", "monolithic") for n in (1, 10, 25, 50)
             for dt in (5e-6, 2.5e-6, 1e-6, 0.5e-6, 0.25e-6, 0.125e-6)]
    common.write_csv("e02_lagged_vs_monolithic.csv", common.pmap(lagged_job, ljobs))
