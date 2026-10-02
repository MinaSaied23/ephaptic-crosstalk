"""E05 - Extracellular leak (kappa = r_e G_e; lambda_e = 1/sqrt(kappa)) sensitivity.

kappa spans five decades (lambda_e = 3 um ... 1 mm) for both C-fiber models over the
n grid (production configuration otherwise).

Output: e05_kappa.csv
"""
import math
import common
from ephaptic import HHParams, NavCParams

KAPPA = (1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9, 3e9, 1e10, 3e10, 1e11)
N_GRID = (1, 5, 10, 25, 50, 100, 200)

if __name__ == "__main__":
    jobs = []
    for C in (HHParams(), NavCParams()):
        for k in KAPPA:
            for n in N_GRID:
                jobs.append(dict(c=C, proto=dict(n_abeta=n, T=25e-3), cleft=dict(kappa=k),
                                 tags=dict(model=C.kind, kappa=k, lambda_e_um=1e6 / math.sqrt(k), n_abeta=n)))
    common.write_csv("e05_kappa.csv", common.pmap(common.run_case, jobs))
