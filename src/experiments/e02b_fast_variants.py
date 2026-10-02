"""E02b - Time-step check for the C-fiber variants with scaled-up conductances, which are
integrated with a conductance-implicit C-fiber ionic current at dt = 1 us ("implicit_c"):
compare with dt = 0.25 us (implicit_c, and fully explicit).

Also: the standard NavC membrane at n = 75 and 100 (Abeta conduction close to block at
the first lesion node) with every ionic treatment and dt, to show which schemes place the
block boundary correctly.

Output: e02b_fast_variants.csv
"""
import common
from variants import hh, navc, label
from ephaptic.metrics import summarize


def job(a):
    C, n, ionic, dt = a
    row = common.run_case(dict(c=C, proto=dict(n_abeta=n, ionic=ionic, dt=dt, T=25e-3)))
    return dict(variant=label(C), n_abeta=n, ionic=ionic, dt_us=dt * 1e6,
                dv_lesion_mV=row["dv_lesion_mV"], c_spike=row["c_spike"], c_cv=row["c_cv"])


if __name__ == "__main__":
    jobs = [(C, n, ion, dt) for C in (hh(6.3, speed=5.0), hh(6.3, speed=10.0), hh(6.3, gscale=5.0), navc(1.5, speed=10.0))
            for n in (15, 25, 50, 100) for ion, dt in (("implicit_c", 1e-6), ("implicit_c", 0.25e-6), ("explicit", 0.25e-6))]
    from ephaptic import NavCParams
    jobs += [(NavCParams(), n, ion, dt) for n in (75, 100)
             for ion in ("explicit", "implicit_c", "implicit") for dt in (1e-6, 0.25e-6, 0.1e-6)]
    common.write_csv("e02b_fast_variants.csv", common.pmap(job, jobs))
