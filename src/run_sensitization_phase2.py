"""
run_sensitization_phase2.py

Phase 2 (Nav1.8/Nav1.9 C-fiber) tonic depolarizing bias protocol.

(1) Space-clamped analysis (uniform bias, quiet Abeta fiber => spatially uniform cable):
    stable equilibrium, its stability, Nav1.8 availability h8, and the long-time behaviour
    reached from the true unbiased rest (-66.82 mV) with the bias switched on at t = 0 (2 s).
(2) Onset of depolarization block (jump to the depolarized, Nav1.8-inactivated branch).
(3) Full coupled cable: Abeta-evoked response (w_cleft = 20 nm, 100 nA stimulus) on top of the
    biased baseline, for n = 1 and n = 25 fibers, with the C-fiber baseline relaxed for 150 ms
    (the production default of 20 ms is converged only for bias <= ~0.4 A/m^2 because the Nav1.9
    gate has tau = 10 ms).

Outputs (results/convergence/):
  sensitization_phase2_bias.csv
  sensitization_phase2_cable.csv
  sensitization_phase2_summary.md
"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, "phase2_nav18_nav19"))
import nav_kinetics as nk  # noqa: E402
from navc_cable import g_Na18, g_Na19, g_K_HH, g_leak_HH, E_leak_2, hh_k_rates  # noqa: E402
from ephaptic_model import Cm, E_Na, E_K  # noqa: E402
from coupled_navc_model import run_coupled_navc  # noqa: E402

OUT = os.path.join(base_dir, "..", "results", "convergence")
os.makedirs(OUT, exist_ok=True)


def rhs(t, y, b):
    v, m8, h8, m9, n = y
    m8i, tm8, h8i, th8, m9i, tm9 = [float(x) for x in nk.nav_c_fiber_rates(v)]
    an, bn = [float(x) for x in hh_k_rates(v)]
    I = (g_Na18 * m8**3 * h8 * (v - E_Na) + g_Na19 * m9 * (v - E_Na)
         + g_K_HH * n**4 * (v - E_K) + g_leak_HH * (v - E_leak_2))
    return [(b - I) / Cm, (m8i - m8) / tm8, (h8i - h8) / th8, (m9i - m9) / tm9, an * (1 - n) - bn * n]


def gates_ss(v):
    m8i, _, h8i, _, m9i, _ = [float(x) for x in nk.nav_c_fiber_rates(v)]
    an, bn = [float(x) for x in hh_k_rates(v)]
    return m8i, h8i, m9i, an / (an + bn)


def f_eq(v, b):
    m8, h8, m9, n = gates_ss(v)
    return b - (g_Na18 * m8**3 * h8 * (v - E_Na) + g_Na19 * m9 * (v - E_Na)
                + g_K_HH * n**4 * (v - E_K) + g_leak_HH * (v - E_leak_2))


def equilibria(b):
    vs = np.linspace(-0.09, 0.04, 5201)
    fv = np.array([f_eq(v, b) for v in vs])
    out = []
    for i in range(len(vs) - 1):
        if fv[i] * fv[i + 1] < 0:
            v = brentq(f_eq, vs[i], vs[i + 1], args=(b,), xtol=1e-13)
            if abs(v * 1e3 + 55.0) < 1e-3:   # removable singularity of alpha_n at -55 mV
                continue
            y = np.array([v, *gates_ss(v)])
            J = np.zeros((5, 5))
            for j in range(5):
                d = np.zeros(5)
                d[j] = 1e-6 * (1e-3 if j == 0 else 1.0)
                J[:, j] = (np.array(rhs(0, y + d, b)) - np.array(rhs(0, y - d, b))) / (2 * d[j])
            out.append((v * 1e3, float(np.max(np.linalg.eigvals(J).real)), float(y[2])))
    return out


def from_rest(b, T=2.0):
    v0 = equilibria(0.0)[0][0] * 1e-3
    sol = solve_ivp(rhs, (0, T), [v0, *gates_ss(v0)], args=(b,), method="LSODA",
                    rtol=1e-9, atol=1e-12, max_step=5e-4, dense_output=True)
    t, v = sol.t, sol.y[0] * 1e3
    late = v[t > 0.5 * T]
    n_sp = int(np.sum((late[1:] > 0) & (late[:-1] <= 0)))
    amp = float(late.max() - late.min())
    beh = "repetitive spiking" if n_sp > 0 else ("oscillation" if amp > 2.0 else "quiescent")
    return beh, float(v[-1]), float(sol.y[2][-1])


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join("" if (isinstance(x, float) and np.isnan(x)) else (f"{x:.6g}" if isinstance(x, float) else str(x)) for x in r) + "\n")


def main():
    biases = [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 3.2, 3.4, 4.0, 5.0, 10.0]
    rows = []
    print("Phase 2 tonic bias (space-clamped)")
    for b in biases:
        eqs = equilibria(b)
        beh, v_end, h_end = from_rest(b)
        stable = [e for e in eqs if e[1] < 0]
        low = stable[0]
        rows.append([b, low[0], low[2], len(stable), beh, v_end, h_end])
        print(f"  bias={b:5.2f}  lowest stable eq={low[0]:7.2f} mV (h8={low[2]:.3f}); stable equilibria={len(stable)}; from rest: {beh}, ends at {v_end:7.2f} mV (h8={h_end:.3f})")
    write_csv(os.path.join(OUT, "sensitization_phase2_bias.csv"),
              ["bias_A_per_m2", "lowest_stable_equilibrium_mV", "h8_at_equilibrium", "n_stable_equilibria",
               "behavior_from_rest", "end_state_mV", "end_state_h8"], rows)

    # onset of depolarization block (end state jumps to the Nav1.8-inactivated branch, h8 < 0.1)
    lo, hi = 3.0, 3.6
    for _ in range(10):
        mid = 0.5 * (lo + hi)
        if from_rest(mid, T=1.0)[2] < 0.1:
            hi = mid
        else:
            lo = mid
    block_onset = 0.5 * (lo + hi)
    print(f"  onset of depolarization block from rest: {block_onset:.3f} A/m2")

    rows = []
    print("Phase 2 cable: Abeta-evoked response on biased baseline (w_cleft = 20 nm, 100 nA, baseline relaxed 150 ms)")
    for b in [0.0, 0.25, 0.5, 1.0, 2.0]:
        v_eq = equilibria(b)[0][0]
        for nab in [1, 25]:
            r = run_coupled_navc(w_cleft=20e-9, T=10e-3, stim_amp=100e-9, stim_dur=0.2e-3, sens_bias=b,
                                 n_abeta=nab, record_full=True, settle_time=0.15)
            v2 = r["v2"] * 1e3
            mid = v2[:, v2.shape[1] // 2]
            n5 = int(5e-3 / 1e-6)
            dv_mid_5ms = float(mid[:n5].max() - mid[0])          # production 5 ms window
            sub = v2[int(1.5e-3 / 1e-6):, 30:]                      # z >= 0.3 mm, t > 1.5 ms
            fired = bool(sub.max() > 0.0)
            rows.append([b, nab, v2[0].mean(), v_eq, dv_mid_5ms, float(v2[:n5, 100:].max() - v2[0].mean()), fired, float(sub.max())])
            print(f"  bias={b:4.2f} n={nab:2d}: baseline={v2[0].mean():8.3f} mV (exact {v_eq:8.3f})  dV_mid(5 ms)={dv_mid_5ms:6.3f} mV  spike within 10 ms={fired}")
    write_csv(os.path.join(OUT, "sensitization_phase2_cable.csv"),
              ["bias_A_per_m2", "n_abeta", "baseline_mV", "exact_equilibrium_mV", "dV_mid_5ms_mV",
               "dV_downstream_max_5ms_mV", "C_fiber_spike_within_10ms", "max_V_z_ge_0p3mm_t_gt_1p5ms_mV"], rows)

    with open(os.path.join(OUT, "sensitization_phase2_summary.md"), "w", encoding="utf-8") as f:
        f.write("# Phase 2 tonic bias protocol (generated by run_sensitization_phase2.py)\n\n")
        f.write(f"- Onset of depolarization block (jump to Nav1.8-inactivated branch, h8 < 0.1) from rest: {block_onset:.3f} A/m^2\n")
        f.write("- Below this the fiber stays on a stable quiescent branch; see sensitization_phase2_bias.csv\n")
    print("done")


if __name__ == "__main__":
    main()
