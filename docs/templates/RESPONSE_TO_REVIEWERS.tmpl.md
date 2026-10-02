<!-- Generated from docs/templates/RESPONSE_TO_REVIEWERS.tmpl.md by manuscript/build_manuscript.py; numbers come from results/data. Edit the template, not docs/RESPONSE_TO_REVIEWERS.md. -->
# Response to the reviewers

**Manuscript:** Ephaptic Aβ-to-C-Fiber Crosstalk and Multi-Fiber Spatial Summation: A Closed-Loop Core-Conductor Study with Nociceptor-Realistic Channel Kinetics
**Journal:** *Journal of Computational Neuroscience*
**Author:** Mina Saied Attia Rizk

---

## Statement before the point-by-point replies

I thank both reviewers for the time they gave this manuscript. Reviewer 2's report sent me back to
the implementation rather than to the text, and that re-examination found two errors that neither
reviewer could have been expected to find in full, and whose consequences reach the central result.
I set them out here rather than leaving them to be discovered among the replies.

**1. The inactivation gate of the Aβ membrane was inverted.** Reviewer 2 is right (Major 2). In the
submitted code the two CRRSS *h*-rate expressions were exchanged, so steady-state inactivation rose
with depolarization and the action potential settled on a positive plateau instead of repolarizing.
The rates are corrected. Inactivation now falls from *h*~∞~ = {{ab_hinf_m80}} at −80 mV to
{{ab_hinf_m40}} at −40 mV, the action potential returns to rest within {{ab_ap_return_ms}} ms
(Fig. S1), and the fiber shows an ordinary refractory period and recovery (Table S3). Everything
that uses the Aβ fiber as its source has been recomputed.

**2. The coupling scheme was not convergent in the number of fibers.** The submitted solver computed
the extracellular potential from the previous step's membrane potentials and fed it back explicitly.
That lagged term cancels a fraction *n g*~1~/Σ~G~ of the implicit axial term, so its time-step error
grows with the number of fibers: at *n* = 25 the submitted scheme gives {{lag_n25_dt2p5}} mV where
the converged answer is {{mono_n25_dt2p5}} mV. The reported ≈8 mV multi-fiber trend, and the
"stability ceiling" and artifact-detection protocol built around it, were therefore properties of the
discretization. Intracellular and extracellular potentials are now advanced together by backward
Euler in one banded solve, and every endpoint is shown to converge (Section 3.1, Tables S1–S2).

**What this does to the conclusions.** The direction of the central finding is unchanged and is now
much better supported: no propagating C-fiber action potential occurs for any standard membrane,
over *n* = 1–300, five decades of extracellular leak, lesion lengths of 1–7 mm, stimuli of 1.2–20 ×
threshold, 50–400-Hz trains, onset dispersion, or sensitizing bias. What changes is the multi-fiber
story. Summation does not saturate; it grows to {{NavC_max_dv}} mV and is then limited by failure of
the Aβ action potential inside the confined lesion — the same confinement that strengthens the
coupling blocks its source. The submitted manuscript's proposal that multi-fiber spatial summation
is "a plausible, partially-supported candidate mechanism" is therefore withdrawn, and the title has
been changed from "… Requires Multi-Fiber Spatial Summation" accordingly. The artifact-detection
protocol is gone, replaced by convergence evidence.

Because so much was recomputed, the code was rewritten as a single documented package with one
parameter module, and every number, table and figure in the manuscript is now generated from the
simulation outputs by a script (`src/build_tables.py`); the build fails if any quoted value has no
generating run behind it. `docs/MANIFEST.md` links every figure, table and number to its script and
raw output. An AI assistant (Claude, Anthropic) was used in the re-implementation and in editing;
this is declared in the manuscript, and I have checked the code, results and text and take
responsibility for them.

---

## Reviewer 1

> *"This is a very well written and worked out paper … We encourage the author to study higher
> dimension (two and three) formulations as well … As a minor point which should be addressed before
> acceptance: please cite the 2003 work of Reutskiy-Rossoni-Tirozzi on conduction in bundles of
> demyelinated nerve fibers."*

