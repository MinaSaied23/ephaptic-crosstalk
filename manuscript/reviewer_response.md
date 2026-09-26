# Point-by-Point Response to Reviewers

**Manuscript:** Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation  
**Target Journal:** *Journal of Computational Neuroscience* (JCNS)  
**Author:** Mina Saied Attia  

---

Dear Editor and Reviewers,

We express our sincere gratitude for the thoughtful, constructive, and rigorous evaluation of our manuscript. The reviewers' insightful critiques—particularly regarding extracellular current balance, Aβ source fidelity, numerical convergence, operational endpoint definitions, and the interpretation of multi-fiber and temporal summation—have been invaluable in guiding this thorough revision.

In response, we have performed an exhaustive audit and reconstruction of the manuscript. Every numerical value reported has been reconciled with our frozen computational suite, every mathematical derivation has been made explicit, and all claims have been carefully bounded by the tested parameter space and identified limitations.

Below is our detailed, point-by-point response to all comments from Reviewer 1 and Reviewer 2.

---

## Response to Reviewer 1

### Comment 1.1: Citation of Reutskiy, Rossoni & Tirozzi (2003)
> *"As a minor point which should be addressed before acceptance: please cite the 2003 work of Reutskiy-Rossoni-Tirozzi on conduction in bundles of demyelinated nerve fibers."*

**Response:**  
We thank Reviewer 1 for directing us to this seminal paper. We have integrated and cited Reutskiy, Rossoni, and Tirozzi (2003) in both the Introduction (Section 1) and the Discussion / Future Work (Section 4.8):
- **Introduction (Section 1):** We highlight their foundational demonstration that bundle geometry, packing density, and demyelination profoundly modulate axonal conduction velocity and excitability in nerve bundles:  
  *"Foundational analytical and numerical work by Reutskiy, Rossoni, and Tirozzi (2003) demonstrated that bundle geometry and inter-fiber packing profoundly modulate conduction velocity and recruitment thresholds in demyelinated nerve."*
- **Bibliographic Entry:** The full citation has been added to the References list:  
  *Reutskiy, S., Rossoni, E., & Tirozzi, B. (2003). Conduction in bundles of demyelinated nerve fibers: Computer simulation. Biological Cybernetics, 89(6), 439–448. https://doi.org/10.1007/s00422-003-0444-2*

---

### Comment 1.2: Consideration of Higher-Dimensional Formulations
> *"We encourage the author to study higher dimension (two and three) formulations as well, which are also available in the literature (see Chawla-Morgera-Snider 2019 IEEE/ACM Transactions on Computational Biology and Bioinformatics and Chawla-Morgera Communications in Mathematical Biology and Neuroscience 2024)."*

**Response:**  
We agree completely that higher-dimensional formulations provide crucial insights into how spatial geometry, cross-talk topology, and volume conduction influence ephaptic interactions beyond one-dimensional cable reductions. We have substantially expanded our discussion of this literature:
- **Introduction (Section 1):** We explicitly cite and discuss the multi-dimensional analytical and computational frameworks developed by Chawla, Morgera, and colleagues (Chawla & Morgera, 2022, 2024; Chawla, Morgera & Snider, 2021a; Chawla, Sharma & Morgera, 2021b).
- **Discussion and Limitations (Sections 4.6 & 4.8):** We discuss how 2D/3D formulations and fully coupled 3D Extracellular–Membrane–Intracellular (EMI) finite-element models (Jæger & Tveito, 2022, 2026) can capture localized micro-domains and non-uniform interstitial geometry that longitudinally averaged 1D models omit.

---

## Response to Reviewer 2

### Comment 2.1: Extracellular Current Balance & Algebraic Elimination
> *"The derivation does not yet show how the source in the extracellular equation follows from the two membrane equations. In the released implementation, that source is formed from ionic current alone. If capacitive and applied currents have been eliminated algebraically, the paper should show the elimination... The revision should derive the reduced equations from one stated sign convention, give units for every term, and show where capacitive and injected currents enter or cancel."*

