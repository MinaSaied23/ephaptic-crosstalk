## 2 Methods

### 2.1 Geometry and governing equations

We model one myelinated Aβ axon type and one unmyelinated C-fiber, both of length *L* = 10 mm, that share a restricted extracellular compartment along a focal lesion (z = 2.5–7.5 mm; Fig. 1a). Outside the lesion the fibers lie in grounded bulk fluid (*u*~e~ = 0). The Aβ action potential (AP) is evoked at node 0 (z = 0), outside the lesion, by a 0.2-ms intracellular current pulse of twice the threshold of the uncoupled fiber, and enters the lesion as a propagating wave. *n* identical Aβ fibers are stimulated synchronously (Section 2.5); a single C-fiber is the test fiber.

For fiber *k* (1 = Aβ, 2 = C) with intracellular potential *u*~k~, extracellular potential *u*~e~ and transmembrane potential *v*~k~ = *u*~k~ − *u*~e~, the core-conductor equations are (Fig. 1b)

$$\pi d_k\left(C_{m,k}\frac{\partial v_k}{\partial t}+I_{\mathrm{ion},k}\right)=g_k\frac{\partial^2 (v_k+u_e)}{\partial z^2}+\pi d_k I_{\mathrm{stim},k},\qquad g_k=\frac{1}{r_{i,k}}=\frac{\pi d_k^2}{4\rho_i},$$

where *d*~k~ is the axoplasmic diameter (7 µm for Aβ, i.e. an outer diameter of 10 µm and a g-ratio of 0.7; 1 µm for the C-fiber), ρ~i~ the axoplasmic resistivity, and *C*~m,k~, *I*~ion,k~, *I*~stim,k~ are per unit membrane area. Inside the lesion, conservation of current in the shared compartment gives

$$\frac{1}{r_e}\frac{\partial^2 u_e}{\partial z^2}-G_e u_e+n\,i_{m,1}+i_{m,2}=0,\qquad i_{m,k}=g_k\frac{\partial^2(v_k+u_e)}{\partial z^2},$$

