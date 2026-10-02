"""E10 - Sensitized C-fiber: uniform depolarizing bias current.

(a) Space-clamped equilibria and their stability vs bias (both models).
(b) Coupled runs: bias x n (production configuration), each with a no-stimulus control
    so that spontaneous activity is never attributed to ephaptic input.

Outputs: e10_equilibria.csv, e10_bias.csv
"""
import numpy as np

import common
from ephaptic import HHParams, NavCParams
from ephaptic.model import c_fiber_equilibria

HH_BIAS = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07)
NAVC_BIAS = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)

if __name__ == "__main__":
    eq = []
    for C, grid in ((HHParams(), np.round(np.arange(0.0, 0.1001, 0.005), 4)),
                    (NavCParams(), np.round(np.arange(0.0, 4.001, 0.25), 3))):
        for b in grid:
            roots = c_fiber_equilibria(C, float(b))
            eq.append(dict(model=C.kind, bias_A_m2=float(b), n_equilibria=len(roots),
                           v_lower_mV=roots[0]["v"] * 1e3, lower_stable=roots[0]["stable"],
                           all_mV=";".join(f"{r['v']*1e3:.3f}{'s' if r['stable'] else 'u'}" for r in roots)))
    common.write_csv("e10_equilibria.csv", eq)
    jobs = []
    for C, grid in ((HHParams(), HH_BIAS), (NavCParams(), NAVC_BIAS)):
        for b in grid:
            jobs.append(dict(c=C, proto=dict(n_abeta=1, c_bias=b, stim_amp=0.0, T=200e-3, quiet_after=1.0),
                             tags=dict(model=C.kind, bias_A_m2=b, n_abeta=0, control="no_stimulus")))
            for n in (1, 10, 25, 50, 100):
                jobs.append(dict(c=C, proto=dict(n_abeta=n, c_bias=b, T=25e-3),
                                 tags=dict(model=C.kind, bias_A_m2=b, n_abeta=n, control="")))
    common.write_csv("e10_bias.csv", common.pmap(common.run_case, jobs))