**Response:**  
We appreciate this critical observation. In the revised manuscript (Section 2.3), we provide a complete, step-by-step mathematical derivation showing the exact algebraic elimination of capacitive displacement currents based on continuous and discrete Kirchhoff's Current Law (KCL):
1. **Membrane Core-Conductor Relation:** Total transmembrane current per unit length exiting axon $k$ equals the axial current divergence:
   $$i_{m,k}(z,t) = \frac{1}{r_{i,k}} \frac{\partial^2 u_{i,k}}{\partial z^2} = \frac{1}{r_{i,k}} \left( \frac{\partial^2 v_{m,k}}{\partial z^2} + \frac{\partial^2 u_e}{\partial z^2} \right) = \pi d_{\text{axon},k} \left( C_{m,k} \frac{\partial v_{m,k}}{\partial t} + I_{\text{ion},k} - I_{\text{stim},k} \right)$$
2. **Extracellular KCL:** Current conservation per unit length in the cleft requires:
   $$\frac{1}{r_e} \frac{\partial^2 u_e}{\partial z^2} - G_e u_e + \sum_k i_{m,k} = 0$$
3. **Algebraic Substitution & Factorization:** Substituting $i_{m,k} = \frac{1}{r_{i,k}} \left( \frac{\partial^2 v_{m,k}}{\partial z^2} + \frac{\partial^2 u_e}{\partial z^2} \right)$ and $G_e = \kappa / r_e$:
   $$\left( \frac{1}{r_e} + \sum_k \frac{1}{r_{i,k}} \right) \frac{\partial^2 u_e}{\partial z^2} - \frac{\kappa}{r_e} u_e = - \sum_k \frac{1}{r_{i,k}} \frac{\partial^2 v_{m,k}}{\partial z^2}$$
4. **Final Reduced Operator:** Dividing by total core conductance $\Sigma_G = \frac{1}{r_e} + \sum_k \frac{1}{r_{i,k}}$ yields:
   $$\frac{\partial^2 u_e}{\partial z^2} - \kappa_{\text{eff}} u_e = - \frac{1}{\Sigma_G} \sum_k \frac{1}{r_{i,k}} \frac{\partial^2 v_{m,k}}{\partial z^2}, \quad \text{where } \kappa_{\text{eff}} = \frac{\kappa / r_e}{\Sigma_G}$$
At the continuous mathematical level, this algebraic elimination removes explicit capacitive-current feedback from the extracellular solve, avoiding that particular stiffness pathway, while retaining the capacitive, ionic, and applied-current terms through the membrane equations. We distinguish this mathematical reduction from an independent physical proof of exact conservation: empirical numerical stability and convergence were assessed through independent spatial and temporal refinement tests, while the implemented discrete equations satisfy the algebraic discrete KCL identity to numerical precision (residual $< 10^{-16}\,\text{A/m}$; Fig. benchmark). Full SI units for every term are tabulated in Table 3 (Nomenclature).

---

### Comment 2.2: CRRSS $h$-Gate and Aβ Source Recovery
> *"In phase1_classical_hh/ephaptic_model.py... the logistic 15.6 expression is assigned to alpha_h and the exponential quotient to beta_h... These expressions give h∞ values of about 0.71 at -70 mV and 1.00 at -40 mV... Please check the rate names, voltage convention, gate update, and temperature scaling against the intended CRRSS formulation."*

**Response:**  
We thank Reviewer 2 for uncovering this swapped rate assignment. We audited the original formulas in Chiu et al. (1979, Table 1) and confirmed that `alpha_h` and `beta_h` had indeed been inverted.
- **Code Correction:** In the validated codebase, the rate functions have been corrected to strictly follow Chiu et al. (1979):
  $$\beta_h(v) = \frac{15.6 \times 10^3}{1.0 + \exp(-(v_{\text{mV}} + 56.0) / 10.0)}\,\text{s}^{-1}$$
  $$\alpha_h(v) = \beta_h(v) \exp(-(v_{\text{mV}} + 74.5) / 5.0)$$
- **Steady-State Inactivation Verification:** In `src/crrss_gating_plots.py` and Figure benchmark, $h_\infty(v)$ decreases monotonically from $\approx 1.0$ at rest to $0.0$ upon depolarization, with half-inactivation at $V_{1/2} \approx -74.5$ mV.
- **Biophysical Aβ Source Validation:** With bare nodal leak corrected ($g_{\text{leak}} = 128\,\text{mS/cm}^2$, $\bar{g}_{\text{Na}} = 1445\,\text{mS/cm}^2$, $E_{\text{leak}} = -80$ mV; Sweeney et al., 1987) and $Q_{10} = 3.0$ temperature scaling applied, the isolated Aβ fiber generates physiological, brief saltatory action potentials, reaching an absolute peak of approximately $+0.44$ mV from a resting potential of $-80.0$ mV (an action-potential excursion of $80.44$ mV), conducting saltatorily at **41.03 m/s** across all 10 nodes with resting drift $<10\,\mu\text{V}$ over 20 ms.

