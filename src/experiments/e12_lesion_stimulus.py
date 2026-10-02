"""E12 - Lesion length and stimulus strength (production configuration otherwise).

Output: e12_lesion_stimulus.csv
"""
import common
from ephaptic import HHParams, NavCParams

if __name__ == "__main__":
    jobs = []
    for C in (HHParams(), NavCParams()):
        for Lles in (1.0, 2.0, 3.0, 5.0, 7.0):
            for n in (1, 10, 25, 50, 100):
                jobs.append(dict(c=C, proto=dict(n_abeta=n, T=25e-3),
                                 cleft=dict(lesion_start=(5.0 - Lles / 2) * 1e-3, lesion_end=(5.0 + Lles / 2) * 1e-3),
                                 tags=dict(model=C.kind, study="lesion_length", lesion_mm=Lles, stim_factor=2.0, n_abeta=n)))
        for f in (1.2, 5.0, 20.0):
            for n in (1, 10, 25, 50, 100):
                jobs.append(dict(c=C, proto=dict(n_abeta=n, stim_factor=f, T=25e-3),
                                 tags=dict(model=C.kind, study="stimulus", lesion_mm=5.0, stim_factor=f, n_abeta=n)))
    common.write_csv("e12_lesion_stimulus.csv", common.pmap(common.run_case, jobs))
