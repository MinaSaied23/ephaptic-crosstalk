<!-- Generated from docs/templates/RESPONSE_TO_REVIEW.tmpl.md by manuscript/build_manuscript.py; all numbers come from results/data. -->
# Internal audit response (2 October 2026)

This document answers an independent audit of the submitted version, carried out in addition to
the journal's peer review. The reply to the journal's reviewers is `RESPONSE_TO_REVIEWERS.md`;
this one is kept as the technical record of the audit's 17 issues.

This document answers the 17 issues of the pre-submission review point by point. Every number below is generated from `results/data` by `src/build_tables.py`, the same source used for the manuscript. Version 1 of the code and manuscript is in the git history (commit `63ce2da`).

**Summary.** We accept the review's central findings:
- The multi-fiber magnitudes and the saturation mechanism of version 1 were numerical artifacts.
- The Phase 1 vs Phase 2 comparisons were confounded.
- The "−35 mV threshold" was not a property of the model.

We rebuilt the solver (monolithic implicit coupling) and unified the model. We moved the Aβ stimulus outside the lesion at 2 × threshold, measured excitability for brief inputs directly, and swept every parameter the review named. We then rewrote the manuscript from regenerated data.

The qualitative negative result survives and is now much better supported. Its explanation is different: what prevents firing is the shape of the drive (~{{fwhm_n10_us}} µs, spatially narrow, near-zero net charge) together with the source limit (Aβ conduction failure under confinement). It is not slow gating. Faster gating alone changed the response by < {{kin_NavC_tau_m8_maxdev_pct}} %. Excitation does occur when the whole Hodgkin–Huxley membrane is made fast (time constant at rest ≤ {{kin_hh_speed_min_tau}} ms) and the extracellular cross-section per fiber is very small; it never occurs with Nav1.8/Nav1.9 kinetics, whose activation lies {{navc_m8_gap}} mV above rest. The paper now reports that boundary explicitly.

---

### Issue 1: lagged u_e coupling
**Done.** `src/ephaptic/model.py` advances [v₁, v₂, u_e] together by backward Euler in one banded LU solve. The old scheme is kept only as `run_lagged()` to document its error (Fig. 2a, Table S1):

- In the version 1 geometry and parameters, n = 25 gives {{lag_n25_dt2p5}} mV (lagged, Δt = 2.5 µs) against {{mono_n25_dt2p5}} mV (monolithic, already Δt-converged; {{mono_n25_dt0p125}} mV at 0.125 µs). This reproduces the review's reference values.
- Every endpoint of the production configuration changes by ≤ {{conv_dt_maxdev_pct}} % from Δt = 1 to 0.125 µs and ≤ {{conv_dz_maxdev_pct}} % from Δz = 5 to 1.25 µm, for n = 1–50 and both models (Table S2, Fig. 2b–c).
- A conductance-implicit variant agrees to within {{conv_scheme_maxdev_pct}} % for n ≤ 50 (`e02b_fast_variants.csv` documents where it does not, near the Aβ block boundary, and which scheme is used there).

### Issue 2: saturation / shunting mechanism
**Removed.** The response grows until the Aβ source fails inside the lesion: from n = {{ab_fail_n}} (w_eq ≈ {{ab_fail_weq}} nm), with Aβ CV in the lesion falling from {{ab_cv_n1}} to {{ab_cv_lastcond}} m/s before failure. Section 4.3 explains this as one mechanism: confinement strengthens the coupling and also loads the Aβ fiber.

### Issue 3: the −35 mV threshold
**Removed and replaced by measurements.**
- Strength–duration curves of the isolated C-fiber show that a 0.1-ms point pulse can take the NavC membrane to {{sd_navc_point_v01}} mV without firing; a 20-ms pulse fires it from {{sd_navc_point_v20}} mV.
- An ephaptic safety factor α* (gain on the recorded u_e needed to fire) is {{alpha_navc_n25}} for NavC and {{alpha_hh_n25}} for HH at n = 25. Its minimum over all standard membranes and n is {{alpha_std_min}}.
- τ_m8 (1.5 → 0.05 ms) and HH temperature (6.3–25 °C) were swept, as requested; neither changes the outcome. See Sections 3.5, 3.6 and 4.2.

### Issue 4: parameters vs code; Phase 1 vs Phase 2 confound
**Done.** One parameter module, `src/ephaptic/params.py`, and Table 1 is generated from it.
- One Aβ model (E_Na = +35.64 mV, ρ_i = 54.7 Ω cm), one stimulus (2 × {{abeta_threshold_nA}} nA), one Δt (1 µs) and one C-fiber cable are used for both phases.
- The HH E_Na is now +50 mV, so rest is {{hh_rest}} mV.
- The text now says the CRRSS rates are used as published for 37 °C (no Q₁₀ scaling), and that C_m,node = 2.0 µF cm⁻² and the g-ratio of 0.7 are modelling choices that depart from Sweeney et al.
- `tests/test_model.py::test_parameter_sets_are_the_documented_ones` asserts all of this.

### Issue 5: module-shadowing bug in the lesion control
**Fixed by construction.** There is a single package, and no parameter module is duplicated. The focal-lesion configuration is now the production configuration for every experiment, with each experiment's parameters written to `results/data/*.meta.json`.