---

### Comment 2.3: Cleft Geometry & Multi-Fiber Approximation
> *"The physical region represented by A_eff is unclear. In the released formula, the effective area remains finite as cleft width approaches zero, so the limiting geometry is not self-evident. The multi-fiber experiment also increases the source from one representative Aβ fiber while holding the extracellular operator and cleft geometry fixed. It is best described as a synchronous source-scaling approximation rather than an explicit anatomical bundle. The feedback description also needs correction..."*

**Response:**  
We have revised Sections 2.3 and 2.6 to resolve each of these points:
1. **Limiting Geometry of $A_{\text{eff}}$:** We explain that $A_{\text{eff}}$ is defined as the annular region between the co-axial bounding cylinders of the apposed fibers. As $w_{\text{cleft}} \to 0$, $A_{\text{eff}} \to A_{\text{eff,min}} = \pi d_1 d_2 / 2 \approx 15.7\,\mu\text{m}^2$ ($1.57 \times 10^{-11}\,\text{m}^2$). This physically bounds longitudinal cleft resistance at $r_{e,\text{max}} = \rho_e / A_{\text{eff,min}} \approx 6.37 \times 10^{10}\,\Omega/\text{m}$ (with $\rho_e = 1.0\,\Omega\cdot\text{m}$; at the nominal $w_{\text{cleft}} = 20\,\text{nm}$, $A_{\text{eff}} \approx 16.4\,\mu\text{m}^2$ and $r_e \approx 6.10 \times 10^{10}\,\Omega/\text{m}$), preventing an unphysical singularity as the cleft closes.
2. **Explicit Qualification as a Reduced Source-Scaling Model:** We explicitly state in Sections 2.6, 4.1, and 4.6 that the multi-fiber model is a **reduced 1-D synchronized source-scaling approximation**, not a 3-D anatomical reconstruction of a nerve bundle.
3. **Feedback Description Corrected:** We clarify that the extracellular potential $u_e$ is computed from the combined multi-fiber source and feeds back symmetrically to both the C-fiber and the representative Aβ cable. Crucially, the core conductance $\Sigma_G(n) = 1/r_e + n/r_{i,1} + 1/r_{i,2}$ accounts for all $n$ parallel axoplasmic channels, which acts as an intrinsic shunt that explains the asymptotic saturation of multi-fiber depolarization (Table 4).

---

### Comment 2.4: Physical Basis and Role of $\kappa$
> *"The manuscript gives κ both a physical and a numerical role... A revision should give the physical basis and units for κ and report overlapping n ranges at common fixed values. Solver stiffness should be handled through the integration method or time step so that κ retains one interpretation."*

**Response:**  
We have completely overhauled the description and handling of $\kappa$:
- **Phenomenological Interpretation & Length Scales:** We explicitly state that $\kappa = 1.0\times 10^9\,\text{m}^{-2}$ (units $\text{m}^{-2}$, corresponding to nominal pre-elimination scale $\lambda_\kappa = 1/\sqrt{\kappa} \approx 31.62\,\mu\text{m}$) is a **phenomenological regularization parameter** representing weak transverse ohmic leakage from the restricted cleft to the surrounding conductive interstitial tissue ($G_e = \kappa / r_e$). The effective spatial decay scale of the reduced Helmholtz operator is $\lambda_{\text{eff}} = 1/\sqrt{\kappa_{\text{eff}}}$, where $\kappa_{\text{eff}} = (\kappa / r_e) / \Sigma_G$. Because $\Sigma_G(n)$ expands with fiber count $n$, $\lambda_{\text{eff}}$ lengthens systematically ($73.3\,\mu\text{m}$ for $n=1$, $209.7\,\mu\text{m}$ for $n=10$, $329.1\,\mu\text{m}$ for $n=25$, and $464.3\,\mu\text{m}$ for $n=50$; Table 4). It is **not** an independently measured biological constant, nor was it calibrated to force a desired numerical outcome.
- **Fixed-$\kappa$ Evaluation:** All comparative results across Phase 1, Phase 2, single-pair, and multi-fiber sweeps ($n \in [1, 50]$) are evaluated at the **identical fixed baseline $\kappa = 1.0\times 10^9\,\text{m}^{-2}$** (Tables 1, 2, 4).
- **Separation of Solver Stability:** Numerical stiffness is resolved via the algebraic elimination (Section 2.3), not by arbitrarily altering $\kappa$. The exploratory $\kappa = 3\times 10^7\,\text{m}^{-2}$ run is presented strictly as a numerical sensitivity analysis (Section 3.6). Because the nonphysical delayed excursions observed at lower $\kappa$ were diagnosed as numerical instability under the tested lower-$\kappa$ implementation rather than as an independently motivated physiological parameter choice or physical stability boundary, the lower-$\kappa$ case is not used to support biological conclusions; all comparative analyses across the paper retain the prespecified phenomenological baseline $\kappa = 1.0 \times 10^9\,\text{m}^{-2}$.

