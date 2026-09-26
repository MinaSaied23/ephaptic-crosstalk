# Computational Provenance Manifest: Claim-to-Code Traceability

**Manuscript:** *Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation*  
**Target Journal:** *Journal of Computational Neuroscience* (JCNS)  
**Author:** Mina Saied Attia  
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

## 2. Main-Text Tables & Figures Provenance

### FIG-01: Figure 1: Model Architecture Schematic
- **Manuscript Location:** Sec. 2.1 (Line 39)
- **Source Script:** `N/A (Vector Diagram)`
- **Configuration / Parameters:** Two-fiber coupled core-conductor schematic (CRRSS Aβ + HH/Nav1.8/1.9 C-fiber) with regularized Poisson coupling
- **Raw Output File:** `N/A (Visual architecture)`
- **Plotting / Tabulation Pipeline:** `results/figures/fig1_model_schematic.png`
- **Produced Artifact:** Figure 1 (Embedded in Section 2.1)

### FIG-02: Figure 2: Positive Controls (Uncoupled Fibers)
- **Manuscript Location:** Sec. 3.1 (Line 196)
- **Source Script:** `src/plot_fig2_control.py`
- **Configuration / Parameters:** Uncoupled single fibers (r_e = 0): Aβ alone (100 nA/0.2 ms), C-fiber alone (1 nA/1 ms), dz=10 um, dt=2.5 us
- **Raw Output File:** `results/convergence/spatial_convergence.csv (dz=10 um row)`
- **Plotting / Tabulation Pipeline:** `src/plot_fig2_control.py`
- **Produced Artifact:** Figure 2 (Panels a & b: Aβ saltatory CV 41.03 m/s, C-fiber CV 0.41 m/s)

### FIG-03: Figure 3: Phase 2 Controls & Multi-Fiber Trend
- **Manuscript Location:** Sec. 3.7 (Line 239)
- **Source Script:** `src/plot_fig3_control.py`
- **Configuration / Parameters:** Phase 2 Nav1.8/Nav1.9 model: 20 ms settling, isolated CV (2 nA/1 ms), coupled pulse w_cleft=20 nm, n in [1, 50], kappa=1.0e9 m^-2
- **Raw Output File:** `results/convergence/phase2_headline_results.csv`
- **Plotting / Tabulation Pipeline:** `src/plot_fig3_control.py`
- **Produced Artifact:** Figure 3 (Panels a, b, c: isolated CV 0.26 m/s, coupled humps, multi-fiber plateau near -58.8 mV)

### FIG-04: Figure 4: Phase 2 Multi-Fiber Sweep (Authoritative)
- **Manuscript Location:** Sec. 3.7 (Line 268)
- **Source Script:** `src/phase2_multifiber_sweep.py`
- **Configuration / Parameters:** Nav1.8/Nav1.9 C-fiber, w_cleft=20 nm, kappa=1.0e9 m^-2, settled rest -66.82 mV, n in [1, 50], jitter=0.0 ms vs 1.5 ms
- **Raw Output File:** `results/convergence/phase2_navc_multifiber.csv`
- **Plotting / Tabulation Pipeline:** `src/phase2_multifiber_sweep.py`
- **Produced Artifact:** Figure 4 (phase2_multifiber_sweep.png: n=1 -> -65.07 mV; n=10 -> -58.84 mV; n=25 -> -56.66 mV; n=50 -> -56.40 mV; jittered n=25 -> -66.20 mV)

### FIG-BM1: Benchmark: CRRSS Steady-State Gating Curves
- **Manuscript Location:** Sec. 2.2.1 (Line 72)
- **Source Script:** `src/crrss_gating_plots.py`
- **Configuration / Parameters:** Corrected Chiu et al. (1979) rate equations, V in [-100, +50] mV
- **Raw Output File:** `Analytical gating curves`
- **Plotting / Tabulation Pipeline:** `src/crrss_gating_plots.py`
- **Produced Artifact:** crrss_gating_plots.png (Monotonic h_inf inactivation, V_1/2 = -74.5 mV)

### FIG-BM2: Benchmark: Discrete Kirchhoff's Current Law Conservation
- **Manuscript Location:** Sec. 2.3 (Line 114)
- **Source Script:** `src/current_conservation_benchmark.py`
- **Configuration / Parameters:** w_cleft=100 nm, kappa=1.0e9 m^-2, dt=2.5 us, dz=10 um
- **Raw Output File:** `Calculated discrete KCL residual across 1000 nodes`
- **Plotting / Tabulation Pipeline:** `src/current_conservation_benchmark.py`
- **Produced Artifact:** current_conservation_benchmark.png (KCL residual < 10^-16 A/m)

