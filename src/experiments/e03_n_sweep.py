"""E03 - Synchronous multi-fiber sweep (production configuration).

n synchronously stimulated Abeta fibers share the fixed 16.4 um^2 extracellular
compartment of a 5-mm focal lesion (z = 2.5-7.5 mm) with one C-fiber; both C-fiber
models; Abeta stimulus 2x threshold at node 0 (outside the lesion).
Because all fibers share one compartment, adding fibers acts like reducing the
extracellular cross-section per Abeta fiber to A_e/n (equivalent sleeve thickness w_eq;
E04 measures how closely the two correspond).

Output: e03_n_sweep.csv
"""
import common
from ephaptic import HHParams, NavCParams
from ephaptic.params import A_REF, equivalent_gap

N_GRID = (1, 2, 3, 5, 7, 10, 12, 15, 17, 20, 22, 25, 30, 40, 50, 75, 100, 150, 200, 300)

if __name__ == "__main__":
    jobs = []
    for C in (HHParams(), NavCParams()):
        for n in N_GRID:
            jobs.append(dict(c=C, proto=dict(n_abeta=n, T=25e-3),
                             tags=dict(model=C.kind, n_abeta=n, area_per_fiber_um2=A_REF / n * 1e12,
                                       w_eq_nm=equivalent_gap(A_REF / n) * 1e9)))
    common.write_csv("e03_n_sweep.csv", common.pmap(common.run_case, jobs))
