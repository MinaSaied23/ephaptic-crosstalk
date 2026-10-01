# Computational Provenance Manifest: Claim-to-Code Traceability

**Manuscript:** *Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation*  
**Target Journal:** *Journal of Computational Neuroscience* (JCNS)  
**Author:** Mina Saied Attia Rizk  
**Date:** September 27, 2026  

---

## 1. Overview & Provenance Architecture

This document establishes the end-to-end provenance chain for every quantitative claim, table, and figure appearing in the revised manuscript and reviewer-response letter. Each entry traces directly from:
1. **The Claim & Stated Location:** Exact manuscript section and quoted statement.
2. **Numerical Value & Units:** Nominal value, baseline reference, and physical units.
3. **Source Simulation Code:** Script implementing the numerical integration.
4. **Configuration / Parameters:** Physical constants, spatial/temporal discretization ($\Delta z, \Delta t$), and coupling parameter ($\kappa$).
5. **Raw Output Data:** Generated CSV/dat files storing raw numerical values.
6. **Plotting / Tabulation Pipeline:** Exact script generating the visual figure or table.
7. **Final Deliverable:** Embedded figure or table in the manuscript.

---

> **Numbering note.** FIG-xx / FIG-BMx identifiers are internal. Manuscript numbering: Fig. 1 = FIG-01, Fig. 2 = FIG-BM1, Fig. 3 = FIG-BM2, Fig. 4 = FIG-BM3, Fig. 5 = FIG-02, Fig. 6 = FIG-03, Fig. 7 = FIG-04. TAB-0x identifiers equal the manuscript table numbers. Fig. 5a uses a 2 nA stimulus; all coupled runs use 100 nA.

## 2. Main-Text Tables & Figures Provenance

### FIG-01: Figure 1: Model Architecture Schematic
- **Manuscript Location:** Sec. 2.1 (Line 39)
- **Source Script:** `N/A (Vector Diagram)`
- **Configuration / Parameters:** Two-fiber coupled core-conductor schematic (CRRSS Aβ + HH/Nav1.8/1.9 C-fiber) with regularized Poisson coupling
- **Raw Output File:** `N/A (Visual architecture)`
- **Plotting / Tabulation Pipeline:** `results/figures/fig1_model_schematic.png`
- **Produced Artifact:** Figure 1 (Embedded in Section 2.1)

### FIG-02: Manuscript Fig. 5: Positive Controls (Uncoupled Fibers)
- **Manuscript Location:** Sec. 3.1 (Line 196)
- **Source Script:** `src/plot_fig2_control.py`
- **Configuration / Parameters:** Uncoupled single fibers (r_e = 0): Aβ alone (2 nA/0.2 ms), C-fiber alone (1 nA/1 ms), dz=10 um, dt=2.5 us
- **Raw Output File:** `results/convergence/spatial_convergence.csv (dz=10 um row)`
- **Plotting / Tabulation Pipeline:** `src/plot_fig2_control.py`
- **Produced Artifact:** manuscript Fig. 5 (Panels a & b: Aβ saltatory CV 41.03 m/s, C-fiber CV 0.41 m/s)

### FIG-03: Manuscript Fig. 6: Phase 2 Controls & Multi-Fiber Trend
- **Manuscript Location:** Sec. 3.7 (Line 239)
- **Source Script:** `src/plot_fig3_control.py`
- **Configuration / Parameters:** Phase 2 Nav1.8/Nav1.9 model: 20 ms settling, isolated CV (2 nA/1 ms), coupled pulse w_cleft=20 nm, n in [1, 50], kappa=1.0e9 m^-2
- **Raw Output File:** `results/convergence/phase2_headline_results.csv`
- **Plotting / Tabulation Pipeline:** `src/plot_fig3_control.py`
- **Produced Artifact:** manuscript Fig. 6 (Panels a, b, c: isolated CV 0.26 m/s, coupled humps, multi-fiber saturation near -56.4 mV (n up to 50))

### FIG-04: Manuscript Fig. 7: Phase 2 Multi-Fiber Sweep (Authoritative)
- **Manuscript Location:** Sec. 3.7 (Line 268)
- **Source Script:** `src/phase2_multifiber_sweep.py`
- **Configuration / Parameters:** Nav1.8/Nav1.9 C-fiber, w_cleft=20 nm, kappa=1.0e9 m^-2, settled rest -66.82 mV, n in [1, 50], jitter=0.0 ms vs 1.5 ms
- **Raw Output File:** `results/convergence/phase2_navc_multifiber.csv`
- **Plotting / Tabulation Pipeline:** `src/phase2_multifiber_sweep.py`
- **Produced Artifact:** manuscript Fig. 7 (phase2_multifiber_sweep.png: n=1 -> -65.07 mV; n=10 -> -58.84 mV; n=25 -> -56.66 mV; n=50 -> -56.40 mV; jittered n=25 -> -66.20 mV)