### FIG-BM3: Benchmark: Spatial Grid Refinement (Fixed Node)
- **Manuscript Location:** Sec. 2.4.1 (Line 133)
- **Source Script:** `src/convergence_study.py`
- **Configuration / Parameters:** Fixed l_node=1.0 um, dt=2.5 us, dz in [20, 10, 5, 2.5] um, w_cleft=20 nm, n=25, kappa=1.0e9 m^-2
- **Raw Output File:** `results/convergence/spatial_convergence.csv`
- **Plotting / Tabulation Pipeline:** `src/convergence_study.py`
- **Produced Artifact:** fig_convergence_analysis.png (Spatial stability across grid refinements)

### TAB-01: Table 1: Phase 1 Experimental Summary
- **Manuscript Location:** Sec. Experimental Summary Tables (Line 351)
- **Source Script:** `src/phase1_classical_hh/coupled_model.py & scratch/run_canonical_100hz.py`
- **Configuration / Parameters:** Classical HH C-fiber, w_cleft in [20 nm, 5 um], single-pulse, bias, 100 Hz train (1, 2, 3, 5, 10 pulses, T>=35 ms)
- **Raw Output File:** `results/convergence/final_100Hz_reconciliation.csv`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 1 (Pulse 1: +5.04 mV mid / +6.01 mV max; Pulse 2: +24.70 mV propagated AP; CV 0.41 m/s)

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
- **Source Script:** `scratch/run_phase2_multifiber.py (Phase 1 Classical-HH configuration) & scratch/compute_kappa_table.py`
- **Configuration / Parameters:** Phase 1 Classical HH, w_cleft=20 nm, kappa=1.0e9 m^-2, n in [1, 50], rest = -65.000 mV
- **Raw Output File:** `results/convergence/phase2_multifiber.csv & kappa_effective_table.csv`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 4 (Full n-series: Delta V, peak V2 downstream, midpoint V2, Abeta CV, kappa_eff, lambda_eff)

### TAB-05: Table 5: Spatial Grid Refinement (Fixed Physical Node)
- **Manuscript Location:** Sec. Experimental Summary Tables (Line 396)
- **Source Script:** `src/convergence_study.py`
- **Configuration / Parameters:** l_node=1.0 um fixed, dt=2.5 us, dz in [20, 10, 5, 2.5] um, w_cleft=20 nm, n=1 and n=25
- **Raw Output File:** `results/convergence/spatial_convergence.csv`
- **Plotting / Tabulation Pipeline:** `Markdown Table Generation`
- **Produced Artifact:** Table 5 (Abeta CV 40.82 -> 41.03 m/s; Excursion 79.99 -> 80.67 mV; Delta V single-pair 1.347 -> 1.294 mV; n=25 5.968 -> 6.029 mV)

---

## 3. Individual Numerical Claims Provenance (Full Inventory)

