"""E04 - Extracellular cross-section.

(a) Per-fiber sleeve closure: every Abeta fiber (and the C-fiber) brings its own
    periaxonal sleeve of thickness w, so A_e grows with n.  The C-fiber response is then
    (almost) independent of n and set by w alone.
(b) Fixed-compartment closure (production): n fibers share A_REF = 16.4 um^2, which is
    equivalent to an Abeta sleeve of w_eq(n).  Comparing (a) at w = w_eq(n) with (b) at n
    tests the mean-field equivalence.
(c) The equivalence itself: n fibers sharing (r_e, G_e) vs one fiber with (n r_e, G_e/n),
    i.e. the same kappa and A_e/n.  It is exact only if the C-fiber's own axial conductance
    g_2 is neglected, since that term is not rescaled; g_2/Sigma_G quantifies the error.

Output: e04_geometry.csv
"""
import common
from ephaptic import HHParams, NavCParams
from ephaptic.params import A_REF, equivalent_gap, nm

W_GRID_NM = (5, 10, 15, 20, 30, 50, 100, 200, 500, 1000)

if __name__ == "__main__":
    jobs = []
    for C in (HHParams(), NavCParams()):
        for w in W_GRID_NM:
            for n in (1, 10, 100):
                jobs.append(dict(c=C, proto=dict(n_abeta=n, T=25e-3),
                                 cleft=dict(area_model="per_fiber", w_sleeve=w * nm),
                                 tags=dict(model=C.kind, closure="per_fiber", w_nm=w, n_abeta=n)))
        for n in (1, 5, 25, 100):
            w = equivalent_gap(A_REF / n)
            jobs.append(dict(c=C, proto=dict(n_abeta=1, T=25e-3),
                             cleft=dict(area_model="per_fiber", w_sleeve=w),
                             tags=dict(model=C.kind, closure="per_fiber_equiv", w_nm=w * 1e9, n_equiv=n, n_abeta=1)))
    common.write_csv("e04_geometry.csv", common.pmap(common.run_case, jobs))
    eq = []
    for C in (NavCParams(),):
        for n in (2, 5, 10, 25, 50):
            eq.append(dict(c=C, proto=dict(n_abeta=n, T=25e-3),
                           tags=dict(model=C.kind, case="shared", n_abeta=n)))
            eq.append(dict(c=C, proto=dict(n_abeta=1, T=25e-3), cleft=dict(A_e=A_REF / n),
                           tags=dict(model=C.kind, case="single_equivalent", n_abeta=n)))
    common.write_csv("e04_mean_field.csv", common.pmap(common.run_case, eq))