### FIG-BM1 (manuscript Fig. 2): Benchmark: CRRSS Steady-State Gating Curves
- **Manuscript Location:** Sec. 2.2.1 (Line 72)
- **Source Script:** `src/crrss_gating_plots.py`
- **Configuration / Parameters:** Corrected Chiu et al. (1979) rate equations, V in [-100, +50] mV
- **Raw Output File:** `Analytical gating curves`
- **Plotting / Tabulation Pipeline:** `src/crrss_gating_plots.py`
- **Produced Artifact:** crrss_gating_plots.png (Monotonic h_inf inactivation, V_1/2 = -74.5 mV)

### FIG-BM2 (manuscript Fig. 3): Benchmark: Discrete Kirchhoff's Current Law Conservation
- **Manuscript Location:** Sec. 2.3 (Line 114)
- **Source Script:** `src/current_conservation_benchmark.py`
- **Configuration / Parameters:** w_cleft=100 nm, kappa=1.0e9 m^-2, dt=2.5 us, dz=10 um
- **Raw Output File:** `Calculated discrete KCL residual across 1000 nodes`
- **Plotting / Tabulation Pipeline:** `src/current_conservation_benchmark.py`
- **Produced Artifact:** current_conservation_benchmark.png (KCL residual < 10^-16 A/m)

### FIG-BM3 (manuscript Fig. 4): Benchmark: Spatial Grid Refinement (Fixed Node)
- **Manuscript Location:** Sec. 2.4.1 (Line 133)
- **Source Script:** `src/run_convergence_battery.py`
- **Configuration / Parameters:** Fixed l_node=1.0 um, dt=2.5 us, dz in [20, 10, 5, 2.5, 1.25, 1.0] um, w_cleft=20 nm, n=25, kappa=1.0e9 m^-2
- **Raw Output File:** `results/convergence/spatial_convergence.csv`
- **Plotting / Tabulation Pipeline:** `src/plot_convergence_figure.py`
- **Produced Artifact:** fig_convergence_analysis.png (Spatial stability across grid refinements)

### TAB-01: Table 1: Phase 1 Experimental Summary
- **Manuscript Location:** Sec. Experimental Summary Tables (Line 351)
- **Source Script:** `src/phase1_classical_hh/coupled_model.py`, `src/run_canonical_100hz.py`, `src/interior_lesion_test.py`, & `src/run_lesion_audit.py`
- **Configuration / Parameters:** Classical HH C-fiber, w_cleft in [20 nm, 5 um], single-pulse, bias, 100 Hz train (1, 2, 3, 5, 10 pulses, T>=35 ms), and grounded interior lesion control
- **Raw Output File:** `results/convergence/final_100Hz_reconciliation.csv` & `run_lesion_audit.py`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 1 (Pulse 1: +5.04 mV mid / +6.01 mV max; Pulse 2 window: +24.70 mV propagated AP (spike initiated by Pulse 1); CV 0.41 m/s; Interior lesion control: strictly subthreshold)

### TAB-02: Table 2: Phase 2 Experimental Summary
- **Manuscript Location:** Sec. Experimental Summary Tables (Line 366)
- **Source Script:** `src/phase2_nav18_nav19/coupled_navc_model.py & src/phase2_multifiber_sweep.py`
- **Configuration / Parameters:** Nav1.8/Nav1.9 C-fiber, 20 ms pre-stimulus settling (rest -66.82 mV), w_cleft=20 nm, n=25 synchronous vs 1.5 ms jitter
- **Raw Output File:** `results/convergence/phase2_headline_results.csv & phase2_navc_multifiber.csv`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 2 (Single-pulse < 1.0 mV; n=25 sync: -56.66 mV / Delta V = 10.16 mV; jittered: -66.20 mV / Delta V = 0.63 mV)

### TAB-03: Table 3: Nomenclature and Parameter Definitions
- **Manuscript Location:** Sec. Nomenclature (Line 323)
- **Source Script:** `Analytical derivation & Sweeney et al. (1987) / Hodgkin & Huxley (1952)`
- **Configuration / Parameters:** All SI definitions, core resistances, dimensions, capacitances, conductances
- **Raw Output File:** `Derived parameter formulas`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 3 (Comprehensive symbol, parameter, unit, and definition matrix)

