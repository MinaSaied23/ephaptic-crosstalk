"""E07 - How far is the ephaptic drive from the C-fiber's excitation threshold?

(a) Strength-duration curves of the isolated C-fiber for intracellular current pulses
    (point injection at z = 5 mm, and a uniform current density over the 5-mm lesion
    segment), durations 0.02-20 ms.  Reported: threshold, and the peak depolarization at
    the injection site for a pulse 0.5 % below threshold (the "voltage threshold" for
    that pulse shape).
(b) Gain threshold alpha* of the recorded ephaptic waveform: the u_e(z,t) recorded in the
    coupled run is applied to the isolated C-fiber with gain alpha; alpha* is the smallest
    gain that evokes a propagating C-fiber action potential.  The replay at alpha = 1 is
    compared with the coupled response (a check of the open-loop C-fiber calculation for
    that waveform).
(c) The C-fiber's own contribution to u_e: the coupled run is repeated with the C-fiber left
    out of the compartment equation, and the two u_e (extremes, timing of the Abeta nodes that
    generate them, largest pointwise difference) and the C-fiber responses to them are compared.
(d) Space-time traces of representative replays (NavC, n = 25 and 50, at gains below,
    at and above alpha*) for the figures.

Every run is classified with the propagation criterion of the coupled simulations
(ephaptic.metrics.c_spike_info) and runs until the overshoot has spread over 7 mm, until the
fiber is back at rest, or until 25 ms after the end of the drive.  Thresholds are found by
scanning the amplitude upward on a geometric grid (factor 1.15 for alpha, 1.2 for currents)
from below any threshold, then bisecting (0.5 %) inside the first grid interval in which
firing appears; three further grid points above the threshold are checked as well.  The
outcome of every scan is stored, so that monotonicity can be checked from the data.

Outputs: e07_strength_duration.csv, e07_safety_factor.csv, e07_c_fiber_contribution.csv,
         e07_replay_traces.npz
"""
import os

import numpy as np

import common
from variants import hh, navc, label, ionic_for
from ephaptic import CoupledModel, Protocol, CleftParams, NavCParams
from ephaptic.openloop import run_c_driven, scan_threshold

VARIANTS = [hh(6.3), hh(25.0), hh(6.3, gscale=5.0), hh(6.3, speed=5.0), hh(6.3, speed=10.0),
            navc(1.5), navc(0.05), navc(1.5, speed=10.0)]
DT, DZ = 1e-6, 5e-6
T_AFTER = 25e-3            # time allowed after the end of the drive
SD_X0 = {"point": 0.02e-9, "uniform": 0.005}     # A and A/m^2: below every threshold
SD_FACTOR, ALPHA_FACTOR, RTOL = 1.2, 1.15, 5e-3
ALPHA_MAX = 2000.0


def _scan_summary(res):
    """Compact record of a threshold scan, for the CSV."""
    sub = [x for x, f in res["scan"] if not f]
    return dict(scan_points=len(res["scan"]), scan_fired_below=any(f for _, f in res["scan"][:-1]),
                above_all_fire=all(f for _, f in res["above"]), monotone=res["monotone"],
                bracket_lo=res["lo"] if res["lo"] is not None else np.nan,
                bracket_hi=res["hi"] if res["hi"] is not None else np.nan,
                n_evals=res["n_evals"], scan_max_subthreshold=max(sub) if sub else np.nan)


def sd_job(a):
    C, mode, dur = a
    N = int(round(10e-3 / DZ))
    z = np.arange(N) * DZ
    region = (z > 2.5e-3) & (z < 7.5e-3)
    T = dur + T_AFTER
    ion_c = "implicit" if ionic_for(C) != "explicit" else "explicit"   # open-loop solver: C-fiber only
    kw = dict(I_point=None, z_point=5e-3) if mode == "point" else dict(I_uniform=None, region=region)
    key = "I_point" if mode == "point" else "I_uniform"

    def run(x, **extra):
        return run_c_driven(C, None, DT, DZ, T=T, dur=dur, ionic=ion_c, **{**kw, key: x}, **extra)

    res = scan_threshold(lambda x: run(x)["spike"], SD_X0[mode], factor=SD_FACTOR, x_max=1e3, rtol=RTOL)
    th = res["threshold"]
    at = run(th)
    below = run(0.995 * th, stop_on_spike=False)
    if mode == "point":
        vpk = below["v_max"][int(round(5e-3 / DZ))]
    else:
        vpk = below["v_max"][region].max()
    row = dict(variant=label(C), kind=C.kind, mode=mode, duration_ms=dur * 1e3,
               threshold=th, threshold_units="A" if mode == "point" else "A/m^2",
               charge=th * dur, v_peak_subthreshold_mV=vpk * 1e3,
               dv_peak_subthreshold_mV=(vpk - below["v_rest"][0]) * 1e3, rest_mV=below["v_rest"][0] * 1e3,
               subthreshold_overshoot=below["c_overshoot"], subthreshold_span_mm=below["c_span_mm"],
               at_threshold_cv=at["c_cv"], at_threshold_init_z_mm=at["c_init_z_mm"],
               at_threshold_span_mm=at["c_span_mm"])
    row.update(_scan_summary(res))
    return row


