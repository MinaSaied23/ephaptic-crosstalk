"""Outcome measures computed from CoupledModel.run() results."""
from __future__ import annotations

import numpy as np


def c_spike_info(r, min_span=3.0e-3, cv_bounds=(0.05, 5.0)):
    """A propagating C-fiber action potential is declared when the C-fiber overshoots
    0 mV over a stretch of at least `min_span` and the overshoot front travels outward at
    a conduction velocity within cv_bounds, measured over the outermost 1 mm of the
    overshoot region on either side (this tolerates near-simultaneous initiation at
    several sites)."""
    z, tc = r["z"], r["t_cross_c"]
    crossed = ~np.isnan(tc)
    info = dict(c_spike=False, c_overshoot=bool(crossed.any()), c_init_z_mm=np.nan,
                c_init_t_ms=np.nan, c_cv=np.nan, c_span_mm=0.0)
    if not crossed.any():
        return info
    i0 = int(np.nanargmin(tc))
    info["c_init_z_mm"] = z[i0] * 1e3
    info["c_init_t_ms"] = tc[i0] * 1e3
    idx = np.where(crossed)[0]
    span = z[idx[-1]] - z[idx[0]]
    info["c_span_mm"] = span * 1e3
    dz = z[1] - z[0]
    k = int(round(1e-3 / dz))
    cvs = []
    for outer, inner in ((idx[-1], idx[-1] - k), (idx[0], idx[0] + k)):
        if 0 <= inner < z.size and crossed[inner] and tc[outer] > tc[inner]:
            cvs.append(abs(z[outer] - z[inner]) / (tc[outer] - tc[inner]))
    if cvs:
        info["c_cv"] = float(min(cvs))
    info["c_spike"] = bool(span >= min_span - 1e-12 and cvs and
                           any(cv_bounds[0] <= c <= cv_bounds[1] for c in cvs))
    return info


def abeta_info(r):
    t = r["t_cross_ab"]            # (K, nodes)
    nz = r["node_z"]
    K = t.shape[0]
    j = K // 2
    conducts = bool(np.all(~np.isnan(t[:, -1])))
    out = dict(ab_conducts=conducts, ab_cv_lesion=np.nan, ab_cv_free=np.nan)
    tj = t[j]

    def cv(za, zb):
        ia, ib = np.argmin(np.abs(nz - za)), np.argmin(np.abs(nz - zb))
        if np.isnan(tj[ia]) or np.isnan(tj[ib]) or tj[ib] <= tj[ia]:
            return np.nan
        return (nz[ib] - nz[ia]) / (tj[ib] - tj[ia])
    out["ab_cv_lesion"] = cv(3e-3, 7e-3)
    out["ab_cv_free"] = cv(0.0, 2e-3)
    return out


def summarize(r, zmid=5.0e-3):
    z = r["z"]
    cl = r["cleft"]
    dv = (r["v2_max"] - r["v2_rest"]) * 1e3
    imid = int(np.argmin(np.abs(z - zmid)))
    region = cl if cl.any() else np.ones_like(cl)
    k = np.where(region)[0][np.argmax(dv[region])]
    out = dict(
        status=r["status"], t_end_ms=r["t_end"] * 1e3,
        v2_rest_mV=r["v2_rest"][imid] * 1e3,
        dv_mid_mV=dv[imid], dv_lesion_mV=dv[k], dv_lesion_z_mm=z[k] * 1e3,
        v2_peak_lesion_mV=r["v2_max"][k] * 1e3,
        hyp_lesion_mV=((r["v2_min"] - r["v2_rest"]) * 1e3)[region].min(),
        ue_max_mV=r["ue_max"].max() * 1e3, ue_min_mV=r["ue_min"].min() * 1e3,
        stim_nA=(r["stim_amp"] or 0.0) * 1e9,
        r_e=r["r_e"], A_e_um2=r["A_e"] * 1e12,
    )
    out.update(c_spike_info(r))
    out.update(abeta_info(r))
    return out