### TAB-04: Table 4: Phase 1 Multi-Fiber Spatial Summation Sweep
- **Manuscript Location:** Sec. Experimental Summary Tables (Line 379)
- **Source Script:** `src/run_phase2_multifiber.py (Phase 1 Classical-HH configuration) & src/compute_kappa_table.py`
- **Configuration / Parameters:** Phase 1 Classical HH, w_cleft=20 nm, kappa=1.0e9 m^-2, n in [1, 50], rest = -65.000 mV
- **Raw Output File:** `results/convergence/phase2_multifiber.csv & kappa_effective_table.csv`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 4 (Full n-series: Delta V, peak V2 downstream, midpoint V2, Abeta CV, kappa_eff, lambda_eff)

### TAB-05: Table 5: Spatial Grid Refinement (Fixed Physical Node)
- **Manuscript Location:** Sec. Experimental Summary Tables (Line 396)
- **Source Script:** `src/run_convergence_battery.py`
- **Configuration / Parameters:** l_node=1.0 um fixed, dt=2.5 us, dz in [20, 10, 5, 2.5, 1.25, 1.0] um, w_cleft=20 nm, n=1 and n=25
- **Raw Output File:** `results/convergence/spatial_convergence.csv`
- **Plotting / Tabulation Pipeline:** `python src/run_convergence_battery.py` (rows transcribed into Table 5)
- **Produced Artifact:** Table 5 (Abeta CV 41.03 m/s and excursion 80.44 mV at every grid step; Delta V single-pair 1.237 -> 1.354 mV; n=25 5.919 -> 6.050 mV)

---

## 3. Individual Numerical Claims Provenance (Full Inventory)

