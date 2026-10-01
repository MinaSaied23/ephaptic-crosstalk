"""
run_convergence_battery.py

Spatial and temporal refinement studies (Sec. 2.4.1, 2.4.2; Table 5; Fig. 4).

For every grid the following are computed with the production IMEX scheme and
the fixed-node geometry (physical node length l_node held constant, so the
nodal membrane area does not change with dz):

  * isolated Abeta fiber, 2 nA / 0.2 ms stimulus at node 0
    (conduction velocity from the time of maximum upstroke dV/dt between
    z = 4 mm and z = 8 mm; peak and excursion at z = 4 mm and z = 8 mm);
  * the same fiber with the nodal sodium conductance removed;
  * coupled Abeta / C-fiber pair, n = 1 and n = 25 synchronized Abeta fibers,
    100 nA / 0.2 ms stimulus, cleft width w_cleft (default 20 nm, as in the
    manuscript), kappa = 1e9 m^-2.

Outputs (written to --out-dir, default results/convergence/):
    spatial_convergence.csv
    temporal_convergence_final.csv

Usage:
    python src/run_convergence_battery.py                 # manuscript settings
    python src/run_convergence_battery.py --w-cleft-nm 50 # other cleft width
    python src/run_convergence_battery.py --verify        # 3-second regression check, writes no files
"""

import argparse
import csv
import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC)
_P1 = os.path.join(_SRC, "phase1_classical_hh")
if _P1 not in sys.path:
    sys.path.insert(0, _P1)

import numpy as np                      # noqa: E402
from scipy.linalg import solve_banded   # noqa: E402

from ephaptic_model import *            # noqa: E402,F401,F403
from validate_single_fibers import build_implicit_operator  # noqa: E402
from coupled_model import build_poisson_operator, laplacian_neumann  # noqa: E402
from spike_detector import build_fixed_node_geometry, classify_waveform  # noqa: E402

import time                             # noqa: E402


def run_abeta_sim(dz_val, dt_val, T_val=6e-3, stim_amp=2e-9, stim_dur=0.2e-3, disable_na=False):
    N_val, z_val, node_mask_val, f_node_val = build_fixed_node_geometry(dz=dz_val)

    Cm_node_comp_val = (2.0 * f_node_val + 0.005 * (1.0 - f_node_val)) * uF_cm2_to_F_m2
    Cm_arr_val = np.where(node_mask_val, Cm_node_comp_val, Cm_internode)

    g_Na_val = (0.0 if disable_na else 1445.0) * f_node_val * mS_cm2_to_S_m2
    g_leak_node_val = (128.0 * f_node_val + 0.006 * (1.0 - f_node_val)) * mS_cm2_to_S_m2
    g_leak_arr_val = np.where(node_mask_val, g_leak_node_val, g_leak_internode)

    axial_coeff = d1_axon / (4.0 * rho_i)
    A_banded = build_implicit_operator(axial_coeff, dt_val, Cm_arr_val, dz_val, N_val)

    v = np.full(N_val, -80e-3)
    am, bm, ah, bh = crrss_rates(-80e-3)
    m = np.full(N_val, am / (am + bm))
    h = np.full(N_val, ah / (ah + bh))

    nsteps = int(round(T_val / dt_val))
    v_rec = np.zeros((nsteps, N_val))

    t0 = time.time()
    for step in range(nsteps):
        t_curr = step * dt_val
        am, bm, ah, bh = crrss_rates(v)
        tau_m = 1.0 / (am + bm); m_inf = am * tau_m
        tau_h = 1.0 / (ah + bh); h_inf = ah * tau_h
        m = np.where(node_mask_val, m_inf + (m - m_inf) * np.exp(-dt_val / tau_m), m)
        h = np.where(node_mask_val, h_inf + (h - h_inf) * np.exp(-dt_val / tau_h), h)

        I_active = g_Na_val * m**2 * h * (v - E_Na) + g_leak_arr_val * (v - E_leak_1)
        I_passive = g_leak_arr_val * (v - E_leak_1)
        I_ion = np.where(node_mask_val, I_active, I_passive)

        I_stim = np.zeros(N_val)
        if t_curr < stim_dur:
            I_stim[0] = stim_amp / (np.pi * d1_axon * dz_val)

        rhs = Cm_arr_val / dt_val * v + (I_stim - I_ion)
        v = solve_banded((1, 1), A_banded, rhs)
        v_rec[step] = v

    elapsed = time.time() - t0
    res_detect = classify_waveform(v_rec, z_val, dt_val, fiber_type="abeta")

    # Waveform values at the exact physical coordinates 4.0 mm and 8.0 mm
    idx_4mm = np.argmin(np.abs(z_val - 4.0e-3))
    idx_8mm = np.argmin(np.abs(z_val - 8.0e-3))

    pk_4mm = np.max(v_rec[:, idx_4mm]) * 1e3
    amp_4mm = pk_4mm - (-80.0)
    pk_8mm = np.max(v_rec[:, idx_8mm]) * 1e3
    amp_8mm = pk_8mm - (-80.0)

    dvdt_4mm = np.max(np.diff(v_rec[:, idx_4mm])) / (dt_val * 1e3)
    dvdt_8mm = np.max(np.diff(v_rec[:, idx_8mm])) / (dt_val * 1e3)

    t_pk_4mm = np.argmax(v_rec[:, idx_4mm]) * dt_val * 1e3
    t_pk_8mm = np.argmax(v_rec[:, idx_8mm]) * dt_val * 1e3

    # CV via maximum dV/dt between 4 mm and 8 mm
    t_dv_4 = np.argmax(np.diff(v_rec[:, idx_4mm])) * dt_val
    t_dv_8 = np.argmax(np.diff(v_rec[:, idx_8mm])) * dt_val
    cv_clean = (z_val[idx_8mm] - z_val[idx_4mm]) / (t_dv_8 - t_dv_4) if t_dv_8 > t_dv_4 else None

    return {
        "classification": res_detect["classification"],
        "spiked": res_detect["spiked"],
        "pk_4mm": pk_4mm,
        "amp_4mm": amp_4mm,
        "dvdt_4mm": dvdt_4mm,
        "t_pk_4mm": t_pk_4mm,
        "pk_8mm": pk_8mm,
        "amp_8mm": amp_8mm,
        "dvdt_8mm": dvdt_8mm,
        "t_pk_8mm": t_pk_8mm,
        "cv_clean": cv_clean,
        "elapsed": elapsed,
    }


