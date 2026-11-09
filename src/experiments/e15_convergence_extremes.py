"""E15 - Numerical convergence at the largest responses and near conduction block.

E02 refines dt and dz for n = 1-50.  This experiment repeats the refinement where the
response is largest or the Abeta action potential is close to failing:

(a) the baseline maximum of the synchronous sweep (n = 100, kappa = 1e9 m^-2, both C-fiber
    models) and the largest response of the kappa sweep (NavC, kappa = 3e10 m^-2, n = 200),
    for dt = 1, 0.25, 0.1 us and dz = 10, 5, 2.5, 1.25 us;
(b) the time-compressed HH membrane (rates and conductances x 10) that fires at
    kappa = 1e10 m^-2, n = 75 while the Abeta action potential still conducts: dt = 1, 0.25,
    0.1 us (C-fiber conductance-implicit, as in production, and fully explicit) and
    dz = 5, 2.5, 1.25 um;
(c) temporal dispersion near conduction block: the synchronous volley and dispersed volleys
    (NavC, n = 25 at W = 0.2, 0.5, 1.5 ms; n = 50 at W = 0.1, 0.2, 0.5 ms) on dz = 20, 10 and
    5 um, with the number of onset phases chosen as in E08 (spacing <= 25 us), reporting the
    C-fiber peak, the Abeta outcome and the attenuation relative to the synchronous volley on
    the same grid.

Outputs: e15_convergence_extremes.csv, e15_dispersion_grid.csv
"""
import common
from variants import hh, label, ionic_for
from e08_jitter import phases_for
from ephaptic import HHParams, NavCParams


def conv_job(a):
    case, C, n, kappa, dt, dz, ionic = a
    row = common.run_case(dict(c=C, proto=dict(n_abeta=n, dt=dt, dz=dz, T=25e-3, ionic=ionic),
                               cleft=dict(kappa=kappa)))
    keep = ("dv_lesion_mV", "dv_lesion_z_mm", "v2_peak_lesion_mV", "c_spike", "c_overshoot", "c_cv",
            "c_init_z_mm", "c_init_t_ms", "ab_conducts", "ab_cv_lesion", "status", "t_end_ms")
    out = dict(case=case, variant=label(C), model=C.kind, n_abeta=n, kappa=kappa, dt_us=dt * 1e6,
               dz_um=dz * 1e6, ionic=ionic)
    out.update({k: row[k] for k in keep})
    return out


def jitter_job(a):
    n, w_ms, dz = a
    K = phases_for(w_ms)
    row = common.run_case(dict(c=NavCParams(), proto=dict(n_abeta=n, jitter=w_ms * 1e-3, jitter_phases=K,
                                                         dz=dz, T=20e-3 + w_ms * 1e-3)))
    return dict(model="NavC", n_abeta=n, jitter_ms=w_ms, K=K, dz_um=dz * 1e6,
                dv_lesion_mV=row["dv_lesion_mV"], c_spike=row["c_spike"], ab_conducts=row["ab_conducts"],
                ab_cv_lesion=row["ab_cv_lesion"], status=row["status"])


if __name__ == "__main__":
    jobs = []
    grid = [(dt, dz) for dt in (1e-6, 0.25e-6, 0.1e-6) for dz in (10e-6, 5e-6, 2.5e-6, 1.25e-6)]
    for C in (NavCParams(), HHParams()):
        jobs += [("n_sweep_max", C, 100, 1e9, dt, dz, "explicit") for dt, dz in grid]
    jobs += [("kappa_sweep_max", NavCParams(), 200, 3e10, dt, dz, "explicit") for dt, dz in grid]
    fast = hh(6.3, speed=10.0)
    jobs += [("hh_x10_fires", fast, 75, 1e10, dt, dz, ionic_for(fast))
             for dt in (1e-6, 0.25e-6, 0.1e-6) for dz in (5e-6, 2.5e-6, 1.25e-6)]
    jobs += [("hh_x10_fires", fast, 75, 1e10, dt, 5e-6, "explicit") for dt in (0.25e-6, 0.1e-6)]
    # largest jobs first, so the pool finishes evenly
    jobs.sort(key=lambda j: -(1.0 / j[4]) * (1.0 / j[5]))
    common.write_csv("e15_convergence_extremes.csv", common.pmap(conv_job, jobs))

    djobs = [(n, w, dz) for n, ws in ((25, (0.0, 0.2, 0.5, 1.5)), (50, (0.0, 0.1, 0.2, 0.5)))
             for w in ws for dz in (20e-6, 10e-6, 5e-6)]
    djobs.sort(key=lambda j: -phases_for(j[1]) / j[2])
    common.write_csv("e15_dispersion_grid.csv", common.pmap(jitter_job, djobs))
