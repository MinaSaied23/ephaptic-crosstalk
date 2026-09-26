# Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation

Official simulation codebase, mathematical benchmarks, reproduction battery, and manuscript package for the revised study submitted to the *Journal of Computational Neuroscience* (JCNS).

**Author:** Mina Saied Attia  
**Affiliation:** New Cairo STEM School, Cairo, Egypt  
**Status:** Revised Resubmission (100% Zero-Trust Audited & Reconciled)

---

## 1. Scientific Overview & Key Biophysical Findings

Dynamic mechanical allodynia—pain evoked by light touch—is widely hypothesized to involve non-synaptic ephaptic crosstalk between large myelinated Aβ tactile afferents and unmyelinated C-fiber nociceptors at sites of focal demyelination or nerve compression. This repository implements a biophysically grounded, closed-loop, one-dimensional core-conductor cable model coupling a Chiu-Ritchie-Rogart-Stagg-Sweeney (CRRSS) myelinated Aβ axon to an unmyelinated C-fiber across a shared pathologically restricted extracellular cleft ($w_{\text{cleft}} = 20\,\text{nm}$ to $5\,\mu\text{m}$).

To eliminate numerical stiffness from explicit capacitive displacement feedback, the framework implements an algebraic elimination of capacitive currents derived from continuous Kirchhoff's Current Law (KCL). Crosstalk is evaluated across two distinct kinetic paradigms:
1. **Phase 1 (Classical Hodgkin-Huxley):** Classical HH kinetics serving as an established baseline model ($V_{\text{rest}} = -65.000$ mV).
2. **Phase 2 (Nociceptor-Realistic Nav1.8/Nav1.9):** Incorporates mammalian TTX-resistant Nav1.8 and persistent Nav1.9 channel kinetics with a settled 20-ms pre-stimulus resting baseline ($V_{\text{rest}} = -66.82$ mV; drift $< 10\,\mu\text{V}$).

### Summary of Authoritative Quantitative Findings

| Biophysical Phenomenon | Phase 1 (Classical HH) | Phase 2 (Nav1.8/Nav1.9 Nociceptor) | Biophysical Mechanism |
|---|:---:|:---:|---|
| **Single-Pair Single-Pulse Coupling** | $\Delta V = 1.325$ mV ($20$ nm cleft) | $\Delta V < 1.0$ mV (midpoint $-65.07$ mV) | **Strictly subthreshold**; limited single-fiber source current into the cleft. |
| **Multi-Fiber Spatial Summation ($n=25$)** | $\Delta V = 5.039$ mV (midpoint), $6.015$ mV (downstream max) | $\Delta V = 10.16$ mV (midpoint peak $-56.66$ mV) | Order-of-magnitude amplification, remaining well below threshold ($-35.0$ mV in Phase 2). |
| **Multi-Fiber Saturation Plateau ($n \to 50$)** | Depolarization saturates near $+6.2$ mV ($6.184$ mV at $n=50$) | Depolarization saturates near $-56.4$ mV ($10.42$ mV at $n=50$) | **Parallel core conductance shunting:** $\Sigma_G(n)$ expands with fiber count, lengthening $\lambda_{\text{eff}}$ ($73.3 \to 464.3\,\mu\text{m}$) and shunting cleft current. |
| **Conduction Velocity Deceleration** | Aβ CV slows: $40.00$ ($n=1$) $\to 32.00$ ($n=25$) $\to 27.12$ m/s ($n=50$) | N/A (single Aβ driver) | Collective cleft resistive loading decelerates the active source. |
| **Temporal Dispersion / Jitter Attenuation** | **92.9% attenuation** ($5.04 \to 0.426$ mV across $1.5$ ms window) | **93.9% attenuation** ($-56.66 \to -66.20$ mV across $1.5$ ms window) | Desynchronization collapses temporal overlap of source currents across fibers. |
| **100-Hz Repetitive Train ($n=25$)** | **Pulse 2 triggers first propagated AP** ($+24.70$ mV peak, CV $0.41$ m/s) | Not required for suprathreshold demonstration | Governed by residual C-fiber membrane and gating-state accumulation; requires observation window $T \ge 35$ ms. |
| **Discrete KCL Conservation** | Algebraic residual $< 10^{-16}$ A/m | Algebraic residual $< 10^{-16}$ A/m | Machine-precision current conservation across all 1000 compartments. |

---

## 2. Repository Structure

