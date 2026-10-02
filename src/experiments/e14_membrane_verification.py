"""E14 - Direct verification of the Abeta source waveform and of the C-fiber passive properties.

The Abeta action potential is the source of every result in the study, so its gating is checked
directly rather than assumed:

    1. The CRRSS steady states and time constants over the modelled voltage range, so that
       h_inf can be read off directly.
    2. A single action potential followed through repolarization back to rest.
    3. A paired-pulse protocol: a second stimulus at increasing intervals, reporting whether the
       second action potential conducts to the last node and with what peak and velocity.
    4. The C-fiber passive properties under a defined geometry: resting potential, input
       resistance at the injection site, passive time constant, length constant, and the
       rheobase of a 1-ms point injection.

Outputs: e14_abeta_gates.csv, e14_abeta_ap_trace.csv, e14_abeta_paired_pulse.csv,
         e14_cfiber_passive.csv
"""
import numpy as np

import common
from ephaptic import (CoupledModel, Protocol, CleftParams, HHParams, NavCParams, AbetaParams,
                      abeta_threshold)
from ephaptic.kinetics import crrss_inf_tau
from ephaptic.params import ABETA_THRESHOLD

NO_CLEFT = dict(lesion_start=10e-3, lesion_end=10e-3)   # both fibers in grounded bulk
NODE_Z = 5.0e-3                                          # the node the traces are read at


def gates():
    """CRRSS steady states and time constants over the modelled range."""
    rows = []
    for vmV in range(-100, 41, 5):
        mi, tm, hi, th = crrss_inf_tau(np.array([vmV * 1e-3]), AbetaParams().phi)
        rows.append(dict(v_mV=vmV, m_inf=mi[0], tau_m_ms=tm[0] * 1e3,
                         h_inf=hi[0], tau_h_ms=th[0] * 1e3))
    return rows


