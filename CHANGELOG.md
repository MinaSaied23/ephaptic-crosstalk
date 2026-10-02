# Changelog

## Version 2.0 (October 2026): full re-analysis after pre-submission review

A pre-submission review found that the multi-fiber results and the proposed saturation
mechanism of version 1 were numerical artifacts, and that the Phase 1 vs Phase 2
comparisons were confounded. Version 2 replaces the code, data, figures and manuscript.
Version 1 remains available in the git history (commit `63ce2da`).

### Numerics
- **Coupling scheme (review Issue 1).** Version 1 computed the extracellular potential
  from the previous step's membrane potentials and fed it back explicitly. That lagged term cancels a
  fraction n·g₁/Σ_G of the implicit axial term, so the time-step error grew with the
  number of fibers n (n = 25: 6.0 mV at Δt = 2.5 µs vs 15.4 mV converged). Version 2
  advances [v₁, v₂, u_e] together by backward Euler in one banded LU solve
  (`src/ephaptic/model.py`). The old scheme is kept only as `run_lagged()`, to document
  its error (`e02_lagged_vs_monolithic.csv`, Fig. 2a).
- **Convergence of every endpoint.** Every coupled endpoint is shown to converge under
  Δt and Δz refinement (`e02_refinement.csv`). A conductance-implicit variant of the
  scheme serves as an independent check; it is used for the C-fiber in the fast kinetic
  variants, whose membrane time constant approaches the time step (`e02b_fast_variants.csv`).
- **Current balance (Issue 14).** The physical Kirchhoff residual is now reported
  (≈10⁻¹¹ of the peak source); the algebraic solve residual is no longer cited as
  evidence of conservation.
- **Initial conditions (Issue 15).** Runs start from the exact coupled steady state
  (Newton), seeded by the space-clamped equilibrium, not from an approximate state.
- **Production grid.** Δz = 5 µm and Δt = 1 µs for all runs. Version 1 used
  2.5 µs in Phase 1 and 1 µs in Phase 2.
- **Conduction-velocity times.** Crossing times are interpolated within a step, which
  removes the Δt quantization of conduction velocity.

### One consistent model (Issues 4, 5, 13)
- **Single parameter module.** All parameters live in `src/ephaptic/params.py`
  (dataclasses). The two `ephaptic_model.py` files, whose shared name caused the Phase 2
  lesion control to run with Phase 1 constants, are gone.
- **One Aβ model.** The same Aβ model is used throughout (CRRSS, E_Na = +35.64 mV,
  ρ_i = 54.7 Ω cm), with the same stimulus and Δt. In version 1, Phase 2 also changed
  the Aβ E_Na (+50 mV), ρ_i (50 Ω cm) and the effective stimulus (π·d₁ normalization).
- **HH C-fiber E_Na.** Now +50 mV as stated in the text (version 1 code used +35.64 mV);
  the resting potential is −65.00 mV.
- **Shared C-fiber cable.** Both C-fiber models use the same cable (1 µm, 1 µF cm⁻²,
  54.7 Ω cm). Phase 1 and Phase 2 now differ only in membrane kinetics.
- **CRRSS temperature.** The manuscript now says that the CRRSS rates are used as
  published for 37 °C with no extra Q₁₀ scaling (version 1 text claimed Q₁₀ = 3
  scaling). It also states that C_m,node = 2.0 µF cm⁻² and the g-ratio of 0.7 are
  modelling choices that depart from Sweeney et al. (1987).
- **HH temperature.** Squid HH kinetics at 6.3 °C are stated explicitly, and
  temperature (6.3–25 °C) is varied.

### Configuration and endpoints (Issues 6, 7, 15)
- **Focal lesion.** The production configuration is a 5-mm focal lesion (z = 2.5–7.5 mm)
  with grounded bulk outside. The Aβ stimulus is 2× threshold (3.0 nA), applied outside
  the lesion. Version 1 applied 100 nA inside a compartment spanning the whole cable,
  which drove the stimulated Aβ node to more than +700 mV (+1316 mV in the coupled
  n = 25 run).
