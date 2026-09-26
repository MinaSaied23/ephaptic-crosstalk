"""
Experiment: Phase 2 Temporal Summation Sweep (Section 3.8 of the paper).

Re-tests high-frequency temporal summation using the Nav1.8/Nav1.9 C-fiber
model (coupled_navc_model.py) at a reduced but representative sweep density
(200-400 Hz, 5-10 pulses, cleft widths 20-200 nm, unsensitized C-fiber).

Usage: python experiment_summation_navc.py
"""
import numpy as np
from coupled_navc_model import run_coupled_navc

def check_spike(res, lo=200, hi=800):
    """True if any C-fiber compartment away from injection/boundary crosses 0 mV."""
    return bool((res['v2'][:, lo:hi] > 0).any())

def run_summation_experiment():
    sens_bias = 0.0   # unsensitized
    cleft_widths = [200e-9, 100e-9, 50e-9, 20e-9]
    freqs = [200, 400]
    pulse_counts = [5, 10]

    results = []
    print(f"{'w_cleft(nm)':>12} {'freq(Hz)':>9} {'n_pulses':>9} {'train_dur(ms)':>14} {'spiked':>8}")
    for w in cleft_widths:
        for f in freqs:
            for npulses in pulse_counts:
                train_dur = npulses / f
                # T must be long enough for late C-fiber spike plus settling time (if any)
                T = train_dur + 10e-3
                # coupled_navc_model uses 1 Aβ fiber by default if n_fibers=1
                res = run_coupled_navc(w_cleft=w, T=T, stim_amp=100e-9, stim_dur=0.2e-3,
                                   sens_bias=sens_bias, stim_freq=f, n_pulses=npulses,
                                   n_abeta=1, record_full=True)
                spiked = check_spike(res)
                results.append((w, f, npulses, train_dur, spiked))
                print(f"{w*1e9:12.1f} {f:9d} {npulses:9d} {train_dur*1e3:14.2f} {str(spiked):>8}", flush=True)
    return results

if __name__ == "__main__":
    results = run_summation_experiment()
    spiking = [r for r in results if r[4]]
    print(f"\n{len(spiking)} / {len(results)} conditions produced summation-triggered ectopic spikes in NavC.")
    if spiking:
        print("Spiking conditions:")
        for w, f, n, td, sp in spiking:
            print(f"  w_cleft={w*1e9:.0f} nm, freq={f} Hz, n_pulses={n} (train={td*1e3:.1f} ms)")