```
├── .gitignore                          # Clean git ignores for Python cache, OS, and temporary files
├── LICENSE                             # MIT Open-Source Research License
├── README.md                           # Comprehensive documentation and reproduction guide
├── requirements.txt                    # Pinned library dependencies
├── test_invariants.py                  # Unit and invariant test suite (parameters, homogenization, units)
├── run_verification_battery.py         # Automated end-to-end verification battery (10 verification suites)
├── manuscript/
│   ├── ephaptic_crosstalk_paper_JCNS_revised.docx  # Final typeset submission manuscript
│   ├── ephaptic_crosstalk_paper_JCNS_revised.md    # Source markdown text with mathematical notation
│   ├── reviewer_response.docx          # Typeset point-by-point reviewer response letter
│   ├── reviewer_response.md            # Markdown author response document
│   ├── cover_letter.docx               # Resubmission cover letter
│   └── cover_letter.md                 # Markdown cover letter
├── peer_review/
│   ├── peer_review_1.pdf               # Original Reviewer 1 report
│   └── peer_review_2.docx              # Original Reviewer 2 report
├── results/
│   ├── figures/                        # High-resolution 300-DPI publication figures
│   │   ├── fig1_model_schematic.png    # Figure 1: Model architecture schematic
│   │   ├── fig2_phase1_control.png     # Figure 2: Phase 1 positive controls (Aβ & C-fiber CVs)
│   │   ├── fig3_phase2_control.png     # Figure 3: Phase 2 positive controls & multi-fiber trend
│   │   ├── phase2_multifiber_sweep.png # Figure 4: Authoritative Phase 2 sweep & jitter attenuation
│   │   ├── crrss_gating_plots.png      # Benchmark BM1: CRRSS steady-state gating curves
│   │   ├── current_conservation_benchmark.png # Benchmark BM2: Discrete KCL residual (< 1e-16 A/m)
│   │   └── fig_convergence_analysis.png # Benchmark BM3: Fixed-node spatial refinement
│   └── convergence/                    # Authoritative frozen CSV datasets
│       ├── EXP_E02_E03_reconciliation.csv   # Midpoint vs downstream spatial maximum reconciliation
│       ├── final_100Hz_reconciliation.csv   # Pulse 1 vs Pulse 2 propagation trajectory data
│       ├── kappa_effective_table.csv        # Effective regularization scale across n in [1, 50]
│       ├── phase2_headline_results.csv      # Baseline headline results across coupling configurations
│       ├── phase2_multifiber.csv            # Phase 1 multi-fiber n-series (n in [1, 50])
│       ├── phase2_navc_multifiber.csv       # Phase 2 multi-fiber sweep data (Figure 4)
│       ├── phase2_synchrony.csv             # Phase 1 jitter attenuation sweep
│       ├── phase2_temporal_summation.csv    # Frequency sweep (50 to 800 Hz)
│       ├── spatial_convergence.csv          # Fixed-node spatial grid refinement (dz in [20, 2.5] um)
│       └── temporal_convergence_final.csv   # Temporal grid refinement (dt in [10, 0.125] us)
├── src/
│   ├── abeta_recovery_test.py          # Aβ refractory and dual-pulse recovery check
│   ├── convergence_study.py            # Spatial and temporal grid convergence driver
│   ├── crrss_gating_plots.py           # Corrected Chiu et al. (1979) steady-state gating curves
│   ├── current_conservation_benchmark.py # Discrete KCL conservation benchmark
│   ├── interior_lesion_test.py         # Boundary condition isolation verification
│   ├── phase2_multifiber_sweep.py      # Script generating authoritative Figure 4
│   ├── plot_fig2_control.py            # Script generating Figure 2
│   ├── plot_fig3_control.py            # Script generating Figure 3
│   ├── run_lesion_audit.py             # Lesion audit test driver
│   ├── phase1_classical_hh/
│   │   ├── artifact_timing_check.py    # Lower-kappa sensitivity test
│   │   ├── coupled_model.py            # Phase 1 closed-loop coupled core-conductor solver
│   │   ├── ephaptic_model.py           # Phase 1 biophysical parameters & CRRSS kinetics
│   │   ├── experiment1_single_pulse.py # Single-pulse cleft-width parameter sweep
│   │   ├── experiment_summation.py     # High-frequency pulse train driver (100 Hz)
│   │   ├── positive_control.py         # Direct stimulation positive controls
│   │   ├── sensitization_bias_sweep.py # Tonic depolarizing bias current sweep
│   │   ├── sensitization_bias_sweep_plot.py # Plotting script for bias sweep
│   │   ├── spike_detector.py           # Fixed-node discretization & waveform classifier
│   │   └── validate_single_fibers.py   # Uncoupled single-fiber solvers and CV estimators
│   └── phase2_nav18_nav19/
│       ├── coupled_navc_model.py       # Phase 2 closed-loop coupled nociceptor solver
│       ├── ephaptic_model.py           # Phase 2 parameters & shared cleft geometry
│       ├── experiment_summation_navc.py# Phase 2 pulse train simulations
│       ├── nav_kinetics.py             # Nav1.8/Nav1.9 voltage-gated activation/inactivation rates
│       ├── navc_cable.py               # Nav1.8/Nav1.9 unmyelinated cable with 20-ms settling
│       ├── tune_point.py               # Single-compartment rheobase tuning
│       └── validate_single_fibers.py   # Phase 2 uncoupled single-fiber validation
└── supplementary/
    ├── MANIFEST.md                     # Claim-to-code traceability manifest (56 claims + n-series)
    ├── manuscript_number_inventory.csv # Line-item quantitative inventory
    ├── manuscript_before_after_matrix.csv # 33-item revision change log
    └── manuscript_zero_trust_verification_report.md # Comprehensive forensic audit report
```

