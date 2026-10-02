"""E01 - Uncoupled positive controls.

Abeta: stimulation threshold (0.2-ms pulse at node 0), conduction velocity and
action-potential excursion at z = 4 mm for the 2x-threshold stimulus used throughout.
C-fiber membrane variants: resting potential, passive time constant, AP peak,
conduction velocity (1-ms pulse at z = 0 of 2 nA times the conductance scale factor)
and APD50 at z = 5 mm.

Outputs: results/data/e01_abeta_control.csv, results/data/e01_cfiber_controls.csv
"""
import numpy as np

import common
from variants import hh, navc, label, ionic_for
from ephaptic import CoupledModel, Protocol, CleftParams, HHParams, NavCParams, AbetaParams, abeta_threshold
from ephaptic.params import ABETA_THRESHOLD, as_dict

NO_CLEFT = dict(lesion_start=10e-3, lesion_end=10e-3)


def _tau_rest(C):
    """Passive membrane time constant at rest, Cm / g_total(rest)."""
    from ephaptic.model import c_fiber_equilibria
    from ephaptic.membranes import make_c_membrane
    v = c_fiber_equilibria(C)[0]["v"]
    G, _ = make_c_membrane(C, 1).steady_conductance(np.array([v]))
    return C.cable.Cm / G[0]


def c_job(C):
    # direct stimulus 2 nA x conductance scale factor (input conductance grows with it)
    gfac = (C.gNa / HHParams().gNa) if C.kind == "HH" else (C.g18 / NavCParams().g18)
    pr = Protocol(stim_amp=0.0, c_stim_amp=2e-9 * max(1.0, gfac), c_stim_dur=1e-3, T=40e-3,
                  stop_on_spike=False, quiet_after=1.0, ionic=ionic_for(C))
    m = CoupledModel(C, pr, CleftParams(**NO_CLEFT))
    r = m.run(record=["v2"], record_stride=10)
    z, tc = r["z"], r["t_cross_c"]
    i3, i7, i5 = (int(round(x / pr.dz)) for x in (3e-3, 7e-3, 5e-3))
    cv = (z[i7] - z[i3]) / (tc[i7] - tc[i3]) if np.all(~np.isnan(tc[[i3, i7]])) else np.nan
    tr = r["v2"][:, i5]
    t = r["t"]
    base = r["v2_rest"][i5]
    half = base + 0.5 * (tr.max() - base)
    above = t[tr > half]
    apd50 = (above.max() - above.min()) if above.size else np.nan
    return dict(variant=label(C), kind=C.kind,
                phi=getattr(C, "phi", np.nan),
                temperature_C=getattr(C, "temperature", np.nan),
                gNa_mS_cm2=getattr(C, "gNa", np.nan) / 10.0,
                tau_m8_ms=getattr(C, "tau_m8", np.nan) * 1e3,
                g18_mS_cm2=getattr(C, "g18", np.nan) / 10.0,
                tau_rest_ms=_tau_rest(C) * 1e3,
                rest_mV=base * 1e3, ap_peak_mV=tr.max() * 1e3,
                cv_m_s=cv, apd50_ms=apd50 * 1e3, propagates=bool(not np.isnan(cv)),
                stim_nA=pr.c_stim_amp * 1e9)


def abeta_job(stim_amp):
    pr = Protocol(stim_amp=stim_amp, T=3e-3, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(HHParams(), pr, CleftParams(**NO_CLEFT))
    r = m.run(record=["v1"], record_stride=1)
    tab = r["t_cross_ab"][0]
    nz = r["node_z"]
    i4, i8 = np.argmin(np.abs(nz - 4e-3)), np.argmin(np.abs(nz - 8e-3))
    cv = (nz[i8] - nz[i4]) / (tab[i8] - tab[i4])
    k4 = int(round(4e-3 / pr.dz))
    return dict(stim_nA=stim_amp * 1e9, cv_4_8mm_m_s=cv,
                peak_z4_mV=r["v1_max"][0, k4] * 1e3,
                excursion_z4_mV=(r["v1_max"][0, k4] - r["v1_rest"][0, k4]) * 1e3,
                node0_peak_mV=r["v1_max"][0, 0] * 1e3,
                rest_node_mV=r["v1_rest"][0, k4] * 1e3, rest_internode_mV=r["v1_rest"][0, k4 + 100] * 1e3)


VARIANTS = ([hh(T) for T in (6.3, 10.0, 15.0, 20.0, 25.0, 30.0)]
            + [hh(6.3, speed=s) for s in (2.0, 3.0, 4.0, 5.0, 7.0, 10.0)]
            + [hh(6.3, gscale=s) for s in (2.0, 5.0, 10.0)]
            + [navc(t) for t in (1.5, 1.0, 0.5, 0.2, 0.1, 0.05)]
            + [navc(1.5, speed=s) for s in (2.0, 5.0, 10.0)])

if __name__ == "__main__":
    th = abeta_threshold(AbetaParams(), Protocol())
    print(f"Abeta threshold {th*1e9:.4f} nA (cached constant {ABETA_THRESHOLD*1e9:.4f} nA)")
    rows = common.pmap(abeta_job, [2 * ABETA_THRESHOLD, 100e-9])
    for r in rows:
        r["threshold_nA"] = th * 1e9
    common.write_csv("e01_abeta_control.csv", rows, meta=dict(abeta=as_dict(AbetaParams()), protocol=as_dict(Protocol())))
    common.write_csv("e01_cfiber_controls.csv", common.pmap(c_job, VARIANTS),
                     meta=dict(stimulus="1 ms at z = 0; 2 nA scaled by the conductance factor of each variant (column stim_nA)", protocol=as_dict(Protocol())))