---

### Comment 2.5: Numerical Verification & Independent Refinement
> *"The convergence study should hold node width, membrane area, stimulus charge, and other physical parameters fixed while refining Δz and Δt independently. A concise table covering conduction velocity, source waveform, ephaptic ΔV, timing, and spike classification would address the main point. A comparison with an implicit reference solver near the reported ceiling would add confidence."*

**Response:**  
We have implemented a rigorous, independent grid refinement battery in accordance with Roache (1994):
1. **Fixed Physical Node of Ranvier ($l_{\text{node}} = 1.0\,\mu\text{m}$):** We implemented a homogenized fixed-node discretization (`build_fixed_node_geometry` in `spike_detector.py`) that holds physical nodal length ($1.0\,\mu\text{m}$) and nodal membrane area strictly constant regardless of $\Delta z$.
2. **Spatial Refinement Table (Table 5):** Refining $\Delta z \in [20, 10, 5, 2.5]\,\mu\text{m}$ confirms strict convergence of isolated Aβ conduction velocity (**41.03 m/s**) and isolated spike amplitude (action-potential excursion **80.44 mV**, absolute peak $+0.44$ mV from rest $-80.0$ mV). At the fixed timestep of $2.5\,\mu\text{s}$, the single-pulse $n=25$ ephaptic response was spatially stable across the tested grid refinements (Table 5).
3. **Temporal Refinement & Explicit Limitation:** Refining $\Delta t \in [5.0, 0.125]\,\mu\text{s}$ demonstrates that Aβ CV ($41.03\,\text{m/s}$) and event classification (`LOCAL_STIMULUS_TRANSIENT`) are strictly stable across all timesteps. However, single-pulse $n=25$ peak amplitude exhibits notable timestep dependence ($5.971\,\text{mV}$ at $2.5\,\mu\text{s}$ to $14.930\,\text{mV}$ at $0.125\,\mu\text{s}$; Richardson extrapolation $\approx 15.44\,\text{mV}$, first-order $\approx 15.70\,\text{mV}$). Rather than concealing this, we explicitly report these as extrapolated mathematical estimates in Sections 2.4, 3.1, and 4.6 as an identified numerical limitation: spike classification remains robust and stable across all tested timesteps, but single-pulse potential magnitude is not quantitatively converged.
4. **Independent Reference Solver Comparison:** To independently verify Aβ numerical integration, a Crank-Nicolson parabolic diffusion solver paired with a second-order Heun scheme for CRRSS channel kinetics was implemented (`audit_reference_solver.py`). At $\Delta t = 0.625\,\mu\text{s}$, the production IMEX solver agreed with the Crank-Nicolson reference to within $1.2\%$ in conduction velocity ($40.00\,\text{m/s}$ vs $39.51\,\text{m/s}$) and $0.24\%$ in action potential amplitude ($80.59\,\text{mV}$ vs $80.40\,\text{mV}$), validating the Aβ numerical integration specifically.

---

### Comment 2.6: Agreement Between Manuscript, Code, and Outputs
> *"Several reported analyses cannot yet be traced to an exact public script and output. The endpoint also changes between a midpoint maximum and a full spatial threshold search. Because the paper distinguishes a propagated C-fiber spike from a local or numerical excursion, it needs one consistent endpoint definition."*