with *r*~e~ = ρ~e~/*A*~e~ the longitudinal resistance per unit length of a compartment of cross-section *A*~e~, and *G*~e~ a transverse leak conductance per unit length from the compartment to grounded bulk tissue. We parameterize the leak by κ = *r*~e~*G*~e~ (m^−2^), so that λ~e~ = κ^−1/2^ is the passive length constant of the compartment alone. Outside the lesion *u*~e~ = 0. The cable ends are sealed. Any current injected by the stimulating electrode leaves through the membrane of the stimulated compartment, which lies outside the lesion in all production runs.

![**Fig. 1** Model. (a) Geometry: *n* synchronously stimulated Aβ fibers (CRRSS nodes every 1 mm) and one C-fiber share an extracellular compartment of cross-section *A*~e~ along a 5-mm focal lesion; outside the lesion the fibers lie in grounded bulk fluid. The Aβ stimulus (2× threshold, 0.2 ms) is applied at node 0, outside the lesion. (b) Equivalent circuit per unit length and governing equations; the three fields are advanced together.](../results/figures/fig1_model.png){width=100%}

### 2.2 Membrane models

**Aβ fiber.** Nodes of Ranvier (length *l*~node~ = 1 µm, spacing 1 mm, ten nodes at z = 0, 1, …, 9 mm) carry CRRSS kinetics (Chiu et al., 1979; Sweeney et al., 1987):

$$\alpha_m=\frac{97+0.363\,Y}{1+e^{(31-Y)/5.3}},\quad \beta_m=\frac{\alpha_m}{e^{(Y-23.8)/4.17}},\quad \beta_h=\frac{15.6}{1+e^{(24-Y)/10}},\quad \alpha_h=\frac{\beta_h}{e^{(Y-5.5)/5}}\ \ (\mathrm{ms^{-1}}),$$

with *Y* = *V* + 80 mV and *I*~Na~ = *ḡ*~Na~ *m*^2^*h*(*V* − *E*~Na~). The rate constants are used as given by Sweeney et al. (1987) for 37 °C, without further temperature scaling. Internodes are passive compact myelin. A computational compartment of width Δz containing a node is homogenized with node fraction *f* = *l*~node~/Δz, so that nodal membrane area, capacitance and conductances are independent of the grid (Table 1). Two values depart from Sweeney et al. (1987) and are modelling choices: the nodal capacitance (2.0 rather than 2.5 µF cm^−2^) and the g-ratio (0.7 rather than 0.6).

**C-fiber, Phase 1 (HH).** Classical Hodgkin–Huxley kinetics (Hodgkin & Huxley, 1952) with *ḡ*~Na~ = 120, *ḡ*~K~ = 36, *g*~L~ = 0.3 mS cm^−2^, *E*~Na~ = +50, *E*~K~ = −77, *E*~L~ = −54.4 mV (resting potential −65.00 mV). The rate functions are the squid-axon rates at 6.3 °C, multiplied by φ = 3^(*T*−6.3)/10^ when a temperature *T* is specified (Section 2.6).

**C-fiber, Phase 2 (NavC).** A phenomenological, calibrated TTX-resistant membrane: Nav1.8 (*m*~8~^3^*h*~8~), persistent Nav1.9 (*m*~9~), the HH delayed rectifier (*n*^4^) and a leak,

$$I_{\mathrm{ion},2}=\bar g_{18}m_8^3h_8(V-E_{\mathrm{Na}})+\bar g_{19}m_9(V-E_{\mathrm{Na}})+\bar g_{\mathrm K}n^4(V-E_{\mathrm K})+g_L(V-E_L),$$

with Boltzmann steady states (*V*~1/2~, *k*) = (−25, 6), (−42, 6) and (−50, 5) mV for *m*~8~, *h*~8~ (inactivating) and *m*~9~, and voltage-independent time constants τ~m8~ = 1.5 ms, τ~h8~ = 2 ms and τ~m9~ = 10 ms. The activation parameters are in the range reported for TTX-resistant currents of small DRG neurons (Akopian et al., 1996; Cummins et al., 1999), but the model is a simplification: the time constants are voltage independent, there is no Nav1.7 and only one K^+^ current, and two parameters were calibrated rather than taken from data. With the literature-range inactivation values (*V*~1/2~ ≈ −30 mV, τ~h8~ ≈ 17 ms) the reduced membrane settled on a non-repolarizing depolarized state, so *V*~1/2~ was moved to −42 mV and τ~h8~ to 2 ms; *ḡ*~K~ was raised to 60 mS cm^−2^, and *ḡ*~18~ = 2000 and *ḡ*~19~ = 0.2 mS cm^−2^ were chosen to give an overshooting AP with APD~50~ ≈ 7 ms. Resting potential −66.82 mV.

**Shared cable properties.** Both C-fiber models use the same cable (diameter 1 µm, *C*~m~ = 1 µF cm^−2^, ρ~i~ = 54.7 Ω cm), and ρ~i~ is the same for the Aβ fiber. Phase 1 and Phase 2 therefore differ only in C-fiber membrane kinetics; the Aβ model, stimulus, geometry, numerics and endpoints are identical. All parameters are collected in Table 1 and are read from a single parameter module in the code.

{{TABLE:table1_parameters}}

**Table 1.** Model parameters, as defined in `src/ephaptic/params.py` (this table is generated from that module). "Modelling choice", "calibrated" and "assumption" mark values that are not taken directly from the cited source.

### 2.3 Extracellular compartment

The production compartment has a fixed cross-section *A*~e~ = 16.4 µm^2^. This is the cross-section of a fiber pair whose surrounding space is a circle circumscribing both fibers, widened by 20 nm, minus the two fiber cross-sections. Spread uniformly around one Aβ fiber, 16.4 µm^2^ corresponds to a periaxonal gap of 0.50 µm; the model is a one-dimensional mean-field description and does not resolve a 20-nm cleft as such. When *n* fibers share *A*~e~, the extracellular cross-section per Aβ fiber is *A*~e~/*n*. In the compartment equation the fiber count and the cross-section enter together: dividing the equation by *n* replaces (1/*r*~e~, *G*~e~) with (1/*n r*~e~, *G*~e~/*n*) at the same κ, so adding fibers to a fixed compartment acts like shrinking the compartment around one fiber. The correspondence is not exact, because the C-fiber's own axial conductance *g*~2~ is not rescaled; it is 1.6 % of the total axial conductance at *n* = 1 and 0.08 % at *n* = 25, and the resulting deviation grows with *n* (Section 3.5). We therefore report every multi-fiber result also in terms of the equivalent periaxonal gap *w*~eq~ of a uniform sleeve with area *A*~e~/*n* around a 10-µm fiber (*w*~eq~ = 0.50 µm at *n* = 1, 21 nm at *n* = 25, 5 nm at *n* = 100), as a readable measure of confinement rather than as an exact mapping. We also used an alternative closure in which every fiber brings its own sleeve of width *w*, so that *A*~e~ grows with *n* and the confinement is set by *w* alone (Section 3.5).

κ is not a measured quantity. The baseline κ = 10^9^ m^−2^ (λ~e~ = 31.6 µm) is a calibration rather than a measurement: it is the value at which a single fiber pair produces a response of a few millivolts, which is the regime this study is about. Because that is a choice and not a datum, no conclusion is drawn from it alone, and κ is varied over five decades (10^6^–10^11^ m^−2^, λ~e~ = 1 mm to 3 µm), which brackets a nearly sealed compartment and one that is short-circuited to the bulk within a few micrometres.

### 2.4 Numerical method

The three fields are discretized with second-order central differences (Δz = 5 µm, 2000 compartments) and advanced together by backward Euler (Δt = 1 µs): at each step the linear system for [*v*~1~, *v*~2~, *u*~e~] at the new time level is solved in one banded LU solve (LAPACK `gbtrf/gbtrs`, factorized once per run), so the extracellular potential is never lagged behind the membrane potentials. Gating variables are advanced by a Rush–Larsen step at the old potential, and ionic currents are evaluated at the updated gates and old potentials. A conductance-implicit variant (ionic conductances in the system matrix, refactorized every step) was used as an independent check. It agreed with the production scheme for *n* ≤ 50, but at Δt = 1 µs it misplaced the Aβ conduction-block boundary at *n* = 100 ({{nearblock_implicit_dt1p0}} mV vs {{nearblock_explicit_dt0p1}} mV at Δt = 0.1 µs, which the explicit scheme reproduces at 1 µs: {{nearblock_explicit_dt1p0}} mV). It is therefore not used for the Aβ fiber. Initial conditions are the exact steady state of the coupled system, obtained by Newton's method from the space-clamped resting potential of each membrane; it is uniform to within 10^−6^ V (resting Na^+^ conductance holds the Aβ nodes a fraction of a microvolt above the internodes, which drives a standing extracellular potential of the same order).

A cheaper and widely used alternative is to compute *u*~e~ from the membrane potentials of the previous step and feed ∂^2^*u*~e~/∂z^2^ back explicitly, which keeps the two cables independent and tridiagonal. Because the explicit term cancels a fraction *n g*~1~/Σ~G~ of the implicit axial term, with Σ~G~ = 1/*r*~e~ + *n g*~1~ + *g*~2~, the resulting time-step error grows with *n*. We implement that scheme as well (`run_lagged`) and quantify its error against the monolithic solution (Section 3.1), because the error is invisible at *n* = 1, where the two schemes agree, and appears only as fibers are added.

### 2.5 Multi-fiber volleys and temporal dispersion

Synchronous volleys use one representative Aβ cable whose axial conductance enters the compartment equation with weight *n*. Dispersed volleys use *K* explicit Aβ cables, each representing *n*/*K* fibers, all sharing the same compartment, with stimulus onsets spaced uniformly over a window of width *W*. Because the depolarization produced by one fiber lasts only ~0.1 ms, *K* must be large enough that the spacing *W*/(*K* − 1) is well below that, or the ensemble peak merely tracks the response of one group. We therefore set *K* so that the spacing is at most 25 µs (*K* = 61 at *W* = 1.5 ms), and verified convergence in *K* and in Δz (Table S7). Because the cost of a step grows with *K* times the number of compartments, the dispersion sweep uses Δz = 20 µm; the grid dependence is reported in the same table. *W* was varied from 0 to 2 ms.

