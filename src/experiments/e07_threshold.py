"""E07 - How far is the ephaptic drive from the C-fiber's excitation threshold?

(a) Strength-duration curves of the isolated C-fiber for intracellular current pulses
    (point injection at z = 5 mm, and a uniform current density over the 5-mm lesion
    segment), durations 0.02-20 ms.  Reported: threshold, and the peak depolarization at
    the injection site for a pulse 0.5 % below threshold (the "voltage threshold" for
    that pulse shape).
(b) Ephaptic safety factor alpha*: the u_e(z,t) recorded in the closed-loop run is applied
    to the isolated C-fiber with gain alpha; alpha* is the smallest gain that evokes a
    propagating C-fiber action potential.  alpha = 1 reproduces the closed-loop response.

Outputs: e07_strength_duration.csv, e07_safety_factor.csv
"""
import numpy as np

import common
from variants import hh, navc, label, ionic_for
from ephaptic import CoupledModel, Protocol, CleftParams
from ephaptic.openloop import run_c_driven, bisect_threshold

VARIANTS = [hh(6.3), hh(25.0), hh(6.3, gscale=5.0), hh(6.3, speed=5.0), hh(6.3, speed=10.0),
            navc(1.5), navc(0.05), navc(1.5, speed=10.0)]
DT, DZ = 1e-6, 5e-6
LESION = None


def sd_job(a):
    C, mode, dur = a
    N = int(round(10e-3 / DZ))
    z = np.arange(N) * DZ
    region = (z > 2.5e-3) & (z < 7.5e-3)
    T = dur + 25e-3
    ion_c = "implicit" if ionic_for(C) != "explicit" else "explicit"   # open-loop solver: C-fiber only

    def fires(x):
        if mode == "point":
            r = run_c_driven(C, None, DT, DZ, T=T, I_point=x, z_point=5e-3, dur=dur, ionic=ion_c)
        else:
            r = run_c_driven(C, None, DT, DZ, T=T, I_uniform=x, region=region, dur=dur, ionic=ion_c)
        return r["spike"]
    x0 = 1e-10 if mode == "point" else 0.01
    th, nev = bisect_threshold(fires, 0.0, x0, rtol=5e-3)
    if mode == "point":
        r = run_c_driven(C, None, DT, DZ, T=T, I_point=0.995 * th, z_point=5e-3, dur=dur, stop_on_spike=False, ionic=ion_c)
        k = int(round(5e-3 / DZ))
        vpk = r["v_max"][k]
    else:
        r = run_c_driven(C, None, DT, DZ, T=T, I_uniform=0.995 * th, region=region, dur=dur, stop_on_spike=False, ionic=ion_c)
        vpk = r["v_max"][region].max()
    return dict(variant=label(C), kind=C.kind, mode=mode, duration_ms=dur * 1e3,
                threshold=th, threshold_units="A" if mode == "point" else "A/m^2",
                charge=th * dur, v_peak_subthreshold_mV=vpk * 1e3,
                dv_peak_subthreshold_mV=(vpk - r["v_rest"][0]) * 1e3, rest_mV=r["v_rest"][0] * 1e3)


def sf_job(a):
    C, n, kappa, bias = a
    ion = ionic_for(C)
    ion_c = "implicit" if ion != "explicit" else "explicit"           # open-loop solver: C-fiber only
    pr = Protocol(n_abeta=n, T=4e-3, stop_on_spike=False, quiet_after=1.0, c_bias=bias, ionic=ion)
    m = CoupledModel(C, pr, CleftParams(kappa=kappa))
    r = m.run(record=["ue", "v2"], record_stride=1)
    ue = r["ue"]
    closed_dv = ((r["v2_max"] - r["v2_rest"]) * 1e3)[m.geo.cleft].max()
    r1 = run_c_driven(C, ue, DT, DZ, alpha=1.0, bias=bias, T=4e-3, stop_on_spike=False, ionic=ion_c)
    open_dv = ((r1["v_max"] - r1["v_rest"]) * 1e3)[m.geo.cleft].max()

    def fires(alpha):
        return run_c_driven(C, ue, DT, DZ, alpha=alpha, bias=bias, T=25e-3, ionic=ion_c)["spike"]
    if fires(1.0):
        astar = 1.0
    else:
        astar, _ = bisect_threshold(fires, 1.0, 2.0, rtol=5e-3, hi_max=2000.0)
    return dict(variant=label(C), kind=C.kind, n_abeta=n, kappa=kappa, c_bias=bias,
                closed_loop_dv_mV=closed_dv, open_loop_dv_alpha1_mV=open_dv, alpha_star=astar,
                ue_min_mV=ue.min() * 1e3, ue_max_mV=ue.max() * 1e3)


if __name__ == "__main__":
    durs = (0.02e-3, 0.05e-3, 0.1e-3, 0.2e-3, 0.5e-3, 1e-3, 2e-3, 5e-3, 20e-3)
    jobs = [(C, mode, d) for C in VARIANTS for mode in ("point", "uniform") for d in durs]
    common.write_csv("e07_strength_duration.csv", common.pmap(sd_job, jobs))
    sjobs = [(C, n, 1e9, 0.0) for C in VARIANTS for n in (1, 10, 25, 50, 100)]
    sjobs += [(navc(1.5), n, 1e9, b) for n in (25, 100) for b in (1.0, 2.0, 3.0)]
    sjobs += [(hh(6.3), n, 1e9, b) for n in (25, 100) for b in (0.03, 0.05)]
    common.write_csv("e07_safety_factor.csv", common.pmap(sf_job, sjobs))