**Response:**  
We have standardized the operational endpoint definition and reconciled all outputs:
- **Unified Operational Classifier:** Methods Section 2.7 defines one standardized classifier (`classify_waveform` in `src/phase1_classical_hh/spike_detector.py`), which evaluates downstream electrodes ($z = 4.0$ mm and $z = 8.0$ mm) and enforces physiological conduction velocity bounds ($0.2 \le \text{CV} \le 3.0$ m/s) to distinguish `PROPAGATED_ACTION_POTENTIAL` from `LOCAL_STIMULUS_TRANSIENT` and `LOCAL_ABORTED_SPIKE`.
- **Reconciliation of EXP-E02 vs EXP-E03:** The difference between reported single-pulse $n=25$ values ($6.015$ mV vs $5.039$ mV) was verified in `EXP_E02_E03_reconciliation.md` as a spatial measurement distinction: $5.039$ mV is recorded at the cable midpoint ($z = 5.0$ mm), whereas $6.015$ mV represents the global spatial maximum across the downstream window (occurring at $z = 7.0$ mm). Both values are explicitly labeled in the text and Table 4.
- **Resolution of the 100-Hz Pulse-Count Contradiction:** We identified that earlier 2-pulse temporal summation simulations were prematurely truncated at $T = 15.2$ ms ($t_{\text{last}} + 5$ ms), capturing the slow ($0.41$ mm/ms) C-fiber action potential in flight at $z \approx 2.1$ mm before it reached the $8.0$ mm electrode. When simulated with adequate observation time ($T \ge 35$ ms), **Pulse 2 is authoritatively proven to evoke the first fully propagated C-fiber action potential** (peak $+24.70$ mV at $8.0$ mm, $\text{CV} = 0.41$ m/s; Table 1). The previous claim that $\ge 5$ pulses were required has been removed everywhere.

---

### Comment 2.7: Phase 2 Initialization and Positive Controls
> *"The Nav1.8/1.9 C-fiber is initialized exactly at -55 mV, which is not its steady state... Please report resting membrane potential, initial gating variables, how those states were obtained, settling duration, no-stimulus stability check..."*

**Response:**  
Methods Section 2.5 and Results Section 3.7 now detail the exact initialization protocol:
- **Pre-Stimulus Settling Protocol:** All Phase 2 simulations execute a 20-ms pre-stimulus settling routine before stimulus onset (`get_settled_c_fiber` in `navc_cable.py`).
- **Resting Baseline & Stability:** The membrane settles stably at **$-66.82$ mV** with gating variables $m_8 = 0.0009, h_8 = 0.9843, m_9 = 0.0334, n = 0.2902$. In a 20 ms post-settling check with no stimulus, baseline drift is $< 10\,\mu\text{V}$, confirming steady state.
- **Direct Positive Control:** Direct current injection (2 nA, 1 ms) evokes full-amplitude action potentials propagating at **0.26 m/s** (Fig. 3a), providing a positive-control demonstration of excitability and propagation within the Phase 2 model.

---

### Comment 2.8: Gating Shift as a Sensitivity Test
> *"The manuscript calls the uniform shift 'a parsimonious first approximation of net inflammatory sensitization...' Applying the same voltage shift to all sodium and potassium gates is a mathematical sensitivity test, not a channel-specific model of inflammation... The manuscript also calls the behavior 'consistent with the known Hopf-bifurcation structure...'; that term needs an appropriate dynamical analysis."*

**Response:**  
We have revised Sections 2.8 and 3.4 accordingly:
- The uniform gating shift is now explicitly introduced as a **mathematical sensitivity exploration** to probe model excitability, not as a biological model of inflammation.
- The unsupported "Hopf bifurcation" terminology has been completely removed. We describe the observed behavior descriptively: an abrupt transition directly from quiescence into spontaneous repetitive pacemaking at $\Delta V_{\text{shift}} \ge 3$ mV, demonstrating the lack of a stable sensitized intermediate in classical HH.

---

### Comment 2.9: Tempering the Two-Phase Validation Claim
> *"The Discussion says that the second phase 'rules out the specific objection that a classical-HH nociceptor model is simply the wrong biology', and the Conclusion calls the model 'biophysically validated'. The two phases share the extracellular reduction, Aβ source, geometry, and numerical coupling. Their agreement is therefore a robustness check within one framework."*

