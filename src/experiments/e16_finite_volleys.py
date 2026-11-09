"""E16 - Finite volleys: n individual Abeta fibers instead of K weighted onset groups.

E08 represents a dispersed volley of n fibers by K explicit Abeta cables, each carrying n/K
fibers, with onsets evenly spaced over the window W.  Increasing K therefore approximates a
continuous distribution of onset times for a fixed total source weight (at n = 25,
W = 1.5 ms, K = 61, each cable carries 0.41 of one fiber).  A real volley of n axons has n
onset times, each contributing one fiber's source.  Here every fiber is an explicit cable of
unit weight (K = n), with onsets evenly spaced over [0, W], compared with the weighted-cable
approximation on the same grid.

NavC, n = 25, W = 0.5 and 1.5 ms (and the synchronous reference), dz = 20 um (the grid of
the E08 sweep) and 5 um (the production grid).

Output: e16_finite_volleys.csv
"""
import common
from e08_jitter import phases_for
from ephaptic import NavCParams

N_FIB = 25


def job(a):
    kind, w_ms, dz, seed = a
    W = w_ms * 1e-3
    if kind == "synchronous":
        proto = dict(n_abeta=N_FIB)
        K = 1
    elif kind == "weighted":                        # E08: K groups of n/K fibers
        K = phases_for(w_ms)
        proto = dict(n_abeta=N_FIB, jitter=W, jitter_phases=K)
    else:                                           # n fibers, evenly spaced onsets
        K = N_FIB
        proto = dict(n_abeta=N_FIB, jitter=W, jitter_phases=N_FIB)
    proto.update(dz=dz, T=20e-3 + W)
    row = common.run_case(dict(c=NavCParams(), proto=proto))
    return dict(model="NavC", n_abeta=N_FIB, kind=kind, jitter_ms=w_ms, dz_um=dz * 1e6, K=K,
                weight_per_cable=N_FIB / K,
                dv_lesion_mV=row["dv_lesion_mV"], c_spike=row["c_spike"],
                ab_conducts=row["ab_conducts"], status=row["status"])


if __name__ == "__main__":
    jobs = []
    for dz in (20e-6, 5e-6):
        jobs.append(("synchronous", 0.0, dz, -1))
        for w in (0.5, 1.5):
            jobs += [("weighted", w, dz, -1), ("unit_even", w, dz, -1)]
    jobs.sort(key=lambda j: -(phases_for(j[1]) if j[0] == "weighted" else N_FIB) / j[2])
    common.write_csv("e16_finite_volleys.csv", common.pmap(job, jobs))
