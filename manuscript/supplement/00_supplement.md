---
title: "Supplementary Information: Ephaptic coupling between myelinated Aβ and unmyelinated C-fibers in a focal nerve lesion"
author: "Mina Saied Attia Rizk"
lang: en-GB
---

## S1 Numerical verification

{{TABLE:tableS1_lagged}}

**Table S1.** The lagged coupling scheme of the earlier version vs the monolithic scheme, in the earlier full-length geometry and parameters (HH E~Na~ = +35.64 mV, 100-nA stimulus inside the compartment, Δz = 10 µm). Entries are the peak C-fiber depolarization between z = 3 and 8 mm (mV). The lagged error grows with *n*; the monolithic values are Δt-independent to within {{mono_dt_spread_pct}} %.

{{TABLE:tableS2_refinement}}

**Table S2.** Grid and time-step refinement of the peak C-fiber depolarization in the lesion (mV) in the production configuration. Unless stated, Δz = 5 µm, Δt = 1 µs, explicit ionic currents. "Conductance-implicit": ionic conductances in the system matrix.

## S2 Strength–duration characterization

{{TABLE:tableS3_strength_duration}}

**Table S3.** Point current injection at z = 5 mm into the isolated C-fiber. Q~th~: threshold charge for a 0.1-ms pulse; V~peak~: largest membrane potential at the injection site for a pulse 0.5 % below threshold; last column: ratio of threshold currents for 0.1-ms and 20-ms pulses.

## S3 Sensitizing bias

{{TABLE:tableS4_bias}}

**Table S4.** Uniform depolarizing bias current on the C-fiber (production configuration). "Spontaneous AP": no-stimulus control of 200 ms. Peak V: largest C-fiber membrane potential in the lesion after the Aβ volley. The HH resting state is linearly stable up to {{bias_HH_stable_max}} A m^−2^ and unstable from {{bias_HH_unstable_min}} A m^−2^; the NavC resting state stays stable over the whole tested range (to {{bias_NavC_tested_max}} A m^−2^) and a second stable, depolarized state appears above {{bias_navc_bistable_min}} A m^−2^ (space-clamped analysis with linear stability from the Jacobian, `e10_equilibria.csv`).

## S4 Temporal dispersion: convergence in the number of onset phases

{{TABLE:tableS5_jitter_convergence}}

**Table S5.** Dispersed volley (*n* = 25, *W* = 1.5 ms, NavC). The peak depends on the number of onset phases *K* until the spacing *W*/(*K* − 1) is well below the ~0.1-ms duration of one fiber's contribution; the production runs use a spacing of at most 25 µs. Grid refinement at *K* = 41 changes the peak by {{jit_dz_spread_pct}} %, so the sweep is run at Δz = 20 µm. One classification does depend on that choice: the synchronous *n* = 25 volley is close to Aβ conduction block, and on Δz = 20 µm its action potentials still cross the lesion, slowly ({{conv_dz20_n25_cv}} m/s), where every grid from Δz = {{conv_block_dz_max}} µm down blocks them (Table S2). The peak depolarization differs by only {{conv_dz20_n25_dev_pct}} % between the two grids, and the attenuations quoted in the text are ratios taken within one grid, so neither the attenuation nor the primary endpoint is affected.

## S5 The earlier full-length geometry

{{TABLE:tableS6_full_length}}

**Table S6.** Shared compartment along the whole cable, sealed ends, Aβ electrode at node 0 inside the compartment (κ = 10^9^ m^−2^, *A*~e~ = 16.4 µm^2^). C-fiber action potentials are launched at the electrode site only with suprathreshold electrode currents; the electrode-site membrane potentials show the non-physiological state produced by 100 nA.

![**Fig. S1** Earlier full-length geometry. (a, b) Peak C-fiber membrane potential at the electrode site z = 0 vs *n* for Aβ stimuli of 2× threshold to 100 nA (stars: propagating C-fiber AP launched at the electrode). (c) Peak Aβ membrane potential at the stimulated node.](../results/figures/figS1_full_length.png){width=100%}

![**Fig. S2** Lesion length (a) and Aβ stimulus strength (b) in the production configuration (NavC). No C-fiber action potential occurred.](../results/figures/figS2_lesion_stimulus.png){width=75%}
