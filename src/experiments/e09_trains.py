"""E09 - Repetitive Abeta trains (5 pulses at 50-400 Hz) in the production configuration.

Reported per pulse: peak C-fiber depolarization in the lesion within the pulse window,
and whether a propagating C-fiber action potential occurred.

Output: e09_trains.csv
"""
import numpy as np

import common
from ephaptic import CoupledModel, Protocol, HHParams, NavCParams, CleftParams
from ephaptic.metrics import summarize


def job(a):
    C, n, f, npulses = a
    period = 1.0 / f
    pulses = tuple(i * period for i in range(npulses))
    pr = Protocol(n_abeta=n, pulse_times=pulses, T=pulses[-1] + 20e-3, quiet_after=pulses[-1] + 4e-3)
    m = CoupledModel(C, pr, CleftParams())
    r = m.run(record=["v2"], record_stride=5)
    s = summarize(r)
    t, v2 = r["t"], r["v2"]
    dv = (v2[:, m.geo.cleft] - r["v2_rest"][m.geo.cleft]) * 1e3
    per = []
    for i, p0 in enumerate(pulses):
        w = (t >= p0) & (t < p0 + period)
        per.append(dv[w].max() if w.any() else np.nan)
    row = dict(model=C.kind, n_abeta=n, freq_Hz=f, n_pulses=npulses,
               c_spike=s["c_spike"], c_init_z_mm=s["c_init_z_mm"], status=s["status"],
               dv_max_all_mV=np.nanmax(per), ab_conducts_last=s["ab_conducts"])
    for i, p in enumerate(per):
        row[f"dv_pulse{i+1}_mV"] = p
    return row


if __name__ == "__main__":
    jobs = [(C, n, f, 5) for C in (HHParams(), NavCParams()) for n in (1, 10, 25)
            for f in (50.0, 100.0, 200.0, 400.0)]
    common.write_csv("e09_trains.csv", common.pmap(job, jobs))