def sf_job(a):
    C, n, kappa, bias = a
    ion = ionic_for(C)
    ion_c = "implicit" if ion != "explicit" else "explicit"           # open-loop solver: C-fiber only
    pr = Protocol(n_abeta=n, T=4e-3, stop_on_spike=False, quiet_after=1.0, c_bias=bias, ionic=ion)
    m = CoupledModel(C, pr, CleftParams(kappa=kappa))
    r = m.run(record=["ue", "v2"], record_stride=1)
    ue = r["ue"]
    cl = m.geo.cleft
    closed_dv = ((r["v2_max"] - r["v2_rest"]) * 1e3)[cl].max()
    from ephaptic.metrics import c_spike_info
    closed_spike = c_spike_info(r)["c_spike"]
    r1 = run_c_driven(C, ue, DT, DZ, alpha=1.0, bias=bias, T=4e-3, stop_on_spike=False, ionic=ion_c)
    open_dv = ((r1["v_max"] - r1["v_rest"]) * 1e3)[cl].max()
    # (c) the same coupled run with the C-fiber left out of the compartment equation
    m0 = CoupledModel(C, pr, CleftParams(kappa=kappa, c_fiber_loads_compartment=False))
    ue0 = m0.run(record=["ue"], record_stride=1)["ue"]
    du = np.abs(ue0 - ue).max() / np.abs(ue).max()
    r0 = run_c_driven(C, ue0, DT, DZ, alpha=1.0, bias=bias, T=4e-3, stop_on_spike=False, ionic=ion_c)
    nocf_dv = ((r0["v_max"] - r0["v_rest"]) * 1e3)[cl].max()
    sigma_frac = m.g2 / m.Sigma

    def run(alpha):
        return run_c_driven(C, ue, DT, DZ, alpha=alpha, bias=bias, T=ue.shape[0] * DT + T_AFTER, ionic=ion_c)
    res = scan_threshold(lambda x: run(x)["spike"], 1.0, factor=ALPHA_FACTOR, x_max=ALPHA_MAX, rtol=RTOL)
    astar = res["threshold"]
    at = run(astar) if np.isfinite(astar) else None
    row = dict(variant=label(C), kind=C.kind, n_abeta=n, kappa=kappa, c_bias=bias,
               closed_loop_dv_mV=closed_dv, closed_loop_spike=closed_spike,
               open_loop_dv_alpha1_mV=open_dv, alpha_star=astar,
               at_alpha_star_cv=at["c_cv"] if at else np.nan,
               at_alpha_star_init_z_mm=at["c_init_z_mm"] if at else np.nan,
               ue_min_mV=ue.min() * 1e3, ue_max_mV=ue.max() * 1e3,
               ue_end_abs_max_mV=np.abs(ue[-500:]).max() * 1e3,
               c_axial_fraction=sigma_frac, ue_noC_maxdiff_rel=du, noC_dv_alpha1_mV=nocf_dv)
    row.update(_scan_summary(res))
    return row


