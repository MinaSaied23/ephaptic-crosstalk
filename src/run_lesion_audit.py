"""
Script to execute the complete Interior Lesion Test Audit (Task 2.1)
"""
import sys
import os
import numpy as np

base_dir = os.path.dirname(__file__)
sys.path.insert(0, base_dir)
from interior_lesion_test import run_interior_lesion_phase1, run_interior_lesion_phase2

def run_audit():
    print("=" * 80)
    print("TASK 2.1: INTERIOR LESION TEST AUDIT")
    print("Stimulation site z in [0, 2] mm is GROUNDED (r_e = 0, u_e = 0).")
    print("Restricted pathological cleft exists ONLY in lesion zone z in [3, 7] mm.")
    print("=" * 80)

    # -------------------------------------------------------------
    # Test 1: Temporal Summation at 800 Hz (Phase 1 Classical HH)
    # -------------------------------------------------------------
    print("\n--- TEST 1: TEMPORAL SUMMATION (800 Hz) - Phase 1 (Classical HH) ---")
    for w in [20e-9, 50e-9]:
        for n_pulses in [5, 10, 20]:
            train_dur = n_pulses / 800.0
            T = train_dur + 3e-3
            res = run_interior_lesion_phase1(w_cleft=w, T=T, stim_freq=800.0, n_pulses=n_pulses,
                                            lesion_z_start=3e-3, lesion_z_end=7e-3, ground_z=2e-3)
            v2 = res['v2'] * 1e3
            peak_stim = v2[:, :200].max()
            peak_lesion = v2[:, 300:700].max()
            peak_distal = v2[:, 700:].max()
            spiked_lesion = (v2[:, 300:700] > 0.0).any()
            print(f"w_cleft={w*1e9:.0f}nm, pulses={n_pulses:2d} | Peak stim(0-2mm): {peak_stim:6.2f} mV | Peak lesion(3-7mm): {peak_lesion:6.2f} mV | Spiked in lesion? {spiked_lesion}")

    # -------------------------------------------------------------
    # Test 2: Multi-fiber (n = 25) - Phase 2 (Nav1.8/Nav1.9 Nociceptor)
    # -------------------------------------------------------------
    print("\n--- TEST 2: MULTI-FIBER BUNDLE (n = 25) - Phase 2 (Nav1.8/Nav1.9) ---")
    for w in [20e-9, 50e-9]:
        res = run_interior_lesion_phase2(w_cleft=w, T=5e-3, n_abeta=25.0, jitter_ms=0.0,
                                         lesion_z_start=3e-3, lesion_z_end=7e-3, ground_z=2e-3, dt=1e-6)
        v2 = res['v2'] * 1e3
        peak_stim = v2[:, :200].max()
        peak_lesion = v2[:, 300:700].max()
        peak_distal = v2[:, 700:].max()
        spiked_lesion = (v2[:, 300:700] > 0.0).any()
        print(f"w_cleft={w*1e9:.0f}nm, n=25 | Peak stim(0-2mm): {peak_stim:6.2f} mV | Peak lesion(3-7mm): {peak_lesion:6.2f} mV | Spiked in lesion? {spiked_lesion}")

    # -------------------------------------------------------------
    # Test 3: Multi-fiber (n = 25) + Temporal Summation (800 Hz, 10 pulses)
    # -------------------------------------------------------------
    print("\n--- TEST 3: MULTI-FIBER (n = 25) COMBINED WITH 800 Hz TRAIN (10 pulses) ---")
    for w in [20e-9, 50e-9]:
        train_dur = 10.0 / 800.0
        T = train_dur + 5e-3
        res = run_interior_lesion_phase2(w_cleft=w, T=T, stim_freq=800.0, n_pulses=10, n_abeta=25.0, jitter_ms=0.0,
                                         lesion_z_start=3e-3, lesion_z_end=7e-3, ground_z=2e-3, dt=1e-6)
        v2 = res['v2'] * 1e3
        peak_stim = v2[:, :200].max()
        peak_lesion = v2[:, 300:700].max()
        spiked_lesion = (v2[:, 300:700] > 0.0).any()
        print(f"w_cleft={w*1e9:.0f}nm, n=25, 800Hz 10-pulse | Peak stim(0-2mm): {peak_stim:6.2f} mV | Peak lesion(3-7mm): {peak_lesion:6.2f} mV | Spiked in lesion? {spiked_lesion}")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_audit()