| Claim ID | Manuscript Location | Stated Quantity & Claim | Value | Baseline | Units | Source Code / Origin | Raw Output File & Row | Status |
|:---:|---|---|:---:|:---:|:---:|---|---|:---:|
| **CLM-01** | Sec. 2.2.1, 3.1 | Isolated Aβ Conduction Velocity | `41.03` | N/A | m/s | `results/convergence/spatial_convergence.csv` | `row 2 (dz=10.0 um)` | **VERIFIED_FROZEN** |
| **CLM-02** | Sec. 2.2.1, 3.1 | Isolated Aβ Action Potential Excursion | `80.44 (peak +0.44 from rest -80.0)` | -80.0 mV | mV | `results/convergence/spatial_convergence.csv` | `row 2 (dz=10.0 um)` | **VERIFIED_FROZEN** |
| **CLM-03** | Sec. 2.2.1, 3.1 | Isolated Aβ Resting Baseline Drift | `< 10 µV` | N/A | µV | `src/phase1_classical_hh/ephaptic_model.py` | `Resting potential equilibrium test` | **VERIFIED_FROZEN** |
| **CLM-04** | Sec. 2.4.3 | Aβ Reference Solver CV Comparison | `40.00 vs 39.51` | Isolated CV 40.0 m/s | m/s | `audit_reference_solver.py` | `run_test1_convergence.py reference audit` | **VERIFIED_FROZEN** |
| **CLM-05** | Sec. 2.4.3 | Aβ Reference Solver Peak Amplitude Comparison | `80.59 vs 80.40` | N/A | mV | `audit_reference_solver.py` | `Abeta reference benchmark` | **VERIFIED_FROZEN** |
| **CLM-06** | Sec. 2.2.2, 3.1 | Isolated Classical C-Fiber CV | `0.41` | N/A | m/s | `results/convergence/phase2_headline_results.csv` | `positive_control.py; row 4` | **VERIFIED_FROZEN** |
| **CLM-07** | Sec. 2.2.2, 3.1 | Isolated Classical C-Fiber Peak Potential | `+24.7 (+24.77)` | N/A | mV | `results/convergence/phase2_headline_results.csv` | `positive_control.py` | **VERIFIED_FROZEN** |
| **CLM-08** | Sec. 2.5, 3.7 | Nav1.8/Nav1.9 C-Fiber Resting Potential | `-66.82` | N/A | mV | `src/phase2_nav18_nav19/coupled_navc_model.py` | `get_settled_c_fiber; phase2_navc_multifiber.csv` | **VERIFIED_FROZEN** |
| **CLM-09** | Sec. 3.7 | Isolated Nav1.8/Nav1.9 C-Fiber CV | `0.26` | N/A | m/s | `results/figures/fig3_phase2_control.png` | `Phase 2 positive control` | **VERIFIED_FROZEN** |
| **CLM-10** | Sec. 3.9.1, Fig. 4 | Phase 2 Multi-Fiber Midpoint Peak (n=25, synchronous) | `-56.66 (ΔV = 10.16)` | N/A | mV | `results/convergence/phase2_navc_multifiber.csv` | `row 7 (n=25, j=0.0 ms)` | **VERIFIED_FROZEN** |
| **CLM-11** | Sec. 3.9.2, Fig. 4 | Phase 2 Multi-Fiber Midpoint Peak (n=25, 1.5 ms jitter) | `-66.20 (ΔV = 0.63)` | N/A | mV | `results/convergence/phase2_navc_multifiber.csv` | `row 17 (n=25, j=1.5 ms)` | **VERIFIED_FROZEN** |
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
| **CLM-25** | Sec. 3.9.2, Table 1 | Phase 1 Jitter Attenuation Ratio (n=25) | `92.9` | N/A | % | `results/convergence/phase2_synchrony.csv` (legacy filename; Phase 1 classical-HH synchrony configuration) | `row 11 (jitter 1.5 ms); phase2_synchrony_audit.md` | **VERIFIED_FROZEN** |
| **CLM-26** | Sec. 3.9.2 | Phase 1 Jittered Peak Depolarization (n=25) | `0.426` | N/A | mV | `results/convergence/phase2_synchrony.csv` (legacy filename; Phase 1 classical-HH synchrony configuration) | `row 11` | **VERIFIED_FROZEN** |
| **CLM-27** | Sec. 3.7, Sec. 3.9.2, Fig. 4, Table 2 | Phase 2 Jitter Attenuation Ratio (n=25) | `93.9` | N/A | % | `results/convergence/phase2_navc_multifiber.csv` | `row 17 (jitter 1.5 ms, n=25)` | **VERIFIED_FROZEN** |
| **CLM-28** | Sec. 3.5, Table 1 | 100 Hz Train Pulse 1 C-Fiber Peak Potential | `-58.99 (downstream), -59.96 (midpoint)` | N/A | mV | `results/convergence/final_100Hz_reconciliation.csv` | `row 1 (pulse 1)` | **VERIFIED_FROZEN** |
| **CLM-29** | Sec. 3.5, Table 1 | 100 Hz Train First Propagated Spike Pulse Number | `2` | N/A | dimensionless | `results/convergence/final_100Hz_reconciliation.csv` | `row 2 (pulse 2); final_100Hz_reconciliation.md` | **VERIFIED_FROZEN** |
| **CLM-30** | Sec. 3.5, Table 1 | 100 Hz Train Pulse 2 Downstream Peak Voltage | `+24.70` | N/A | mV | `results/convergence/final_100Hz_reconciliation.csv` | `row 2 (downstream peak)` | **VERIFIED_FROZEN** |
| **CLM-31** | Sec. 3.5, Table 1 | 100 Hz Train Pulse 2 Midpoint Peak Voltage | `+24.83` | N/A | mV | `results/convergence/final_100Hz_reconciliation.csv` | `row 2 (midpoint peak)` | **VERIFIED_FROZEN** |
| **CLM-32** | Sec. 3.5 | Truncation Artifact In-Flight AP Location | `2.1` | N/A | mm | `results/convergence/final_100Hz_reconciliation.md` | `Section 1.1 mathematical demonstration` | **VERIFIED_FROZEN** |
| **CLM-33** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 20 um | `40.82 (CV), 79.99 (Excursion), 1.347 (n=1), 5.968 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 1 (dz=20 um)` | **VERIFIED_FROZEN** |
| **CLM-34** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 10 um (Nominal) | `41.03 (CV), 80.44 (Excursion), 1.325 (n=1), 6.015 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 2 (dz=10 um)` | **VERIFIED_FROZEN** |
| **CLM-35** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 5 um | `41.03 (CV), 80.60 (Excursion), 1.306 (n=1), 6.027 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 3 (dz=5 um)` | **VERIFIED_FROZEN** |
| **CLM-36** | Sec. 2.4.1, Table 5 | Spatial Refinement Grid Step 2.5 um | `41.03 (CV), 80.67 (Excursion), 1.294 (n=1), 6.029 (n=25)` | N/A | m/s, mV, mV, mV | `results/convergence/spatial_convergence.csv` | `row 4 (dz=2.5 um)` | **VERIFIED_FROZEN** |
| **CLM-37** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 2.5 us) | `5.971` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 2 (dt=2.5 us)` | **VERIFIED_FROZEN** |
| **CLM-38** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 1.25 us) | `8.595` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 3 (dt=1.25 us)` | **VERIFIED_FROZEN** |
| **CLM-39** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.625 us) | `11.405` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 4 (dt=0.625 us)` | **VERIFIED_FROZEN** |
| **CLM-40** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.5 us) | `12.237` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 5 (dt=0.5 us)` | **VERIFIED_FROZEN** |
| **CLM-41** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.25 us) | `14.161` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 6 (dt=0.25 us)` | **VERIFIED_FROZEN** |
| **CLM-42** | Sec. 2.4.2 | Temporal Refinement Peak ΔV (dt = 0.125 us) | `14.930` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `row 7 (dt=0.125 us)` | **VERIFIED_FROZEN** |
| **CLM-43** | Sec. 2.4.2, 4.6 | Richardson Extrapolation Asymptotic Estimate | `15.44 (second-order) / 15.70 (first-order)` | N/A | mV | `results/convergence/temporal_convergence_final.csv` | `Richardson extrapolation analysis` | **EXTRAPOLATED_ESTIMATE** |
| **CLM-44** | Sec. 2.3 | Pre-Elimination Regularization Scale lambda_kappa | `31.62` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `Core-conductor derivation` | **VERIFIED_DERIVATION** |
| **CLM-45** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=1) | `73.3` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 1 (n=1)` | **VERIFIED_DERIVATION** |
| **CLM-46** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=10) | `209.7` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 4 (n=10)` | **VERIFIED_DERIVATION** |
| **CLM-47** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=25) | `329.1` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 7 (n=25)` | **VERIFIED_DERIVATION** |
| **CLM-48** | Sec. 2.3, Table 4 | Effective Regularization Scale lambda_eff (n=50) | `464.3` | N/A | µm | `results/convergence/kappa_effective_table.csv` | `row 10 (n=50)` | **VERIFIED_DERIVATION** |
| **CLM-49** | Sec. 2.3 | Discrete Current Conservation Residual | `< 10^-16` | N/A | A/m | `results/figures/current_conservation_benchmark.png` | `audit_conservation_invariance.py` | **VERIFIED_FROZEN** |
| **CLM-50** | Sec. 2.1, Table 3 | Outer Fiber Diameter D_1 | `10.0` | N/A | µm | `src/phase1_classical_hh/coupled_model.py` | `D1 definition` | **PRESCRIBED_PARAMETER** |
| **CLM-51** | Sec. 2.1, Table 3 | Axonal Core Diameters | `7.0 (Aβ), 1.0 (C-fiber)` | N/A | µm | `src/phase1_classical_hh/coupled_model.py` | `d1, d2 definition` | **PRESCRIBED_PARAMETER** |
| **CLM-52** | Sec. 2.1, Table 3 | Nodal Length l_node | `1.0` | N/A | µm | `src/phase1_classical_hh/spike_detector.py` | `node_len_um = 1.0` | **PRESCRIBED_PARAMETER** |
| **CLM-53** | Sec. 2.1, Table 3 | Resistivity Parameters rho_i, rho_e | `0.547 (rho_i), 1.0 (rho_e)` | N/A | Ohm*m | `src/phase1_classical_hh/coupled_model.py` | `rho_i, rho_e definitions` | **PRESCRIBED_PARAMETER** |
| **CLM-54** | Sec. 2.3 | Asymptotic Maximum Cleft Resistance r_{e,max} | `6.37 x 10^10` | N/A | Ohm/m | `manuscript/ephaptic_crosstalk_paper_JCNS_revised.md` | `Section 2.3 geometric derivation` | **VERIFIED_DERIVATION** |
| **CLM-55** | Sec. 2.3 | Nominal Longitudinal Cleft Resistance r_e | `6.10 x 10^10` | N/A | Ohm/m | `src/phase1_classical_hh/ephaptic_model.py` | `r_e_from_cleft definition` | **VERIFIED_FROZEN** |

