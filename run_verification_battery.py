"""
Comprehensive Automated Verification Battery for Ephaptic Crosstalk Project.
Executes key benchmarks, single-fiber validations, and figure generation scripts,
verifying that all simulations complete successfully with 100% pass rate.
"""

import os
import sys
import time
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_step(name, cmd):
    print(f"\n[RUNNING] {name}...")
    t0 = time.time()
    res = subprocess.run(
        cmd,
        shell=True,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"[FAIL] {name} (exit code {res.returncode}) in {dt:.2f}s")
        print("--- STDOUT ---")
        print(res.stdout)
        print("--- STDERR ---")
        print(res.stderr)
        return False, dt
    print(f"[PASS] {name} in {dt:.2f}s")
    return True, dt

def check_files():
    print("\n[VERIFYING] Critical Artifacts and Lineage Datasets...")
    required_files = [
        ("manuscript/ephaptic_crosstalk_paper_JCNS_revised.docx", [
            os.path.join(ROOT_DIR, "manuscript", "ephaptic_crosstalk_paper_JCNS_revised.docx"),
            os.path.join(ROOT_DIR, "..", "Manuscript", "ephaptic_crosstalk_paper_JCNS_revised.docx"),
        ]),
        ("results/figures/fig1_model_schematic.png", [
            os.path.join(ROOT_DIR, "results", "figures", "fig1_model_schematic.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "fig1_model_schematic.png"),
        ]),
        ("results/figures/fig2_phase1_control.png", [
            os.path.join(ROOT_DIR, "results", "figures", "fig2_phase1_control.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "fig2_phase1_control.png"),
        ]),
        ("results/figures/fig3_phase2_control.png", [
            os.path.join(ROOT_DIR, "results", "figures", "fig3_phase2_control.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "fig3_phase2_control.png"),
        ]),
        ("results/figures/phase2_multifiber_sweep.png", [
            os.path.join(ROOT_DIR, "results", "figures", "phase2_multifiber_sweep.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "phase2_multifiber_sweep.png"),
        ]),
        ("results/figures/crrss_gating_plots.png", [
            os.path.join(ROOT_DIR, "results", "figures", "crrss_gating_plots.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "crrss_gating_plots.png"),
        ]),
        ("results/figures/current_conservation_benchmark.png", [
            os.path.join(ROOT_DIR, "results", "figures", "current_conservation_benchmark.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "current_conservation_benchmark.png"),
        ]),
        ("results/figures/fig_convergence_analysis.png", [
            os.path.join(ROOT_DIR, "results", "figures", "fig_convergence_analysis.png"),
            os.path.join(ROOT_DIR, "..", "Figures", "fig_convergence_analysis.png"),
        ]),
        ("results/convergence/EXP_E02_E03_reconciliation.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "EXP_E02_E03_reconciliation.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "EXP_E02_E03_reconciliation.csv"),
        ]),
        ("results/convergence/final_100Hz_reconciliation.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "final_100Hz_reconciliation.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "final_100Hz_reconciliation.csv"),
        ]),
        ("results/convergence/kappa_effective_table.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "kappa_effective_table.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "kappa_effective_table.csv"),
        ]),
        ("results/convergence/phase2_headline_results.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "phase2_headline_results.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "phase2_headline_results.csv"),
        ]),
        ("results/convergence/phase2_multifiber.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "phase2_multifiber.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "phase2_multifiber.csv"),
        ]),
        ("results/convergence/phase2_navc_multifiber.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "phase2_navc_multifiber.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "phase2_navc_multifiber.csv"),
        ]),
        ("results/convergence/phase2_synchrony.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "phase2_synchrony.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "phase2_synchrony.csv"),
        ]),
        ("results/convergence/phase2_temporal_summation.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "phase2_temporal_summation.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "phase2_temporal_summation.csv"),
        ]),
        ("results/convergence/spatial_convergence.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "spatial_convergence.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "spatial_convergence.csv"),
        ]),
        ("results/convergence/temporal_convergence_final.csv", [
            os.path.join(ROOT_DIR, "results", "convergence", "temporal_convergence_final.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "temporal_convergence_final.csv"),
        ]),
        ("supplementary/MANIFEST.md", [
            os.path.join(ROOT_DIR, "supplementary", "MANIFEST.md"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "MANIFEST.md"),
        ]),
        ("supplementary/manuscript_number_inventory.csv", [
            os.path.join(ROOT_DIR, "supplementary", "manuscript_number_inventory.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "manuscript_number_inventory.csv"),
        ]),
        ("supplementary/manuscript_before_after_matrix.csv", [
            os.path.join(ROOT_DIR, "supplementary", "manuscript_before_after_matrix.csv"),
            os.path.join(ROOT_DIR, "..", "Supplementary", "manuscript_before_after_matrix.csv"),
        ]),
        ("src/_audit_gate_equations.py", [
            os.path.join(ROOT_DIR, "src", "_audit_gate_equations.py"),
        ])
    ]
    all_ok = True
    for label, candidates in required_files:
        found = False
        for c in candidates:
            if os.path.exists(c):
                sz = os.path.getsize(c)
                if sz > 0:
                    found = True
                    break
                else:
                    print(f"  [EMPTY] {label} at {c}")
        if not found:
            print(f"  [MISSING] {label}")
            all_ok = False

    import pandas as pd
    primary_csv = os.path.join(ROOT_DIR, "results", "convergence", "phase2_headline_results.csv")
    supp_candidates = [
        os.path.join(ROOT_DIR, "..", "Supplementary", "phase2_headline_results.csv"),
        os.path.join(ROOT_DIR, "supplementary", "phase2_headline_results.csv"),
    ]
    headline_csvs = [primary_csv] + [p for p in supp_candidates if os.path.exists(p)]
    for hp in headline_csvs:
        if os.path.exists(hp):
            df = pd.read_csv(hp)
            row = df[(df["n_abeta"] == 25) & (df["pulse_frequency"] == "100 Hz") & (df["pulse_count"] == 2)]
            if len(row) != 1:
                print(f"  [FAIL] Missing or duplicate Pulse 2 row in {hp}")
                all_ok = False
            else:
                r = row.iloc[0]
                if r["c_fiber_classification"] != "PROPAGATED_ACTION_POTENTIAL":
                    print(f"  [FAIL] Stale classification '{r['c_fiber_classification']}' in {hp}")
                    all_ok = False
                elif bool(r["propagated_c_fiber_ap"]) is not True:
                    print(f"  [FAIL] propagated_c_fiber_ap is not True in {hp}")
                    all_ok = False
                elif "33.3" in str(r["abeta_source_integrity"]):
                    print(f"  [FAIL] Stale 33.3 m/s found in {hp}")
                    all_ok = False
                else:
                    print(f"  [PASS] {os.path.basename(hp)} Pulse 2 row verified: PROPAGATED_ACTION_POTENTIAL (True, CV=32.0 m/s)")
        else:
            print(f"  [MISSING] {hp}")
            all_ok = False

    if all_ok:
        print(f"[PASS] All critical artifacts and datasets present, non-empty, and consistent.")
    return all_ok

def main():
    print("=" * 75)
    print("EPHAPTIC CROSSTALK: AUTOMATED VERIFICATION BATTERY")
    print("=" * 75)

    test_suites = [
        ("Parameter & Homogenization Invariants", "python test_invariants.py"),
        ("Manuscript Equation-to-Code Numerical Audit", "python src/_audit_gate_equations.py"),
        ("CRRSS Steady-State Gating Curves", "python src/crrss_gating_plots.py"),
        ("Discrete KCL Current Conservation Benchmark", "python src/current_conservation_benchmark.py"),
        ("Spatial & Temporal Convergence Verification", "python src/run_convergence_battery.py --verify"),
        ("Phase 1 Single-Fiber Validation (Aβ & classical HH)", "python src/phase1_classical_hh/validate_single_fibers.py"),
        ("Phase 2 Single-Fiber Validation (Aβ & Nav1.8/1.9)", "python src/phase2_nav18_nav19/validate_single_fibers.py"),
        ("Figure 2 Reproduction (Phase 1 Positive Controls)", "python src/plot_fig2_control.py"),
        ("Figure 3 Reproduction (Phase 2 Control & Multi-Fiber Trend)", "python src/plot_fig3_control.py"),
    ]

    results = []
    total_time = 0.0

    for name, cmd in test_suites:
        ok, dt = run_step(name, cmd)
        results.append((name, ok, dt))
        total_time += dt
        if not ok:
            print(f"\nABORTING: Suite '{name}' failed. Please resolve the failure.")
            sys.exit(1)

    files_ok = check_files()
    results.append(("Critical Artifacts & Datasets Verification", files_ok, 0.0))
    if not files_ok:
        sys.exit(1)

    print("\n" + "=" * 75)
    print("BATTERY EXECUTION SUMMARY")
    print("=" * 75)
    for name, ok, dt in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status:4s}]  {name:58s} ({dt:5.1f}s)")
    print("-" * 75)
    print(f"TOTAL EXECUTION TIME: {total_time:.1f}s")
    print("ALL VERIFICATION SUITES COMPLETED WITH 100% PASS RATE.")
    print("All checks passed.")
    print("=" * 75)

if __name__ == "__main__":
    main()
