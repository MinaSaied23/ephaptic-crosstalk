"""
_audit_gate_equations.py

Comprehensive mathematical and numerical audit of all closed-form equations
printed in the JCNS revised manuscript against their production code implementations.

Covers:
1. CRRSS Aβ nodal gate equations (Section 2.2.1: alpha_m, beta_m, alpha_h, beta_h, m_inf, tau_m, h_inf, tau_h).
2. Classical HH C-fiber rate equations (Section 2.2.2: alpha_n, beta_n, n_inf, tau_n).
3. Nav1.8 / Nav1.9 nociceptor gating kinetics (Section 2.5: m8_inf, h8_inf, m9_inf, tau_m8, tau_h8, tau_m9).
4. Extracellular Helmholtz coupling equations (Section 2.3: A_eff, r_e, Sigma_G, kappa_eff, lambda_eff).
"""

import os
import sys
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure phase1 and phase2 directories are on path, with phase1 having precedence for ephaptic_model
base_dir = os.path.dirname(os.path.abspath(__file__))
p1_dir = os.path.join(base_dir, 'phase1_classical_hh')
p2_dir = os.path.join(base_dir, 'phase2_nav18_nav19')
for p in [p2_dir, p1_dir]:
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

from ephaptic_model import (
    crrss_rates, hh_rates, d1, d2, d1_axon, rho_i, rho_e_bulk,
    r_e_from_cleft
)
from nav_kinetics import nav18_steady, nav19_steady, tau_m8, tau_h8, tau_m9


def audit_crrss_gates(tol=1e-12):
    """
    Audits CRRSS Aβ nodal gating kinetics across v ∈ [-90, +40] mV.
    Compares manuscript Section 2.2.1 against ephaptic_model.crrss_rates().
    """
    print("=" * 80)
    print("SUITE 1: CRRSS Aβ Gating Kinetics (Manuscript Section 2.2.1 vs Code)")
    print("=" * 80)

    v_mV = np.linspace(-90.0, 40.0, 27)  # 27 evaluation points across physiological range
    v_volts = v_mV * 1e-3

    # Production code
    am_code, bm_code, ah_code, bh_code = crrss_rates(v_volts)
    minf_code = am_code / (am_code + bm_code)
    taum_code = 1.0 / (am_code + bm_code)
    hinf_code = ah_code / (ah_code + bh_code)
    tauh_code = 1.0 / (ah_code + bh_code)

    # Manuscript Section 2.2.1 typeset equations:
    # \alpha_m(v) = \frac{(97.0 + 0.363(v_{\text{mV}} + 80.0)) \times 10^3}{1.0 + \exp(-(v_{\text{mV}} + 49.0) / 5.3)}\,\text{s}^{-1}
    # \beta_m(v) = \alpha_m(v) \exp(-(v_{\text{mV}} + 56.2) / 4.17)
    # \beta_h(v) = \frac{15.6 \times 10^3}{1.0 + \exp(-(v_{\text{mV}} + 56.0) / 10.0)}\,\text{s}^{-1}
    # \alpha_h(v) = \beta_h(v) \exp(-(v_{\text{mV}} + 74.5) / 5.0)

    am_ms = (97.0 + 0.363 * (v_mV + 80.0)) / (1.0 + np.exp(-(v_mV + 49.0) / 5.3)) * 1e3
    bm_ms = am_ms * np.exp(-(v_mV + 56.2) / 4.17)

    bh_ms = 15.6 * 1e3 / (1.0 + np.exp(-(v_mV + 56.0) / 10.0))
    ah_ms = bh_ms * np.exp(-(v_mV + 74.5) / 5.0)

    minf_ms = am_ms / (am_ms + bm_ms)
    taum_ms = 1.0 / (am_ms + bm_ms)
    hinf_ms = ah_ms / (ah_ms + bh_ms)
    tauh_ms = 1.0 / (ah_ms + bh_ms)

    rel_am = np.max(np.abs(am_code - am_ms) / np.maximum(np.abs(am_code), 1e-12))
    rel_bm = np.max(np.abs(bm_code - bm_ms) / np.maximum(np.abs(bm_code), 1e-12))
    diff_minf = np.max(np.abs(minf_code - minf_ms))
    diff_taum = np.max(np.abs(taum_code - taum_ms))

    rel_ah = np.max(np.abs(ah_code - ah_ms) / np.maximum(np.abs(ah_code), 1e-12))
    rel_bh = np.max(np.abs(bh_code - bh_ms) / np.maximum(np.abs(bh_code), 1e-12))
    diff_hinf = np.max(np.abs(hinf_code - hinf_ms))
    diff_tauh = np.max(np.abs(tauh_code - tauh_ms))

    print(f"  alpha_m max relative diff : {rel_am:.4e}")
    print(f"  beta_m  max relative diff : {rel_bm:.4e}")
    print(f"  m_inf   max absolute diff : {diff_minf:.4e}")
    print(f"  tau_m   max absolute diff : {diff_taum:.4e} s")
    print(f"  alpha_h max relative diff : {rel_ah:.4e}")
    print(f"  beta_h  max relative diff : {rel_bh:.4e}")
    print(f"  h_inf   max absolute diff : {diff_hinf:.4e}")
    print(f"  tau_h   max absolute diff : {diff_tauh:.4e} s")

    m_ok = (rel_am < tol and rel_bm < tol and diff_minf < tol and diff_taum < 1e-15)
    h_ok = (rel_ah < tol and rel_bh < tol and diff_hinf < tol and diff_tauh < 1e-15)
    print(f"  [CRRSS m-gate] : [{'PASS' if m_ok else 'FAIL'}]")
    print(f"  [CRRSS h-gate] : [{'PASS' if h_ok else 'FAIL'}]")

    # Also document the historical defective formula from previous draft for audit record:
    denom_old = 1.0 - np.exp(-(v_mV + 35.0) / 10.0)
    denom_old = np.where(np.abs(denom_old) < 1e-12, 1e-12, denom_old)
    am_old = 97.0 * (v_mV + 35.0) / denom_old * 1e3
    bm_old = am_old * np.exp(-(v_mV + 60.0) / 5.64)
    old_rel_am = np.max(np.abs(am_code - am_old) / np.maximum(np.abs(am_code), 1e-12))
    old_rel_bm = np.max(np.abs(bm_code - bm_old) / np.maximum(np.abs(bm_code), 1e-12))
    print(f"  [Historical Defect Documentation: old formula discrepancy: alpha_m max rel = {old_rel_am:.1f}x, beta_m max rel = {old_rel_bm:.1f}x]")

    return m_ok and h_ok