---

## 4. Multi-Fiber $n$-Series Exhaustive Provenance ($n \in [1, 50]$)

### 4.1 Phase 1 Classical Hodgkin-Huxley Multi-Fiber Series
Simulated via `scratch/run_phase2_multifiber.py` (`coupled_model.py`), raw data saved in `results/convergence/phase2_multifiber.csv`:

| $n$ | Downstream $\Delta V$ (mV) | Downstream Peak $V_2$ (mV) | Midpoint Peak $V_2$ (mV) | Aβ CV (m/s) | $\kappa_{\text{eff}}$ ($\text{m}^{-2}$) | $\lambda_{\text{eff}}$ ($\mu\text{m}$) | Event Classification |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | 1.325 | -63.675 | -63.712 | 40.00 | 1.86e8 | 73.3 | `LOCAL_STIMULUS_TRANSIENT` |
| 2 | 2.240 | -62.760 | -62.810 | 40.00 | 1.03e8 | 98.3 | `LOCAL_STIMULUS_TRANSIENT` |
| 5 | 3.763 | -61.237 | -61.320 | 37.21 | 4.44e7 | 150.1 | `LOCAL_STIMULUS_TRANSIENT` |
| 10 | 4.929 | -60.071 | -60.190 | 34.78 | 2.27e7 | 209.7 | `LOCAL_STIMULUS_TRANSIENT` |
| 15 | 5.507 | -59.493 | -59.620 | 34.04 | 1.53e7 | 255.8 | `LOCAL_STIMULUS_TRANSIENT` |
| 20 | 5.829 | -59.171 | -59.310 | 32.65 | 1.15e7 | 294.8 | `LOCAL_STIMULUS_TRANSIENT` |
| 25 | 6.015 | -58.985 | -59.962 | 32.00 | 9.23e6 | 329.1 | `LOCAL_STIMULUS_TRANSIENT` |
| 30 | 6.121 | -58.879 | -59.010 | 30.19 | 7.71e6 | 360.3 | `LOCAL_STIMULUS_TRANSIENT` |
| 40 | 6.197 | -58.803 | -58.920 | 28.57 | 5.79e6 | 415.6 | `LOCAL_STIMULUS_TRANSIENT` |
| 50 | 6.184 | -58.816 | -58.940 | 27.12 | 4.64e6 | 464.3 | `LOCAL_STIMULUS_TRANSIENT` |