| Claim ID | Manuscript Location | Stated Quantity & Claim | Value | Baseline | Units | Source Code / Origin | Raw Output File & Row | Status |
|:---:|---|---|:---:|:---:|:---:|---|---|:---:|
| **CLM-01** | Sec. 2.2.1, 3.1 | Isolated Aβ Conduction Velocity | `41.03` | N/A | m/s | `results/convergence/spatial_convergence.csv` | `row 2 (dz=10.0 um)` | **VERIFIED_FROZEN** |
| **CLM-02** | Sec. 2.2.1, 3.1 | Isolated Aβ Action Potential Excursion | `80.44 (peak +0.44 from rest -80.0)` | -80.0 mV | mV | `results/convergence/spatial_convergence.csv` | `row 2 (dz=10.0 um)` | **VERIFIED_FROZEN** |
| **CLM-03** | Sec. 2.2.1, 3.1 | Isolated Aβ Resting Baseline Drift | `< 10 µV` | N/A | µV | `src/phase1_classical_hh/ephaptic_model.py` | `Resting potential equilibrium test` | **VERIFIED_FROZEN** |
| **CLM-04** | Sec. 2.4.3 | Aβ Reference Solver CV Comparison | `40.00 vs 39.51` | Isolated CV 40.0 m/s | m/s | `audit_reference_solver.py` | `python src/audit_reference_solver.py` | **VERIFIED_FROZEN** |
| **CLM-05** | Sec. 2.4.3 | Aβ Reference Solver Peak Amplitude Comparison | `79.98 vs 79.78` | N/A | mV | `audit_reference_solver.py` | `python src/audit_reference_solver.py` | **VERIFIED_FROZEN** |
| **CLM-06** | Sec. 2.2.2, 3.1 | Isolated Classical C-Fiber CV | `0.41` | N/A | m/s | `results/convergence/phase2_headline_results.csv` | `positive_control.py; row 4` | **VERIFIED_FROZEN** |
| **CLM-07** | Sec. 2.2.2, 3.1 | Isolated Classical C-Fiber Peak Potential | `+24.7 (+24.77)` | N/A | mV | `results/convergence/phase2_headline_results.csv` | `positive_control.py` | **VERIFIED_FROZEN** |
| **CLM-08** | Sec. 2.5, 3.7 | Nav1.8/Nav1.9 C-Fiber Resting Potential | `-66.82` | N/A | mV | `src/phase2_nav18_nav19/coupled_navc_model.py` | `get_settled_c_fiber; phase2_navc_multifiber.csv` | **VERIFIED_FROZEN** |
| **CLM-09** | Sec. 3.7 | Isolated Nav1.8/Nav1.9 C-Fiber CV | `0.26` | N/A | m/s | `results/figures/fig3_phase2_control.png` | `Phase 2 positive control` | **VERIFIED_FROZEN** |
| **CLM-10** | Sec. 3.9.1, Fig. 7 | Phase 2 Multi-Fiber Midpoint Peak (n=25, synchronous) | `-56.66 (ΔV = 10.16)` | N/A | mV | `results/convergence/phase2_navc_multifiber.csv` | `row 7 (n=25, j=0.0 ms)` | **VERIFIED_FROZEN** |
| **CLM-11** | Sec. 3.9.2, Fig. 7 | Phase 2 Multi-Fiber Midpoint Peak (n=25, 1.5 ms jitter) | `-66.20 (ΔV = 0.63)` | N/A | mV | `results/convergence/phase2_navc_multifiber.csv` | `row 17 (n=25, j=1.5 ms)` | **VERIFIED_FROZEN** |
| **CLM-12** | Sec. 3.2, Table 1 | Single-Pulse Single-Pair Downstream Peak ΔV (n=1) | `1.325` | N/A | mV | `results/convergence/phase2_headline_results.csv` | `row 1 (single pulse, n=1)` | **VERIFIED_FROZEN** |
| **CLM-13** | Sec. 3.2, Table 4 | Single-Pulse Single-Pair Midpoint Peak ΔV (n=1) | `1.289` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 1 (n=1)` | **VERIFIED_FROZEN** |
| **CLM-14** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=2) | `2.240` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 2 (n=2)` | **VERIFIED_FROZEN** |
| **CLM-15** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=5) | `3.763` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 3 (n=5)` | **VERIFIED_FROZEN** |
| **CLM-16** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=10) | `4.929` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 4 (n=10)` | **VERIFIED_FROZEN** |
| **CLM-17** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=15) | `5.507` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 5 (n=15)` | **VERIFIED_FROZEN** |
| **CLM-18** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=20) | `5.829` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 6 (n=20)` | **VERIFIED_FROZEN** |
| **CLM-19** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=25) | `6.015` | N/A | mV | `results/convergence/EXP_E02_E03_reconciliation.csv` | `row 1 (downstream max)` | **VERIFIED_FROZEN** |
| **CLM-20** | Sec. 3.9.1, Table 4 | Multi-Fiber Midpoint Peak ΔV (n=25) | `5.039` | N/A | mV | `results/convergence/EXP_E02_E03_reconciliation.csv` | `row 2 (midpoint)` | **VERIFIED_FROZEN** |
| **CLM-21** | Sec. 3.9.1, Table 4 | Coupled Aβ Bundle CV (n=25) | `32.00` | N/A | m/s | `results/convergence/phase2_multifiber.csv` | `row 7 (n=25); final_100Hz_reconciliation.md` | **VERIFIED_FROZEN** |
| **CLM-22** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=30) | `6.121` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 8 (n=30)` | **VERIFIED_FROZEN** |
| **CLM-23** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=40) | `6.197` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 9 (n=40)` | **VERIFIED_FROZEN** |
| **CLM-24** | Sec. 3.9.1, Table 4 | Multi-Fiber Downstream Peak ΔV (n=50) | `6.184` | N/A | mV | `results/convergence/phase2_multifiber.csv` | `row 10 (n=50)` | **VERIFIED_FROZEN** |
| **CLM-25** | Sec. 3.9.2, Table 1 | Phase 1 Jitter Attenuation Ratio (n=25) | `92.9` | N/A | % | `results/convergence/phase2_synchrony.csv` (legacy filename; Phase 1 classical-HH synchrony configuration) | `row n_abeta = 25, jitter_ms = 1.5 (attenuation computed from downstream maxima, 6.015 -> 0.426 mV)` | **VERIFIED_FROZEN** |
| **CLM-26** | Sec. 3.9.2 | Phase 1 Jittered Peak Depolarization (n=25) | `0.426` | N/A | mV | `results/convergence/phase2_synchrony.csv` (legacy filename; Phase 1 classical-HH synchrony configuration) | `row 11` | **VERIFIED_FROZEN** |
| **CLM-27** | Sec. 3.7, Sec. 3.9.2, Fig. 7, Table 2 | Phase 2 Jitter Attenuation Ratio (n=25) | `93.8` | N/A | % | `results/convergence/phase2_navc_multifiber.csv` | `row 17 (jitter 1.5 ms, n=25)` | **VERIFIED_FROZEN** |
| **CLM-28** | Sec. 3.5, Table 1 | 100 Hz Train Pulse 1 C-Fiber Peak Potential | `-58.99 (downstream), -59.96 (midpoint)` | N/A | mV | `results/convergence/final_100Hz_reconciliation.csv` | `row 1 (pulse 1)` | **VERIFIED_FROZEN** |
| **CLM-29** | Sec. 3.5, Table 1 | 100 Hz Train Pulse Window in Which First Propagated Spike Is Recorded | `2` | N/A | dimensionless | `results/convergence/final_100Hz_reconciliation.csv` | `row 2 (pulse 2); final_100Hz_reconciliation.md` | **VERIFIED_FROZEN** |
| **CLM-30** | Sec. 3.5, Table 1 | 100 Hz Train Pulse-2-Window Downstream Peak Voltage | `+24.70` | N/A | mV | `results/convergence/final_100Hz_reconciliation.csv` | `row 2 (downstream peak)` | **VERIFIED_FROZEN** |
| **CLM-31** | Sec. 3.5, Table 1 | 100 Hz Train Pulse-2-Window Midpoint Peak Voltage | `+24.83` | N/A | mV | `results/convergence/final_100Hz_reconciliation.csv` | `row 2 (midpoint peak)` | **VERIFIED_FROZEN** |
| **CLM-32** | Sec. 3.5 | Truncation Artifact In-Flight AP Location | `2.1` | N/A | mm | `results/convergence/final_100Hz_reconciliation.md` | `Section 1.1 mathematical demonstration` | **VERIFIED_FROZEN** |
| **CLM-33** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 20 um | `41.03 (CV), 80.44 (Excursion), 1.237 (n=1), 5.919 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 1 (dz=20 um)` | **VERIFIED_FROZEN** |
| **CLM-34** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 10 um (Nominal) | `41.03 (CV), 80.44 (Excursion), 1.325 (n=1), 6.015 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 2 (dz=10 um)` | **VERIFIED_FROZEN** |
| **CLM-35** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 5 um | `41.03 (CV), 80.44 (Excursion), 1.347 (n=1), 6.041 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 3 (dz=5 um)` | **VERIFIED_FROZEN** |
| **CLM-36** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 2.5 um | `41.03 (CV), 80.44 (Excursion), 1.352 (n=1), 6.047 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 4 (dz=2.5 um)` | **VERIFIED_FROZEN** |
| **CLM-36a** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 1.25 um | `41.03 (CV), 80.44 (Excursion), 1.353 (n=1), 6.049 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 5 (dz=1.25 um)` | **VERIFIED_FROZEN** |
| **CLM-36b** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 1.0 um | `41.03 (CV), 80.44 (Excursion), 1.354 (n=1), 6.050 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 6 (dz=1.0 um)` | **VERIFIED_FROZEN** |
| **CLM-37** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 2.5 us) | `6.015` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 2 (dt=2.5 us)` | **VERIFIED_FROZEN** |
| **CLM-38** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 1.25 us) | `8.673` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 3 (dt=1.25 us)` | **VERIFIED_FROZEN** |
| **CLM-39** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.625 us) | `11.557` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 4 (dt=0.625 us)` | **VERIFIED_FROZEN** |
| **CLM-40** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.5 us) | `12.424` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 5 (dt=0.5 us)` | **VERIFIED_FROZEN** |
| **CLM-41** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.25 us) | `14.470` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 6 (dt=0.25 us)` | **VERIFIED_FROZEN** |
| **CLM-42** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.125 us) | `15.313` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 7 (dt=0.125 us)` | **VERIFIED_FROZEN** |
| **CLM-43** | Sec. 2.4.2, 4.6 | Richardson Extrapolation Asymptotic Estimate | `15.90 (second-order, p = 1.28) / 16.16 (first-order)` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `Richardson extrapolation analysis` | **EXTRAPOLATED_ESTIMATE** |
| **CLM-44** | Sec. 2.3 | Pre-Elimination Regularization Scale lambda_kappa | `31.62` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `Core-conductor derivation` | **VERIFIED_DERIVATION** |
| **CLM-45** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=1) | `73.3` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 1 (n=1)` | **VERIFIED_DERIVATION** |
| **CLM-46** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=10) | `209.7` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 4 (n=10)` | **VERIFIED_DERIVATION** |
| **CLM-47** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=25) | `329.1` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 7 (n=25)` | **VERIFIED_DERIVATION** |
| **CLM-48** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=50) | `464.3` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 10 (n=50)` | **VERIFIED_DERIVATION** |
| **CLM-49** | Sec. 2.3 | Discrete Current Conservation Residual (benchmark default w_cleft = 100 nm) | `< 10^-16` | N/A | A/m | `results/figures/current_conservation_benchmark.png` | `python src/current_conservation_benchmark.py` | **VERIFIED_FROZEN** |
| **CLM-50** | Sec. 2.1, Table 3 | Outer Fiber Diameter D_1 | `10.0` | N/A | µm | `src/phase1_classical_hh/coupled_model.py` | `D1 definition` | **PRESCRIBED_PARAMETER** |
| **CLM-51** | Sec. 2.1, Table 3 | Axonal Core Diameters | `7.0 (Aβ), 1.0 (C-fiber)` | N/A | µm | `src/phase1_classical_hh/coupled_model.py` | `d1, d2 definition` | **PRESCRIBED_PARAMETER** |
| **CLM-52** | Sec. 2.1, Table 3 | Nodal Length l_node | `1.0` | N/A | µm | `src/phase1_classical_hh/spike_detector.py` | `node_len_um = 1.0` | **PRESCRIBED_PARAMETER** |
| **CLM-53** | Sec. 2.1, Table 3 | Resistivity Parameters rho_i, rho_e | `0.547 (rho_i), 1.0 (rho_e)` | N/A | Ohm*m | `src/phase1_classical_hh/coupled_model.py` | `rho_i, rho_e definitions` | **PRESCRIBED_PARAMETER** |
| **CLM-54** | Sec. 2.3 | Asymptotic Maximum Cleft Resistance r_{e,max} | `6.37 x 10^10` | N/A | Ohm/m | `manuscript/ephaptic_crosstalk_paper_JCNS_revised.md` | `Section 2.3 geometric derivation` | **VERIFIED_DERIVATION** |
| **CLM-55** | Sec. 2.3 | Nominal Longitudinal Cleft Resistance r_e | `6.10 x 10^10` | N/A | Ohm/m | `src/phase1_classical_hh/ephaptic_model.py` | `r_e_from_cleft definition` | **VERIFIED_FROZEN** |