def ap_trace():
    """One action potential at z = 5 mm, followed to rest."""
    pr = Protocol(stim_amp=2.0 * ABETA_THRESHOLD, T=5e-3, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(HHParams(), pr, CleftParams(**NO_CLEFT))
    r = m.run(record=["v1"], record_stride=5)
    i = int(round(NODE_Z / pr.dz))
    v = r["v1"][:, i]
    rest = r["v1"][0, i]
    return [dict(t_ms=t * 1e3, v_node_mV=x * 1e3, dv_from_rest_mV=(x - rest) * 1e3)
            for t, x in zip(r["t"], v)]


def paired_pulse():
    """Second stimulus at increasing intervals: does the second AP conduct, and how fast."""
    rows = []
    for isi_ms in (0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0):
        isi = isi_ms * 1e-3
        pr = Protocol(stim_amp=2.0 * ABETA_THRESHOLD, pulse_times=(0.0, isi), T=isi + 4e-3,
                      stop_on_spike=False, quiet_after=1.0)
        m = CoupledModel(HHParams(), pr, CleftParams(**NO_CLEFT))
        r = m.run(record=["v1"], record_stride=1)
        t, z = r["t"], r["z"]
        i4, i8 = (int(round(x / pr.dz)) for x in (4e-3, 8e-3))
        out = dict(isi_ms=isi_ms)
        for tag, i in (("z4", i4), ("z8", i8)):
            v = r["v1"][:, i]
            up = np.where((v[1:] >= -0.040) & (v[:-1] < -0.040))[0]       # upward crossings
            out[f"n_aps_{tag}"] = int(up.size)
            out[f"t_ap1_{tag}_ms"] = t[up[0]] * 1e3 if up.size > 0 else np.nan
            out[f"t_ap2_{tag}_ms"] = t[up[1]] * 1e3 if up.size > 1 else np.nan
        # peak of each AP at z = 8 mm, split at the second stimulus
        v8 = r["v1"][:, i8]
        first, second = v8[t < isi], v8[t >= isi]
        out["peak1_mV"] = first.max() * 1e3 if first.size else np.nan
        out["peak2_mV"] = second.max() * 1e3 if second.size else np.nan
        for k, tag in ((1, "ap1"), (2, "ap2")):
            ta, tb = out[f"t_{tag}_z4_ms"], out[f"t_{tag}_z8_ms"]
            out[f"cv{k}_m_s"] = (z[i8] - z[i4]) / ((tb - ta) * 1e-3) if np.isfinite(ta) and np.isfinite(tb) else np.nan
        out["second_conducts"] = bool(out["n_aps_z8"] >= 2)
        rows.append(out)
    return rows


def cfiber_passive():
    """Resting potential, input resistance, time and length constants, 1-ms rheobase."""
    from ephaptic.model import c_fiber_equilibria
    from ephaptic.membranes import make_c_membrane
    rows = []
    for C in (HHParams(), NavCParams()):
        v_rest = c_fiber_equilibria(C)[0]["v"]
        mem = make_c_membrane(C, 1)

        def i_ion(v):
            G, J = mem.steady_conductance(np.array([v]))
            return G[0] * v - J[0]

        G, _ = mem.steady_conductance(np.array([v_rest]))                    # S/m^2
        g_chord = G[0]                      # sum of the resting conductances
        d = 1e-5
        g_slope = (i_ion(v_rest + d) - i_ion(v_rest - d)) / (2.0 * d)        # dI/dV at rest
        tau = C.cable.Cm / g_chord                                           # s
        r_i = 4.0 * C.cable.rho_i / (np.pi * C.cable.d ** 2)                 # ohm/m

        def cable(g):
            r_m = 1.0 / (np.pi * C.cable.d * g)                              # ohm*m
            return np.sqrt(r_m / r_i), 0.5 * np.sqrt(r_m * r_i)              # lambda (m), R_in (ohm)

        lam, R_in = cable(g_chord)
        lam_s, R_in_s = cable(g_slope)
        # measured input resistance: small steady injection at the middle of the fiber
        I = 1e-12
        pr = Protocol(stim_amp=0.0, c_stim_amp=I, c_stim_z=NODE_Z, c_stim_dur=60e-3, T=60e-3,
                      stop_on_spike=False, quiet_after=1.0, ionic="explicit")
        m = CoupledModel(C, pr, CleftParams(**NO_CLEFT))
        r = m.run(record=["v2"], record_stride=200)
        i = int(round(NODE_Z / pr.dz))
        dv = r["v2"][-1, i] - r["v2_rest"][i]
        rows.append(dict(model=C.kind, v_rest_mV=v_rest * 1e3, tau_rest_ms=tau * 1e3,
                         g_chord_S_m2=g_chord, g_slope_S_m2=g_slope,
                         lambda_chord_um=lam * 1e6, lambda_slope_um=lam_s * 1e6,
                         R_in_chord_Mohm=R_in * 1e-6, R_in_slope_Mohm=R_in_s * 1e-6,
                         R_in_measured_Mohm=(dv / I) * 1e-6,
                         rheobase_1ms_nA=_rheobase(C) * 1e9))
    return rows


def _rheobase(C, dur=1e-3, lo=1e-12, hi=5e-9):
    """Smallest 1-ms point injection at z = 5 mm that makes the isolated C-fiber fire."""
    def fires(I):
        pr = Protocol(stim_amp=0.0, c_stim_amp=I, c_stim_z=NODE_Z, c_stim_dur=dur, T=25e-3,
                      stop_on_spike=True, quiet_after=1.0, ionic="explicit")
        r = CoupledModel(C, pr, CleftParams(**NO_CLEFT)).run()
        return bool(np.isfinite(r["t_cross_c"]).sum() > 0)
    if not fires(hi):
        return np.nan
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        if fires(mid):
            hi = mid
        else:
            lo = mid
    return hi


if __name__ == "__main__":
    common.write_csv("e14_abeta_gates.csv", gates())
    common.write_csv("e14_abeta_ap_trace.csv", ap_trace())
    common.write_csv("e14_abeta_paired_pulse.csv", paired_pulse())
    common.write_csv("e14_cfiber_passive.csv", cfiber_passive())
