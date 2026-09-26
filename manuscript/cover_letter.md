# Cover Letter for Revised Submission

**Date:** September 26, 2026  
**To:** Editor-in-Chief, *Journal of Computational Neuroscience* (Springer Nature)  
**From:** Mina Saied Attia  
New Cairo STEM School, Cairo, Egypt  
Email: Mina.3024031@stemnewcairo.moe.edu.eg  

**Subject:** Resubmission of Revised Manuscript (JCNS)  
**Title:** *Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation*  

---

Dear Editor-in-Chief,

I am pleased to resubmit the substantially revised manuscript entitled **"Ephaptic Aβ-to-C-Fiber Crosstalk in Pathologically Restricted Nerve Clefts: A Closed-Loop Core-Conductor Study of Spatial and Temporal Summation"** for continued consideration for publication as a regular research article in the *Journal of Computational Neuroscience*.

We express our sincere appreciation to the Editorial Board and both reviewers for their thorough, insightful, and constructive evaluations. Their rigorous critiques—particularly regarding the exact derivation of extracellular current balance, Aβ source fidelity, spatial and temporal grid convergence, operational endpoint standardization, and the nuanced interpretation of multi-fiber spatial and temporal summation—have guided a comprehensive forensic audit, reconstruction, and mathematical reconciliation of our study.

### Summary of Major Revisions and Forensic Reconciliations:
1. **Extracellular Current-Balance Derivation & Exact Algebraic Elimination:** In Section 2.3, we provide a complete, 4-step continuous mathematical derivation demonstrating the exact algebraic elimination of membrane capacitive displacement currents from the extracellular solve. We tabulate full SI units for every parameter and variable in Table 3 (Nomenclature) and verify that the discrete equations satisfy the discrete Kirchhoff's Current Law identity to numerical precision (residual $< 10^{-16}\,\text{A/m}$, verified in an accompanying benchmark figure).
2. **Correction of CRRSS $h$-Gate Kinetics & Physiological Aβ Source Recovery:** Following Reviewer 2's identification of inverted rate assignments, we corrected the $\alpha_h/\beta_h$ formulation strictly according to Chiu et al. (1979). Inactivation $h_\infty(v)$ now decreases monotonically with $V_{1/2} \approx -74.5$ mV (documented in a benchmark figure). With Sweeney et al. (1987) nodal leakage parameters and temperature scaling applied, the isolated Aβ fiber generates physiological action potentials (excursion $80.44$ mV, resting baseline $-80.0$ mV with drift $<10\,\mu\text{V}$) propagating saltatorily at **$41.03$ m/s**.
3. **Rigorous Physical Refinement & Numerical Verification:** We implemented a homogenized fixed-node discretization ($l_{\text{node}} = 1.0\,\mu\text{m}$) holding physical nodal area strictly invariant under spatial refinement ($\Delta z \in [20, 2.5]\,\mu\text{m}$, Table 5). An independent Crank-Nicolson parabolic diffusion solver validated our Aβ integration within $1.2\%$ in velocity and $0.24\%$ in spike amplitude. Furthermore, temporal refinement ($\Delta t \in [5.0, 0.125]\,\mu\text{s}$) was rigorously analyzed: while spike classifications (`LOCAL_STIMULUS_TRANSIENT`) remain strictly invariant, the single-pulse $n=25$ peak potential magnitude exhibits notable timestep dependence, which we transparently disclose and report as an identified numerical limitation with Richardson extrapolation ($\approx 15.44$ mV).
4. **Resolution of Central Contradictions & Operational Standardization:** We implemented a unified operational classifier (`classify_waveform`) with dual downstream electrodes ($z = 4.0$ mm and $8.0$ mm) and physiological conduction velocity bounds ($0.2 \le \text{CV} \le 3.0$ m/s). This resolved the 100-Hz temporal summation discrepancy: we diagnosed that early 2-pulse runs had been prematurely truncated at $T = 15.2$ ms, capturing the slow ($0.41$ mm/ms) C-fiber spike in flight; canonical simulations with adequate observation time ($T \ge 35$ ms) authoritatively prove that **Pulse 2 evokes the first fully propagated C-fiber action potential** ($+24.70$ mV at $8.0$ mm). We also reconciled the EXP-E02 vs EXP-E03 measurement locations ($5.039$ mV midpoint vs $6.015$ mV downstream maximum).
5. **Phase 2 Steady-State Settling & Positive Controls:** We introduced a dedicated 20-ms pre-stimulus settling routine, establishing a stable resting baseline of **$-66.82$ mV** (drift $<10\,\mu\text{V}$). A direct positive-control simulation demonstrates that the Phase 2 Nav1.8/Nav1.9 model propagates action potentials at **$0.26$ m/s**.
6. **Tempering of Claims & Methodological Reframing:** In response to both reviewers, all overclaims have been thoroughly eliminated. The term "biophysically validated" has been excised; Phase 2 is presented strictly as a biological sensitivity and robustness check within the same 1D core-conductor framework; the multi-fiber model is explicitly qualified as a reduced 1D source-scaling approximation rather than an anatomical bundle; the uniform gating shift is framed as a mathematical sensitivity test (removing unsupported "Hopf bifurcation" terminology); and the clinical extrapolation to human dynamic mechanical allodynia is carefully circumscribed as a hypothesis-generating computational finding.
7. **Bibliographic Completeness & Reutskiy et al. (2003):** As specifically requested by Reviewer 1, foundational work by Reutskiy, Rossoni, and Tirozzi (2003) on bundle geometry and demyelination is cited and discussed in the Introduction (Section 1) and Future Work (Section 4.8). Higher-dimensional analytical (Chawla-Morgera) and finite-element EMI formulations (Jæger-Tveito) are comprehensively reviewed. All 30 references have been verified for complete metadata and DOIs.
8. **Compliance and Metadata:** Author contributions have been restated using standard sole-author CRediT taxonomy, and authoritative Research Resource Identifiers (RRIDs) have been provided for all scientific software.

### Accompanying Submission Materials:
1. **Revised Manuscript:** Clean, fully reconciled markdown document (`ephaptic_crosstalk_paper_JCNS_revised.md`).
2. **Point-by-Point Response to Reviewers:** Comprehensive document responding to each comment with exact manuscript locations and computational evidence (`reviewer_response.md`).
3. **Figures (7 files, 300 DPI):** Figures 1–4, plus three rigorous verification benchmarks (CRRSS gating curves, discrete KCL conservation residual, and spatial grid convergence).
4. **Supplementary Verification Artifacts:** Number inventory matrix (54 verified claims), before/after revision matrix (38 items), forensic zero-trust verification report, and raw spatial/temporal convergence CSV datasets.

The manuscript has not been published elsewhere, nor is it under consideration by any other journal. The author declares no competing financial or non-financial interests.

Thank you very much for your time and editorial guidance. We look forward to hearing your decision.

Sincerely,

**Mina Saied Attia**  
New Cairo STEM School  
Cairo, Egypt  
Email: Mina.3024031@stemnewcairo.moe.edu.eg  