def run_coupled_sim(dz_val, dt_val, n_abeta=1, w_cleft=20e-9, kappa=1e9, T_val=4e-3,
                    stim_amp=100e-9, stim_dur=0.2e-3):
    N_val, z_val, node_mask_val, f_node_val = build_fixed_node_geometry(dz=dz_val)

    r_e = r_e_from_cleft(w_cleft)
    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)

    Cm_node_comp_val = (2.0 * f_node_val + 0.005 * (1.0 - f_node_val)) * uF_cm2_to_F_m2
    Cm_arr_val = np.where(node_mask_val, Cm_node_comp_val, Cm_internode)

    g_Na_val = 1445.0 * f_node_val * mS_cm2_to_S_m2
    g_leak_node_val = (128.0 * f_node_val + 0.006 * (1.0 - f_node_val)) * mS_cm2_to_S_m2
    g_leak_arr_val = np.where(node_mask_val, g_leak_node_val, g_leak_internode)

    A1 = build_implicit_operator(axial1, dt_val, Cm_arr_val, dz_val, N_val)
    A2 = build_implicit_operator(axial2, dt_val, Cm, dz_val, N_val)

    # Multi-fiber symmetry scaling: n_abeta representative synchronous fibers
    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e
    sum_inv_r = inv_re + n_abeta * inv_r1 + inv_r2
    kappa_eff = (kappa / r_e) / sum_inv_r
    A_poisson_eff = build_poisson_operator(dz_val, N_val, kappa=kappa_eff)

    v1 = np.full(N_val, -80e-3)
    am1, bm1, ah1, bh1 = crrss_rates(-80e-3)
    m1 = np.full(N_val, am1 / (am1 + bm1))
    h1 = np.full(N_val, ah1 / (ah1 + bh1))

    v2 = np.full(N_val, -65e-3)
    m2 = np.full(N_val, 0.05); h2 = np.full(N_val, 0.6); n2 = np.full(N_val, 0.32)

    nsteps = int(round(T_val / dt_val))
    v2_rec = np.zeros((nsteps, N_val))

    t0 = time.time()
    for step in range(nsteps):
        t_now = step * dt_val

        am1, bm1, ah1, bh1 = crrss_rates(v1)
        tau_m1 = 1.0 / (am1 + bm1); m1_inf = am1 * tau_m1
        tau_h1 = 1.0 / (ah1 + bh1); h1_inf = ah1 * tau_h1
        m1 = np.where(node_mask_val, m1_inf + (m1 - m1_inf) * np.exp(-dt_val / tau_m1), m1)
        h1 = np.where(node_mask_val, h1_inf + (h1 - h1_inf) * np.exp(-dt_val / tau_h1), h1)
        I_active1 = g_Na_val * m1**2 * h1 * (v1 - E_Na) + g_leak_arr_val * (v1 - E_leak_1)
        I_passive1 = g_leak_arr_val * (v1 - E_leak_1)
        I_ion1 = np.where(node_mask_val, I_active1, I_passive1)

        am2, bm2, ah2, bh2, an2, bn2 = hh_rates(v2)
        m2 = np.clip(m2 + dt_val*(am2*(1-m2) - bm2*m2), 0, 1)
        h2 = np.clip(h2 + dt_val*(ah2*(1-h2) - bh2*h2), 0, 1)
        n2 = np.clip(n2 + dt_val*(an2*(1-n2) - bn2*n2), 0, 1)
        I_ion2 = (g_Na_HH * m2**3 * h2 * (v2 - E_Na)
                  + g_K_HH * n2**4 * (v2 - E_K)
                  + g_leak_HH * (v2 - E_leak_2))

        I_stim1 = np.zeros(N_val)
        if t_now < stim_dur:
            I_stim1[0] = stim_amp / (np.pi * d1_axon * dz_val)

        d2v1 = laplacian_neumann(v1, dz_val)
        d2v2 = laplacian_neumann(v2, dz_val)

        B = - (n_abeta * inv_r1 * d2v1 + inv_r2 * d2v2) / sum_inv_r
        u_e = solve_banded((1, 1), A_poisson_eff, B)
        d2ue = laplacian_neumann(u_e, dz_val)

        I_eph1 = axial1 * d2ue
        I_eph2 = axial2 * d2ue

        rhs1 = Cm_arr_val / dt_val * v1 + (I_stim1 - I_ion1 + I_eph1)
        v1 = solve_banded((1, 1), A1, rhs1)

        rhs2 = Cm / dt_val * v2 + (- I_ion2 + I_eph2)
        v2 = solve_banded((1, 1), A2, rhs2)
        v2_rec[step] = v2

    elapsed = time.time() - t0
    res_detect = classify_waveform(v2_rec, z_val, dt_val, fiber_type="c_fiber")

    # Downstream C-fiber metrics (3 mm to 8 mm)
    idx_down = np.where((z_val >= 3.0e-3 - 1e-9) & (z_val <= 8.0e-3 + 1e-9))[0]
    v2_down = v2_rec[:, idx_down] * 1e3  # mV
    v2_max = np.max(v2_down)
    v2_base = np.mean(v2_down[0, :])
    delta_v2 = v2_max - v2_base

    # Spatial location and time of the peak ephaptic perturbation
    max_step, max_col = np.unravel_index(np.argmax(v2_down), v2_down.shape)
    z_max_peak_mm = z_val[idx_down[max_col]] * 1e3
    t_max_peak_ms = max_step * dt_val * 1e3

    return {
        "classification": res_detect["classification"],
        "spiked": res_detect["spiked"],
        "c_base": v2_base,
        "c_peak": v2_max,
        "ephaptic_delta_v": delta_v2,
        "t_peak_ms": t_max_peak_ms,
        "z_peak_mm": z_max_peak_mm,
        "elapsed": elapsed,
    }


