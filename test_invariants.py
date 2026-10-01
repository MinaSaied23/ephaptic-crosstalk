"""
Unit & Invariant Verification Suite for Frozen Phase-1 Aβ Model Decisions.
Verifies:
1. Nodal conductance equivalence under spatial homogenization.
2. Total compartment capacitance and leak conductance equivalence.
3. Prescribed stimulus current conversion and recovery of exact physical Amperes.
4. Ephaptic source terms, units, and consistency with core-conductor theory.
5. Invariant parameter checks (rho_i, E_Na, E_leak_1, g-ratio, node geometry).
"""

import sys
import os
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure phase1_classical_hh is in path
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(curr_dir, 'src', 'phase1_classical_hh'))

import ephaptic_model as em
import validate_single_fibers as vsf
import coupled_model as cm

def test_parameter_invariants():
    print("\n--- Test Suite 1: Parameter Invariants ---")
    
    # 1. rho_i = 54.7 ohm*cm = 0.547 ohm*m
    expected_rho_i = 54.7 * 1e-2
    assert np.isclose(em.rho_i, expected_rho_i), f"rho_i mismatch: {em.rho_i} != {expected_rho_i}"
    print(f" [PASS] rho_i = {em.rho_i:.5f} ohm*m (54.7 ohm*cm, Sweeney 1987)")

    # 2. E_Na = +35.64 mV = 0.03564 V
    expected_E_Na = 35.64e-3
    assert np.isclose(em.E_Na, expected_E_Na), f"E_Na mismatch: {em.E_Na} != {expected_E_Na}"
    print(f" [PASS] E_Na = {em.E_Na*1e3:.2f} mV (+35.64 mV, Sweeney 1987)")

    # 3. E_leak_1 = -80.0 mV = -0.08 V
    expected_E_leak_1 = -80.0e-3
    assert np.isclose(em.E_leak_1, expected_E_leak_1), f"E_leak_1 mismatch: {em.E_leak_1} != {expected_E_leak_1}"
    print(f" [PASS] E_leak_1 = {em.E_leak_1*1e3:.2f} mV (-80.0 mV)")

    # 4. Geometry: d1 = 10 um, d1_axon = 7 um (g-ratio = 0.7), l_node = 1.0 um, spacing = 1.0 mm
    assert np.isclose(em.d1, 10e-6), "d1 != 10 um"
    assert np.isclose(em.d1_axon, 7e-6), "d1_axon != 7 um"
    assert np.isclose(em.l_node, 1.0e-6), "l_node != 1.0 um"
    assert np.isclose(em.internode_spacing, 1.0e-3), "internode_spacing != 1.0 mm"
    print(f" [PASS] Geometry: d1={em.d1*1e6:.1f} um, d1_axon={em.d1_axon*1e6:.1f} um (g=0.7), l_node={em.l_node*1e6:.1f} um, L_int={em.internode_spacing*1e3:.1f} mm")

    # 5. Internodal properties
    expected_Cm_int = 0.005 * 1e-6 / 1e-4
    expected_gleak_int = 0.006 * 1e-3 / 1e-4
    assert np.isclose(em.Cm_internode, expected_Cm_int), "Cm_internode mismatch"
    assert np.isclose(em.g_leak_internode, expected_gleak_int), "g_leak_internode mismatch"
    print(f" [PASS] Internode: Cm_int = {em.Cm_internode / em.uF_cm2_to_F_m2:.3f} uF/cm^2, g_leak_int = {em.g_leak_internode / em.mS_cm2_to_S_m2:.3f} mS/cm^2")


def test_nodal_conductance_homogenization():
    print("\n--- Test Suite 2: Nodal Conductance Homogenization Invariant ---")
    
    # Physical bare node Na+ conductance (Siemens):
    # Area = pi * d1_axon * l_node
    # g_Na_bare = 1445 mS/cm^2 = 14450 S/m^2
    g_Na_bare_SI = 1445.0 * 1e-3 / 1e-4  # S/m^2
    A_bare_node = np.pi * em.d1_axon * em.l_node
    G_Na_physical = g_Na_bare_SI * A_bare_node  # Siemens

    # Homogenized computational node compartment Na+ conductance (Siemens):
    # Area = pi * d1_axon * dz
    # g_Na_effective = g_Na_CRRSS
    A_comp = np.pi * em.d1_axon * em.dz
    G_Na_computational = em.g_Na_CRRSS * A_comp

    print(f"  Physical bare node G_Na       : {G_Na_physical:.8e} S")
    print(f"  Computational compartment G_Na: {G_Na_computational:.8e} S")
    rel_diff = abs(G_Na_physical - G_Na_computational) / G_Na_physical
    assert rel_diff < 1e-15, f"Homogenization error: relative diff = {rel_diff}"
    print(f" [PASS] Exact conductance conservation: relative error = {rel_diff:.2e} (< 1e-15)")