### 2.6 Sensitivity analysis

Around the production configuration we varied, one or two factors at a time:

- the number of synchronous fibers *n* (1–300, i.e. *w*~eq~ = 0.5 µm to 1.7 nm);
- κ (10^6^–10^11^ m^−2^);
- lesion length (1–7 mm);
- stimulus strength (1.2–20 × threshold);
- the dispersion window *W* (0–2 ms);
- repetitive trains of 5 pulses at 50–400 Hz;
- a uniform depolarizing bias current on the C-fiber, up to the loss of stability of its resting state (HH, at 0.1 A m^−2^) or to 3.5 A m^−2^ (NavC, whose resting state stays stable over that range), with the equilibria and their linear stability computed from the space-clamped membrane equations, and a no-stimulus control for every bias;
- the speed of C-fiber kinetics.

For the kinetics, we used HH at 6.3–25 °C; a "time-compressed" HH membrane in which all rates *and* maximal conductances are multiplied by *s* = 2–10, which is equivalent to dividing all time scales and the membrane time constant by *s* while preserving excitability (HH with standard conductances fails to conduct at 30 °C); HH with the conductances alone multiplied by *s*; NavC with τ~m8~ = 1.5–0.05 ms; and a time-compressed NavC membrane (all gate time constants divided by *s*, all conductances multiplied by *s*). Every kinetic variant was first verified to conduct an AP when stimulated directly (Table 2). The variants span C-fiber conduction velocities of {{variant_cv_min}}–{{variant_cv_max}} m/s. Variants with scaled-up conductances have membrane time constants comparable to Δt. Their C-fiber ionic current was treated conductance-implicitly, while the Aβ fiber kept the explicit treatment. This agreed with Δt = 0.25 µs runs (implicit and explicit) to within {{fast_dt_maxdev_pct}} % in subthreshold peak depolarization, with identical spike classification (`e02b_fast_variants.csv`).

