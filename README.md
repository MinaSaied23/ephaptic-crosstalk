# Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation

Official simulation codebase, mathematical benchmarks, reproduction battery, and manuscript package for the revised study submitted to the *Journal of Computational Neuroscience* (JCNS).

**Author:** Mina Saied Attia Rizk  
**Affiliation:** New Cairo STEM School, Cairo, Egypt  
**Status:** Code and data accompanying the revised manuscript under review at the *Journal of Computational Neuroscience*

---

## 1. Scientific Overview & Key Biophysical Findings

Dynamic mechanical allodynia—pain evoked by light touch—is widely hypothesized to involve non-synaptic ephaptic crosstalk between large myelinated Aβ tactile afferents and unmyelinated C-fiber nociceptors at sites of focal demyelination or nerve compression. This repository implements a biophysically grounded, closed-loop, one-dimensional core-conductor cable model coupling a Chiu-Ritchie-Rogart-Stagg-Sweeney (CRRSS) myelinated Aβ axon to an unmyelinated C-fiber across a shared pathologically restricted extracellular cleft ($w_{\text{cleft}} = 20\,\text{nm}$ to $5\,\mu\text{m}$).

To eliminate numerical stiffness from explicit capacitive displacement feedback, the framework implements an algebraic elimination of capacitive currents derived from continuous Kirchhoff's Current Law (KCL). Crosstalk is evaluated across two distinct kinetic paradigms:
1. **Phase 1 (Classical Hodgkin-Huxley):** Classical HH kinetics serving as an established baseline model ($V_{\text{rest}} = -65.000$ mV).
2. **Phase 2 (Nociceptor-Realistic Nav1.8/Nav1.9):** Incorporates mammalian TTX-resistant Nav1.8 and persistent Nav1.9 channel kinetics with a settled 20-ms pre-stimulus resting baseline ($V_{\text{rest}} = -66.82$ mV; drift $< 10\,\mu\text{V}$).

### Summary of Authoritative Quantitative Findings

| Biophysical Phenomenon | Phase 1 (Classical HH) | Phase 2 (Nav1.8/Nav1.9 Nociceptor) | Biophysical Mechanism |
|---|:---:|:---:|---|
| **Single-Pair Single-Pulse Coupling** | $\Delta V = 1.325$ mV ($20$ nm cleft) | $\Delta V = 1.76$ mV (midpoint $-65.07$ mV) | **Strictly subthreshold**; limited single-fiber source current into the cleft. |
| **Multi-Fiber Spatial Summation ($n=25$)** | $\Delta V = 5.039$ mV (midpoint), $6.015$ mV (downstream max) | $\Delta V = 10.16$ mV (midpoint peak $-56.66$ mV) | Order-of-magnitude amplification, remaining well below threshold ($-35.0$ mV in Phase 2). |
| **Multi-Fiber Saturation Plateau ($n \to 50$)** | Depolarization saturates near $+6.2$ mV ($6.184$ mV at $n=50$) | Depolarization saturates near $-56.4$ mV ($10.42$ mV at $n=50$) | **Parallel core conductance shunting:** $\Sigma_G(n)$ expands with fiber count, lengthening $\lambda_{\text{eff}}$ ($73.3 \to 464.3\,\mu\text{m}$) and shunting cleft current. |
| **Conduction Velocity Deceleration** | Aβ CV slows: $40.00$ ($n=1$) $\to 32.00$ ($n=25$) $\to 27.12$ m/s ($n=50$) | N/A (single Aβ driver) | Collective cleft resistive loading decelerates the active source. |
| **Temporal Dispersion / Jitter Attenuation** | **92.9% attenuation** ($6.02 \to 0.426$ mV downstream max across $1.5$ ms window) | **93.8% attenuation** ($-56.66 \to -66.20$ mV across $1.5$ ms window) | Desynchronization collapses temporal overlap of source currents across fibers. |
| **100-Hz Repetitive Train ($n=25$)** | **Spike initiated by Pulse 1 at the sealed boundary arrives during the Pulse 2 window** ($+24.70$ mV peak, CV $0.41$ m/s) | Not required for suprathreshold demonstration | Conduction delay, not demonstrated temporal summation (a single pulse yields the same spike); requires observation window $T \ge 35$ ms. |
| **Discrete KCL Conservation** | Algebraic residual $< 10^{-16}$ A/m | Algebraic residual $< 10^{-16}$ A/m | Machine-precision current conservation across all 1000 compartments. |

---

## 2. Repository Structure