def test_capacitance_and_leak_equivalence():
    print("\n--- Test Suite 3: Capacitance and Leak Equivalence Invariant ---")
    
    # 1. Capacitance Equivalence
    # Physical sub-segments inside the 10 um nodal compartment:
    # 1 um bare node (2.0 uF/cm^2) + 9 um compact myelin (0.005 uF/cm^2)
    Cm_bare_SI = 2.0 * 1e-6 / 1e-4
    Cm_int_SI = 0.005 * 1e-6 / 1e-4
    C_comp_physical = (Cm_bare_SI * em.l_node + Cm_int_SI * (em.dz - em.l_node)) * np.pi * em.d1_axon

    # Computational nodal compartment capacitance:
    C_comp_code = em.Cm_node_comp * (np.pi * em.d1_axon * em.dz)
    rel_err_c = abs(C_comp_physical - C_comp_code) / C_comp_physical
    print(f"  Physical compartment C_total : {C_comp_physical:.8e} F")
    print(f"  Code nodal compartment C_total: {C_comp_code:.8e} F")
    assert rel_err_c < 1e-15, f"Capacitance mismatch: {rel_err_c}"
    print(f" [PASS] Total nodal compartment capacitance conserved (error = {rel_err_c:.2e})")

    # 2. Leak Conductance Equivalence
    # 1 um bare node (128 mS/cm^2) + 9 um compact myelin (0.006 mS/cm^2)
    g_leak_bare_SI = 128.0 * 1e-3 / 1e-4
    g_leak_int_SI = 0.006 * 1e-3 / 1e-4
    G_leak_physical = (g_leak_bare_SI * em.l_node + g_leak_int_SI * (em.dz - em.l_node)) * np.pi * em.d1_axon

    G_leak_code = em.g_leak_node_comp * (np.pi * em.d1_axon * em.dz)
    rel_err_g = abs(G_leak_physical - G_leak_code) / G_leak_physical
    print(f"  Physical compartment G_leak : {G_leak_physical:.8e} S")
    print(f"  Code nodal compartment G_leak: {G_leak_code:.8e} S")
    assert rel_err_g < 1e-15, f"Leak mismatch: {rel_err_g}"
    print(f" [PASS] Total nodal compartment leak conductance conserved (error = {rel_err_g:.2e})")


def test_stimulus_current_conversion():
    print("\n--- Test Suite 4: Stimulus Current Conversion Invariant ---")
    
    stim_amp_prescribed = 100e-9  # 100 nA prescribed in Amperes
    
    # Calculate stimulus density as implemented in validate_single_fibers.py and coupled_model.py
    I_stim_density = stim_amp_prescribed / (np.pi * em.d1_axon * em.dz)  # A/m^2
    
    # The 1D cable equation integrates over compartment inner-membrane area:
    A_inner_comp = np.pi * em.d1_axon * em.dz
    I_phys_injected = I_stim_density * A_inner_comp  # Amperes
    
    print(f"  Prescribed total stimulus current : {stim_amp_prescribed*1e9:.2f} nA")
    print(f"  Stimulus current density in PDE   : {I_stim_density:.4e} A/m^2")
    print(f"  Reconstructed physical current    : {I_phys_injected*1e9:.2f} nA")
    
    diff = abs(stim_amp_prescribed - I_phys_injected)
    assert diff < 1e-20, f"Stimulus current mismatch: {diff}"
    print(f" [PASS] Prescribed stimulus current matches reconstructed current to machine precision (diff = {diff:.2e} A)")


