#!/usr/bin/env python3
"""Build every manuscript table and the dictionary of quoted numbers from results/data.

Outputs (results/tables/):
    numbers.json        key -> formatted value: every number quoted in the manuscript
    table*.md           the manuscript tables, as markdown
Nothing in these files is typed by hand.
"""
import json
import math
import os
import sys
from dataclasses import fields

import numpy as np
import pandas as pd

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
DATA = os.path.join(ROOT, "results", "data")
OUT = os.path.join(ROOT, "results", "tables")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, "experiments"))

from ephaptic.params import (AbetaParams, HHParams, NavCParams, CleftParams, Protocol, A_REF,  # noqa: E402
                             ABETA_THRESHOLD, equivalent_gap)
from ephaptic.model import c_fiber_equilibria  # noqa: E402

N = {}


def put(key, value, fmt="{:.2f}"):
    if isinstance(value, (bool, np.bool_)):
        N[key] = "yes" if value else "no"
    elif isinstance(value, str):
        N[key] = value
    else:
        N[key] = fmt.format(value)
    return N[key]


def read(name):
    return pd.read_csv(os.path.join(DATA, name))


def md_table(df, name, caption=None, floatfmt=None):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join([":---"] + ["---:"] * (len(cols) - 1)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float) and floatfmt and c in floatfmt:
                cells.append(floatfmt[c].format(v) if not (isinstance(v, float) and math.isnan(v)) else "–")
            elif isinstance(v, float):
                cells.append("–" if math.isnan(v) else f"{v:.3g}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    with open(os.path.join(OUT, f"{name}.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  wrote results/tables/{name}.md")


PRETTY = {
    "HH_phi1_gNa120": "HH, 6.3 °C",
    "HH_phi7.8_gNa120": "HH, 25 °C",
    "HH_phi1_gNa600": "HH, conductances × 5",
    "HH_phi5_gNa600": "HH, rates & conductances × 5",
    "HH_phi10_gNa1200": "HH, rates & conductances × 10",
    "NavC_tm8_1.5ms_g18_2000": "NavC, τ~m8~ = 1.5 ms",
    "NavC_tm8_0.05ms_g18_2000": "NavC, τ~m8~ = 0.05 ms",
    "NavC_tm8_0.15ms_g18_20000": "NavC, time constants ÷ 10, conductances × 10",
}


def pretty(v):
    return PRETTY.get(v, v)


def yes(v):
    return str(v).strip().lower() in ("true", "1", "yes")


# ----------------------------------------------------------------------------
def table_parameters():
    ab, hh, nc, cl, pr = AbetaParams(), HHParams(), NavCParams(), CleftParams(), Protocol()
    R = []

    def row(group, sym, val, unit, src):
        R.append({"Group": group, "Quantity": sym, "Value": val, "Units": unit, "Source / status": src})
    row("Aβ fiber", "outer diameter D₁; g-ratio; axon diameter d₁", f"{ab.D_outer*1e6:g}; {ab.g_ratio:g}; {ab.d_axon*1e6:g}", "µm; –; µm", "g-ratio: modelling choice (Sweeney 1987: 0.6)")
    row("Aβ fiber", "node spacing; node length", f"{ab.internode*1e3:g}; {ab.l_node*1e6:g}", "mm; µm", "modelling choice")
    row("Aβ fiber", "C_m node; C_m myelin", f"{ab.Cm_node/1e-2:g}; {ab.Cm_internode/1e-2:g}", "µF cm⁻²", "node: modelling choice (Sweeney 1987: 2.5)")
    row("Aβ fiber", "ḡ_Na; g_L node; g_L myelin", f"{ab.gNa/10:g}; {ab.gL_node/10:g}; {ab.gL_internode/10:g}", "mS cm⁻²", "Sweeney et al. 1987; myelin: assumption")
    row("Aβ fiber", "E_Na; E_L", f"{ab.ENa*1e3:+.2f}; {ab.EL*1e3:.1f}", "mV", "Sweeney et al. 1987")
    row("Aβ fiber", "CRRSS rates", "as published for 37 °C (φ = 1)", "–", "Chiu et al. 1979; Sweeney et al. 1987")
    row("Axoplasm", "ρ_i (all fibers)", f"{ab.rho_i/1e-2:g}", "Ω cm", "Sweeney et al. 1987")
    row("C-fiber cable", "diameter; C_m", f"{hh.cable.d*1e6:g}; {hh.cable.Cm/1e-2:g}", "µm; µF cm⁻²", "both C-fiber models")
    row("HH C-fiber", "ḡ_Na; ḡ_K; g_L", f"{hh.gNa/10:g}; {hh.gK/10:g}; {hh.gL/10:g}", "mS cm⁻²", "Hodgkin & Huxley 1952")
    row("HH C-fiber", "E_Na; E_K; E_L", f"{hh.ENa*1e3:+.0f}; {hh.EK*1e3:.0f}; {hh.EL*1e3:.1f}", "mV", "Hodgkin & Huxley 1952")
    row("HH C-fiber", "kinetics temperature", f"{hh.temperature:g} °C (varied 6.3–25 °C)", "–", "squid rates; Q₁₀ = 3 when varied")
    row("NavC C-fiber", "ḡ₁₈; ḡ₁₉; ḡ_K; g_L", f"{nc.g18/10:g}; {nc.g19/10:g}; {nc.gK/10:g}; {nc.gL/10:g}", "mS cm⁻²", "calibrated")
    row("NavC C-fiber", "E_Na; E_K; E_L", f"{nc.ENa*1e3:+.0f}; {nc.EK*1e3:.0f}; {nc.EL*1e3:.0f}", "mV", "–")
    row("NavC C-fiber", "m₈: V½, k, τ", f"{nc.V8m*1e3:g}, {nc.k8m*1e3:g}, {nc.tau_m8*1e3:g} (τ varied 0.05–1.5)", "mV, mV, ms", "literature range, τ voltage independent")
    row("NavC C-fiber", "h₈: V½, k, τ", f"{nc.V8h*1e3:g}, {nc.k8h*1e3:g}, {nc.tau_h8*1e3:g}", "mV, mV, ms", "calibrated (literature ≈ −30 mV, 17 ms)")
    row("NavC C-fiber", "m₉: V½, k, τ", f"{nc.V9m*1e3:g}, {nc.k9m*1e3:g}, {nc.tau_m9*1e3:g}", "mV, mV, ms", "literature range")
    row("Compartment", "ρ_e; A_e (production)", f"{cl.rho_e/1e-2:g}; {cl.A_e*1e12:.2f}", "Ω cm; µm²", "A_e: earlier pair geometry (w_eq = 0.50 µm at n = 1)")
    row("Compartment", "κ (λ_e)", f"10⁹ ({1e6/math.sqrt(cl.kappa):.1f} µm); varied 10⁶–10¹¹", "m⁻²", "phenomenological, calibrated (Section 2.3); varied over five decades")
    row("Compartment", "lesion", f"z = {cl.lesion_start*1e3:g}–{cl.lesion_end*1e3:g} (varied 1–7 mm long)", "mm", "grounded bulk outside")
    row("Stimulus", "Aβ pulse at node 0", f"{pr.stim_dur*1e3:g} ms, {pr.stim_factor:g} × {ABETA_THRESHOLD*1e9:.3f} nA = {pr.stim_factor*ABETA_THRESHOLD*1e9:.2f} nA", "–", "threshold of the uncoupled fiber")
    row("Numerics", "L; Δz; Δt", f"{pr.L*1e3:g} mm; {pr.dz*1e6:g} µm; {pr.dt*1e6:g} µs", "–", "monolithic backward Euler")
    md_table(pd.DataFrame(R), "table1_parameters")


def controls():
    ab = read("e01_abeta_control.csv")
    a = ab.iloc[0]
    put("abeta_threshold_nA", a.threshold_nA, "{:.2f}")
    put("abeta_stim_nA", a.stim_nA, "{:.2f}")
    put("abeta_cv", a.cv_4_8mm_m_s, "{:.1f}")
    put("abeta_excursion", a.excursion_z4_mV, "{:.1f}")
    put("abeta_rest", a.rest_node_mV, "{:.2f}")
    put("abeta_node0_2x", a.node0_peak_mV, "{:+.1f}")
    b = ab.iloc[1]
    put("abeta_node0_100nA", b.node0_peak_mV, "{:+.0f}")
    put("abeta_cv_100nA", b.cv_4_8mm_m_s, "{:.1f}")
    cc = read("e01_cfiber_controls.csv")
    names = {
        "HH_phi1_gNa120": "HH, 6.3 °C (Phase 1)",
        "NavC_tm8_1.5ms_g18_2000": "NavC, τ~m8~ = 1.5 ms (Phase 2)",
    }

    def lab(r):
        if r.variant in names:          # mark the two membranes the study reports
            return names[r.variant]
        if r.kind == "HH":
            g = r.gNa_mS_cm2 / 120.0
            s = r.phi
            if abs(g - 1) < 1e-6:
                return f"HH, {r.temperature_C:.3g} °C (φ = {s:.2g})"
            if abs(g - s) < 1e-6 * g:
                return f"HH, rates & conductances × {g:.0f}"
            return f"HH, conductances × {g:.0f}"
        g = r.g18_mS_cm2 / 2000.0
        if abs(g - 1) < 1e-6:
            return f"NavC, τ~m8~ = {r.tau_m8_ms:.3g} ms"
        return f"NavC, time constants ÷ {g:.0f}, conductances × {g:.0f}"
    t = pd.DataFrame({
        "C-fiber membrane": [lab(r) for _, r in cc.iterrows()],
        "rest (mV)": cc.rest_mV.round(2),
        "τ~m~ at rest (ms)": cc.tau_rest_ms.round(2),
        "AP peak (mV)": cc.ap_peak_mV.round(1),
        "CV (m/s)": cc.cv_m_s.round(3),
        "APD~50~ (ms)": cc.apd50_ms.round(2),
        "conducts": ["yes" if yes(p) else "no" for p in cc.propagates],
    })
    md_table(t, "table2_controls", floatfmt={"CV (m/s)": "{:.2f}", "rest (mV)": "{:.2f}", "AP peak (mV)": "{:.1f}",
                                             "APD~50~ (ms)": "{:.2f}", "τ~m~ at rest (ms)": "{:.2f}"})
    r = cc.set_index("variant")
    put("hh_rest", r.loc["HH_phi1_gNa120"].rest_mV, "{:.2f}")
    put("hh_cv", r.loc["HH_phi1_gNa120"].cv_m_s, "{:.2f}")
    put("hh_peak", r.loc["HH_phi1_gNa120"].ap_peak_mV, "{:.1f}")
    put("navc_rest", r.loc["NavC_tm8_1.5ms_g18_2000"].rest_mV, "{:.2f}")
    put("navc_cv", r.loc["NavC_tm8_1.5ms_g18_2000"].cv_m_s, "{:.2f}")
    put("navc_peak", r.loc["NavC_tm8_1.5ms_g18_2000"].ap_peak_mV, "{:.1f}")
    put("navc_apd50", r.loc["NavC_tm8_1.5ms_g18_2000"].apd50_ms, "{:.1f}")
    prop = cc[cc.propagates.map(yes)]
    put("variant_cv_min", prop.cv_m_s.min(), "{:.2f}")
    put("variant_cv_max", prop.cv_m_s.max(), "{:.2f}")
    put("hh_tau_rest", r.loc["HH_phi1_gNa120"].tau_rest_ms, "{:.2f}")
    cab = HHParams().cable
    for key, v in (("hh", "HH_phi1_gNa120"), ("navc", "NavC_tm8_1.5ms_g18_2000")):
        G = cab.Cm / (r.loc[v].tau_rest_ms * 1e-3)            # S/m^2 at rest
        put(f"{key}_lambda_chord_um", math.sqrt(cab.d / (4.0 * cab.rho_i * G)) * 1e6, "{:.0f}")
    put("navc_tau_rest", r.loc["NavC_tm8_1.5ms_g18_2000"].tau_rest_ms, "{:.2f}")
    hot = cc[(cc.kind == "HH") & (np.isclose(cc.gNa_mS_cm2, 120)) & (~cc.propagates.map(yes))]
    put("hh_block_temp", hot.temperature_C.min() if len(hot) else float("nan"), "{:.0f}")


def convergence():
    ref = read("e02_refinement.csv")
    prod = ref[(ref.dt_us == 1.0) & (ref.dz_um == 5.0) & (ref.ionic == "explicit")].set_index(["model", "n_abeta"])
    dts, dzs = [], []
    for (m, n), r in prod.iterrows():
        fine_t = ref[(ref.model == m) & (ref.n_abeta == n) & (ref.dz_um == 5.0) & (ref.ionic == "explicit")].sort_values("dt_us").iloc[0]
        fine_z = ref[(ref.model == m) & (ref.n_abeta == n) & (ref.dt_us == 1.0) & (ref.ionic == "explicit")].sort_values("dz_um").iloc[0]
        dts.append(abs(r.dv_lesion_mV / fine_t.dv_lesion_mV - 1) * 100)
        dzs.append(abs(r.dv_lesion_mV / fine_z.dv_lesion_mV - 1) * 100)
        imp = ref[(ref.model == m) & (ref.n_abeta == n) & (ref.ionic == "implicit") & (ref.dt_us == 1.0)].iloc[0]
    put("conv_dt_maxdev_pct", max(dts), "{:.1f}")
    put("conv_dz_maxdev_pct", max(dzs), "{:.1f}")
    impdev = []
    for _, r in ref[(ref.ionic == "implicit") & (ref.dt_us == 1.0)].iterrows():
        e = prod.loc[(r.model, r.n_abeta)]
        impdev.append(abs(r.dv_lesion_mV / e.dv_lesion_mV - 1) * 100)
    put("conv_scheme_maxdev_pct", max(impdev), "{:.1f}")
    # classification invariance
    put("conv_classification_invariant", ref.groupby(["model", "n_abeta"]).c_spike.nunique().max() == 1)
    # The Abeta action potential is close to conduction block at n = 25: it blocks on every
    # grid from 10 um down, and conducts slowly on the coarsest grid (20 um) used by the
    # dispersion sweep.  Report that explicitly rather than only the peak deviations.
    q = ref[(ref.n_abeta == 25) & (ref.dt_us == 1.0) & (ref.ionic == "explicit") & (ref.model == "NavC")].set_index("dz_um")
    put("conv_dz20_n25_dev_pct", abs(q.loc[20.0].dv_lesion_mV / q.loc[5.0].dv_lesion_mV - 1) * 100, "{:.1f}")
    put("conv_dz20_n25_cv", q.loc[20.0].ab_cv_lesion, "{:.0f}")
    blocked = sorted(dz for dz, r in q.iterrows() if not yes(r.ab_conducts))
    put("conv_block_dz_max", max(blocked), "{:.0f}")
    k = read("e02_kcl.csv")
    put("kcl_rel_max", k.relative.max(), "{:.0e}")
    lag = read("e02_lagged_vs_monolithic.csv")
    piv = lag.pivot_table(index=["n_abeta", "dt_us"], columns="scheme", values="dv_downstream_mV")
    put("lag_n25_dt2p5", piv.loc[(25, 2.5), "lagged"], "{:.2f}")
    put("lag_n25_dt0p125", piv.loc[(25, 0.125), "lagged"], "{:.2f}")
    put("mono_n25_dt2p5", piv.loc[(25, 2.5), "monolithic"], "{:.2f}")
    put("mono_n25_dt0p125", piv.loc[(25, 0.125), "monolithic"], "{:.2f}")
    put("lag_n50_dt2p5", piv.loc[(50, 2.5), "lagged"], "{:.2f}")
    put("mono_n50_dt2p5", piv.loc[(50, 2.5), "monolithic"], "{:.2f}")
    put("mono_n1_dt2p5", piv.loc[(1, 2.5), "monolithic"], "{:.2f}")
    put("lag_n1_dt2p5", piv.loc[(1, 2.5), "lagged"], "{:.2f}")
    mono_spread = []
    for n in (1, 10, 25, 50):
        v = piv.loc[n, "monolithic"]
        mono_spread.append((v.max() - v.min()) / v.min() * 100)
    put("mono_dt_spread_pct", max(mono_spread), "{:.1f}")
    # table
    rows = []
    for n in (1, 10, 25, 50):
        rows.append({"n": n,
                     "lagged, Δt = 2.5 µs": piv.loc[(n, 2.5), "lagged"],
                     "lagged, Δt = 0.125 µs": piv.loc[(n, 0.125), "lagged"],
                     "monolithic, Δt = 5 µs": piv.loc[(n, 5.0), "monolithic"],
                     "monolithic, Δt = 0.125 µs": piv.loc[(n, 0.125), "monolithic"]})
    md_table(pd.DataFrame(rows), "tableS1_lagged", floatfmt={c: "{:.2f}" for c in rows[0] if c != "n"})
    rows = []
    for (m, n), r in prod.iterrows():
        sub = ref[(ref.model == m) & (ref.n_abeta == n)]
        g = lambda dt, dz, ion="explicit": sub[(sub.dt_us == dt) & (sub.dz_um == dz) & (sub.ionic == ion)].dv_lesion_mV.values[0]
        rows.append({"model": m, "n": n, "Δz 20 µm": g(1.0, 20.0), "Δz 10 µm": g(1.0, 10.0),
                     "production (5 µm, 1 µs)": g(1.0, 5.0), "Δz 1.25 µm": g(1.0, 1.25),
                     "Δt 0.125 µs": g(0.125, 5.0), "conductance-implicit": g(1.0, 5.0, "implicit")})
    md_table(pd.DataFrame(rows), "tableS2_refinement", floatfmt={c: "{:.2f}" for c in rows[0] if c not in ("model", "n")})


def fast_variants():
    f = read("e02b_fast_variants.csv")
    std = f[f.variant == "NavC_tm8_1.5ms_g18_2000"]
    f = f[f.variant != "NavC_tm8_1.5ms_g18_2000"]
    for ion in ("explicit", "implicit_c", "implicit"):
        for dt in (1.0, 0.1):
            r = std[(std.ionic == ion) & np.isclose(std.dt_us, dt) & (std.n_abeta == 100)]
            put(f"nearblock_{ion}_dt{str(dt).replace('.', 'p')}", r.dv_lesion_mV.values[0], "{:.1f}")
    dev, agree = [], True
    for (v, n), d in f.groupby(["variant", "n_abeta"]):
        ref = d[(d.ionic == "implicit_c") & np.isclose(d.dt_us, 1.0)].iloc[0]
        for _, r in d.iterrows():
            if not yes(r.c_spike) and not yes(ref.c_spike):
                dev.append(abs(r.dv_lesion_mV / ref.dv_lesion_mV - 1) * 100)
            agree &= (yes(r.c_spike) == yes(ref.c_spike))
    put("fast_dt_maxdev_pct", max(dev), "{:.1f}")
    put("fast_classification_agree", agree)


def n_sweep():
    d = read("e03_n_sweep.csv")
    sf = read("e07_safety_factor.csv")
    for m in ("NavC", "HH"):
        dm = d[d.model == m].set_index("n_abeta")
        for n in (1, 10, 25, 50, 100):
            put(f"{m}_n{n}_dv", dm.loc[n].dv_lesion_mV, "{:.1f}")
            put(f"{m}_n{n}_peak", dm.loc[n].v2_peak_lesion_mV, "{:.1f}")
        put(f"{m}_n1_dv2", dm.loc[1].dv_lesion_mV, "{:.2f}")
        put(f"{m}_max_dv", dm.dv_lesion_mV.max(), "{:.1f}")
        put(f"{m}_max_dv_n", dm.dv_lesion_mV.idxmax(), "{:d}")
        put(f"{m}_max_peak", dm.v2_peak_lesion_mV.max(), "{:.1f}")
        put(f"{m}_n25_hyp", dm.loc[25].hyp_lesion_mV, "{:.1f}")
        put(f"{m}_any_spike", bool(dm.c_spike.map(yes).any()))
    dn = d[d.model == "NavC"].set_index("n_abeta")
    cond = dn.ab_conducts.map(yes)
    nfail = cond[~cond].index.min()
    put("ab_fail_n", nfail, "{:d}")
    put("ab_last_n", cond[cond].index.max(), "{:d}")
    put("ab_fail_weq", equivalent_gap(A_REF / nfail) * 1e9, "{:.0f}")
    put("ab_cv_n1", dn.loc[1].ab_cv_lesion, "{:.1f}")
    put("ab_cv_lastcond", dn.loc[cond[cond].index.max()].ab_cv_lesion, "{:.1f}")
    put("ue_min_n25", dn.loc[25].ue_min_mV, "{:.1f}")
    collapse = dn[(dn.index > dn.dv_lesion_mV.idxmax())].dv_lesion_mV.min()
    put("dv_collapse", collapse, "{:.1f}")
    put("hh_navc_maxdiff", (d[d.model == "HH"].set_index("n_abeta").dv_lesion_mV - dn.dv_lesion_mV).abs().max(), "{:.2f}")
    for n in (1, 10, 25, 100):
        put(f"weq_n{n}", equivalent_gap(A_REF / n) * 1e9, "{:.0f}")
    # Table 3: main outcome
    rows = []
    for n in (1, 2, 5, 10, 15, 20, 25, 30, 50, 100, 150, 300):
        a, b = dn.loc[n], d[d.model == "HH"].set_index("n_abeta").loc[n]
        s_nc = sf[(sf.variant == "NavC_tm8_1.5ms_g18_2000") & (sf.n_abeta == n) & (sf.c_bias == 0)]
        s_hh = sf[(sf.variant == "HH_phi1_gNa120") & (sf.n_abeta == n) & (sf.c_bias == 0)]
        rows.append({"n": n, "w_eq (nm)": equivalent_gap(A_REF / n) * 1e9,
                     "ΔV NavC (mV)": a.dv_lesion_mV, "ΔV HH (mV)": b.dv_lesion_mV,
                     "peak hyperpol. (mV)": a.hyp_lesion_mV,
                     "u_e min (mV)": a.ue_min_mV,
                     "Aβ through lesion": "yes" if yes(a.ab_conducts) else "no",
                     "Aβ CV in lesion (m/s)": a.ab_cv_lesion,
                     "α* NavC": s_nc.alpha_star.values[0] if len(s_nc) else float("nan"),
                     "α* HH": s_hh.alpha_star.values[0] if len(s_hh) else float("nan"),
                     "C-fiber AP": "no" if not (yes(a.c_spike) or yes(b.c_spike)) else "YES"})
    md_table(pd.DataFrame(rows), "table3_n_sweep",
             floatfmt={"w_eq (nm)": "{:.0f}", "ΔV NavC (mV)": "{:.2f}", "ΔV HH (mV)": "{:.2f}",
                       "peak hyperpol. (mV)": "{:.1f}", "u_e min (mV)": "{:.1f}", "Aβ CV in lesion (m/s)": "{:.1f}",
                       "α* NavC": "{:.1f}", "α* HH": "{:.1f}"})


def membrane_verification():
    """E14: the Abeta source waveform and the C-fiber passive properties."""
    g = read("e14_abeta_gates.csv").set_index("v_mV")
    for v in (-80, -70, -60, -40):
        put(f"ab_hinf_m{abs(v)}", g.loc[v].h_inf, "{:.3f}")
        put(f"ab_minf_m{abs(v)}", g.loc[v].m_inf, "{:.3f}")
    put("ab_tau_m_rest_us", g.loc[-80].tau_m_ms * 1e3, "{:.0f}")
    put("ab_tau_h_rest_us", g.loc[-80].tau_h_ms * 1e3, "{:.0f}")
    put("ab_hinf_halfV", float(np.interp(0.5, g.h_inf.values[::-1], g.index.values[::-1])), "{:.0f}")
    tr = read("e14_abeta_ap_trace.csv")
    put("ab_ap_rest_mV", tr.v_node_mV.iloc[0], "{:.2f}")
    put("ab_ap_peak_mV", tr.v_node_mV.max(), "{:+.1f}")
    put("ab_ap_final_mV", tr.v_node_mV.iloc[-1], "{:.2f}")
    after = tr[(tr.t_ms > tr.t_ms[tr.v_node_mV.idxmax()]) & (tr.dv_from_rest_mV.abs() < 1.0)]
    put("ab_ap_return_ms", after.t_ms.min(), "{:.2f}")
    put("ab_trace_T_ms", tr.t_ms.max(), "{:.0f}")
    pp = read("e14_abeta_paired_pulse.csv").sort_values("isi_ms")
    ok = pp[pp.second_conducts.map(yes)]
    bad = pp[~pp.second_conducts.map(yes)]
    put("ab_refractory_max_fail_ms", bad.isi_ms.max() if len(bad) else float("nan"), "{:.2f}")
    put("ab_recovery_min_ms", ok.isi_ms.min() if len(ok) else float("nan"), "{:.2f}")
    full = ok[(ok.peak2_mV - ok.peak1_mV).abs() / ok.peak1_mV.abs() < 0.02]
    put("ab_full_recovery_ms", full.isi_ms.min() if len(full) else float("nan"), "{:.1f}")
    put("ab_cv1", pp.cv1_m_s.iloc[0], "{:.1f}")
    md_table(pp[["isi_ms", "n_aps_z8", "peak2_mV", "cv2_m_s", "second_conducts"]].rename(columns={
        "isi_ms": "interval (ms)", "n_aps_z8": "APs at z = 8 mm", "peak2_mV": "2nd AP peak (mV)",
        "cv2_m_s": "2nd AP CV (m/s)", "second_conducts": "2nd AP conducts"}),
        "tableS3_abeta_recovery",
        floatfmt={"interval (ms)": "{:.2f}", "2nd AP peak (mV)": "{:+.1f}", "2nd AP CV (m/s)": "{:.1f}"})
    pas = read("e14_cfiber_passive.csv").set_index("model")
    for m, key in (("HH", "hh"), ("NavC", "navc")):
        r = pas.loc[m]
        put(f"{key}_lambda_um", r.lambda_slope_um, "{:.0f}")
        put(f"{key}_Rin_Mohm", r.R_in_measured_Mohm, "{:.0f}")
        put(f"{key}_Rin_pred_Mohm", r.R_in_slope_Mohm, "{:.0f}")
        put(f"{key}_rheobase_nA", r.rheobase_1ms_nA, "{:.2f}")
    put("cf_Rin_maxdev_pct", ((pas.R_in_measured_Mohm - pas.R_in_slope_Mohm).abs()
                              / pas.R_in_slope_Mohm).max() * 100, "{:.1f}")
    md_table(pas.reset_index()[["model", "v_rest_mV", "tau_rest_ms", "lambda_slope_um",
                                "R_in_slope_Mohm", "R_in_measured_Mohm", "rheobase_1ms_nA"]].rename(columns={
        "model": "C-fiber membrane", "v_rest_mV": "rest (mV)", "tau_rest_ms": "τ~m~ at rest (ms)",
        "lambda_slope_um": "λ, small signal (µm)", "R_in_slope_Mohm": "R~in~ predicted (MΩ)",
        "R_in_measured_Mohm": "R~in~ measured (MΩ)", "rheobase_1ms_nA": "rheobase, 1 ms (nA)"}),
        "tableS4_cfiber_passive",
        floatfmt={"rest (mV)": "{:.2f}", "τ~m~ at rest (ms)": "{:.2f}", "λ, small signal (µm)": "{:.0f}",
                  "R~in~ predicted (MΩ)": "{:.1f}", "R~in~ measured (MΩ)": "{:.1f}",
                  "rheobase, 1 ms (nA)": "{:.2f}"})


def geometry():
    mf = read("e04_mean_field.csv")
    dev = []
    for n, d in mf.groupby("n_abeta"):
        a = d[d.case == "shared"].dv_lesion_mV.values[0]
        b = d[d.case == "single_equivalent"].dv_lesion_mV.values[0]
        dev.append(abs(a / b - 1) * 100)
    put("meanfield_maxdev_pct", max(dev), "{:.0f}")
    put("meanfield_mindev_pct", min(dev), "{:.1f}")
    g = read("e04_geometry.csv")
    pf = g[g.closure == "per_fiber"]
    dev = []
    for (m, w), d in pf.groupby(["model", "w_nm"]):
        cond = d.ab_conducts.map(yes)
        if cond.all():
            v = d.dv_lesion_mV
            dev.append((v.max() - v.min()) / v.max() * 100)
    put("geom_n_invariance_pct", max(dev), "{:.0f}")
    big = pf[(pf.n_abeta == 100) & (pf.model == "NavC")].set_index("w_nm")
    put("geom_w20_dv", big.loc[20].dv_lesion_mV, "{:.1f}")
    put("geom_w100_dv", big.loc[100].dv_lesion_mV, "{:.1f}")
    put("geom_w1000_dv", big.loc[1000].dv_lesion_mV, "{:.2f}")
    put("geom_max_dv", pf.dv_lesion_mV.max(), "{:.1f}")
    put("geom_any_spike", bool(pf.c_spike.map(yes).any()))
    cond100 = pf[(pf.model == "NavC") & (pf.n_abeta == 100) & pf.ab_conducts.map(yes)]
    wcond = cond100.w_nm.min()
    put("geom_w_block", wcond, "{:.0f}")
    put("geom_w_block_dv", cond100[cond100.w_nm == wcond].dv_lesion_mV.values[0], "{:.1f}")


def kappa():
    k = read("e05_kappa.csv")
    put("kappa_runs", len(k), "{:d}")
    put("kappa_any_spike", bool(k.c_spike.map(yes).any()))
    put("kappa_any_overshoot", bool(k.c_overshoot.map(yes).any()))
    put("kappa_max_dv", k.dv_lesion_mV.max(), "{:.1f}")
    r = k.loc[k.dv_lesion_mV.idxmax()]
    put("kappa_max_dv_kappa", f"{r.kappa:.0e}".replace("e+", "×10^").replace("^0", "^") + "^")
    put("kappa_max_dv_n", r.n_abeta, "{:.0f}")
    put("kappa_max_peak", k.v2_peak_lesion_mV.max(), "{:.1f}")
    for m in ("NavC",):
        d = k[(k.model == m)]
        n1 = d[d.n_abeta == 1]
        put("kappa_n1_min", n1.dv_lesion_mV.min(), "{:.2f}")
        put("kappa_n1_max", n1.dv_lesion_mV.max(), "{:.2f}")


def kinetics():
    k = read("e06_kinetics.csv")
    put("kin_runs", len(k), "{:d}")
    base = k[(k.family == "NavC_tau_m8") & (np.isclose(k.value, 1.5))].set_index(["kappa", "n_abeta"]).dv_lesion_mV
    for fam in ("NavC_tau_m8", "HH_temperature"):
        d = k[k.family == fam]
        dev = []
        ref = k[(k.family == fam) & np.isclose(k.value, 1.5 if fam == "NavC_tau_m8" else 6.3)].set_index(["kappa", "n_abeta"]).dv_lesion_mV
        for _, r in d.iterrows():
            if not yes(r.c_spike):
                dev.append(abs(r.dv_lesion_mV / ref.loc[(r.kappa, r.n_abeta)] - 1) * 100)
        put(f"kin_{fam}_maxdev_pct", max(dev), "{:.1f}")
        put(f"kin_{fam}_any_spike", bool(d.c_spike.map(yes).any()))
    sp = k[k.c_spike.map(yes)]
    put("kin_spiking_families", ", ".join(sorted(sp.family.unique())) if len(sp) else "none")
    if len(sp):
        put("kin_spike_cv_min", sp.c_cv.min(), "{:.1f}")
        put("kin_spike_cv_max", sp.c_cv.max(), "{:.1f}")
        put("kin_spike_init_min_mm", sp.c_init_z_mm.min(), "{:.1f}")
        put("kin_spike_init_max_mm", sp.c_init_z_mm.max(), "{:.1f}")
    # conduction velocity of the variants that fire (from the uncoupled controls)
    cc = read("e01_cfiber_controls.csv").set_index("variant")
    fire = sorted(set(sp.variant)) if len(sp) else []
    cvs = [cc.loc[v].cv_m_s for v in fire if v in cc.index]
    put("kin_fire_cv_min", min(cvs) if cvs else float("nan"), "{:.1f}")
    put("kin_fire_cv_max", max(cvs) if cvs else float("nan"), "{:.2f}")
    nc10 = cc.loc["NavC_tm8_0.15ms_g18_20000"] if "NavC_tm8_0.15ms_g18_20000" in cc.index else None
    if nc10 is not None:
        put("navcs10_tau_rest", nc10.tau_rest_ms, "{:.2f}")
    put("navc_m8_gap", abs(NavCParams().V8m * 1e3 - c_fiber_equilibria(NavCParams())[0]["v"] * 1e3), "{:.0f}")
    # minimal n for spike per variant and kappa
    rows = []
    for (fam, val), d in k.groupby(["family", "value"]):
        for kap, dd in d.groupby("kappa"):
            s = dd[dd.c_spike.map(yes)]
            rows.append(dict(family=fam, value=val, kappa=kap, n_min=s.n_abeta.min() if len(s) else np.nan,
                             n_max=s.n_abeta.max() if len(s) else np.nan, max_dv=dd[~dd.c_spike.map(yes)].dv_lesion_mV.max()))
    nm = pd.DataFrame(rows)
    nm.to_csv(os.path.join(OUT, "kinetics_nmin.csv"), index=False)
    for fam in ("HH_speed", "NavC_speed", "HH_gscale"):
        for kap in (1e9, 1e10):
            for val in sorted(nm[nm.family == fam].value.unique()):
                r = nm[(nm.family == fam) & np.isclose(nm.value, val) & np.isclose(nm.kappa, kap)].iloc[0]
                key = f"kin_{fam}_{val:g}_k{int(round(math.log10(kap)))}_nmin"
                put(key, "none" if math.isnan(r.n_min) else f"{r.n_min:.0f}")
    # smallest speed with any spike
    hs = nm[(nm.family == "HH_speed") & nm.n_min.notna()]
    put("kin_hh_speed_min", hs.value.min() if len(hs) else float("nan"), "{:g}")
    if len(hs):
        cc2 = read("e01_cfiber_controls.csv")
        smin = hs.value.min()
        row = cc2[(cc2.kind == "HH") & np.isclose(cc2.phi, smin) & np.isclose(cc2.gNa_mS_cm2, 120 * smin)]
        put("kin_hh_speed_min_tau", row.tau_rest_ms.values[0] if len(row) else float("nan"), "{:.2f}")
    ns_no = nm[(nm.family == "HH_speed") & nm.n_min.isna()]
    put("kin_hh_speed_nofire_max", ns_no.value.max() if len(ns_no) else float("nan"), "{:g}")
    ns = nm[(nm.family == "NavC_speed") & nm.n_min.notna()]
    put("kin_navc_speed_min", ns.value.min() if len(ns) else float("nan"), "{:g}")
    put("kin_navc_speed_any", bool(len(ns)))


def threshold():
    sd = read("e07_strength_duration.csv")
    for v, key in (("HH_phi1_gNa120", "hh"), ("NavC_tm8_1.5ms_g18_2000", "navc")):
        for mode in ("point", "uniform"):
            d = sd[(sd.variant == v) & (sd["mode"] == mode)].set_index("duration_ms")
            put(f"sd_{key}_{mode}_v01", d.loc[0.1].v_peak_subthreshold_mV, "{:.0f}")
            put(f"sd_{key}_{mode}_v20", d.loc[20.0].v_peak_subthreshold_mV, "{:.0f}")
            put(f"sd_{key}_{mode}_th01_over_th20", d.loc[0.1].threshold / d.loc[20.0].threshold, "{:.0f}")
            if mode == "point":
                put(f"sd_{key}_point_q01_pC", d.loc[0.1].charge * 1e12, "{:.2f}")
    sf = read("e07_safety_factor.csv")
    s0 = sf[sf.c_bias == 0]
    for v, key in (("HH_phi1_gNa120", "hh"), ("NavC_tm8_1.5ms_g18_2000", "navc"), ("NavC_tm8_0.05ms_g18_2000", "navc005"),
                   ("HH_phi7.8_gNa120", "hh25"), ("HH_phi1_gNa600", "hhg5"), ("HH_phi5_gNa600", "hhs5"),
                   ("HH_phi10_gNa1200", "hhs10"), ("NavC_tm8_0.15ms_g18_20000", "navcs10")):
        d = s0[s0.variant == v].set_index("n_abeta")
        if not len(d):
            continue
        for n in (1, 10, 25, 50, 100):
            if n in d.index:
                put(f"alpha_{key}_n{n}", d.loc[n].alpha_star, "{:.1f}")
        put(f"alpha_{key}_min", d.alpha_star.min(), "{:.1f}")
    std = s0[s0.variant.isin(["HH_phi1_gNa120", "NavC_tm8_1.5ms_g18_2000", "NavC_tm8_0.05ms_g18_2000", "HH_phi7.8_gNa120"])]
    put("alpha_std_min", std.alpha_star.min(), "{:.1f}")
    put("openloop_maxdiff_pct", ((s0.open_loop_dv_alpha1_mV - s0.closed_loop_dv_mV).abs() / s0.closed_loop_dv_mV).max() * 100, "{:.2f}")
    sb = sf[sf.c_bias > 0]
    for _, r in sb.iterrows():
        put(f"alpha_{'navc' if r.kind == 'NavC' else 'hh'}_bias{r.c_bias:g}_n{r.n_abeta:.0f}", r.alpha_star, "{:.1f}")
    # SD table
    rows = []
    for v, d in sd[sd["mode"] == "point"].groupby("variant", sort=False):
        d = d.set_index("duration_ms")
        rows.append({"C-fiber membrane": pretty(v), "Q_th 0.1 ms (pC)": d.loc[0.1].charge * 1e12,
                     "V_peak 0.1 ms (mV)": d.loc[0.1].v_peak_subthreshold_mV,
                     "V_peak 1 ms (mV)": d.loc[1.0].v_peak_subthreshold_mV,
                     "V_peak 20 ms (mV)": d.loc[20.0].v_peak_subthreshold_mV,
                     "I_th 0.1 / I_th 20 ms": d.loc[0.1].threshold / d.loc[20.0].threshold})
    md_table(pd.DataFrame(rows), "tableS5_strength_duration",
             floatfmt={"Q_th 0.1 ms (pC)": "{:.2f}", "V_peak 0.1 ms (mV)": "{:.0f}", "V_peak 1 ms (mV)": "{:.0f}",
                       "V_peak 20 ms (mV)": "{:.0f}", "I_th 0.1 / I_th 20 ms": "{:.1f}"})


def jitter():
    j = read("e08_jitter.csv")
    for m in ("NavC", "HH"):
        for n in (10, 25, 50):
            d = j[(j.model == m) & (j.n_abeta == n)].set_index("jitter_ms")
            if 0.0 not in d.index:
                continue
            att = (1 - d.dv_lesion_mV / d.loc[0.0].dv_lesion_mV) * 100
            for w, key in ((0.2, "0p2"), (0.5, "0p5"), (1.5, "1p5")):
                if w in att.index:
                    put(f"jit_{m}_n{n}_att{key}", att.loc[w], "{:.0f}")
                    put(f"jit_{m}_n{n}_dv{key}", d.loc[w].dv_lesion_mV, "{:.2f}")
            # the attenuation is not monotone at small W (see below), so take the first
            # crossing of 50 % rather than interpolating in a sorted attenuation
            x, y = att.index.values, att.values
            w50 = float("nan")
            for i in range(1, len(y)):
                if y[i - 1] < 50.0 <= y[i]:
                    w50 = x[i - 1] + (50.0 - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])
                    break
            put(f"jit_{m}_n{n}_w50_ms", w50, "{:.2f}")
    put("jit_any_spike", bool(j.c_spike.map(yes).any()))
    # At the largest n the synchronous Abeta action potential fails inside the lesion; a small
    # dispersion restores conduction, so the peak first rises before it falls.
    d50 = j[(j.model == "NavC") & (j.n_abeta == 50)].set_index("jitter_ms").sort_index()
    put("jit_relief_n", "50")
    put("jit_relief_dv0", d50.dv_lesion_mV.loc[0.0], "{:.1f}")
    put("jit_relief_dvmax", d50.dv_lesion_mV.max(), "{:.1f}")
    put("jit_relief_wmax", d50.dv_lesion_mV.idxmax(), "{:.2f}")
    cond = d50[d50.ab_conducts.map(yes)]
    put("jit_relief_wcond", cond.index.min(), "{:.1f}")
    put("jit_relief_cv", cond.ab_cv_lesion.loc[cond.index.min()], "{:.0f}")
    j25 = j[(j.model == "NavC") & (j.n_abeta == 25)].set_index("jitter_ms")
    put("jit_n25_sync_dv", j25.dv_lesion_mV.loc[0.0], "{:.1f}")
    put("jit_n25_sync_cv", j25.ab_cv_lesion.loc[0.0], "{:.0f}")
    c = read("e08_jitter_convergence.csv")
    kk = c[c.study == "K"].set_index("K").dv_lesion_mV
    put("jit_K11", kk.loc[11], "{:.2f}")
    put("jit_K21", kk.loc[21], "{:.2f}")
    put("jit_K41", kk.loc[41], "{:.2f}")
    put("jit_K61", kk.loc[61], "{:.2f}")
    put("jit_K81", kk.loc[81], "{:.2f}")
    put("jit_K_converged_pct", abs(kk.loc[81] / kk.loc[61] - 1) * 100, "{:.1f}")
    dz = c[c.study == "dz"].set_index("dz_um").dv_lesion_mV
    put("jit_dz_spread_pct", (dz.max() - dz.min()) / dz.mean() * 100, "{:.1f}")
    rows = []
    for _, r in c.iterrows():
        rows.append({"study": "phases K" if r.study == "K" else "grid Δz",
                     "K": int(r.K), "Δz (µm)": r.dz_um, "spacing W/(K−1) (µs)": 1500.0 / (r.K - 1),
                     "peak ΔV (mV)": r.dv_lesion_mV})
    md_table(pd.DataFrame(rows), "tableS7_jitter_convergence",
             floatfmt={"peak ΔV (mV)": "{:.2f}", "spacing W/(K−1) (µs)": "{:.0f}", "Δz (µm)": "{:.0f}"})


