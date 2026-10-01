# State-Reset Mechanism Control (100 Hz train, n = 25, w_cleft = 20 nm)

**Setup:** Phase 1 classical-HH C-fiber, 10 Abeta pulses at 100 Hz. CONTROL A is the normal closed-loop run. In CONTROL B the C-fiber membrane potential and gating variables are reset to rest immediately before each pulse; the Abeta source train is unchanged.

| Metric | CONTROL A (normal) | CONTROL B (C-fiber state reset) |
| :--- | :--- | :--- |
| Pulse 1 peak midpoint V2 | -59.96 mV (dV = 5.04 mV; spike detected in window) | -59.96 mV (dV = 5.04 mV; no spike in window) |
| Pulse 2 peak midpoint V2 | +24.83 mV (dV = 89.93 mV; spike detected in window) | -59.97 mV (dV = 5.04 mV; no spike in window) |
| Pulse 10 peak midpoint V2 | -69.93 mV (dV = 5.56 mV; spike detected in window) | -59.97 mV (dV = 5.04 mV; no spike in window) |
| Peak extracellular u_e, range over pulses (mV) | 14.32 to 14.34 | 14.33 to 14.33 |

**Interpretation (consistent with Sec. 3.9.3 of the manuscript):** the extracellular peak is the same on every pulse, so there is no pulse-to-pulse accumulation of u_e in the cleft. Resetting the C-fiber before a pulse removes a wave that is already propagating, by construction, so this control alone does not separate membrane-state accumulation from conduction delay. The single-pulse run observed for T >= 30 ms (Table 1) reproduces the same downstream spike and shows that it is initiated by Pulse 1 at the sealed boundary; the 100 Hz result is therefore not evidence of temporal summation.
