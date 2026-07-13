import numpy as np
from coupled_model import run_coupled

def check_spike(res, lo=200, hi=800):
    """True if any C-fiber compartment away from injection/boundary crosses 0 mV."""
    return bool((res['v2'][:, lo:hi] > 0).any())

def run_summation_experiment():
    sens_bias = 0.5   # mild, physiologically plausible sensitization (~-60 mV resting)
    cleft_widths = [1e-6, 200e-9, 50e-9]
    freqs = [50, 100, 200, 400]
    pulse_counts = [5, 10, 20]

    results = []
    print(f"{'w_cleft(nm)':>12} {'freq(Hz)':>9} {'n_pulses':>9} {'train_dur(ms)':>14} {'spiked':>8}")
    for w in cleft_widths:
        for f in freqs:
            for npulses in pulse_counts:
                train_dur = npulses / f
                T = train_dur + 3e-3
                res = run_coupled(w_cleft=w, T=T, stim_amp=100e-9, stim_dur=0.2e-3,
                                   sens_bias=sens_bias, stim_freq=f, n_pulses=npulses,
                                   record_full=True)
                spiked = check_spike(res)
                results.append((w, f, npulses, train_dur, spiked))
                print(f"{w*1e9:12.1f} {f:9d} {npulses:9d} {train_dur*1e3:14.2f} {str(spiked):>8}")
    return results

if __name__ == "__main__":
    results = run_summation_experiment()
    spiking = [r for r in results if r[4]]
    print(f"\n{len(spiking)} / {len(results)} conditions produced summation-triggered ectopic spikes.")
    if spiking:
        print("Spiking conditions:")
        for w, f, n, td, sp in spiking:
            print(f"  w_cleft={w*1e9:.0f} nm, freq={f} Hz, n_pulses={n} (train={td*1e3:.1f} ms)")
