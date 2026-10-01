"""
Build Phase 2 Headline Results Summary CSV.
Compiles the authoritative simulation findings across single-pulse, multi-fiber,
train frequencies (100 Hz, 200 Hz, 400 Hz), and temporal jitter.
"""

import os
import sys
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(base_dir, "..", "results", "convergence")
os.makedirs(out_dir, exist_ok=True)

headline_rows = [
    {
        "row_id": 1,
        "n_abeta": 1,
        "pulse_frequency": "Single pulse",
        "pulse_count": 1,
        "delta_v_peak_mV": 1.325,
        "c_fiber_peak_V_mV": -63.675,
        "c_fiber_classification": "LOCAL_STIMULUS_TRANSIENT",
        "propagated_c_fiber_ap": False,
        "abeta_source_integrity": "Verified (single AP, CV=41.0 m/s, amp=80.4 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Subthreshold single-pair perturbation; decays passively."
    },
    {
        "row_id": 2,
        "n_abeta": 25,
        "pulse_frequency": "Single pulse",
        "pulse_count": 1,
        "delta_v_peak_mV": 6.015,
        "c_fiber_peak_V_mV": -58.986,
        "c_fiber_classification": "LOCAL_STIMULUS_TRANSIENT",
        "propagated_c_fiber_ap": False,
        "abeta_source_integrity": "Verified (single AP, CV=41.0 m/s, amp=80.4 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Magnitude sensitive to dt (extrapolates to ~15.9 mV at dt->0); classification strictly stable (no spike)."
    },
    {
        "row_id": 3,
        "n_abeta": 50,
        "pulse_frequency": "Single pulse",
        "pulse_count": 1,
        "delta_v_peak_mV": 6.184,
        "c_fiber_peak_V_mV": -58.816,
        "c_fiber_classification": "LOCAL_STIMULUS_TRANSIENT",
        "propagated_c_fiber_ap": False,
        "abeta_source_integrity": "Verified (single AP, CV=41.0 m/s, amp=80.4 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Asymptotic saturation: parallel axoplasmic conductance shunts cleft potential as n->infinity."
    },
    {
        "row_id": 4,
        "n_abeta": 25,
        "pulse_frequency": "100 Hz",
        "pulse_count": 2,
        "delta_v_peak_mV": 89.832,
        "c_fiber_peak_V_mV": 24.832,
        "c_fiber_classification": "PROPAGATED_ACTION_POTENTIAL",
        "propagated_c_fiber_ap": True,
        "abeta_source_integrity": "Verified (2/2 APs stable, CV=32.0 m/s, amp=88.6 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Fully propagated C-fiber AP recorded in the Pulse 2 window; initiated by Pulse 1 at the sealed boundary (a single pulse yields the same spike); requires adequate observation time (T >= 35 ms)."
    },
    {
        "row_id": 5,
        "n_abeta": 25,
        "pulse_frequency": "100 Hz",
        "pulse_count": 5,
        "delta_v_peak_mV": 89.832,
        "c_fiber_peak_V_mV": 24.832,
        "c_fiber_classification": "PROPAGATED_ACTION_POTENTIAL",
        "propagated_c_fiber_ap": True,
        "abeta_source_integrity": "Verified (5/5 APs stable, CV=32.0 m/s, amp=88.6 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Propagated C-fiber AP recorded; consistent with boundary initiation plus conduction delay; pulse-to-pulse mechanism not isolated. Requires tight bundle synchrony."
    },
    {
        "row_id": 6,
        "n_abeta": 25,
        "pulse_frequency": "100 Hz",
        "pulse_count": 10,
        "delta_v_peak_mV": 89.832,
        "c_fiber_peak_V_mV": 24.832,
        "c_fiber_classification": "PROPAGATED_ACTION_POTENTIAL",
        "propagated_c_fiber_ap": True,
        "abeta_source_integrity": "Verified (10/10 APs stable, CV=32.0 m/s, amp=88.6 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Repetitive C-fiber firing; pulse 10 encounters refractory afterhyperpolarization."
    },
    {
        "row_id": 7,
        "n_abeta": 25,
        "pulse_frequency": "200 Hz",
        "pulse_count": 5,
        "delta_v_peak_mV": 89.869,
        "c_fiber_peak_V_mV": 24.869,
        "c_fiber_classification": "PROPAGATED_ACTION_POTENTIAL",
        "propagated_c_fiber_ap": True,
        "abeta_source_integrity": "Verified (5/5 APs stable, CV=32.0 m/s, amp=88.6 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Propagated AP evoked; higher frequency induces 2:1 refractory conduction pattern."
    },
    {
        "row_id": 8,
        "n_abeta": 25,
        "pulse_frequency": "400 Hz",
        "pulse_count": 5,
        "delta_v_peak_mV": 89.955,
        "c_fiber_peak_V_mV": 24.955,
        "c_fiber_classification": "LOCAL_ABORTED_SPIKE",
        "propagated_c_fiber_ap": False,
        "abeta_source_integrity": "Verified (5/5 APs stable, CV=32.0 m/s, amp=88.6 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "5 pulses at 400 Hz (10 ms total) initiates local threshold crossing but aborts before full downstream propagation."
    },
    {
        "row_id": 9,
        "n_abeta": 25,
        "pulse_frequency": "400 Hz",
        "pulse_count": 10,
        "delta_v_peak_mV": 89.601,
        "c_fiber_peak_V_mV": 24.601,
        "c_fiber_classification": "PROPAGATED_ACTION_POTENTIAL",
        "propagated_c_fiber_ap": True,
        "abeta_source_integrity": "Verified (10/10 APs stable, CV=32.0 m/s, amp=88.6 mV)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Propagated spike recorded; contribution of cumulative integration versus boundary initiation not isolated; subsequent pulses arrive during refractory state."
    },
    {
        "row_id": 10,
        "n_abeta": 25,
        "pulse_frequency": "Single volley (jittered)",
        "pulse_count": 1,
        "delta_v_peak_mV": 0.426,
        "c_fiber_peak_V_mV": -64.574,
        "c_fiber_classification": "NO_RESPONSE",
        "propagated_c_fiber_ap": False,
        "abeta_source_integrity": "Verified (21/21 independent APs propagated, CV=41.0 m/s)",
        "dt_us": 2.5,
        "dz_um": 10.0,
        "kappa_m2": "1.0e9",
        "relevant_limitation": "Temporal jitter window of 1.5 ms causes destructive phase cancellation, reducing ephaptic drive by 92.9%."
    }
]

df_headline = pd.DataFrame(headline_rows)

# Save to Code_Data/results/convergence
csv_headline = os.path.join(out_dir, "phase2_headline_results.csv")
df_headline.to_csv(csv_headline, index=False)
print(f"Saved {csv_headline}")

# Save to Supplementary
supp_dir = os.path.join(base_dir, "..", "..", "Supplementary")
if os.path.exists(supp_dir):
    csv_supp = os.path.join(supp_dir, "phase2_headline_results.csv")
    df_headline.to_csv(csv_supp, index=False)
    print(f"Saved {csv_supp}")

# Save to github mirror
github_dir = os.path.join(base_dir, "..", "..", "..", "github", "results", "convergence")
if os.path.exists(github_dir):
    csv_github = os.path.join(github_dir, "phase2_headline_results.csv")
    df_headline.to_csv(csv_github, index=False)
    print(f"Saved {csv_github}")
