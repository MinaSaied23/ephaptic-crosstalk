"""E06 - C-fiber kinetics sensitivity (temperature, time compression, tau_m8) x n x kappa.

Variants: HH at 6.3-25 degC (rates x 3^((T-6.3)/10)); time-compressed HH (rates and
conductances x s, s = 2-10); HH with conductances x s only; NavC with tau_m8 = 1.5-0.05 ms;
time-compressed NavC (time constants / s, conductances x s).  Each variant conducts
(E01).  Production configuration otherwise; kappa = 1e9 and 1e10 m^-2.

Output: e06_kinetics.csv
"""
import common
from variants import hh, navc, label, ionic_for

N_GRID = (1, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300)
VARIANTS = ([("HH_temperature", T, hh(T)) for T in (6.3, 10.0, 15.0, 20.0, 25.0)]
            + [("HH_speed", s, hh(6.3, speed=s)) for s in (2.0, 3.0, 4.0, 5.0, 7.0, 10.0)]
            + [("HH_gscale", s, hh(6.3, gscale=s)) for s in (2.0, 5.0, 10.0)]
            + [("NavC_tau_m8", t, navc(t)) for t in (1.5, 1.0, 0.5, 0.2, 0.1, 0.05)]
            + [("NavC_speed", s, navc(1.5, speed=s)) for s in (2.0, 5.0, 10.0)])

if __name__ == "__main__":
    jobs = []
    for fam, val, C in VARIANTS:
        for kappa in (1e9, 1e10):
            for n in N_GRID:
                jobs.append(dict(c=C, proto=dict(n_abeta=n, T=25e-3, ionic=ionic_for(C)), cleft=dict(kappa=kappa),
                                 tags=dict(family=fam, value=val, variant=label(C), kappa=kappa, n_abeta=n)))
    common.write_csv("e06_kinetics.csv", common.pmap(common.run_case, jobs))