def _micro(x):
    """x micro-units -> SI as a decimal literal (e.g. 2.5 -> 2.5e-6 exactly as typed).

    Multiplying by 1e-6 can produce 2.4999999999999998e-06, which changes the number of
    time steps for which the 0.2 ms stimulus is on (step*dt < stim_dur) by one.
    """
    return float(f"{x!r}e-6")


def _write_csv(path, rows):
    cols = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            w.writerow([("" if (isinstance(r[c], float) and np.isnan(r[c])) else r[c]) for c in cols])


def _status(rel):
    """Stability label for a successive relative change (fraction)."""
    if rel < 0.01:
        return "CONVERGED <1%"
    if rel <= 0.02:
        return "PRACTICALLY STABLE 1-2%"
    return "CHANGING >2%"


def spatial_battery(dz_um_list, dt_us, w_cleft, out_dir):
    print(f"Spatial battery: dz in {dz_um_list} um at dt = {dt_us} us, w_cleft = {w_cleft*1e9:.0f} nm")
    rows = []
    for dz_um in dz_um_list:
        dz_i = _micro(dz_um)
        dt_i = _micro(dt_us)
        print(f"\n--- dz = {dz_um:.2f} um ---", flush=True)
        a = run_abeta_sim(dz_i, dt_i, stim_amp=2e-9, disable_na=False)
        print(f"  Abeta (2 nA): CV = {a['cv_clean']:.2f} m/s | 4 mm amp = {a['amp_4mm']:.3f} mV | 8 mm amp = {a['amp_8mm']:.3f} mV | {a['classification']}", flush=True)
        na = run_abeta_sim(dz_i, dt_i, stim_amp=2e-9, disable_na=True)
        print(f"  Sodium-off  : 4 mm amp = {na['amp_4mm']:.3f} mV | {na['classification']}", flush=True)
        c1 = run_coupled_sim(dz_i, dt_i, n_abeta=1, w_cleft=w_cleft)
        print(f"  Coupled n=1 : dV = {c1['ephaptic_delta_v']:.3f} mV at z = {c1['z_peak_mm']:.1f} mm | {c1['classification']}", flush=True)
        c25 = run_coupled_sim(dz_i, dt_i, n_abeta=25, w_cleft=w_cleft)
        print(f"  Coupled n=25: dV = {c25['ephaptic_delta_v']:.3f} mV at z = {c25['z_peak_mm']:.1f} mm | {c25['classification']}", flush=True)
        rows.append({
            "dz_um": dz_um, "dt_us": dt_us, "w_cleft_nm": w_cleft * 1e9,
            "abeta_cv_mps": a["cv_clean"],
            "abeta_pk_4mm_mV": a["pk_4mm"], "abeta_amp_4mm_mV": a["amp_4mm"],
            "abeta_dvdt_4mm_Vps": a["dvdt_4mm"], "abeta_t_pk_4mm_ms": a["t_pk_4mm"],
            "abeta_pk_8mm_mV": a["pk_8mm"], "abeta_amp_8mm_mV": a["amp_8mm"],
            "abeta_classification": a["classification"],
            "nona_amp_4mm_mV": na["amp_4mm"], "nona_amp_8mm_mV": na["amp_8mm"],
            "nona_classification": na["classification"],
            "c1_delta_v_mV": c1["ephaptic_delta_v"], "c1_peak_z_mm": c1["z_peak_mm"],
            "c1_classification": c1["classification"],
            "c25_delta_v_mV": c25["ephaptic_delta_v"], "c25_peak_z_mm": c25["z_peak_mm"],
            "c25_classification": c25["classification"],
            "runtime_s": a["elapsed"] + na["elapsed"] + c1["elapsed"] + c25["elapsed"],
        })
    _write_csv(os.path.join(out_dir, "spatial_convergence.csv"), rows)
    print(f"\nSaved {os.path.join(out_dir, 'spatial_convergence.csv')}")