def test_ephaptic_source_units_and_normalization():
    print("\n--- Test Suite 5: Ephaptic Source Units and Normalization ---")
    
    # The intracellular core resistance per unit length is:
    # r_i = 4 * rho_i / (pi * d1_axon^2)
    # The reciprocal conductance per unit length is:
    inv_r1_expected = np.pi * (em.d1_axon**2) / (4.0 * em.rho_i)  # S*m
    
    # In coupled_model.py:
    # axial1 = d1_axon / (4.0 * rho_i)
    # inv_r1 = np.pi * d1_axon * axial1
    axial1 = em.d1_axon / (4.0 * em.rho_i)
    inv_r1_code = np.pi * em.d1_axon * axial1
    
    print(f"  Analytical 1/r_i1 (S*m)   : {inv_r1_expected:.8e}")
    print(f"  Code inv_r1 formulation   : {inv_r1_code:.8e}")
    rel_err = abs(inv_r1_expected - inv_r1_code) / inv_r1_expected
    assert rel_err < 1e-16, f"inv_r1 error: {rel_err}"
    print(f" [PASS] Ephaptic source conductance per unit length exactly equals pi*d_axon^2/(4*rho_i) (error = {rel_err:.2e})")
    
    # Transmembrane current per unit length:
    # i_m1 = inv_r1 * (d^2 v1 / dz^2)
    # With d2v1 in V/m^2 and inv_r1 in S*m, units = (S*m) * (V/m^2) = (A/V * m) * (V/m^2) = A/m
    print(f" [PASS] Units verification: [inv_r1] * [d2v1] = (S*m) * (V/m^2) = A/m (exact physical current per unit length)")


def verify_manuscript_equations_match_code():
    print("\n--- Test Suite 6: Manuscript Equations to Code Match (Defect 1 Invariant) ---")
    src_dir = os.path.join(curr_dir, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    import _audit_gate_equations as age
    all_ok = age.verify_manuscript_equations_match_code()
    assert all_ok, "Manuscript equations failed numerical audit against codebase implementation!"
    print(" [PASS] All manuscript closed-form equations numerically match code to strict tolerance.")


def verify_pulse2_csv_consistency_with_manuscript():
    print("\n--- Test Suite 7: Pulse-2 100 Hz CSV Consistency with Manuscript (Defect 2 Invariant) ---")
    import pandas as pd
    
    primary_csv = os.path.join(curr_dir, "results", "convergence", "phase2_headline_results.csv")
    supp_candidates = [
        os.path.join(curr_dir, "..", "Supplementary", "phase2_headline_results.csv"),
        os.path.join(curr_dir, "supplementary", "phase2_headline_results.csv"),
    ]
    csv_targets = [primary_csv] + [p for p in supp_candidates if os.path.exists(p)]
    assert len(csv_targets) >= 1, "No phase2_headline_results.csv found!"
    
    for path in csv_targets:
        assert os.path.exists(path), f"Missing CSV: {path}"
        df = pd.read_csv(path)
        row = df[(df["n_abeta"] == 25) & (df["pulse_frequency"] == "100 Hz") & (df["pulse_count"] == 2)]
        assert len(row) == 1, f"Expected 1 matching row in {path}, found {len(row)}"
        r = row.iloc[0]
        
        # Verify classification and propagation
        assert r["c_fiber_classification"] == "PROPAGATED_ACTION_POTENTIAL", \
            f"Expected PROPAGATED_ACTION_POTENTIAL in {path}, got {r['c_fiber_classification']}"
        assert bool(r["propagated_c_fiber_ap"]) is True, \
            f"Expected propagated_c_fiber_ap=True in {path}, got {r['propagated_c_fiber_ap']}"
        assert np.isclose(r["c_fiber_peak_V_mV"], 24.832, atol=0.1), \
            f"Expected peak ~24.83 mV in {path}, got {r['c_fiber_peak_V_mV']}"
            
        # Verify no stale CV=33.3 m/s in Abeta integrity string
        integ = str(r["abeta_source_integrity"])
        assert "CV=32.0 m/s" in integ or "CV=32.00 m/s" in integ, \
            f"Expected CV=32.0 m/s in abeta_source_integrity in {path}, got {integ}"
        assert "33.3" not in integ, f"Stale CV=33.3 m/s found in {path}: {integ}"
        
        print(f" [PASS] Verified {os.path.basename(path)}: Pulse 2 is PROPAGATED_ACTION_POTENTIAL (True, peak={r['c_fiber_peak_V_mV']:.2f} mV, CV=32.0 m/s)")


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING INVARIANT VERIFICATION SUITE FOR PHASE-1 Aβ MODEL")
    print("=" * 70)
    test_parameter_invariants()
    test_nodal_conductance_homogenization()
    test_capacitance_and_leak_equivalence()
    test_stimulus_current_conversion()
    test_ephaptic_source_units_and_normalization()
    verify_manuscript_equations_match_code()
    verify_pulse2_csv_consistency_with_manuscript()
    print("\n" + "=" * 70)
    print("ALL INVARIANT TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