---

### 3.1 Sensitization, kinetics-shift and boundary-spike claims (regenerated, Sec. 2.8, 3.3, 3.4, 3.8, 3.9.1)

| Claim ID | Manuscript Location | Quantity | Value | Script | Output |
|:---:|---|---|:---:|---|---|
| **SEN-01** | Sec. 3.3, Table 1 | Stable resting potential at 0.05 / 0.10 A/m² (Phase 1) | `-61.92 / -59.81 mV` | `src/run_sensitization_phase1.py` | `results/convergence/sensitization_phase1_bias.csv` |
| **SEN-02** | Sec. 3.3, Table 1 | Onset of repetitive spiking from rest (Phase 1) | `0.1077 A/m²` | `src/run_sensitization_phase1.py` | `results/convergence/sensitization_phase1_summary.md` |
| **SEN-03** | Sec. 3.3, Table 1 | Upper edge of oscillatory regime (depolarization block above) | `1.228 A/m²` | `src/run_sensitization_phase1.py` | `results/convergence/sensitization_phase1_summary.md` |
| **SEN-04** | Sec. 3.3, Table 1 | Abeta-evoked midpoint ΔV (n = 1) at bias 0 to 0.10 | `1.33 mV` | `src/run_sensitization_phase1.py` | `results/convergence/sensitization_phase1_cable_check.csv` |
| **SEN-05** | Sec. 3.4, Table 1 | Onset of spontaneous spiking under kinetics shift | `8.556 mV` | `src/run_sensitization_phase1.py` | `results/convergence/sensitization_phase1_kinetics_shift.csv` |
| **SEN-06** | Sec. 3.8, Table 2 | Phase 2 baseline at 0.25 / 2 A/m² | `-59.30 / -47.39 mV` | `src/run_sensitization_phase2.py` | `results/convergence/sensitization_phase2_bias.csv` |
| **SEN-07** | Sec. 3.8, Table 2 | Phase 2 onset of depolarization block from rest | `3.212 A/m²` | `src/run_sensitization_phase2.py` | `results/convergence/sensitization_phase2_summary.md` |
| **SEN-08** | Sec. 3.8, Table 2 | Phase 2 Abeta-evoked midpoint ΔV, bias 0-2 A/m² (n = 1 / n = 25) | `1.71-1.76 / 9.54-10.16 mV` | `src/run_sensitization_phase2.py` | `results/convergence/sensitization_phase2_cable.csv` |
| **SEN-09** | Sec. 3.9.1 | Boundary-spike threshold n* (Phase 1 / Phase 2) | `~1.8 / ~28.5` | `src/run_boundary_spike_threshold.py` | `results/convergence/boundary_spike_phase1.csv`, `boundary_spike_phase2.csv` |
| **SEN-10** | Sec. 3.9.1 | Grounded interior-lesion peak, Phase 2, n = 50 / 200 | `-56.68 / -58.49 mV` | `src/run_boundary_spike_threshold.py` | `results/convergence/lesion_control_high_n.csv` |