I thank the reviewer for the encouraging assessment.

**R1.1 — Reutskiy, Rossoni and Tirozzi (2003).** Cited, in the Introduction, among the closed-loop
core-conductor treatments of bundles of demyelinated fibers that precede this work.

**R1.2 — Higher-dimensional formulations.** Chawla, Morgera and Snider (*IEEE/ACM TCBB*) and Chawla
and Morgera (2024) are now cited in the Introduction alongside the other higher-dimensional and
resistor-network treatments, and the Discussion names the move to a resolved two- or
three-dimensional geometry, specifically a fully coupled EMI formulation (Jæger & Tveito, 2026), as
the step that would test the one-dimensional mean-field reduction used here. The present study stays
one-dimensional; Section 2.3 and Section 3.5 now state what that reduction does and does not
represent, and quantify the error of its mean-field step ({{meanfield_mindev_pct}} % at *n* = 2
rising to {{meanfield_maxdev_pct}} % at *n* = 50).

---

## Reviewer 2 — major comments

**R2.1 Extracellular current balance.**
Done. Section 2.1 now derives the compartment equation from one stated sign convention, with units
for every term, and shows where the capacitive and applied currents enter: the axial current that
each fiber delivers to the compartment is *g*~k~ ∂²(*v*~k~ + *u*~e~)/∂z², so the capacitive and
ionic terms are not separated in the source, and electrode current that enters the compartment is
returned through it. The physical Kirchhoff residual of the assembled system is reported as a
result, not as an algebraic solver residual: it is at most {{kcl_rel_max}} of the peak source
(`e02_kcl.csv`). The submitted implementation's ionic-only source is one of the things corrected.

**R2.2 CRRSS h gate and recovery of the Aβ source.**
The reviewer's diagnosis was correct; see the statement above. Section 3.3 and Fig. S1 now report
*m*~∞~, *h*~∞~, τ~m~ and τ~h~ over the modelled range, an action potential followed through
repolarization to rest, and a paired-pulse protocol: a second stimulus at
{{ab_refractory_max_fail_ms}} ms evokes no propagating action potential, recovery begins at
{{ab_recovery_min_ms}} ms, and by {{ab_full_recovery_ms}} ms the second action potential matches the
first (Table S3). The uncoupled fiber conducts at {{abeta_cv}} m/s with a
{{abeta_excursion}}-mV excursion, and the stimulus is now {{abeta_stim_nA}} nA — twice the measured
threshold of {{abeta_threshold_nA}} nA — applied outside the lesion, instead of 100 nA inside the
compartment, which drove node 0 to {{abeta_node0_100nA}} mV. All analyses were rerun.

