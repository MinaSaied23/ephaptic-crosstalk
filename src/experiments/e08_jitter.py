"""E08 - Temporal dispersion of the Abeta volley.

The onsets of the n fibers are spread uniformly over a window of width W.  The ensemble is
represented by K groups of n/K fibers, each an explicit Abeta cable sharing the compartment.
Because the depolarization produced by one fiber lasts only ~0.1 ms, K must be large enough
that the spacing between groups, W/(K-1), is well below that: K is chosen adaptively so the
spacing is at most 25 us (capped at K = 81), and K-convergence is verified explicitly.
The sweep runs on dz = 20 um, because the cost of one step grows with K x (grid size);
the grid is checked separately at dz = 20, 10 and 5 um.  This is also the one experiment
that is slower in parallel: the coupled matrix is factorized once, and each step streams the
whole LU factor (about 90 MB at K = 61), so several workers only contend for memory
bandwidth.  run_all.py runs it with EPHAPTIC_WORKERS=1; set that variable when running it
directly.

Outputs: e08_jitter.csv (sweep), e08_jitter_convergence.csv (K and grid convergence)
"""
import math

import common
from ephaptic import HHParams, NavCParams

W_MS = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0)
MAX_SPACING = 25e-6
K_MAX = 81


def phases_for(w_ms):
    if w_ms <= 0:
        return 1
    return int(min(K_MAX, max(3, math.ceil(w_ms * 1e-3 / MAX_SPACING) + 1)))


if __name__ == "__main__":
    jobs = []
    for C in (NavCParams(),):
        for n in (10, 25, 50):
            for w in W_MS:
                K = phases_for(w)
                jobs.append(dict(c=C, proto=dict(n_abeta=n, jitter=w * 1e-3, jitter_phases=K,
                                                 dz=20e-6, T=20e-3 + w * 1e-3),
                                 tags=dict(model=C.kind, n_abeta=n, jitter_ms=w, K=K, dz_um=20)))
    for w in (0.0, 0.5, 1.5):            # HH check at n = 25
        K = phases_for(w)
        jobs.append(dict(c=HHParams(), proto=dict(n_abeta=25, jitter=w * 1e-3, jitter_phases=K,
                                                  dz=20e-6, T=20e-3 + w * 1e-3),
                         tags=dict(model="HH", n_abeta=25, jitter_ms=w, K=K, dz_um=20)))
    common.write_csv("e08_jitter.csv", common.pmap(common.run_case, jobs))

    conv = []
    for K in (11, 21, 41, 61, 81):
        conv.append(dict(c=NavCParams(), proto=dict(n_abeta=25, jitter=1.5e-3, jitter_phases=K,
                                                    dz=20e-6, T=22e-3),
                         tags=dict(study="K", n_abeta=25, jitter_ms=1.5, K=K, dz_um=20)))
    for dz in (20e-6, 10e-6, 5e-6):
        conv.append(dict(c=NavCParams(), proto=dict(n_abeta=25, jitter=1.5e-3, jitter_phases=41,
                                                    dz=dz, T=22e-3),
                         tags=dict(study="dz", n_abeta=25, jitter_ms=1.5, K=41, dz_um=dz * 1e6)))
    common.write_csv("e08_jitter_convergence.csv", common.pmap(common.run_case, conv))