```
├── .gitignore                          # Clean git ignores for Python cache, OS, and temporary files
├── LICENSE                             # MIT Open-Source Research License
├── README.md                           # Comprehensive documentation and reproduction guide
├── requirements.txt                    # Pinned library dependencies
├── test_invariants.py                  # Unit and invariant test suite (parameters, homogenization, units)
├── run_verification_battery.py         # Automated end-to-end verification battery 
├── manuscript/
│   ├── ephaptic_crosstalk_paper_JCNS_revised.docx  # Revised manuscript (Word)
│   └── ephaptic_crosstalk_paper_JCNS_revised.pdf   # PDF rendering of the manuscript
├── results/
│   ├── figures/                        # High-resolution 300-DPI publication figures
│   │   ├── fig1_model_schematic.png    # Manuscript Fig. 1: Model architecture schematic
│   │   ├── fig2_phase1_control.png     # Manuscript Fig. 5: Phase 1 positive controls (Aβ & C-fiber CVs)
│   │   ├── fig3_phase2_control.png     # Manuscript Fig. 6: Phase 2 positive controls & multi-fiber trend
│   │   ├── phase2_multifiber_sweep.png # Manuscript Fig. 7: Phase 2 multi-fiber sweep & jitter attenuation
│   │   ├── crrss_gating_plots.png      # Manuscript Fig. 2: CRRSS steady-state gating curves
│   │   ├── current_conservation_benchmark.png # Manuscript Fig. 3: Discrete KCL residual (< 1e-16 A/m)
│   │   └── fig_convergence_analysis.png # Manuscript Fig. 4: Spatial/temporal refinement
│   └── convergence/                    # Authoritative frozen CSV datasets
│       ├── EXP_E02_E03_reconciliation.csv   # Midpoint vs downstream spatial maximum reconciliation
│       ├── final_100Hz_reconciliation.csv   # Pulse 1 vs Pulse 2 propagation trajectory data
│       ├── kappa_effective_table.csv        # Effective regularization scale across n in [1, 50]
│       ├── phase2_headline_results.csv      # Baseline headline results across coupling configurations
│       ├── phase2_multifiber.csv            # Phase 1 multi-fiber n-series (n in [1, 50])
│       ├── phase2_navc_multifiber.csv       # Phase 2 multi-fiber sweep data (manuscript Fig. 7)
│       ├── phase2_synchrony.csv             # Phase 1 jitter attenuation sweep
│       ├── phase2_temporal_summation.csv    # Frequency sweep (50 to 800 Hz)
│       ├── sensitization_phase1_*.csv       # Phase 1 bias / kinetics-shift results and cable cross-checks
│       ├── sensitization_phase2_*.csv       # Phase 2 bias results and cable responses
│       ├── boundary_spike_phase1.csv, boundary_spike_phase2.csv  # Boundary-initiated spike vs n
│       ├── lesion_control_high_n.csv        # Grounded interior-lesion control, n up to 200
│       ├── spatial_convergence.csv          # Fixed-node spatial grid refinement (dz in [20, 2.5] um)
│       └── temporal_convergence_final.csv   # Temporal grid refinement (dt in [10, 0.125] us)
├── src/
│   ├── abeta_recovery_test.py          # Aβ refractory and dual-pulse recovery check
│   ├── audit_reference_solver.py       # Crank-Nicolson reference check of the Aβ cable solver (Sec. 2.4.3)
│   ├── run_convergence_battery.py      # Spatial and temporal grid convergence (Table 5, Sec. 2.4.1-2.4.2)
│   ├── plot_convergence_figure.py      # Fig. 4 from the convergence CSVs
│   ├── crrss_gating_plots.py           # Corrected Chiu et al. (1979) steady-state gating curves
│   ├── current_conservation_benchmark.py # Discrete KCL conservation benchmark
│   ├── interior_lesion_test.py         # Boundary condition isolation verification
│   ├── phase2_multifiber_sweep.py      # Script generating manuscript Fig. 7
│   ├── plot_fig2_control.py            # Script generating manuscript Fig. 5
│   ├── plot_fig3_control.py            # Script generating manuscript Fig. 6
│   ├── run_lesion_audit.py             # Lesion audit test driver
│   ├── run_sensitization_phase1.py     # Phase 1 tonic-bias and HH kinetics-shift protocols (Sec. 2.8, 3.3, 3.4)
│   ├── run_sensitization_phase2.py     # Phase 2 tonic-bias protocol and depolarization block (Sec. 3.8)
│   ├── run_boundary_spike_threshold.py # Boundary-spike threshold n* and grounded-lesion control up to n = 200 (Sec. 3.9.1)
│   ├── phase1_classical_hh/
│   │   ├── artifact_timing_check.py    # Lower-kappa sensitivity test
│   │   ├── coupled_model.py            # Phase 1 closed-loop coupled core-conductor solver
│   │   ├── ephaptic_model.py           # Phase 1 biophysical parameters & CRRSS kinetics
│   │   ├── experiment1_single_pulse.py # Single-pulse cleft-width parameter sweep
│   │   ├── experiment_summation.py     # High-frequency pulse train driver (100 Hz)
│   │   ├── positive_control.py         # Direct stimulation positive controls
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
    ├── MANIFEST.md                     # Claim-to-code traceability manifest 
    ├── manuscript_number_inventory.csv # Line-item quantitative inventory
    └── manuscript_before_after_matrix.csv # Revision change log
```