def trains():
    t = read("e09_trains.csv")
    pc = [c for c in t.columns if c.startswith("dv_pulse")]
    rel = []
    for _, r in t.iterrows():
        v = r[pc].values.astype(float)
        rel.append(np.nanmax(np.abs(v - v[0])) / v[0] * 100)
    t["rel"] = rel
    put("train_any_spike", bool(t.c_spike.map(yes).any()))
    put("train_max_rel_change_pct", max(rel), "{:.2f}")
    r = t.loc[t.rel.idxmax()]
    put("train_max_rel_where", f"{r.model}, n = {r.n_abeta:.0f}, {r.freq_Hz:.0f} Hz")
    t100 = t[(t.freq_Hz <= 100)]
    put("train_le100_max_rel_pct", t100.rel.max(), "{:.2f}")
    put("train_maxdv", t.dv_max_all_mV.max(), "{:.1f}")


def bias():
    eq = read("e10_equilibria.csv")
    for m in ("HH", "NavC"):
        d = eq[eq.model == m]
        st = d[d.lower_stable.map(yes)]
        un = d[~d.lower_stable.map(yes)]
        put(f"bias_{m}_stable_max", st.bias_A_m2.max(), "{:.3g}")
        put(f"bias_{m}_tested_max", d.bias_A_m2.max(), "{:.3g}")
        put(f"bias_{m}_loses_stability", bool(len(un)))
        put(f"bias_{m}_unstable_min", un.bias_A_m2.min() if len(un) else float("nan"), "{:.3g}")
        put(f"bias_{m}_vrest_at_stable_max", st[st.bias_A_m2 == st.bias_A_m2.max()].v_lower_mV.values[0], "{:.1f}")
    d = eq[(eq.model == "NavC") & (eq.n_equilibria > 1)]
    put("bias_navc_bistable_min", d.bias_A_m2.min() if len(d) else float("nan"), "{:.3g}")
    b = read("e10_bias.csv")
    ctrl = b[b.control == "no_stimulus"]
    put("bias_spont_any", bool(ctrl.c_spike.map(yes).any()))
    stim = b[b.control != "no_stimulus"]
    put("bias_any_spike", bool(stim.c_spike.map(yes).any()))
    nc = stim[stim.model == "NavC"]
    r = nc.loc[nc.v2_peak_lesion_mV.idxmax()]
    put("bias_navc_maxpeak", r.v2_peak_lesion_mV, "{:.1f}")
    put("bias_navc_maxpeak_bias", r.bias_A_m2, "{:g}")
    put("bias_navc_maxpeak_n", r.n_abeta, "{:.0f}")
    hh = stim[stim.model == "HH"]
    r = hh.loc[hh.v2_peak_lesion_mV.idxmax()]
    put("bias_hh_maxpeak", r.v2_peak_lesion_mV, "{:.1f}")
    put("bias_hh_maxpeak_bias", r.bias_A_m2, "{:g}")
    rows = []
    for (m, bb), d in stim.groupby(["model", "bias_A_m2"]):
        dd = d.set_index("n_abeta")
        cc = ctrl[(ctrl.model == m) & np.isclose(ctrl.bias_A_m2, bb)]
        rows.append({"model": m, "bias (A/m²)": bb, "rest (mV)": dd.loc[1].v2_rest_mV,
                     "spontaneous AP": "yes" if (len(cc) and yes(cc.c_spike.values[0])) else "no",
                     "peak V, n = 25 (mV)": dd.loc[25].v2_peak_lesion_mV,
                     "peak V, n = 100 (mV)": dd.loc[100].v2_peak_lesion_mV,
                     "evoked AP (any n)": "YES" if d.c_spike.map(yes).any() else "no"})
    md_table(pd.DataFrame(rows), "tableS6_bias", floatfmt={"rest (mV)": "{:.2f}", "peak V, n = 25 (mV)": "{:.1f}",
                                                         "peak V, n = 100 (mV)": "{:.1f}", "bias (A/m²)": "{:g}"})