## 4. Multi-Fiber $n$-Series Exhaustive Provenance ($n \in [1, 50]$)

#### 4.1 Phase 1 Classical Hodgkin-Huxley Multi-Fiber Series
Simulated via `src/run_phase2_multifiber.py` (`coupled_model.py`), raw data saved in `results/convergence/phase2_multifiber.csv`:

| $n$ | Downstream $\Delta V$ (mV) | Downstream Peak $V_2$ (mV) | Midpoint Peak $V_2$ (mV) | Aβ CV (m/s) | $\kappa_{\text{eff}}$ ($\text{m}^{-2}$) | $\lambda_{\text{eff}}$ ($\mu\text{m}$) | Event Classification |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | 1.325 | -63.675 | -63.712 | 40.00 | 1.86e8 | 73.3 | `LOCAL_STIMULUS_TRANSIENT` |
| 2 | 2.240 | -62.760 | -62.857 | 40.00 | 1.03e8 | 98.3 | `LOCAL_STIMULUS_TRANSIENT` |
| 5 | 3.763 | -61.237 | -61.524 | 37.21 | 4.44e7 | 150.1 | `LOCAL_STIMULUS_TRANSIENT` |
| 10 | 4.929 | -60.071 | -60.612 | 34.78 | 2.27e7 | 209.7 | `LOCAL_STIMULUS_TRANSIENT` |
| 15 | 5.507 | -59.493 | -60.216 | 34.04 | 1.53e7 | 255.8 | `LOCAL_STIMULUS_TRANSIENT` |
| 20 | 5.829 | -59.171 | -60.036 | 32.65 | 1.15e7 | 294.8 | `LOCAL_STIMULUS_TRANSIENT` |
| 25 | 6.015 | -58.985 | -59.962 | 32.00 | 9.23e6 | 329.1 | `LOCAL_STIMULUS_TRANSIENT` |
| 30 | 6.121 | -58.879 | -59.950 | 30.19 | 7.71e6 | 360.3 | `LOCAL_STIMULUS_TRANSIENT` |
| 40 | 6.197 | -58.803 | -60.032 | 28.57 | 5.79e6 | 415.6 | `LOCAL_STIMULUS_TRANSIENT` |
| 50 | 6.184 | -58.816 | -60.186 | 27.12 | 4.64e6 | 464.3 | `LOCAL_STIMULUS_TRANSIENT` |

