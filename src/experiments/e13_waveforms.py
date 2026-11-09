"""E13 - Space-time recordings for the figures (production configuration).

Stored at reduced resolution, enough for the figures and small enough to version:
  maps   u_e and C-fiber dV over z (10 um) and t <= 1.2 ms (10 us)
  traces C-fiber dV and u_e at the peak site, and Abeta V_m at the nodes, at 2 us
  controls  uncoupled action potentials at 0.1 mm spacing
and at full spatial resolution, for the widths of the depolarized peaks:
  dv_profile_full     C-fiber dV(z) at the time of the global peak
  node_peak_profiles  C-fiber dV(z) at the time each lesion node's own depolarization peaks
                      (node_peak_t, node_peak_z_mm), one row per node
  fwhm grid check     the same node-peak profiles for NavC, n = 10 at dz = 2.5 and 1.25 um

Output: results/data/e13_waveforms.npz
"""
import os
import numpy as np

import common
from ephaptic import CoupledModel, Protocol, CleftParams, HHParams, NavCParams

ZS = 2      # keep every 2nd compartment (10 um)
TS_MAP = 10  # map frames every 10 us
TMAP = 1.2e-3


def node_peaks(m, r, dv):
    """dV(z) at full resolution at the time each lesion node's own depolarization peaks."""
    nodes = [i for i in m.mem1.node_idx if m.geo.cleft[i]]
    kk = [int(np.argmax(dv[:, i])) for i in nodes]
    return dict(node_peak_z_mm=r["z"][nodes] * 1e3, node_peak_t=r["t"][kk],
                node_peak_profiles=dv[kk].astype(np.float32), z_full=r["z"])


def job(a):
    C, n = a
    pr = Protocol(n_abeta=n, T=3e-3, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(C, pr)
    r = m.run(record=["v1", "v2", "ue"], record_stride=2)
    t = r["t"]
    dv = (r["v2"] - r["v2_rest"]) * 1e3
    ue = r["ue"] * 1e3
    k, i = np.unravel_index(np.argmax(dv), dv.shape)
    sel = t <= TMAP
    out = dict(key=f"{C.kind}_n{n}", z=r["z"][::ZS], t_map=t[sel][::TS_MAP // 2],
               ue_map=ue[sel][::TS_MAP // 2, ::ZS].astype(np.float32),
               dv_map=dv[sel][::TS_MAP // 2, ::ZS].astype(np.float32),
               t=t, dv_peak=dv[:, i].astype(np.float32), ue_peak=ue[:, i].astype(np.float32),
               peak_z_mm=np.array([r["z"][i] * 1e3]), peak_t_ms=np.array([t[k] * 1e3]),
               dv_profile=dv[k, ::ZS].astype(np.float32), ue_profile=ue[k, ::ZS].astype(np.float32),
               dv_profile_full=dv[k].astype(np.float32),
               v1_nodes=(r["v1"][:, m.mem1.node_idx] * 1e3).astype(np.float32),
               node_z_mm=r["node_z"] * 1e3, cleft=m.geo.cleft[::ZS])
    out.update(node_peaks(m, r, dv))
    return out


def fwhm_grid_job(dz):
    """Node-peak profiles of NavC, n = 10 on a finer grid (width of the depolarized peaks)."""
    pr = Protocol(n_abeta=10, dz=dz, T=1.0e-3, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(NavCParams(), pr)
    r = m.run(record=["v2"], record_stride=1)
    dv = (r["v2"] - r["v2_rest"]) * 1e3
    out = dict(key=f"fwhmgrid_dz{dz * 1e6:g}")
    out.update(node_peaks(m, r, dv))
    return out


def control_job(C):
    pr = Protocol(stim_amp=0.0, c_stim_amp=2e-9, c_stim_dur=1e-3, T=30e-3,
                  stop_on_spike=False, quiet_after=1.0)
    r = CoupledModel(C, pr, CleftParams(lesion_start=10e-3, lesion_end=10e-3)).run(
        record=["v2"], record_stride=20)
    return dict(key=f"ctrl_{C.kind}", t=r["t"], z=r["z"][::200],
                v2=(r["v2"][:, ::200] * 1e3).astype(np.float32))


def abeta_control():
    pr = Protocol(T=1.5e-3, stop_on_spike=False, quiet_after=1.0)
    r = CoupledModel(HHParams(), pr, CleftParams(lesion_start=10e-3, lesion_end=10e-3)).run(
        record=["v1"], record_stride=2)
    return dict(key="ctrl_abeta", t=r["t"], z=r["z"][::200],
                v1=(r["v1"][:, ::200] * 1e3).astype(np.float32))


if __name__ == "__main__":
    res = common.pmap(job, [(C, n) for C in (NavCParams(), HHParams()) for n in (1, 10, 25)])
    res += common.pmap(fwhm_grid_job, [2.5e-6, 1.25e-6])
    res += common.pmap(control_job, [HHParams(), NavCParams()])
    res.append(abeta_control())
    out = {}
    for r in res:
        k = r.pop("key")
        for f, v in r.items():
            out[f"{k}__{f}"] = v
    path = os.path.join(common.DATA, "e13_waveforms.npz")
    np.savez_compressed(path, **out)
    print(f"  wrote {os.path.relpath(path, common.ROOT)} ({os.path.getsize(path)/1e6:.1f} MB)")