**R2.3 Cleft geometry and the multi-fiber approximation.**
Reframed as the reviewer suggests. The compartment is described as a one-dimensional mean-field
channel of cross-section *A*~e~, not as a resolved bundle; Section 2.3 gives the fiber geometry, the
grounded-bulk boundary outside the lesion, the area formula and its limiting behaviour, and states
that *A*~e~ = 16.4 µm² spread around one fiber corresponds to a {{weq_n1}}-nm periaxonal gap, so the
model does not resolve a 20-nm cleft as such. Because *n* fibers sharing *A*~e~ are equivalent to one
fiber in *A*~e~/*n*, every multi-fiber result is also reported as an extracellular cross-section per
fiber and an equivalent gap *w*~eq~ ({{weq_n25}} nm at *n* = 25, {{weq_n100}} nm at *n* = 100). The
experiment is called a synchronous source-scaling approximation, its mean-field error is measured
(above), and an alternative closure in which every fiber carries its own sleeve is run as a check
(Section 3.5, Fig. 5c). The feedback description is corrected: the field solved from the *n*-scaled
source is fed back to the representative cable, as the implementation does.

**R2.4 Physical role of κ.**
κ now has one interpretation and is never changed for solver behaviour. Section 2.3 gives its
definition (κ = *r*~e~*G*~e~, m⁻², equivalently a compartment length constant λ~e~ = κ^−1/2^) and
states plainly that the submitted version's value was calibrated to produce a response of a few mV
and then raised when the explicit scheme became hard to integrate. In place of calibration, κ is
swept over five decades, 10⁶–10¹¹ m⁻², at every *n* ({{kappa_runs}} runs): no C-fiber action
potential occurs anywhere in that range, and the largest depolarization is {{kappa_max_dv}} mV.
Stiffness is handled by the implicit scheme, as the reviewer recommends. Every script now writes the
parameter set it actually ran into a `.meta.json` beside its output; the mislabelled
`artifact_timing_check.py` was deleted with the rest of the superseded code.

**R2.5 Numerical verification.**
Rebuilt along the lines the reviewer sets out. The root cause of the 35.6 → 42.6 → 49.6 m/s velocity
drift was that the nodal mask was tied to the grid: refining Δz changed the physical node. Each node
is now homogenized into its compartment with area fraction *l*~node~/Δz, so nodal membrane area,
capacitance and conductance are grid-invariant, and the stimulus is specified as a current, not a
current density. Δt and Δz are then refined independently at fixed physics (Table S2): the production
values change by at most {{conv_dt_maxdev_pct}} % under Δt refinement and {{conv_dz_maxdev_pct}} %
under Δz refinement, with the spike classification invariant throughout. A conductance-implicit
variant of the scheme serves as the independent reference solver the reviewer asks for, agreeing to
within {{conv_scheme_maxdev_pct}} %. Conduction velocity, the source waveform, ephaptic Δ*V*, timing
and classification are all covered.

**R2.6 Agreement between manuscript, code and outputs.**
One endpoint is now defined once (Section 2.7) and applied to every run: a propagating C-fiber action
potential is an overshoot of 0 mV over at least 3 mm whose front moves outward at 0.05–5 m/s, with
Δ*V* measured against the exact resting state. The midpoint-maximum readout is gone. Every quoted
number, table and figure is generated from `results/data` by `src/build_tables.py`;
`docs/MANIFEST.md` lists, for each figure, table and number, the script that produces it and the raw
output it reads; each CSV has a `.meta.json` recording its parameters; `python run_all.py`
regenerates everything and `python -m pytest` checks the model, the current balance, the parameter
set and the stored values. Settings that differed between text and code (bias, frequency, duration,
cleft width, κ, source count) were reconciled before anything was regenerated.

**R2.7 Phase 2 resting state and stimulus units.**
Done. Point and cable stimuli use the same convention: a current in amperes, converted through the
compartment membrane area, with the area stated. Every run starts from the exact coupled steady
state, obtained by Newton iteration from the space-clamped equilibrium, rather than from an asserted
−55 mV, and every sensitization condition has a matched no-stimulus control, so the baseline drift
the reviewer measured (−55.008 → −65.681 mV) cannot contaminate an ephaptic response. Section 3.3 and
Table S4 add the basic characterization asked for: resting potential, small-signal input resistance
(measured {{navc_Rin_Mohm}} MΩ against {{navc_Rin_pred_Mohm}} MΩ predicted for NavC, agreeing to
{{cf_Rin_maxdev_pct}} %), passive time constant, length constant and the rheobase of a 1-ms point
injection ({{navc_rheobase_nA}} nA), alongside waveform and conduction (Table 2). The membrane is
described throughout as a phenomenological Nav1.8/Nav1.9 model, with each calibrated parameter named
as calibrated, and the conductance sensitivity analysis spans temperature, time compression, τ~m8~
and conductance scaling (Section 3.7).

**R2.8 Central result.**
Table 3 reports every sampled *n* from 1 to 300: the depolarization for both membranes, the
hyperpolarization, min *u*~e~, whether the Aβ action potential still crosses the lesion, its velocity
there, the safety factor α\* for each membrane, and the spike classification — all generated from
`e03_n_sweep.csv` and `e07_safety_factor.csv`. For the tested geometry, synchrony and parameter set,
within the verified numerical range: one Aβ fiber gives {{NavC_n1_dv2}} mV; the largest value at any
*n* is {{NavC_max_dv}} mV at *n* = {{NavC_max_dv_n}}; the Aβ action potential fails inside the lesion
from *n* = {{ab_fail_n}} (*w*~eq~ ≈ {{ab_fail_weq}} nm); and no propagating C-fiber action potential
occurs at any *n*, with a minimum safety factor of {{alpha_std_min}} across the standard membranes.

---

## Reviewer 2 — minor comments

**R2.m1 Equations and nomenclature.** The manuscript is built with native Word equations (via
pandoc), and each symbol now has one form in text, figures, tables and the parameter table. The
Nomenclature section was removed in favour of Table 1, which lists every symbol with its value,
units and source.

**R2.m2 Classical HH as a simplified baseline.** The claim that it is "the field's standard
formulation and the one on which essentially all prior closed-loop ephaptic models rely" is gone.
Section 2.2 presents it as a deliberately simplified baseline and cites Tigerholm et al. (2014),
Sundt et al. (2015) and Pelot et al. (2021) for the materially different formulations used for
mammalian unmyelinated sensory axons.

**R2.m3 Normal Remak anatomy vs lesion geometry.** The Discussion now separates them: a normal Remak
bundle is unmyelinated axons held by a non-myelinating Schwann cell, usually with Schwann-cell
processes between them, and does not ordinarily contain a large myelinated fiber (Murinson &
Griffin, 2004). The pathological change the model presupposes — loss of myelin together with
retraction of the intervening Schwann-cell processes, so that an exposed Aβ axolemma and a C-fiber
share one restricted space over millimetres — is now named explicitly.

**R2.m4 The gate shift as a sensitivity test.** The uniform shift has been dropped rather than
relabelled. Sensitization is now a uniform depolarizing bias current, and the transition the
submitted version described loosely as a Hopf bifurcation is treated with the analysis the reviewer
asks for: the space-clamped equilibria are continued against the bias and classified by the
eigenvalues of the membrane Jacobian, so the loss of stability is located rather than asserted
(Section 3.7, Table S6). Every biased run has a no-stimulus control.

**R2.m5 Figure 3 caption.** The claim of a monotonic ≈8 mV trend is withdrawn with the result it
described. The *n* series is now given in full in Table 3 and plotted in Fig. 5, and the text states
where it rises, where it peaks and where it collapses as the Aβ source fails, rather than asserting
monotonicity.

**R2.m6 Author contributions.** Rewritten in CRediT terms: conceptualization, methodology, software,
validation, formal analysis, investigation, data curation, writing (original draft, review and
editing), visualization. "Testing ground" is gone.

**R2.m7 RRIDs.** Added to Code Availability, with versions: Python 3.11 (RRID:SCR_008394), NumPy
1.26.4 (RRID:SCR_008633), SciPy 1.13.0 (RRID:SCR_008058), pandas 2.2.2 (RRID:SCR_018214), Matplotlib
3.8.4 (RRID:SCR_008624). Biological-resource RRIDs are not applicable.

**R2.m8 Reference metadata.** Corrected throughout: Pelot et al. (2021) *J Neurophysiol* 125(1),
86–104; Tigerholm et al. (2014) 111(9), 1721–1735; Klein et al. (2017) *J Neurosci* 37(20),
5204–5214. The mis-stated Jæger and Tveito entry has been replaced by the EMI paper actually relied
on (Jæger & Tveito, 2026), and the cardiac bidomain paper is no longer cited as an ephaptic model.
Every in-text citation was checked against the final list, and DOIs are given throughout.

**R2.m9 Validation claims tempered.** The Discussion no longer says the second phase "rules out" the
objection that classical HH is the wrong biology, and the Conclusion no longer calls the model
"biophysically validated". The claim made is the one the runs support: no propagating action
potential occurred in the tested implementations and parameter ranges, and the two membranes agree
because they share the extracellular reduction, the source and the numerics, which makes their
agreement a robustness check within one framework.

---

## Items the author should confirm before submission

- The AI-assistance statement in Declarations (wording and placement per journal policy).
- Whether to cite a clinical source for dynamic mechanical allodynia in the Introduction; the
  revision currently cites only the mechanistic literature.