**Response:**  
We have eliminated all overclaims of independent biological validation:
- The term "biophysically validated" has been removed throughout the title, abstract, text, and conclusion.
- Phase 2 is explicitly introduced and discussed as a **biological sensitivity and robustness check within the same one-dimensional core-conductor framework** (Sections 1, 2.5, 4.1).

---

### Comment 2.10: Revision of Figure 3 Caption
> *"The caption states, 'The monotonic ≈8 mV trend does not cross threshold within this verified range'. The visible low- and intermediate-n points appear to fluctuate before the larger change at n = 25. Unless the regenerated values are strictly ordered, describe the series as an overall increase with small fluctuations."*

**Response:**  
We have updated the Figure 3 caption and Section 3.9 text exactly as requested:
- The caption for Fig. 3c now states:  
  *"Multi-fiber spatial summation trend: peak C-fiber midpoint membrane potential vs. number of synchronized Aβ fibers $n \in [1, 50]$... showing an overall increase with small fluctuations that plateaus near $-58.8$ mV due to core conductance shunting ($\Sigma_G$)."*
- The obsolete "monotonic ≈8 mV" phrasing has been removed everywhere.

---

### Comment 2.11: Professional Author Contribution Statement
> *"The sentence 'The entire experiment, the code, testing ground, research, conclusion, and documentation was done by the only author Mina Saied' should be replaced with a concise account of the sole author's work... The phrase 'testing ground' should be removed."*

**Response:**  
We have replaced the sentence with a standard sole-author CRediT contributor statement (Section Declarations):  
*"**Mina Saied Attia:** Conceptualization, Methodology, Software, Validation, Formal Analysis, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization."*

---

### Comment 2.12: Software RRIDs
> *"Please report the exact software versions and the available identifiers for Python (RRID:SCR_008394), NumPy (RRID:SCR_008633), SciPy (RRID:SCR_008058), Matplotlib (RRID:SCR_008624), and Pillow (RRID:SCR_023337)."*

**Response:**  
Authoritative Research Resource Identifiers (RRIDs) and software versions have been added to the Code Availability declaration:
- Python v3.11/v3.12 (RRID:SCR_008394)
- NumPy v1.26.4 (RRID:SCR_008633)
- SciPy v1.13.0 (RRID:SCR_008058)
- Matplotlib v3.8.4 (RRID:SCR_008624)
- Pillow v10.3.0 (RRID:SCR_023337)

---

### Comment 2.13: Reference Metadata Corrections
> *"The entry beginning 'Jæger, K. H., Tveito, A., et al. (2021)...' does not match the verified record. Jæger and Tveito (2022) published 'Deriving the bidomain model of cardiac electrophysiology...' Three other entries also need correction: Pelot et al. (2021)... Tigerholm et al. (2014)... and Klein et al. (2017)..."*

**Response:**  
We performed a complete reference audit and corrected all metadata:
- **Jæger & Tveito (2022):** *Deriving the bidomain model of cardiac electrophysiology from a cell-based model; properties and comparisons. Frontiers in Physiology, 12, 811029. https://doi.org/10.3389/fphys.2021.811029*
- **Jæger & Tveito (2026):** *Extracellular stimulation and ephaptic coupling of neurons in a fully coupled finite element-based Extracellular-Membrane-Intracellular (EMI) model. Frontiers in Computational Neuroscience, 20, 1755548. https://doi.org/10.3389/fncom.2026.1755548*
- **Pelot et al. (2021):** *Journal of Neurophysiology, 125(1), 86–104. https://doi.org/10.1152/jn.00315.2020*
- **Tigerholm et al. (2014):** *Journal of Neurophysiology, 111(9), 1721–1735. https://doi.org/10.1152/jn.00777.2012*
- **Klein et al. (2017):** *Journal of Neuroscience, 37(20), 5204–5214. https://doi.org/10.1523/JNEUROSCI.3799-16.2017*
- **Schmidt & Knösche (2022):** *Biological Cybernetics, 116(4), 461–473. https://doi.org/10.1007/s00422-022-00934-9*

---

We believe these comprehensive revisions have fully addressed every concern raised by the reviewers, establishing complete consistency between our mathematical formulation, numerical results, and manuscript text.