- **Earlier geometry as a supplementary analysis.** The version 1 full-length geometry is
  kept only as a supplementary analysis of the electrode artifact (`e11_full_length.csv`).
  Its "+265 mV" was the C-fiber membrane potential at z = 0, not u_e.
- **Low-κ crossings.** The low-κ "numerical instability" of version 1 was a C-fiber
  spike launched at the stimulated end. It is re-diagnosed in `e11_full_length.csv`; in
  the focal-lesion configuration no κ in 10⁶–10¹¹ m⁻² produces a C-fiber AP.
- **One spike endpoint.** A single propagating-AP criterion (overshoot over ≥ 3 mm,
  outward CV 0.05–5 m/s) is applied to every run. ΔV is measured against the exact
  resting state.
- **Jitter.** The meaningless "n = 1 with jitter" case was dropped; the jitter width is
  swept from 0 to 2 ms and K = 11/21/41 is checked.

### New analyses (Issues 3, 8, 9, 10)
- **Excitability for brief inputs.** Strength–duration curves of the isolated C-fiber
  and an ephaptic safety factor α* (gain on the recorded u_e needed to fire). These
  replace the asserted "−35 mV Nav1.8 threshold".
- **κ swept over five decades.** κ = 10⁶–10¹¹ m⁻²; the version 1 calibration of κ is
  disclosed.
- **Geometry.** The geometry is reinterpreted as an extracellular cross-section per fiber
  (equivalent periaxonal gap). The mean-field equivalence between n fibers sharing A_e
  and one fiber with A_e/n is shown, and an alternative per-fiber-sleeve closure is
  provided.
- **Kinetic sensitivity.** HH temperature, time-compressed HH, HH conductances alone,
  NavC τ_m8 and time-compressed NavC are varied, each with its own positive control.
- **Other factors.** Lesion length, stimulus strength, 5-pulse trains (50–400 Hz) and
  sensitizing bias currents (each with a no-stimulus control).
- **NavC naming.** The NavC membrane is described as phenomenological and calibrated,
  with each calibration stated.

### Reproducibility (Issues 11, 12, 17)
- **Generated tables and numbers.** Every table and every number quoted in the
  manuscript is produced from `results/data` by `src/build_tables.py`. The manuscript
  sources use `{{key}}` placeholders and the build fails on any unresolved key. The
  hand-typed headline CSV and the inventories are removed.
- **New tests.** `tests/test_model.py` checks the parameter sets, the current balance,
  the lagged-scheme error, scheme agreement, the mean-field equivalence and regenerated
  values against the stored CSVs. It replaces the circular `test_invariants.py` and the
  exit-code-only battery.
- **One pipeline.** `run_all.py` regenerates every result, figure and table.
- **Dependencies.** pandas and pytest added to `requirements.txt`. No script writes
  outside the repository.

### Manuscript (Issues 2, 3, 16 and claims audit)
- **Removed.** The saturation / "axoplasmic shunting" mechanism, the −35 mV threshold
  framing, the "21.66 mV below threshold" margin, the "20-nm cleft" framing and the
  "temporal summation" title.
- **Citations.** DRG cross-excitation is no longer cited as ephaptic evidence (Amir &
  Devor 1996 added). LFPy and the cardiac bidomain paper are no longer cited as ephaptic
  models. Binczak et al. 2001, Bokil et al. 2001, Capllonch-Juan & Sepulveda 2020,
  Sheheitli & Jirsa 2020, Bolzoni & Jankowska 2019 and Rattay 1986 are added.
- **Rewritten from regenerated data.** Abstract, Results, Discussion, Conclusion and all
  tables and figures; new Fig. 1 (geometry and equivalent circuit).