---

## 3. Installation & Environment Setup

The codebase is written in standard Python 3.10+ (tested on Python 3.11 and 3.12). No specialized neural simulators (e.g., NEURON, Brian2) are required; all cable partial differential equations (PDEs) are solved using vectorized NumPy and SciPy banded linear solvers (`scipy.linalg.solve_banded`).

### Quickstart

```bash
# Clone the repository
git clone https://github.com/MinaSaied23/ephaptic-crosstalk.git
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

4. **Phase 1 Controls (manuscript Fig. 5):**
   ```bash
   python src/plot_fig2_control.py
   ```
   *Simulates isolated Aβ saltatory conduction ($41.03$ m/s, maximum-upstroke metric between $z = 4$ and $8$ mm) and unmyelinated C-fiber conduction ($0.41$ m/s).*

5. **Phase 2 Controls & Multi-Fiber Trend (manuscript Fig. 6):**
   ```bash
   python src/plot_fig3_control.py
   ```
   *Simulates Nav1.8/Nav1.9 nociceptor cable ($0.26$ m/s) and reproduces the multi-fiber saturation plateau.*

6. **Authoritative Phase 2 Multi-Fiber Sweep (manuscript Fig. 7):**
   ```bash
   python src/phase2_multifiber_sweep.py
   ```
   *Executes the synchronous vs 1.5-ms jitter multi-fiber sweep ($n \in [1, 50]$) from settled rest $-66.82$ mV.*

7. **Spatial Grid Refinement Study:**
   ```bash
   python src/run_convergence_battery.py     # writes results/convergence/spatial_convergence.csv and temporal_convergence_final.csv (about 3 min)
   python src/plot_convergence_figure.py     # redraws results/figures/fig_convergence_analysis.png (Fig. 4)
   ```
   *Sweeps spatial discretization $\Delta z \in [20, 10, 5, 2.5, 1.25, 1.0]\,\mu\text{m}$ (at $\Delta t = 2.5\,\mu\text{s}$) and temporal discretization $\Delta t \in [5.0, \ldots, 0.125]\,\mu\text{s}$ (at $\Delta z = 10\,\mu\text{m}$) with $w_{\text{cleft}} = 20$ nm, holding physical node width $l_{\text{node}} = 1.0\,\mu\text{m}$ fixed. `python src/run_convergence_battery.py --verify` is a 3-second regression check of the nominal grid.*

8. **Independent Reference-Solver Check (Sec. 2.4.3):**
   ```bash
   python src/audit_reference_solver.py
   ```
   *Compares the production IMEX Aβ solver with a Crank-Nicolson reference at $\Delta t = 0.625\,\mu\text{s}$, $\Delta z = 10\,\mu\text{m}$ (2 nA stimulus): conduction velocity $40.00$ vs $39.51$ m/s ($1.2\%$), action potential excursion at $z = 4$ mm $79.98$ vs $79.78$ mV ($0.24\%$). The solvers share the membrane model and geometry, so this checks the Aβ time integration only.*


9. **Sensitization protocols and boundary-spike threshold (Sec. 2.8, 3.3, 3.4, 3.8, 3.9.1):**
   ```bash
   python src/run_sensitization_phase1.py       # tonic bias + HH kinetics shift (about 5 min)
   python src/run_sensitization_phase2.py       # Phase 2 tonic bias, block onset, cable responses (about 8 min)
   python src/run_boundary_spike_threshold.py   # boundary-spike threshold n* (Phase 1, Phase 2) and lesion control up to n = 200 (about 15 min)
   ```
   *The C-fiber starts at its exact resting equilibrium, the perturbation is switched on at t = 0, and the membrane is followed for 1-2 s (space-clamped analysis, which is exact for a spatially uniform perturbation; selected points are verified on the full coupled cable). Outputs are the `sensitization_*`, `boundary_spike_*` and `lesion_control_high_n` CSVs in `results/convergence/`.*
---

## 5. Provenance & Computational Lineage

Every quantitative statement, table row, and plotted data point in the revised manuscript is tied to a frozen data file through the supplementary traceability manifests:
- **[`supplementary/MANIFEST.md`](supplementary/MANIFEST.md):** Detailed claim-by-claim provenance table mapping every number to its generating script, parameter configuration, and raw output row.
- **[`supplementary/manuscript_number_inventory.csv`](supplementary/manuscript_number_inventory.csv):** Machine-readable inventory of the numerical claims in the manuscript.
- **[`supplementary/manuscript_before_after_matrix.csv`](supplementary/manuscript_before_after_matrix.csv):** Log of revisions made in response to peer review.

---

## 6. Citation

If you use this model or code in your research, please cite:

```bibtex
@article{attia2026ephaptic,
  title={Ephaptic A$\beta$-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation},
  author={Attia Rizk, Mina Saied},
  journal={Journal of Computational Neuroscience},
  year={2026},
  note={Under review}
}
```

---

## 7. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