---

## 3. Installation & Environment Setup

The codebase is written in standard Python 3.10+ (tested on Python 3.11, 3.12, and 3.14 on Linux, macOS, and Windows). No specialized neural simulators (e.g., NEURON, Brian2) are required; all cable partial differential equations (PDEs) are solved using vectorized NumPy and SciPy banded linear solvers (`scipy.linalg.solve_banded`).

### Quickstart

```bash
# Clone the repository
git clone https://github.com/your-username/ephaptic-crosstalk.git
cd ephaptic-crosstalk

# Install dependencies
pip install -r requirements.txt
```

---

## 4. Automated Reproduction & Verification Battery

To execute the automated verification suite across all biophysical models, numerical solvers, and figure generators in a single command:

```bash
python test_invariants.py
python run_verification_battery.py
```

### Individual Benchmarks & Figures

1. **Parameter Invariants & Homogenization Check:**
   ```bash
   python test_invariants.py
   ```
   *Verifies nodal conductance conservation ($< 10^{-15}$ relative error), compartment capacitance/leak equivalence, and exact Amperes stimulus recovery.*

2. **Kirchhoff's Current Law & Conservation Benchmark:**
   ```bash
   python src/current_conservation_benchmark.py
   ```
   *Verifies algebraic current balance ($< 10^{-16}$ A/m residual) and generates `results/figures/current_conservation_benchmark.png`.*

3. **CRRSS Steady-State Gating Curves:**
   ```bash
   python src/crrss_gating_plots.py
   ```
   *Generates monotonic $h_\infty$ inactivation curves ($V_{1/2} = -74.5$ mV; Chiu et al. 1979).*

4. **Phase 1 Controls (Figure 2):**
   ```bash
   python src/plot_fig2_control.py
   ```
   *Simulates isolated Aβ saltatory conduction ($42.7$ m/s) and unmyelinated C-fiber conduction ($0.41$ m/s).*

5. **Phase 2 Controls & Multi-Fiber Trend (Figure 3):**
   ```bash
   python src/plot_fig3_control.py
   ```
   *Simulates Nav1.8/Nav1.9 nociceptor cable ($0.26$ m/s) and reproduces the multi-fiber saturation plateau.*

6. **Authoritative Phase 2 Multi-Fiber Sweep (Figure 4):**
   ```bash
   python src/phase2_multifiber_sweep.py
   ```
   *Executes the synchronous vs 1.5-ms jitter multi-fiber sweep ($n \in [1, 50]$) from settled rest $-66.82$ mV.*

7. **Spatial Grid Refinement Study:**
   ```bash
   python src/convergence_study.py
   ```
   *Sweeps spatial discretization $\Delta z \in [20, 10, 5, 2.5]\,\mu\text{m}$ holding physical node width $l_{\text{node}} = 1.0\,\mu\text{m}$ fixed.*

---

## 5. Provenance & Computational Lineage

Every quantitative statement, table row, and plotted data point in the revised manuscript is tied to a frozen data file through the supplementary traceability manifests:
- **[`supplementary/MANIFEST.md`](supplementary/MANIFEST.md):** Detailed claim-by-claim provenance table mapping every number to its generating script, parameter configuration, and raw output row.
- **[`supplementary/manuscript_number_inventory.csv`](supplementary/manuscript_number_inventory.csv):** Machine-readable inventory of all 56 numerical claims.
- **[`supplementary/manuscript_before_after_matrix.csv`](supplementary/manuscript_before_after_matrix.csv):** 33-item comparative audit detailing every revision made in response to peer review.

---

## 6. Citation

If you use this model or code in your research, please cite:

```bibtex
@article{attia2026ephaptic,
  title={Ephaptic A$\beta$-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation},
  author={Attia, Mina Saied},
  journal={Journal of Computational Neuroscience},
  year={2026},
  note={Under review}
}
```

---

## 7. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