### 2.7 Endpoints and threshold characterization

The primary endpoint is a **propagating C-fiber AP**: the C-fiber overshoots 0 mV over a stretch of at least 3 mm, and the overshoot front moves outward at 0.05–5 m/s, measured over the outermost 1 mm on either side. This tolerates near-simultaneous initiation at several nodes. The same criterion is applied to every run. Runs continue until the overshoot has spread over 7 mm, until the system has returned to within 0.25 mV of rest (no earlier than 4 ms, and at least 2 ms after the last stimulus), or until 25 ms. Secondary endpoints are the peak C-fiber depolarization in the lesion (Δ*V*, relative to the exact resting state), the peak hyperpolarization, and whether the Aβ AP conducts through the lesion to the last node (*v*~1~ crossing −40 mV, with crossing times interpolated within the step).

Because no fixed voltage threshold applies to a brief, spatially non-uniform depolarization, we measured excitability directly in two ways:

1. **Strength–duration curves** of the isolated C-fiber for intracellular current pulses of 0.02–20 ms, either injected at one point or applied uniformly over the 5-mm lesion segment. We report the threshold and the peak depolarization reached by a pulse 0.5 % below threshold.
2. **An ephaptic safety factor α\*.** The *u*~e~(z, t) recorded in a closed-loop run is applied with gain α to the isolated C-fiber, and α\* is the smallest gain that evokes a propagating AP. Because the C-fiber carries at most 1.6 % of the compartment's axial conductance, removing it barely changes *u*~e~: at α = 1 the open-loop response reproduced the closed-loop depolarization to within {{openloop_maxdiff_pct}} % in every case. α\* is therefore the factor by which the ephaptic drive would have to grow to excite the fiber, and α\* = 1 means the closed-loop drive itself fires it.
