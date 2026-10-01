"""
run_sensitization_phase1.py

Phase 1 (classical Hodgkin-Huxley C-fiber) sensitization protocols:
  (A) persistent depolarizing bias current,
  (B) uniform shift of all HH rate functions (Sec. 2.8).

Method
------
With a uniform bias (or shift) and a quiescent Abeta fiber the C-fiber cable is spatially
uniform, so its dynamics equal those of a single compartment (Neumann ends). We therefore
analyse the space-clamped membrane equations exactly (LSODA, tight tolerances) using the
SAME rate functions and conductances as the production model (ephaptic_model.hh_rates etc.),
and cross-check selected points against the full coupled cable (coupled_model.run_coupled).

Protocol details (these differ from the legacy sensitization_bias_sweep.py, which was removed):
  * the C-fiber starts at its TRUE resting equilibrium (-65.13 mV with equilibrium gates);
  * the bias (or shift) is switched on at t = 0 and the membrane is followed for 1 s;
  * "repetitive spiking" = upward 0 mV crossings in the last 0.5 s;
    "oscillation" = last-0.5 s peak-to-peak > 2 mV without 0 mV crossings;
  * equilibria are located by root finding and classified by the largest real part of the
    Jacobian eigenvalues (removable rate-function singularities are excluded).

Outputs (results/convergence/):
  sensitization_phase1_bias.csv
  sensitization_phase1_kinetics_shift.csv
  sensitization_phase1_cable_check.csv
  sensitization_phase1_summary.md
"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, "phase1_classical_hh"))
import ephaptic_model as em  # noqa: E402
import coupled_model as cm  # noqa: E402

OUT = os.path.join(base_dir, "..", "results", "convergence")
os.makedirs(OUT, exist_ok=True)

Cm, gNa, gK, gL = em.Cm, em.g_Na_HH, em.g_K_HH, em.g_leak_HH
ENa, EK, EL = em.E_Na, em.E_K, em.E_leak_2


def rates(v, shift_mV):
    return [float(x) for x in em.hh_rates(v + shift_mV * 1e-3)]


def rhs(t, y, bias, shift_mV):
    v, m, h, n = y
    am, bm, ah, bh, an, bn = rates(v, shift_mV)
    I = gNa * m**3 * h * (v - ENa) + gK * n**4 * (v - EK) + gL * (v - EL)
    return [(bias - I) / Cm, am * (1 - m) - bm * m, ah * (1 - h) - bh * h, an * (1 - n) - bn * n]


def gates_ss(v, shift_mV):
    am, bm, ah, bh, an, bn = rates(v, shift_mV)
    return am / (am + bm), ah / (ah + bh), an / (an + bn)


def equilibria(bias, shift_mV):
    """All genuine equilibria (V in mV, max Re(eig)). Removable singularities of alpha_m
    (v + shift = -40 mV) and alpha_n (v + shift = -55 mV) are excluded."""
    def f(v):
        m, h, n = gates_ss(v, shift_mV)
        return bias - (gNa * m**3 * h * (v - ENa) + gK * n**4 * (v - EK) + gL * (v - EL))
    vs = np.linspace(-0.095, 0.08, 3501)
    fv = np.array([f(v) for v in vs])
    out = []
    for i in range(len(vs) - 1):
        if fv[i] * fv[i + 1] < 0:
            v = brentq(f, vs[i], vs[i + 1], xtol=1e-13)
            vmV = v * 1e3
            if abs(vmV + shift_mV + 55.0) < 1e-3 or abs(vmV + shift_mV + 40.0) < 1e-3:
                continue
            y = np.array([v, *gates_ss(v, shift_mV)])
            J = np.zeros((4, 4))
            for j in range(4):
                d = np.zeros(4)
                d[j] = 1e-6 * (1e-3 if j == 0 else 1.0)
                J[:, j] = (np.array(rhs(0, y + d, bias, shift_mV)) - np.array(rhs(0, y - d, bias, shift_mV))) / (2 * d[j])
            out.append((vmV, float(np.max(np.linalg.eigvals(J).real))))
    return out


def rest_state():
    v0 = equilibria(0.0, 0.0)[0][0] * 1e-3
    return v0, gates_ss(v0, 0.0)


def simulate(bias, shift_mV=0.0, T=1.0, y0=None):
    if y0 is None:
        v0, g = rest_state()
        y0 = [v0, *g]
    sol = solve_ivp(rhs, (0, T), y0, args=(bias, shift_mV), method="LSODA",
                    rtol=1e-9, atol=1e-12, max_step=5e-4, dense_output=True)
    t, v = sol.t, sol.y[0] * 1e3
    late = v[t > 0.5 * T]
    n_sp = int(np.sum((late[1:] > 0) & (late[:-1] <= 0)))
    amp = float(late.max() - late.min())
    cross = np.where((v[1:] > 0) & (v[:-1] <= 0))[0]
    if n_sp > 0:
        beh = "repetitive spiking"
    elif amp > 2.0:
        beh = "large oscillation (below 0 mV)"
    else:
        beh = "quiescent"
    return dict(behavior=beh, rate_Hz=n_sp / (0.5 * T), late_min_mV=float(late.min()),
                late_max_mV=float(late.max()), late_mean_mV=float(late.mean()),
                first_spike_ms=float(t[cross[0]] * 1e3) if len(cross) else float("nan"))


def bisect_onset(fn, lo, hi, iters=12):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if fn(mid):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join("" if (isinstance(x, float) and np.isnan(x)) else (f"{x:.6g}" if isinstance(x, float) else str(x)) for x in r) + "\n")


def main():
    # ---------------- (A) tonic bias ----------------
    biases = [0, 0.02, 0.05, 0.08, 0.10, 0.105, 0.11, 0.12, 0.14, 0.16, 0.20, 0.25, 0.30, 0.40, 0.50,
              0.60, 0.80, 1.0, 1.2, 1.3, 1.4, 1.5, 2.0, 3.0, 5.0, 10.0]
    rows = []
    print("Phase 1 tonic bias (space-clamped, 1 s from true rest)")
    for b in biases:
        eqs = equilibria(b, 0.0)
        stable = [e for e in eqs if e[1] < 0]
        s = simulate(b)
        v_eq = stable[0][0] if stable else float("nan")
        rows.append([b, v_eq, len(stable) > 0, s["behavior"], s["rate_Hz"], s["late_min_mV"], s["late_max_mV"], s["first_spike_ms"]])
        print(f"  bias={b:5.3f} A/m2  stable eq={v_eq:8.2f} mV  {s['behavior']:32s} {s['rate_Hz']:5.1f} Hz  [{s['late_min_mV']:.1f}, {s['late_max_mV']:.1f}]")
    write_csv(os.path.join(OUT, "sensitization_phase1_bias.csv"),
              ["bias_A_per_m2", "stable_equilibrium_mV", "stable_equilibrium_exists", "behavior_from_rest",
               "firing_rate_Hz", "late_min_mV", "late_max_mV", "first_0mV_crossing_ms"], rows)

    onset_spiking = bisect_onset(lambda b: simulate(b)["behavior"] == "repetitive spiking", 0.10, 0.12)
    onset_osc_end = bisect_onset(lambda b: simulate(b)["behavior"] == "quiescent", 1.2, 1.4)
    print(f"  onset of repetitive spiking from rest: {onset_spiking:.4f} A/m2")
    print(f"  upper edge of oscillatory regime (silent stable state beyond): {onset_osc_end:.3f} A/m2")

    # ---------------- (B) kinetics shift ----------------
    shifts = [-20, -10, -5, -3, 0, 1, 2, 3, 4, 5, 6, 8, 8.5, 8.6, 9, 10, 12, 15]
    rows = []
    print("Phase 1 uniform HH kinetics shift (alpha(v+dV), beta(v+dV); dV>0 = hyperpolarizing shift)")
    for sh in shifts:
        eqs = equilibria(0.0, sh)
        stable = [e for e in eqs if e[1] < 0]
        v_eq = stable[0][0] if stable else float("nan")
        y0 = None
        if stable:
            vv = v_eq * 1e-3
            y0 = [vv, *gates_ss(vv, sh)]
        else:
            vv = eqs[0][0] * 1e-3
            y0 = [vv + 5e-4, *gates_ss(vv, sh)]
        s = simulate(0.0, shift_mV=sh, y0=y0)
        rows.append([sh, v_eq, len(stable) > 0, s["behavior"], s["rate_Hz"], s["late_min_mV"], s["late_max_mV"]])
        print(f"  shift={sh:6.2f} mV  rest={v_eq:8.2f} mV  {s['behavior']:32s} {s['rate_Hz']:5.1f} Hz")
    write_csv(os.path.join(OUT, "sensitization_phase1_kinetics_shift.csv"),
              ["delta_V_shift_mV", "stable_rest_mV", "stable_rest_exists", "behavior", "firing_rate_Hz", "late_min_mV", "late_max_mV"], rows)

    def shift_spikes(sh):
        eqs = equilibria(0.0, sh)
        vv = eqs[0][0] * 1e-3
        y0 = [vv + (5e-4 if eqs[0][1] > 0 else 0.0), *gates_ss(vv, sh)]
        return simulate(0.0, shift_mV=sh, y0=y0)["behavior"] == "repetitive spiking"
    onset_shift = bisect_onset(shift_spikes, 8.0, 10.0, iters=10)
    print(f"  onset of spontaneous spiking: dV_shift = {onset_shift:.3f} mV")

    # ---------------- cable cross-check (Abeta stimulus, 100 nA, w_cleft = 20 nm) ----------------
    rows = []
    print("Cable cross-check (full coupled model)")
    v0, g0 = rest_state()
    orig_rates = cm.hh_rates
    try:
        # (i) Abeta-evoked response under bias (exact biased equilibrium as initial state)
        for b in [0.0, 0.05, 0.10]:
            ve = equilibria(b, 0.0)[0][0] * 1e-3
            init = (ve, *gates_ss(ve, 0.0))
            for nab in [1, 25]:
                r = cm.run_coupled(w_cleft=20e-9, T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3,
                                   sens_bias=b, n_abeta=nab, c_init=init)
                mid = r["v2_mid"] * 1e3
                rows.append(["bias", b, nab, ve * 1e3, float(mid.max() - ve * 1e3), r["classification"], bool(r["spiked"]), float(r["ephaptic_delta_v"])])
                print(f"  bias={b:4.2f} n={nab:2d}: rest={ve*1e3:7.3f} mV  dV_mid={mid.max()-ve*1e3:6.3f} mV  {r['classification']}")
        # (ii) Abeta-evoked response under kinetics shift
        for sh in [0.0, 3.0, 5.0, 8.0]:
            cm.hh_rates = (lambda v, sh=sh: em.hh_rates(v + sh * 1e-3))
            ve = equilibria(0.0, sh)[0][0] * 1e-3
            init = (ve, *gates_ss(ve, sh))
            for nab in [1, 25]:
                r = cm.run_coupled(w_cleft=20e-9, T=5e-3, stim_amp=100e-9, stim_dur=0.2e-3, n_abeta=nab, c_init=init)
                mid = r["v2_mid"] * 1e3
                rows.append(["shift", sh, nab, ve * 1e3, float(mid.max() - ve * 1e3), r["classification"], bool(r["spiked"]), float(r["ephaptic_delta_v"])])
                print(f"  shift={sh:4.1f} n={nab:2d}: rest={ve*1e3:7.3f} mV  dV_mid={mid.max()-ve*1e3:6.3f} mV  {r['classification']}")
        # (iii) spontaneous behaviour on the full cable (no Abeta input), 200 ms
        cm.hh_rates = orig_rates
        for b in [0.10, 0.12, 0.60, 1.0, 1.5]:
            r = cm.run_coupled(w_cleft=20e-9, T=0.2, stim_amp=0.0, sens_bias=b, c_init=(v0, *g0))
            v = r["v2_mid"] * 1e3
            late = v[len(v) // 2:]
            n_sp = int(np.sum((late[1:] > 0) & (late[:-1] <= 0)))
            rows.append(["bias_spontaneous", b, 0, float("nan"), float(late.max() - late.min()), "spikes_in_last_100ms=%d" % n_sp, n_sp > 0, float(late.max())])
            print(f"  cable, no Abeta input, bias={b:4.2f}: last-100ms range [{late.min():.1f}, {late.max():.1f}] mV, 0 mV crossings={n_sp}")
        cm.hh_rates = (lambda v: em.hh_rates(v + 10.0 * 1e-3))
        r = cm.run_coupled(w_cleft=20e-9, T=0.2, stim_amp=0.0, c_init=(v0, *g0))
        v = r["v2_mid"] * 1e3
        late = v[len(v) // 2:]
        n_sp = int(np.sum((late[1:] > 0) & (late[:-1] <= 0)))
        rows.append(["shift_spontaneous", 10.0, 0, float("nan"), float(late.max() - late.min()), "spikes_in_last_100ms=%d" % n_sp, n_sp > 0, float(late.max())])
        print(f"  cable, no Abeta input, shift=10 mV: last-100ms range [{late.min():.1f}, {late.max():.1f}] mV, 0 mV crossings={n_sp}")
    finally:
        cm.hh_rates = orig_rates
    write_csv(os.path.join(OUT, "sensitization_phase1_cable_check.csv"),
              ["protocol", "value", "n_abeta", "initial_rest_mV", "dV_or_range_mV", "classification", "spiked", "detector_dV_or_max_mV"], rows)

    with open(os.path.join(OUT, "sensitization_phase1_summary.md"), "w", encoding="utf-8") as f:
        f.write("# Phase 1 sensitization protocols (generated by run_sensitization_phase1.py)\n\n")
        f.write(f"- Rest (no bias, no shift): {rest_state()[0]*1e3:.3f} mV\n")
        f.write(f"- Onset of repetitive spiking from rest (tonic bias): {onset_spiking:.4f} A/m^2\n")
        f.write(f"- Large sub-0 mV oscillations persist up to: {onset_osc_end:.3f} A/m^2; beyond this the membrane settles on a stable depolarized silent state (depolarization block)\n")
        f.write(f"- Onset of spontaneous spiking under uniform kinetics shift: dV_shift = {onset_shift:.3f} mV (positive = hyperpolarizing shift of the rate functions)\n")
    print("done")


if __name__ == "__main__":
    main()
