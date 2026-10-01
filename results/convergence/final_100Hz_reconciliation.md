# Final 100 Hz Pulse-Count and Conduction Velocity Reconciliation

**Date:** September 27, 2026  
**Status:** Verified  

---

## 1. Resolution of the 100 Hz Pulse-Count and Timing Dynamics

### Spatiotemporal Propagation and Window Analysis
- An unmyelinated C-fiber conducts at $\text{CV} \approx 0.41\text{ m/s} = 0.41\text{ mm/ms}$.
- In a full-length cleft ($w_{\text{cleft}} = 20\text{ nm}$ from $z = 0$ to $10\text{ mm}$), stimulation of $25$ Aβ fibers at $z = 0$ ($100\text{ nA}$) produces a strong local extracellular transient that initiates C-fiber activation proximal to the electrode ($z \approx 0\text{ mm}$) on the initial pulse.
- Traveling at $0.41\text{ mm/ms}$, this action potential requires:
  - $\approx 12.9\text{ ms}$ to reach the cable midpoint ($z = 5.0\text{ mm}$)
  - $\approx 20.2\text{ ms}$ to reach the downstream electrode ($z = 8.0\text{ mm}$)
- In short observation windows ($T \le 5.0\text{ ms}$), the traveling wave has not reached the downstream cable ($z \ge 3.0\text{ mm}$), where only the subthreshold $+6.015\text{ mV}$ footprint of the passing fast Aβ spike is recorded.
- In a $100\text{ Hz}$ train (interval $= 10\text{ ms}$), the action potential arrives at the cable midpoint at $t = 12.9\text{ ms}$, which falls within the second interpulse interval ($t \in [10, 20]\text{ ms}$), creating the operational appearance of a Pulse-2 threshold crossing when evaluated in sequential $10\text{ ms}$ bins.
- When coupling is confined to an interior lesion ($z \in [3, 7]\text{ mm}$) with the stimulation electrode grounded ($z \le 2\text{ mm}$), pure ephaptic crosstalk remains subthreshold across all pulses (peak in lesion $-63.67\text{ mV}$ in Phase 1, $-57.41\text{ mV}$ in Phase 2; no action potential propagation).

### Canonical Suite Results ($T = t_{\text{last}} + 30\text{ ms}$)

| Train Pulses | Simulation $T$ | First Propagated Spike Pulse | Midpoint Peak $V_2$ | Downstream $8\text{ mm}$ Peak | Overall Classification | Spiked? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 pulse** | $30.0\text{ ms}$ | Pulse 1 (arrives $12.9\text{ ms}$) | $+24.74\text{ mV}$ | $+24.70\text{ mV}$ | `PROPAGATED_ACTION_POTENTIAL` | **True** |
| **2 pulses** | $40.0\text{ ms}$ | Pulse 2 window (arrives $12.9\text{ ms}$) | $+24.83\text{ mV}$ | $+24.70\text{ mV}$ | `PROPAGATED_ACTION_POTENTIAL` | **True** |
| **3 pulses** | $50.0\text{ ms}$ | Pulse 2 window (arrives $12.9\text{ ms}$) | $+24.83\text{ mV}$ | $+24.70\text{ mV}$ | `PROPAGATED_ACTION_POTENTIAL` | **True** |
| **5 pulses** | $70.0\text{ ms}$ | Pulse 2 window (arrives $12.9\text{ ms}$) | $+24.83\text{ mV}$ | $+24.70\text{ mV}$ | `PROPAGATED_ACTION_POTENTIAL` | **True** |
| **10 pulses** | $120.0\text{ ms}$ | Pulse 2 window (arrives $12.9\text{ ms}$) | $+24.83\text{ mV}$ | $+24.70\text{ mV}$ | `PROPAGATED_ACTION_POTENTIAL` | **True** |

---

## 2. Aβ Conduction Velocity Standards

1. **Isolated Aβ Single Fiber:** Report **$41.03\text{ m/s}$** (measured via max upstroke $dV/dt$ between $4.0$ mm and $8.0$ mm).
2. **Coupled Multi-Fiber Bundle ($n=25$):** Report that collective cleft loading decelerates Aβ propagation to **$32.00\text{ m/s}$**.
3. **Historical $33.33\text{ m/s}$ Value:** Diagnosed as a temporal quantization artifact from evaluating discrete voltage peak $\arg\max(V_1)$ on a $2.5\ \mu\text{s}$ grid ($48$ steps $= 0.1200\text{ ms} \implies 4.0\text{ mm} / 0.12\text{ ms} = 33.33\text{ m/s}$) rather than the continuous upstroke metric.