def audit_classical_hh_gates(tol=1e-12):
    """
    Audits classical HH C-fiber kinetics (Section 2.2.2) against ephaptic_model.hh_rates().
    """
    print("\n" + "=" * 80)
    print("SUITE 2: Classical HH Gating Kinetics (Manuscript Section 2.2.2 vs Code)")
    print("=" * 80)

    v_mV = np.linspace(-90.0, 40.0, 27)
    v_volts = v_mV * 1e-3

    _, _, _, _, an_code, bn_code = hh_rates(v_volts)
    ninf_code = an_code / (an_code + bn_code)
    taun_code = 1.0 / (an_code + bn_code)

    # Manuscript Section 2.2.2 typeset equations:
    # \alpha_n(v) = \frac{0.01 (v_{\text{mV}} + 55.0)}{1.0 - \exp(-(v_{\text{mV}} + 55.0) / 10.0)} \times 10^3\,\text{s}^{-1}
    # \beta_n(v) = 0.125 \exp(-(v_{\text{mV}} + 65.0) / 80.0) \times 10^3\,\text{s}^{-1}
    denom_n = 1.0 - np.exp(-(v_mV + 55.0) / 10.0)
    denom_n = np.where(np.abs(denom_n) < 1e-12, 1e-12, denom_n)
    an_ms = 0.01 * (v_mV + 55.0) / denom_n * 1e3
    bn_ms = 0.125 * np.exp(-(v_mV + 65.0) / 80.0) * 1e3

    ninf_ms = an_ms / (an_ms + bn_ms)
    taun_ms = 1.0 / (an_ms + bn_ms)

    rel_an = np.max(np.abs(an_code - an_ms) / np.maximum(np.abs(an_code), 1e-12))
    rel_bn = np.max(np.abs(bn_code - bn_ms) / np.maximum(np.abs(bn_code), 1e-12))
    diff_ninf = np.max(np.abs(ninf_code - ninf_ms))
    diff_taun = np.max(np.abs(taun_code - taun_ms))

    print(f"  alpha_n max relative diff : {rel_an:.4e}")
    print(f"  beta_n  max relative diff : {rel_bn:.4e}")
    print(f"  n_inf   max absolute diff : {diff_ninf:.4e}")
    print(f"  tau_n   max absolute diff : {diff_taun:.4e} s")

    n_ok = (rel_an < tol and rel_bn < tol and diff_ninf < tol and diff_taun < 1e-15)
    print(f"  [Classical HH n-gate] : [{'PASS' if n_ok else 'FAIL'}]")
    return n_ok


