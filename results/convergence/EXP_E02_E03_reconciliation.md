# Reconciliation of EXP-E02 and EXP-E03 Single-Pulse Measurements

**Date:** September 26, 2026  
**Status:** DISCREPANCY FULLY RESOLVED  
**Issue:** Comparison between reported single-pulse $n=25$ ephaptic $\Delta V$:
- **EXP-E02 (Multi-fiber sweep):** $\Delta V = 6.015\text{ mV}$
- **EXP-E03 (Temporal summation 1-pulse):** $\Delta V = 5.039\text{ mV}$

---

## 1. Executive Finding

The numerical simulations in both experiment scripts use **100% IDENTICAL physical equations, conductances, dimensions, discretization steps, and coupling matrices**. 

The difference between $6.015\text{ mV}$ and $5.039\text{ mV}$ is **strictly a spatial measurement sampling difference**, not a modeling, parameter, or numerical divergence:

1. **EXP-E02 (`run_phase2_multifiber.py`)** evaluated the maximum depolarization across the entire downstream cable window $z \in [3.0, 8.0]\text{ mm}$ to capture the spatial peak wherever it occurred along the cable. In this simulation, the spatial peak occurs at **$z = 7.0\text{ mm}$**, reaching **$V_2 = -58.9856\text{ mV}$ ($\Delta V = 6.0145\text{ mV}$)** at $t = 0.25\text{ ms}$.
2. **EXP-E03 (`run_phase2_temporal_summation.py`)** recorded the membrane potential specifically at the cable midpoint **$z = 5.0\text{ mm}$** (`mid_idx = N // 2 = 500`). At this exact spatial coordinate, the peak reaches **$V_2 = -59.9621\text{ mV}$ ($\Delta V = 5.0379\text{ mV}$)** at $t = 0.19\text{ ms}$.

When both extraction methods are applied to the exact same simulation trajectory, they yield the exact reported values:
- Spatial window $z \in [3, 8]\text{ mm}$ peak: **$6.0144\text{ mV}$** (matches EXP-E02: $6.015\text{ mV}$)
- Midpoint $z = 5.0\text{ mm}$ peak: **$5.0379\text{ mV}$** (matches EXP-E03: $5.039\text{ mV}$)

---

## 2. Spatial Profile of Single-Pulse Depolarization ($n=25$, $w_{\text{cleft}} = 20\text{ nm}$)

| Longitudinal Position ($z$) | Node Index | Peak $V_2$ ($	ext{mV}$) | Ephaptic $\Delta V$ ($	ext{mV}$) | Time of Peak ($	ext{ms}$) | Sampling Context |
| :---: | :---: | :---: | :---: | :---: | :--- |
| $z = 3.0\text{ mm}$ | Node 3 | $-62.914$ | $2.086$ | $0.11$ | Downstream window |
| $z = 4.0\text{ mm}$ | Node 4 | $-61.187$ | $3.813$ | $0.15$ | Downstream window |
| **$z = 5.0\text{ mm}$** | **Node 5** | **$-59.962$** | **$5.038$** | **$0.19$** | **EXP-E03 Midpoint Sampling** |
| $z = 6.0\text{ mm}$ | Node 6 | $-59.163$ | $5.837$ | $0.22$ | Downstream window |
| **$z = 7.0\text{ mm}$** | **Node 7** | **$-58.986$** | **$6.015$** | **$0.25$** | **EXP-E02 Spatial Peak** |
| $z = 8.0\text{ mm}$ | Node 8 | $-60.106$ | $4.894$ | $0.27$ | Downstream window boundary |
