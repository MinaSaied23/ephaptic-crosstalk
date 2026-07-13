"""
Experiment 1 (Phase 1, Section III-B of the paper): single-pulse Abeta-to-C
ephaptic crosstalk sweep over extracellular cleft width, using the classical
Hodgkin-Huxley C-fiber model (coupled_model.py).

A single supra-threshold current pulse is injected at the first Abeta node
of Ranvier (z=0); the C-fiber is monitored for any ectopic threshold
crossing at locations away from the stimulation site.

Usage: python3 experiment1_single_pulse.py
"""
import numpy as np
from coupled_model import run_coupled

def run_experiment1():
    cleft_widths = np.geomspace(20e-9, 5e-6, 18)  # 20 nm to 5 um
    results = []
    for w in cleft_widths:
        res = run_coupled(w_cleft=w, T=3e-3, stim_amp=100e-9, stim_dur=0.2e-3)
        peak_mV = res['v2_mid'].max() * 1e3
        results.append((w, peak_mV, res['spiked']))
        print(f"w_cleft = {w*1e9:8.1f} nm  ->  C-fiber midpoint peak = {peak_mV:7.2f} mV   spiked={res['spiked']}")
    return results

if __name__ == "__main__":
    results = run_experiment1()

    spiking = [r for r in results if r[2]]
    if spiking:
        w_threshold = max(r[0] for r in spiking)
        print(f"\nEstimated w_allodynia (largest cleft width producing ectopic spike): {w_threshold*1e9:.1f} nm")
    else:
        print("\nNo ectopic spikes observed across the tested cleft-width range with this stimulus.")