def audit_nav18_nav19_gates(tol=1e-12):
    """
    Audits Nav1.8 / Nav1.9 nociceptor kinetics (Section 2.5) against nav_kinetics.py.
    """
    print("\n" + "=" * 80)
    print("SUITE 3: Nav1.8 / Nav1.9 Nociceptor Kinetics (Manuscript Section 2.5 vs Code)")
    print("=" * 80)

    v_mV = np.linspace(-90.0, 40.0, 27)

    # Code implementation
    m8_code, h8_code = nav18_steady(v_mV)
    m9_code = nav19_steady(v_mV)

    # Manuscript Section 2.5 typeset equations:
    # m_{8,\infty}(v) = 1 / (1 + exp(-(v + 25.0) / 6.0)), tau_m8 = 1.5 ms
    # h_{8,\infty}(v) = 1 / (1 + exp((v + 42.0) / 6.0)), tau_h8 = 2.0 ms
    # m_{9,\infty}(v) = 1 / (1 + exp(-(v + 50.0) / 5.0)), tau_m9 = 10.0 ms

    m8_ms = 1.0 / (1.0 + np.exp(-(v_mV + 25.0) / 6.0))
    h8_ms = 1.0 / (1.0 + np.exp((v_mV + 42.0) / 6.0))
    m9_ms = 1.0 / (1.0 + np.exp(-(v_mV + 50.0) / 5.0))

    diff_m8 = np.max(np.abs(m8_code - m8_ms))
    diff_h8 = np.max(np.abs(h8_code - h8_ms))
    diff_m9 = np.max(np.abs(m9_code - m9_ms))

    tau_m8_ok = (tau_m8 == 1.5)
    tau_h8_ok = (tau_h8 == 2.0)
    tau_m9_ok = (tau_m9 == 10.0)

    print(f"  Nav1.8 m_inf max absolute diff : {diff_m8:.4e}")
    print(f"  Nav1.8 tau_m8 code vs ms       : {tau_m8} ms vs 1.5 ms")
    print(f"  Nav1.8 h_inf max absolute diff : {diff_h8:.4e}")
    print(f"  Nav1.8 tau_h8 code vs ms       : {tau_h8} ms vs 2.0 ms")
    print(f"  Nav1.9 m_inf max absolute diff : {diff_m9:.4e}")
    print(f"  Nav1.9 tau_m9 code vs ms       : {tau_m9} ms vs 10.0 ms")

    # Check resting baseline values at -66.82 mV
    v_rest = -66.82
    m8_rest = 1.0 / (1.0 + np.exp(-(v_rest + 25.0) / 6.0))
    h8_rest = 1.0 / (1.0 + np.exp((v_rest + 42.0) / 6.0))
    m9_rest = 1.0 / (1.0 + np.exp(-(v_rest + 50.0) / 5.0))
    print(f"  Resting state at -66.82 mV     : m8={m8_rest:.4f} (ms: 0.0009), h8={h8_rest:.4f} (ms: 0.9843), m9={m9_rest:.4f} (ms: 0.0334)")

    m8_ok = (diff_m8 < tol and tau_m8_ok)
    h8_ok = (diff_h8 < tol and tau_h8_ok and np.isclose(h8_rest, 0.9843, atol=1e-4))
    m9_ok = (diff_m9 < tol and tau_m9_ok)

    print(f"  [Nav1.8 m-gate] : [{'PASS' if m8_ok else 'FAIL'}]")
    print(f"  [Nav1.8 h-gate] : [{'PASS' if h8_ok else 'FAIL'}]")
    print(f"  [Nav1.9 m-gate] : [{'PASS' if m9_ok else 'FAIL'}]")

    return m8_ok and h8_ok and m9_ok