def full_length():
    f = read("e11_full_length.csv")
    d = f[np.isclose(f.kappa, 1e9)]
    for ret in ("returned", "omitted"):
        dd = d[d.electrode_current == ret]
        pre = "full" if ret == "returned" else "fullO"
        for m in ("HH", "NavC"):
            for stim, key in ((dd.stim_nA.min(), "2x"), (100.0, "100nA")):
                q = dd[(dd.model == m) & np.isclose(dd.stim_nA, stim)]
                sp = q[q.c_spike.map(yes)]
                tag = f"{pre}_{m}_{key}"
                put(f"{tag}_nmin", "none" if not len(sp) else f"{sp.n_abeta.min():.0f}")
                if len(sp):
                    put(f"{tag}_init_z", sp.c_init_z_mm.max(), "{:.2f}")
                    put(f"{tag}_cv", sp.c_cv.min(), "{:.2f}")
                ov = q[q.c_overshoot.map(yes) & ~q.c_spike.map(yes)]
                put(f"{tag}_overshoot_only", "none" if not len(ov) else f"{ov.n_abeta.min():.0f}")
            q = dd[(dd.model == m) & np.isclose(dd.stim_nA, 100.0) & (dd.n_abeta == 25)]
            if len(q):
                put(f"{pre}_{m}_100nA_n25_cz0", q.c_z0_peak_mV.values[0], "{:+.0f}")
                put(f"{pre}_{m}_100nA_n25_ab0", q.abeta_node0_peak_mV.values[0], "{:+.0f}")
                put(f"{pre}_{m}_100nA_n25_ue0", q.ue_z0_max_mV.values[0], "{:.1f}")
                put(f"{pre}_{m}_100nA_n25_ueabs", q.ue_abs_max_mV.values[0], "{:.0f}")
            q2 = dd[(dd.model == m) & np.isclose(dd.stim_nA, dd.stim_nA.min())]
            put(f"{pre}_{m}_2x_maxint", q2[~q2.c_spike.map(yes)].dv_interior_mV.max(), "{:.1f}")
    # the weakest electrode current that launches a spike at the stimulated end
    bsp = d[d.c_spike.map(yes)]
    if len(bsp):
        first = bsp.sort_values(["stim_nA", "n_abeta"]).iloc[0]
        put("full_boundary_min_nA", first.stim_nA, "{:.0f}")
        put("full_boundary_min_n", first.n_abeta, "{:.0f}")
        put("full_boundary_min_model", str(first.model))
        put("full_boundary_min_ret", str(first.electrode_current))
        put("full_boundary_stim_ratio", first.stim_nA / d.stim_nA.min(), "{:.0f}")
    lk = f[np.isclose(f.kappa, 3e7)]
    sp = lk[lk.c_spike.map(yes)]
    put("lowk_any_spike", bool(len(sp)))
    put("lowk_spike_cases", "; ".join(sorted({f"{r.stim_nA:.0f} nA, n = {r.n_abeta:.0f}, {r.electrode_current}, A_e = {r.A_e_um2:.0f} µm²" for _, r in sp.iterrows()})) if len(sp) else "none")
    if len(sp):
        put("lowk_cv", sp.c_cv.min(), "{:.2f}")
        put("lowk_init", sp.c_init_z_mm.max(), "{:.2f}")
    lk2 = lk[np.isclose(lk.stim_nA, lk.stim_nA.min())]
    put("lowk_2x_any_spike", bool(lk2.c_spike.map(yes).any()))
    put("lowk_2x_maxint", lk2.dv_interior_mV.max(), "{:.1f}")
    # 100-Hz trains through the electrode: does the spike need the train, or the electrode?
    tr = read("e11_full_length_trains.csv")
    sp = tr[tr.c_spike.map(yes)]
    put("fulltrain_any_spike", bool(len(sp)))
    put("fulltrain_2x_any_spike", bool(tr[np.isclose(tr.stim_nA, tr.stim_nA.min())].c_spike.map(yes).any()))
    if len(sp):
        put("fulltrain_stim_nA", sp.stim_nA.min(), "{:.0f}")
        put("fulltrain_models", ", ".join(sorted(set(sp.model))))
        put("fulltrain_nmin", sp.n_abeta.min(), "{:.0f}")
        put("fulltrain_init_t_max_ms", sp.c_init_t_ms.max(), "{:.2f}")
        put("fulltrain_init_z_max_mm", sp.c_init_z_mm.max(), "{:.2f}")
        put("fulltrain_cv", sp.c_cv.min(), "{:.2f}")
    ov = tr[tr.c_overshoot.map(yes) & ~tr.c_spike.map(yes)]
    put("fulltrain_overshoot_models", ", ".join(sorted(set(ov.model))) if len(ov) else "none")

    rows = []
    for (ret, m, s_) in sorted({(r.electrode_current, r.model, r.stim_nA) for _, r in d.iterrows()}):
        dd = d[(d.electrode_current == ret) & (d.model == m) & np.isclose(d.stim_nA, s_)]
        sp = dd[dd.c_spike.map(yes)]
        rows.append({"electrode current": ret, "model": m, "Aβ stimulus (nA)": s_,
                     "propagating C-fiber AP for n ≥": "none (n ≤ 50)" if not len(sp) else f"{sp.n_abeta.min():.0f}",
                     "initiation (mm)": "–" if not len(sp) else f"{sp.c_init_z_mm.min():.2f}",
                     "Aβ node 0 peak, n = 25 (mV)": dd[dd.n_abeta == 25].abeta_node0_peak_mV.values[0],
                     "max |u_e|, n = 25 (mV)": dd[dd.n_abeta == 25].ue_abs_max_mV.values[0]})
    md_table(pd.DataFrame(rows), "tableS8_full_length",
             floatfmt={"Aβ stimulus (nA)": "{:.3g}", "Aβ node 0 peak, n = 25 (mV)": "{:+.0f}",
                       "max |u_e|, n = 25 (mV)": "{:.0f}"})


