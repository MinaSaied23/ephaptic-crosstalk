"""
Build Phase 2 Nav1.8/1.9 Multi-Fiber Sweep CSV.
Runs coupled simulation across fiber counts n in [1, 50] with synchronous (0.0 ms) and jittered (1.5 ms) activation.
"""

import os
import sys
import numpy as np
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.abspath(__file__))
phase2_dir = os.path.join(base_dir, "phase2_nav18_nav19")
if phase2_dir not in sys.path:
    sys.path.insert(0, phase2_dir)

from coupled_navc_model import run_coupled_navc

KAPPA = 1.0e9  # m^-2
ns = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50]
jitter_vals = [0.0, 1.5]

records = []
for j in jitter_vals:
    for n in ns:
        res = run_coupled_navc(
            w_cleft=20e-9,
            n_abeta=n,
            jitter_ms=j,
            kappa=KAPPA,
            T=3e-3
        )
        v2_mid = res['v2_mid'] * 1e3  # mV
        v_rest = v2_mid[0]
        v_pk = v2_mid.max()
        dv = v_pk - v_rest
        records.append({
            'n_abeta': n,
            'jitter_ms': j,
            'v_rest_mV': v_rest,
            'v_mid_peak_mV': v_pk,
            'delta_v_mid_mV': dv,
            'spiked': res['spiked'],
            'threshold_crossed': bool(v_pk >= -35.0)
        })
        print(f"n={n:2d} | j={j:3.1f}ms | rest={v_rest:6.2f} mV | peak={v_pk:6.2f} mV | dV={dv:5.2f} mV | spiked={res['spiked']}")

df = pd.DataFrame(records)
out_csv = os.path.join(base_dir, "..", "results", "convergence", "phase2_navc_multifiber.csv")
df.to_csv(out_csv, index=False)
print(f"\nSaved authoritative Phase 2 Nav1.8/1.9 multi-fiber sweep to {out_csv}")