### 4.2 Phase 2 Nav1.8/Nav1.9 Multi-Fiber Series (Figure 4)
Simulated via `src/phase2_multifiber_sweep.py` (`coupled_navc_model.py`), raw data saved in `results/convergence/phase2_navc_multifiber.csv`:

| $n$ | Condition | Midpoint Peak $V_2$ (mV) | Baseline $V_{\text{rest}}$ (mV) | $\Delta V$ (mV) | Spiked? | Classification |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | Synchronous (0.0 ms jitter) | -65.07 | -66.82 | 1.76 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 2 | Synchronous (0.0 ms jitter) | -63.78 | -66.82 | 3.04 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 5 | Synchronous (0.0 ms jitter) | -61.12 | -66.82 | 5.70 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 10 | Synchronous (0.0 ms jitter) | -58.84 | -66.82 | 7.98 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 15 | Synchronous (0.0 ms jitter) | -57.72 | -66.82 | 9.10 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 20 | Synchronous (0.0 ms jitter) | -57.06 | -66.82 | 9.76 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 25 | Synchronous (0.0 ms jitter) | -56.66 | -66.82 | 10.16 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 30 | Synchronous (0.0 ms jitter) | -56.46 | -66.82 | 10.36 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 40 | Synchronous (0.0 ms jitter) | -56.36 | -66.82 | 10.46 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 50 | Synchronous (0.0 ms jitter) | -56.40 | -66.82 | 10.42 | False | `LOCAL_STIMULUS_TRANSIENT` |
| 25 | Temporally Dispersed (1.5 ms jitter) | -66.20 | -66.82 | 0.63 | False | `LOCAL_STIMULUS_TRANSIENT` |