### 4.2 Phase 2 Nav1.8/Nav1.9 Multi-Fiber Series (manuscript Fig. 7)
Simulated via `src/phase2_multifiber_sweep.py` (`coupled_navc_model.py`), raw data saved in `results/convergence/phase2_navc_multifiber.csv`:

| $n$ | Condition | Midpoint Peak $V_2$ (mV) | Baseline $V_{\text{rest}}$ (mV) | $\Delta V$ (mV) | Spiked? |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Synchronous (0.0 ms jitter) | -65.07 | -66.82 | 1.76 | False |
| 2 | Synchronous (0.0 ms jitter) | -63.67 | -66.82 | 3.15 | False |
| 5 | Synchronous (0.0 ms jitter) | -61.03 | -66.82 | 5.79 | False |
| 10 | Synchronous (0.0 ms jitter) | -58.84 | -66.82 | 7.98 | False |
| 15 | Synchronous (0.0 ms jitter) | -57.71 | -66.82 | 9.11 | False |
| 20 | Synchronous (0.0 ms jitter) | -57.05 | -66.82 | 9.77 | False |
| 25 | Synchronous (0.0 ms jitter) | -56.66 | -66.82 | 10.16 | False |
| 30 | Synchronous (0.0 ms jitter) | -56.43 | -66.82 | 10.39 | False |
| 40 | Synchronous (0.0 ms jitter) | -56.29 | -66.82 | 10.53 | False |
| 50 | Synchronous (0.0 ms jitter) | -56.40 | -66.82 | 10.42 | False |
| 1 | Temporally Dispersed (1.5 ms jitter) | -66.74 | -66.82 | 0.09 | False |
| 2 | Temporally Dispersed (1.5 ms jitter) | -66.67 | -66.82 | 0.16 | False |
| 5 | Temporally Dispersed (1.5 ms jitter) | -66.53 | -66.82 | 0.30 | False |
| 10 | Temporally Dispersed (1.5 ms jitter) | -66.40 | -66.82 | 0.42 | False |
| 15 | Temporally Dispersed (1.5 ms jitter) | -66.33 | -66.82 | 0.49 | False |
| 20 | Temporally Dispersed (1.5 ms jitter) | -66.26 | -66.82 | 0.56 | False |
| 25 | Temporally Dispersed (1.5 ms jitter) | -66.20 | -66.82 | 0.63 | False |
| 30 | Temporally Dispersed (1.5 ms jitter) | -66.15 | -66.82 | 0.68 | False |
| 40 | Temporally Dispersed (1.5 ms jitter) | -66.09 | -66.82 | 0.73 | False |
| 50 | Temporally Dispersed (1.5 ms jitter) | -66.04 | -66.82 | 0.78 | False |