def noc_job(a):
    """(c) The coupled run with and without the C-fiber in the compartment equation."""
    C, n, kappa, bias = a
    ion = ionic_for(C)
    ion_c = "implicit" if ion != "explicit" else "explicit"
    pr = Protocol(n_abeta=n, T=4e-3, stop_on_spike=False, quiet_after=1.0, c_bias=bias, ionic=ion)
    m1 = CoupledModel(C, pr, CleftParams(kappa=kappa))
    r1 = m1.run(record=["ue"], record_stride=1)
    r0 = CoupledModel(C, pr, CleftParams(kappa=kappa, c_fiber_loads_compartment=False)).run(
        record=["ue"], record_stride=1)
    ue1, ue0 = r1["ue"], r0["ue"]
    ta1, ta0 = r1["t_cross_ab"][0], r0["t_cross_ab"][0]
    both = ~np.isnan(ta1) & ~np.isnan(ta0)
    from ephaptic.metrics import c_spike_info
    cl = m1.geo.cleft
    dv1 = ((r1["v2_max"] - r1["v2_rest"]) * 1e3)[cl].max()
    o0 = run_c_driven(C, ue0, DT, DZ, alpha=1.0, bias=bias, T=4e-3, stop_on_spike=False, ionic=ion_c)
    dv0 = ((o0["v_max"] - o0["v_rest"]) * 1e3)[cl].max()
    return dict(variant=label(C), kind=C.kind, n_abeta=n, kappa=kappa, c_bias=bias,
                closed_loop_spike=c_spike_info(r1)["c_spike"],
                ue_min_mV=ue1.min() * 1e3, ue_min_noC_mV=ue0.min() * 1e3,
                ue_max_mV=ue1.max() * 1e3, ue_max_noC_mV=ue0.max() * 1e3,
                ue_extreme_change_rel=max(abs(ue0.min() / ue1.min() - 1), abs(ue0.max() / ue1.max() - 1)),
                ue_pointwise_maxdiff_rel=np.abs(ue0 - ue1).max() / np.abs(ue1).max(),
                abeta_same_nodes=bool(np.array_equal(np.isnan(ta1), np.isnan(ta0))),
                abeta_max_shift_us=float(np.abs(ta1[both] - ta0[both]).max() * 1e6) if both.any() else np.nan,
                c_dv_mV=dv1, c_dv_noC_mV=dv0, c_dv_change_rel=abs(dv0 / dv1 - 1))


TRACE_CASES = [(25, 4.5625), (25, None), (50, None)]   # (n, alpha); None: at the computed alpha*


def trace_job(a):
    """NavC replays recorded in space and time: the old span-only 'threshold' at n = 25, and
    the alpha* of the propagation criterion at n = 25 and 50 (and 2 % below it)."""
    n, alpha = a
    C = NavCParams()
    pr = Protocol(n_abeta=n, T=4e-3, stop_on_spike=False, quiet_after=1.0)
    ue = CoupledModel(C, pr, CleftParams()).run(record=["ue"], record_stride=1)["ue"]
    out = {}
    if alpha is None:
        res = scan_threshold(lambda x: run_c_driven(C, ue, DT, DZ, alpha=x, T=4e-3 + T_AFTER)["spike"],
                             1.0, factor=ALPHA_FACTOR, x_max=ALPHA_MAX, rtol=RTOL, n_above=0)
        gains = {"at": res["threshold"], "below": res["lo"]}
    else:
        gains = {"fixed": alpha}
    for tag, g in gains.items():
        r = run_c_driven(C, ue, DT, DZ, alpha=g, T=4e-3 + T_AFTER, stop_on_spike=False, record_stride=40)
        k = f"n{n}_{tag}"
        out[f"{k}__alpha"] = np.array([g])
        out[f"{k}__spike"] = np.array([r["spike"]])
        out[f"{k}__t"] = r["t"]
        out[f"{k}__z"] = r["z"][::4]
        out[f"{k}__v"] = (r["v"][:, ::4] * 1e3).astype(np.float32)
        out[f"{k}__t_cross"] = r["t_cross"]
        out[f"{k}__span_mm"] = np.array([r["c_span_mm"]])
        out[f"{k}__cv"] = np.array([r["c_cv"]])
    return out


if __name__ == "__main__":
    durs = (0.02e-3, 0.05e-3, 0.1e-3, 0.2e-3, 0.5e-3, 1e-3, 2e-3, 5e-3, 20e-3)
    sjobs = [(C, n, 1e9, 0.0) for C in VARIANTS for n in (1, 10, 25, 50, 100)]
    sjobs += [(navc(1.5), n, 1e9, b) for n in (25, 100) for b in (1.0, 2.0, 3.0)]
    sjobs += [(hh(6.3), n, 1e9, b) for n in (25, 100) for b in (0.03, 0.05)]
    common.write_csv("e07_safety_factor.csv", common.pmap(sf_job, sjobs))
    common.write_csv("e07_c_fiber_contribution.csv", common.pmap(noc_job, sjobs))
    jobs = [(C, mode, d) for C in VARIANTS for mode in ("point", "uniform") for d in durs]
    common.write_csv("e07_strength_duration.csv", common.pmap(sd_job, jobs))
    tr = common.pmap(trace_job, TRACE_CASES)
    out = {}
    for d in tr:
        out.update(d)
    path = os.path.join(common.DATA, "e07_replay_traces.npz")
    np.savez_compressed(path, **out)
    print(f"  wrote {os.path.relpath(path, common.ROOT)} ({os.path.getsize(path)/1e6:.1f} MB)")