def temporal_battery(dt_us_list, dz_um, w_cleft, out_dir):
    print(f"\nTemporal battery: dt in {dt_us_list} us at dz = {dz_um} um, w_cleft = {w_cleft*1e9:.0f} nm")
    raw = []
    for dt_us in dt_us_list:
        dt_i = _micro(dt_us)
        dz_i = _micro(dz_um)
        print(f"\n--- dt = {dt_us:.3f} us ---", flush=True)
        a = run_abeta_sim(dz_i, dt_i, stim_amp=2e-9, disable_na=False)
        print(f"  Abeta (2 nA): CV = {a['cv_clean']:.2f} m/s | 4 mm amp = {a['amp_4mm']:.3f} mV | {a['classification']}", flush=True)
        c1 = run_coupled_sim(dz_i, dt_i, n_abeta=1, w_cleft=w_cleft)
        print(f"  Coupled n=1 : dV = {c1['ephaptic_delta_v']:.3f} mV | {c1['classification']}", flush=True)
        c25 = run_coupled_sim(dz_i, dt_i, n_abeta=25, w_cleft=w_cleft)
        print(f"  Coupled n=25: dV = {c25['ephaptic_delta_v']:.3f} mV | {c25['classification']}", flush=True)
        raw.append((dt_us, a, c1, c25))

    rows = []
    for i, (dt_us, a, c1, c25) in enumerate(raw):
        row = {"dt_us": dt_us, "w_cleft_nm": w_cleft * 1e9}
        series = [
            ("cv", "abeta_cv_mps", a["cv_clean"]),
            ("amp", "abeta_amp_4mm_mV", a["amp_4mm"]),
            ("t_pk", "abeta_t_pk_4mm_ms", a["t_pk_4mm"]),
            ("c1", "c1_delta_v_mV", c1["ephaptic_delta_v"]),
            ("c25", "c25_delta_v_mV", c25["ephaptic_delta_v"]),
        ]
        for key, col, val in series:
            row[col] = val
            if i == 0:
                row[f"rel_change_{key}"] = float("nan")
                row[f"class_{key}"] = "BASELINE"
            else:
                prev = {"cv": raw[i-1][1]["cv_clean"], "amp": raw[i-1][1]["amp_4mm"],
                        "t_pk": raw[i-1][1]["t_pk_4mm"], "c1": raw[i-1][2]["ephaptic_delta_v"],
                        "c25": raw[i-1][3]["ephaptic_delta_v"]}[key]
                rel = abs(val - prev) / abs(val)   # change relative to the finer-step value
                row[f"rel_change_{key}"] = rel
                row[f"class_{key}"] = _status(rel)
        row["c25_classification"] = c25["classification"]
        row["c25_spiked"] = bool(c25["spiked"])
        stable = all(r[3]["classification"] == raw[0][3]["classification"] and not r[3]["spiked"] for r in raw)
        row["class_spike_status"] = "CLASSIFICATION STABLE" if stable else "CLASSIFICATION CHANGES"
        rows.append(row)

    # column order identical to the previous temporal_convergence_final.csv (w_cleft_nm inserted after dt_us)
    order = ["dt_us", "w_cleft_nm", "abeta_cv_mps", "rel_change_cv", "class_cv",
             "abeta_amp_4mm_mV", "rel_change_amp", "class_amp",
             "abeta_t_pk_4mm_ms", "rel_change_t_pk", "class_t_pk",
             "c1_delta_v_mV", "rel_change_c1", "class_c1",
             "c25_delta_v_mV", "rel_change_c25", "class_c25",
             "c25_classification", "c25_spiked", "class_spike_status"]
    rows = [{k: r[k] for k in order} for r in rows]
    _write_csv(os.path.join(out_dir, "temporal_convergence_final.csv"), rows)
    print(f"\nSaved {os.path.join(out_dir, 'temporal_convergence_final.csv')}")