---

## 5. Reviewer Response Numerical Claims Cross-Reference

| Reviewer Comment | Stated Claim in Response | Verified Value in Response | Exactly Matches Manuscript? | Provenance File |
|---|---|:---:|:---:|---|
| **Comment 2.1** | Discrete KCL conservation residual | $< 10^{-16}\,	ext{A/m}$ | **YES** (Sec. 2.3) | `src/current_conservation_benchmark.py` |
| **Comment 2.2** | CRRSS monotonic half-inactivation | $V_{1/2} pprox -74.5$ mV | **YES** (Sec. 2.2.1) | `src/crrss_gating_plots.py` |
| **Comment 2.2** | Isolated Aβ conduction velocity | $41.03$ m/s | **YES** (Sec. 3.1) | `results/convergence/spatial_convergence.csv` |
| **Comment 2.2** | Isolated Aβ AP excursion | $80.44$ mV | **YES** (Sec. 3.1) | `results/convergence/spatial_convergence.csv` |
| **Comment 2.3** | Zero-cleft limiting area $A_{	ext{eff,min}}$ | $1.57 	imes 10^{-11}\,	ext{m}^2$ | **YES** (Sec. 2.3) | Analytical limit derivation |
| **Comment 2.3** | Maximum cleft resistance $r_{e,	ext{max}}$ | $6.37 	imes 10^{10}\,\Omega/	ext{m}$ | **YES** (Sec. 2.3) | Analytical limit derivation |
| **Comment 2.4** | Phenomenological $\kappa$ and nominal decay scale | $\kappa = 1.0	imes 10^9\,	ext{m}^{-2}, \lambda_\kappa pprox 31.62\,\mu	ext{m}$ | **YES** (Sec. 2.3) | `scratch/compute_kappa_table.py` |
| **Comment 2.4** | Expanding $\lambda_{	ext{eff}}$ range across $n \in [1, 50]$ | $73.3\,\mu	ext{m}$ to $464.3\,\mu	ext{m}$ | **YES** (Table 4) | `results/convergence/kappa_effective_table.csv` |
| **Comment 2.5** | Fixed physical node length | $l_{	ext{node}} = 1.0\,\mu	ext{m}$ | **YES** (Sec. 2.4.1) | `spike_detector.py` |
| **Comment 2.5** | Crank-Nicolson reference solver agreement | $\le 1.2\%$ CV ($40.00$ vs $39.51$ m/s), $0.24\%$ amp ($80.59$ vs $80.40$ mV) | **YES** (Sec. 2.4.3) | `audit_reference_solver.py` |
| **Comment 2.5** | Richardson extrapolated single-pulse peak estimate | $pprox 15.44$ mV | **YES** (Sec. 2.4.2) | `results/convergence/temporal_convergence_final.csv` |
| **Comment 2.6** | EXP-E02 vs EXP-E03 spatial distinction | $5.039$ mV (midpoint) vs $6.015$ mV (downstream max) | **YES** (Sec. 3.5, Table 4) | `results/convergence/EXP_E02_E03_reconciliation.csv` |
| **Comment 2.6** | 100-Hz train Pulse 2 threshold-crossing AP | $+24.70$ mV at $8.0$ mm, $	ext{CV} = 0.41$ m/s ($T \ge 35$ ms) | **YES** (Sec. 3.5, Table 1) | `results/convergence/final_100Hz_reconciliation.csv` |
| **Comment 2.7** | Phase 2 20-ms pre-stimulus settled resting potential | $-66.82$ mV (drift $< 10\,\mu	ext{V}$) | **YES** (Sec. 2.5, 3.7) | `navc_cable.py` (`get_settled_c_fiber`) |
| **Comment 2.7** | Phase 2 isolated positive control CV | $0.26$ m/s | **YES** (Sec. 3.7, Fig. 3a) | `src/plot_fig3_control.py` |