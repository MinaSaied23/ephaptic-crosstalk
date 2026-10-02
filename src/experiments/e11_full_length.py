"""E11 - The extended-compartment configuration: the shared compartment spans the whole
cable (sealed ends) and the Abeta fiber is stimulated at node 0 inside it, rather than
outside a focal lesion.

Two treatments of the electrode current are compared: "returned" (the injected current
leaves through the membrane into the shared compartment, which is what current conservation
requires) and "omitted" (the electrode current does not appear in the extracellular source,
which is the commoner simplification).

Stimulus 2x threshold (3.0 nA) to 100 nA; n = 1-50; both C-fiber models.  Reports the
electrode-site state (Abeta node 0, C-fiber and u_e at z = 0), whether a C-fiber action
potential is launched and where, and the interior response.  Also a low-kappa case
(kappa = 3e7 m^-2, 100 nA), the same with a 1-um compartment, and 100-Hz trains delivered
through the electrode, which is where a delayed "ephaptic" spike can appear.

Outputs: e11_full_length.csv, e11_full_length_trains.csv
"""
import numpy as np

import common
from ephaptic import CoupledModel, Protocol, CleftParams, HHParams, NavCParams
from ephaptic.params import ABETA_THRESHOLD, a_eff_pair
from ephaptic.metrics import summarize


def job(a, pulses=(0.0,), T=40e-3):
    C, n, stim, kappa, A_e, ret = a
    pr = Protocol(n_abeta=n, stim_amp=stim, T=T, pulse_times=pulses)
    cl = CleftParams(config="full", kappa=kappa, A_e=A_e, stim_current_returns_via_cleft=ret)
    m = CoupledModel(C, pr, cl)
    r = m.run()
    s = summarize(r)
    z = r["z"]
    interior = (z >= 3e-3) & (z <= 7e-3)
    row = dict(model=C.kind, n_abeta=n, stim_nA=stim * 1e9, kappa=kappa, A_e_um2=A_e * 1e12,
               electrode_current="returned" if ret else "omitted",
               abeta_node0_peak_mV=r["v1_max"][0, 0] * 1e3, c_z0_peak_mV=r["v2_max"][0] * 1e3,
               ue_z0_max_mV=r["ue_max"][0] * 1e3, ue_z0_min_mV=r["ue_min"][0] * 1e3,
               ue_abs_max_mV=max(abs(r["ue_max"].max()), abs(r["ue_min"].min())) * 1e3,
               dv_interior_mV=((r["v2_max"] - r["v2_rest"])[interior]).max() * 1e3)
    row.update({k: s[k] for k in ("status", "c_spike", "c_overshoot", "c_init_z_mm", "c_init_t_ms", "c_cv", "ab_conducts")})
    row["n_pulses"] = len(pulses)
    row["t_end_ms"] = s["t_end_ms"]
    return row


def train_job(a):
    """Five pulses at 100 Hz through the same electrode."""
    pulses = tuple(k / 100.0 for k in range(5))
    return job(a, pulses=pulses, T=pulses[-1] + 20e-3)


if __name__ == "__main__":
    A0 = a_eff_pair(20e-9)
    jobs = [(C, n, stim, 1e9, A0, ret) for C in (HHParams(), NavCParams())
            for stim in (2 * ABETA_THRESHOLD, 10e-9, 30e-9, 100e-9) for n in (1, 2, 5, 10, 25, 50)
            for ret in (True, False)]
    # a low-kappa case, in both electrode treatments
    jobs += [(HHParams(), n, stim, 3e7, A_e, ret)
             for n in (1, 25) for stim in (2 * ABETA_THRESHOLD, 100e-9)
             for A_e in (A0, a_eff_pair(1e-6)) for ret in (True, False)]
    common.write_csv("e11_full_length.csv", common.pmap(job, jobs))

    # 100-Hz trains through the electrode, the configuration in which a delayed C-fiber spike
    # appears, at the physiological stimulus and at 100 nA
    tjobs = [(C, n, stim, 1e9, A0, ret) for C in (HHParams(), NavCParams())
             for stim in (2 * ABETA_THRESHOLD, 100e-9) for n in (1, 25) for ret in (True, False)]
    common.write_csv("e11_full_length_trains.csv", common.pmap(train_job, tjobs))