### Issue 6: stimulation and boundary configuration
**Done.**
- **Production setup.** The Aβ stimulus is 2 × threshold ({{abeta_stim_nA}} nA), applied outside the lesion; node 0 peaks at {{abeta_node0_2x}} mV. Electrode current that enters a compartment is now returned through it.
- **Earlier geometry, supplementary.** The version 1 full-length geometry is analysed in Section 3.9 / Table S6. With 2 × threshold stimulation no C-fiber AP occurs for n ≤ 50. With 100 nA, the electrode site becomes non-physiological under either treatment: with the electrode current omitted from the compartment (as in version 1) a propagating AP is launched there from n = {{fullO_HH_100nA_nmin}} (HH; the Nav1.8/1.9 fiber only overshoots locally, from n = {{fullO_NavC_100nA_overshoot_only}}), with it returned through the compartment from n = {{full_HH_100nA_nmin}} (HH) / {{full_NavC_100nA_nmin}} (NavC), and u_e at the electrode reaches {{full_NavC_100nA_n25_ueabs}} mV. The weakest electrode current that launches such a spike is {{full_boundary_min_nA}} nA, {{full_boundary_stim_ratio}} × the physiological stimulus. At n = 25 the Aβ node 0 reaches {{full_NavC_100nA_n25_ab0}} mV and the C-fiber at z = 0 reaches {{full_NavC_100nA_n25_cz0}} mV, while u_e(0) stays below {{full_NavC_100nA_n25_ue0}} mV.
- **The "+265 mV".** The manuscript no longer attributes it to u_e.

### Issue 7: low-κ "numerical instability"
**Re-diagnosed.** In the earlier geometry with 100 nA and κ = 3 × 10⁷ m⁻², the crossings are C-fiber APs launched at the electrode (from z = {{lowk_init}} mm at {{lowk_cv}} m/s; {{lowk_spike_cases}}), and they disappear with a 2 × threshold stimulus (largest interior depolarization {{lowk_2x_maxint}} mV). In the production configuration, no κ in 10⁶–10¹¹ m⁻² produces any C-fiber overshoot ({{kappa_runs}} runs). The time-unit and output-path bugs of `artifact_timing_check.py` disappear with the script, which was removed.

### Issue 8: κ tuning and sensitivity
**Done.** Section 2.3 discloses the calibration of κ. κ is swept over five decades (λ_e = 1 mm to 3 µm) for n = 1–200: no AP, largest depolarization {{kappa_max_dv}} mV (Fig. 7a).

### Issue 9: geometry
**Done.**
- **Cross-section per fiber.** Adding fibers to a fixed compartment is shown to act like shrinking the compartment around one fiber ({{meanfield_mindev_pct}} % difference at n = 2, {{meanfield_maxdev_pct}} % at n = 50; `e04_mean_field.csv`, `test_cross_section_per_fiber_scaling`). All results are also reported against the equivalent periaxonal gap w_eq.
- **Second closure.** A per-fiber-sleeve closure, in which A_e grows with n, gives n-independent responses (to within {{geom_n_invariance_pct}} %) that depend only on the gap.
- **Framing.** The "20-nm cleft" framing is gone. The manuscript states that 16.4 µm² corresponds to a 0.50-µm sleeve at n = 1.

### Issue 10: Nav1.8/1.9 model framing
**Done.** The model is now called phenomenological and calibrated, and each calibration is stated (Section 2.2). The need to test detailed C-fiber models is the main item of future work (Section 4.2).

### Issue 11: hand-typed results, circular tests
**Done.**
- **Generated tables and numbers.** Every table and every quoted number in the manuscript, this response and the README is generated from `results/data`, and the manuscript build fails on any unresolved value.
- **Removed.** The hand-typed headline CSV, the inventories and the "SUBMISSION-READY" battery are gone.
- **New tests.** `tests/test_model.py` regenerates values and compares them to the stored data, checks the current balance and the lagged-scheme error, and asserts the parameter sets.

### Issue 12: untraceable numbers
**Resolved.** Every number is traceable to a CSV row through `manuscript/generated/numbers.json`.

### Issue 13: temperature mismatch
**Done.** HH is stated to be at 6.3 °C and is swept to 25 °C (it fails to conduct at ≥ {{hh_block_temp}} °C with standard conductances). Time-compressed variants (rates and conductances scaled) represent faster membranes.

### Issue 14: KCL claim
**Done.** The physical residual is reported: ≤ {{kcl_rel_max}} of the peak source with the monolithic scheme.

### Issue 15: measurement and classification
**Done.**
- Runs start from the exact coupled steady state (Newton).
- ΔV is measured against the exact rest and within the lesion.
- One propagating-AP criterion is applied to every run.
- The n = 1 jitter case was dropped; the dispersion window is swept 0–2 ms, and the number of onset phases is now chosen so that the phase spacing is below the duration of one fiber's contribution, with convergence shown in K and Δz (Table S5).
- Conduction-velocity crossing times are interpolated within a step.

### Issue 16: literature
**Done.**
- **DRG cross-excitation.** Described as largely chemically mediated, citing Amir & Devor (1996).
- **LFPy and the cardiac bidomain paper.** No longer cited as ephaptic models.
- **Clinical source.** The weak clinical citation was removed.
- **Added.** Binczak et al. 2001, Bokil et al. 2001, Bolzoni & Jankowska 2019, Capllonch-Juan & Sepulveda 2020, Sheheitli & Jirsa 2020 and Rattay 1986; titles, journals and DOIs were checked against publisher/indexing records.
- **Background claims.** The unsupported background CV/APD statements were removed.

### Issue 17: hygiene
**Done.** pandas and pytest added to the requirements; the duplicated solver loops replaced by one solver; no output paths outside the repository; the stale markdown manuscript replaced by the sources in `manuscript/sections`. The README is generated from the same data as the manuscript.

---

### Items for the author to check before submission
1. **AI-assistance statement.** Confirm or edit the statement in the Declarations.
2. **Clinical claims.** Decide whether to re-add a clinical citation for allodynia prevalence; the weak one was removed.
3. **Cover letter.** Check the cover letter date and the journal's current article-type requirements.
4. **Equations.** Open the .docx in Word and check that the equations render as native equations (pandoc converts them; LibreOffice previews them).
