"""
run_boundary_spike_threshold.py

Boundary-initiated C-fiber spike in the UNGROUNDED full-length model, as a function of the number
n of synchronous Abeta fibers, for both phases, plus the GROUNDED interior-lesion control at high n.

Why this exists
---------------
The 100 nA stimulus is injected into node 0 of n Abeta fibers at the sealed boundary z = 0. The
resulting extracellular transient drives the C-fiber at z = 0 to several hundred mV, which can
launch a slow, regenerative C-fiber action potential at the boundary within ~1-3 ms. That spike
then conducts at the C-fiber velocity (0.26-0.41 m/s) and reaches the measurement window
(z >= 3 mm) only after >= 10 ms, i.e. after the 3-5 ms windows used by the n-sweeps. This script
quantifies when it appears (threshold n*) and verifies that the physiologically meaningful
control (stimulation site grounded in bulk fluid, cleft restriction confined to an interior
lesion) never fires, up to n = 200.

Spike criterion: C-fiber voltage > 0 mV anywhere with z >= 0.3 mm at t > 1.5 ms
(excludes the direct, non-regenerative field transient at the electrode).

Usage: python run_boundary_spike_threshold.py [phase1|phase2|lesion]   (default: all, as subprocesses)
Outputs (results/convergence/): boundary_spike_phase1.csv, boundary_spike_phase2.csv, lesion_control_high_n.csv
"""
import os
import subprocess
import sys

import numpy as np

base_dir = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(base_dir, "..", "results", "convergence")
os.makedirs(OUT, exist_ok=True)


def _spike_any(v2_mV, dt):
    return float(v2_mV[int(1.5e-3 / dt):, 30:].max())


def phase1():
    sys.path.insert(0, os.path.join(base_dir, "phase1_classical_hh"))
    from coupled_model import run_coupled
    dt = 2.5e-6

    def peak(n):
        r = run_coupled(w_cleft=20e-9, T=15e-3, stim_amp=100e-9, stim_dur=0.2e-3, n_abeta=n, record_full=True)
        return _spike_any(r["v2"] * 1e3, dt)
    rows = []
    for n in [1, 2, 3, 4, 5, 10, 25]:
        p = peak(float(n))
        rows.append(["phase1", float(n), p, p > 0])
        print(f"phase1 n={n}: peak {p:.2f} mV spike={p > 0}", flush=True)
    lo, hi = 1.0, 5.0
    for _ in range(6):
        mid = 0.5 * (lo + hi)
        if peak(mid) > 0:
            hi = mid
        else:
            lo = mid
    print(f"phase1 threshold n* in ({lo:.3f}, {hi:.3f}]")
    rows.append(["phase1_threshold_bracket_low", lo, float("nan"), False])
    rows.append(["phase1_threshold_bracket_high", hi, float("nan"), True])
    return rows


def phase2():
    sys.path.insert(0, os.path.join(base_dir, "phase2_nav18_nav19"))
    from coupled_navc_model import run_coupled_navc
    dt = 1e-6

    def peak(n):
        r = run_coupled_navc(w_cleft=20e-9, T=10e-3, stim_amp=100e-9, stim_dur=0.2e-3, n_abeta=n, record_full=True)
        return _spike_any(r["v2"] * 1e3, dt)
    rows = []
    for n in [1, 5, 10, 20, 25, 28, 30, 40, 50]:
        p = peak(float(n))
        rows.append(["phase2", float(n), p, p > 0])
        print(f"phase2 n={n}: peak {p:.2f} mV spike={p > 0}", flush=True)
    lo, hi = 28.0, 30.0
    for _ in range(6):
        mid = 0.5 * (lo + hi)
        if peak(mid) > 0:
            hi = mid
        else:
            lo = mid
    print(f"phase2 threshold n* in ({lo:.3f}, {hi:.3f}]")
    rows.append(["phase2_threshold_bracket_low", lo, float("nan"), False])
    rows.append(["phase2_threshold_bracket_high", hi, float("nan"), True])
    return rows


def lesion():
    sys.path.insert(0, base_dir)
    sys.path.insert(0, os.path.join(base_dir, "phase2_nav18_nav19"))
    from interior_lesion_test import run_interior_lesion_phase2
    rows = []
    for n in [25, 50, 100, 200]:
        r = run_interior_lesion_phase2(w_cleft=20e-9, T=12e-3, n_abeta=float(n), lesion_z_start=3e-3,
                                       lesion_z_end=7e-3, ground_z=2e-3, dt=1e-6)
        v2 = r["v2"] * 1e3
        rows.append([n, float(v2[:, :200].max()), float(v2[:, 300:700].max()), float(v2[:, 700:].max()), bool((v2[:, 300:700] > 0).any())])
        print(f"lesion phase2 n={n}: stim zone {rows[-1][1]:.2f}, lesion {rows[-1][2]:.2f}, distal {rows[-1][3]:.2f} mV, spiked={rows[-1][4]}", flush=True)
    return rows


def _write(path, header, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join("" if (isinstance(x, float) and np.isnan(x)) else (f"{x:.6g}" if isinstance(x, float) else str(x)) for x in r) + "\n")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "all":
        for w in ("phase1", "phase2", "lesion"):
            subprocess.run([sys.executable, os.path.abspath(__file__), w], check=True)
    elif which in ("phase1", "phase2"):
        rows = phase1() if which == "phase1" else phase2()
        _write(os.path.join(OUT, f"boundary_spike_{which}.csv"),
               ["case", "n_abeta", "max_C_fiber_V_mV_z_ge_0p3mm_t_gt_1p5ms", "spike"], rows)
    else:
        rows = lesion()
        _write(os.path.join(OUT, "lesion_control_high_n.csv"),
               ["n_abeta", "peak_stim_zone_0_2mm_mV", "peak_lesion_3_7mm_mV", "peak_distal_mV", "spiked_in_lesion"], rows)