def verify():
    """Regression check of the nominal grid (dz = 10 um, dt = 2.5 us, w_cleft = 20 nm)
    against the values printed in the manuscript (Table 5, Sec. 3.1). Writes no files."""
    dz, dt, w = 10e-6, 2.5e-6, 20e-9
    a = run_abeta_sim(dz, dt, stim_amp=2e-9)
    c1 = run_coupled_sim(dz, dt, n_abeta=1, w_cleft=w)
    c25 = run_coupled_sim(dz, dt, n_abeta=25, w_cleft=w)
    checks = [
        ("Abeta conduction velocity (m/s)", a["cv_clean"], 41.03, 0.01),
        ("Abeta excursion at z = 4 mm (mV)", a["amp_4mm"], 80.44, 0.01),
        ("Coupled n = 1 dV (mV)", c1["ephaptic_delta_v"], 1.325, 0.002),
        ("Coupled n = 25 dV (mV)", c25["ephaptic_delta_v"], 6.015, 0.005),
    ]
    ok = True
    for label, got, ref, tol in checks:
        good = abs(got - ref) <= tol
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}: {got:.4f} (manuscript {ref}, tol {tol})")
    for tag, r in (("n = 1", c1), ("n = 25", c25)):
        good = r["classification"] == "LOCAL_STIMULUS_TRANSIENT" and not r["spiked"]
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {tag} classification: {r['classification']}")
    print("ALL CHECKS PASSED" if ok else "CHECKS FAILED")
    return ok


def _floats(s):
    return [float(x) for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--w-cleft-nm", type=float, default=20.0, help="cleft width for coupled runs (default 20 nm)")
    ap.add_argument("--spatial-dz-um", type=_floats, default=_floats("20,10,5,2.5,1.25,1.0"))
    ap.add_argument("--spatial-dt-us", type=float, default=2.5)
    ap.add_argument("--temporal-dt-us", type=_floats, default=_floats("5,2.5,1.25,0.625,0.5,0.25,0.125"))
    ap.add_argument("--temporal-dz-um", type=float, default=10.0)
    ap.add_argument("--out-dir", default=os.path.join(_ROOT, "results", "convergence"))
    ap.add_argument("--skip-spatial", action="store_true")
    ap.add_argument("--skip-temporal", action="store_true")
    ap.add_argument("--verify", action="store_true", help="fast regression check against the manuscript values")
    args = ap.parse_args()

    if args.verify:
        sys.exit(0 if verify() else 1)

    os.makedirs(args.out_dir, exist_ok=True)
    w = float(f"{args.w_cleft_nm!r}e-9")
    if not args.skip_spatial:
        spatial_battery(args.spatial_dz_um, args.spatial_dt_us, w, args.out_dir)
    if not args.skip_temporal:
        temporal_battery(args.temporal_dt_us, args.temporal_dz_um, w, args.out_dir)


if __name__ == "__main__":
    main()