---

## 5. Reviewer Response Numerical Claims Cross-Reference

| Reviewer Comment | Stated Claim in Response | Verified Value in Response | Exactly Matches Manuscript? | Provenance File |
|---|---|:---:|:---:|---|
| **Comment 2.1** | Discrete KCL conservation residual | $< 10^{-16}\,\text{A/m}$ | **YES** (Sec. 2.3) | `src/current_conservation_benchmark.py` |
| **Comment 2.2** | CRRSS monotonic half-inactivation | $V_{1/2} \approx -74.5$ mV | **YES** (Sec. 2.2.1) | `src/crrss_gating_plots.py` |
| **Comment 2.2** | Isolated Aβ conduction velocity | $41.03$ m/s | **YES** (Sec. 3.1) | `results/convergence/spatial_convergence.csv` |
| **Comment 2.2** | Isolated Aβ AP excursion | $80.44$ mV | **YES** (Sec. 3.1) | `results/convergence/spatial_convergence.csv` |
| **Comment 2.3** | Zero-cleft limiting area $A_{\text{eff,min}}$ | $1.57 \times 10^{-11}\,\text{m}^2$ | **YES** (Sec. 2.3) | Analytical limit derivation |
| **Comment 2.3** | Maximum cleft resistance $r_{e,\text{max}}$ | $6.37 \times 10^{10}\,\Omega/\text{m}$ | **YES** (Sec. 2.3) | Analytical limit derivation |
| **Comment 2.4** | Phenomenological $\kappa$ and nominal decay scale | $\kappa = 1.0\times 10^9\,\text{m}^{-2}, \lambda_\kappa \approx 31.62\,\mu\text{m}$ | **YES** (Sec. 2.3) | `src/compute_kappa_table.py` |
| **Comment 2.4** | Expanding $\lambda_{\text{eff}}$ range across $n \in [1, 50]$ | $73.3\,\mu\text{m}$ to $464.3\,\mu\text{m}$ | **YES** (Table 4) | `results/convergence/kappa_effective_table.csv` |
| **Comment 2.5** | Fixed physical node length | $l_{\text{node}} = 1.0\,\mu\text{m}$ | **YES** (Sec. 2.4.1) | `src/phase1_classical_hh/spike_detector.py` |
| **Comment 2.5** | Crank-Nicolson reference solver agreement | $\le 1.2\%$ CV ($40.00$ vs $39.51$ m/s), $0.24\%$ amp ($79.98$ vs $79.78$ mV) | **YES** (Sec. 2.4.3) | `audit_reference_solver.py` |
| **Comment 2.5** | Richardson extrapolated single-pulse peak estimate | $\approx 15.90$ mV | **YES** (Sec. 2.4.2) | `results/convergence/temporal_convergence_final.csv` |
| **Comment 2.6** | EXP-E02 vs EXP-E03 spatial distinction | $5.039$ mV (midpoint) vs $6.015$ mV (downstream max) | **YES** (Sec. 3.5, Table 4) | `results/convergence/EXP_E02_E03_reconciliation.csv` |
| **Comment 2.6** | 100-Hz train propagated AP recorded in Pulse 2 window (initiated by Pulse 1) | $+24.70$ mV at $8.0$ mm, $\text{CV} = 0.41$ m/s ($T \ge 35$ ms) | **YES** (Sec. 3.5, Table 1) | `results/convergence/final_100Hz_reconciliation.csv` |
| **Comment 2.7** | Phase 2 20-ms pre-stimulus settled resting potential | $-66.82$ mV (drift $< 10\,\mu\text{V}$) | **YES** (Sec. 2.5, 3.7) | `src/phase2_nav18_nav19/navc_cable.py` (`get_settled_c_fiber`) |
| **Comment 2.7** | Phase 2 isolated positive control CV | $0.26$ m/s | **YES** (Sec. 3.7, Fig. 6a) | `src/plot_fig3_control.py` |