def lesion_stim():
    e = read("e12_lesion_stimulus.csv")
    put("les_any_spike", bool(e.c_spike.map(yes).any()))
    L = e[e.study == "lesion_length"]
    put("les_max_dv", L.dv_lesion_mV.max(), "{:.1f}")
    S = e[e.study == "stimulus"]
    put("stim_max_dv", S.dv_lesion_mV.max(), "{:.1f}")
    base = read("e03_n_sweep.csv")
    b = base[(base.model == "NavC")].set_index("n_abeta").dv_lesion_mV
    dev = []
    for _, r in S[(S.model == "NavC") & (S.n_abeta <= 10)].iterrows():
        dev.append(abs(r.dv_lesion_mV / b.loc[r.n_abeta] - 1) * 100)
    put("stim_n_le10_maxdev_pct", max(dev), "{:.1f}")
    l1 = L[(L.model == "NavC") & np.isclose(L.lesion_mm, 1.0)].set_index("n_abeta")
    put("les1_n25_dv", l1.loc[25].dv_lesion_mV, "{:.1f}")


def waveforms():
    W = np.load(os.path.join(DATA, "e13_waveforms.npz"))
    for n in (1, 10, 25):
        k = f"NavC_n{n}"
        t, tr = W[f"{k}__t"], W[f"{k}__dv_peak"]
        above = t[tr >= tr.max() / 2]
        put(f"fwhm_n{n}_us", (above.max() - above.min()) * 1e6, "{:.0f}")
        z, prof = W[f"{k}__z"], W[f"{k}__dv_profile"]
        pos = z[prof >= prof.max() / 2]
        put(f"halfwidth_n{n}_um", (pos.max() - pos.min()) * 1e6, "{:.0f}")
        put(f"ue_peak_n{n}_mV", np.abs(W[f"{k}__ue_profile"]).max(), "{:.1f}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    steps = [table_parameters, controls, convergence, fast_variants, membrane_verification, n_sweep,
             geometry, kappa, kinetics, threshold, jitter, trains, bias, full_length, lesion_stim, waveforms]
    for f in steps:
        try:
            f()
        except FileNotFoundError as e:
            print(f"  skipped {f.__name__}: {e.filename} missing")
    with open(os.path.join(OUT, "numbers.json"), "w") as fh:
        json.dump(N, fh, indent=1, sort_keys=True)
    print(f"  wrote results/tables/numbers.json ({len(N)} values)")