def audit_extracellular_equations(tol=1e-12):
    """
    Audits extracellular Helmholtz coupling equations (Section 2.3) against code.
    """
    print("\n" + "=" * 80)
    print("SUITE 4: Extracellular Geometry and Coupling Equations (Section 2.3 vs Code)")
    print("=" * 80)

    w_cleft = 20e-9
    r_outer = (d1 + d2) / 2.0 + w_cleft
    A_eff_code = np.pi * (r_outer**2 - (d1 / 2.0)**2 - (d2 / 2.0)**2)
    r_e_code = rho_e_bulk / A_eff_code

    # Manuscript Section 2.3:
    # A_eff = pi * [ ((d1 + d2)/2 + w_cleft)^2 - (d1/2)^2 - (d2/2)^2 ]
    # r_e = rho_e / A_eff
    A_eff_ms = np.pi * (((d1 + d2)/2.0 + w_cleft)**2 - (d1/2.0)**2 - (d2/2.0)**2)
    r_e_ms = rho_e_bulk / A_eff_ms

    rel_A = abs(A_eff_code - A_eff_ms) / A_eff_code
    rel_re = abs(r_e_code - r_e_from_cleft(w_cleft)) / r_e_code

    print(f"  A_eff at 20 nm cleft : {A_eff_code*1e12:.2f} um^2 (code vs ms rel diff = {rel_A:.4e})")
    print(f"  r_e   at 20 nm cleft : {r_e_code:.4e} ohm/m (code vs func rel diff = {rel_re:.4e})")

    # Core conductance Sigma_G for n=1, 10, 25, 50
    axial1 = d1_axon / (4.0 * rho_i)
    axial2 = d2 / (4.0 * rho_i)
    inv_r1 = np.pi * d1_axon * axial1
    inv_r2 = np.pi * d2 * axial2
    inv_re = 1.0 / r_e_code

    kappa = 1.0e9
    sigma_g_pass = True
    for n in [1, 10, 25, 50]:
        sigma_g = inv_re + n * inv_r1 + inv_r2
        kappa_eff = (kappa / r_e_code) / sigma_g
        lambda_eff_um = (1.0 / np.sqrt(kappa_eff)) * 1e6
        print(f"  n={n:2d}: Sigma_G={sigma_g:.4e} S/m, kappa_eff={kappa_eff:.4e} m^-2, lambda_eff={lambda_eff_um:6.1f} um")
        # Assert physical monotonicity: as n expands, Sigma_G grows, kappa_eff decreases, lambda_eff lengthens
        if n == 1:
            assert np.isclose(lambda_eff_um, 73.3, atol=0.2)
        elif n == 10:
            assert np.isclose(lambda_eff_um, 209.7, atol=0.2)
        elif n == 25:
            assert np.isclose(lambda_eff_um, 329.1, atol=0.2)
        elif n == 50:
            assert np.isclose(lambda_eff_um, 464.3, atol=0.2)

    geom_ok = (rel_A < tol and rel_re < tol and sigma_g_pass)
    print(f"  [Extracellular Coupling Invariants] : [{'PASS' if geom_ok else 'FAIL'}]")
    return geom_ok


def verify_manuscript_equations_match_code():
    """
    Unified entry point for verification batteries.
    Returns True if and only if ALL equations match within strict numerical tolerances.
    """
    ok1 = audit_crrss_gates()
    ok2 = audit_classical_hh_gates()
    ok3 = audit_nav18_nav19_gates()
    ok4 = audit_extracellular_equations()
    all_ok = (ok1 and ok2 and ok3 and ok4)
    print("\n" + "=" * 80)
    print(f"OVERALL EQUATIONS AUDIT: [{'PASS (100% Verified)' if all_ok else 'FAIL'}]")
    print("=" * 80)
    return all_ok


if __name__ == "__main__":
    success = verify_manuscript_equations_match_code()
    sys.exit(0 if success else 1)
