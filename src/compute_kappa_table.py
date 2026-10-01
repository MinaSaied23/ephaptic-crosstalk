"""
Compute Kappa Effective Table across cleft widths and fiber counts.
Calculates numerical decay lengths, transverse leakage conductance, and effective coupling parameters.
"""

import os
import sys
import numpy as np
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
phase1_dir = os.path.join(base_dir, "phase1_classical_hh")
if phase1_dir not in sys.path:
    sys.path.insert(0, phase1_dir)

from ephaptic_model import d1, d2, d1_axon, rho_i, rho_e_bulk, r_e_from_cleft

out_dir = os.path.join(base_dir, "..", "results", "convergence")
os.makedirs(out_dir, exist_ok=True)

kappa = 1.0e9 # m^-2
lambda_kappa_um = 1.0 / np.sqrt(kappa) * 1e6 # 31.6228 um

axial1 = d1_axon / (4.0 * rho_i)
axial2 = d2 / (4.0 * rho_i)
inv_r1 = np.pi * d1_axon * axial1
inv_r2 = np.pi * d2 * axial2

n_list = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50]
cleft_list = [20e-9, 50e-9, 100e-9, 200e-9]

rows = []
for w in cleft_list:
    r_e = r_e_from_cleft(w)
    inv_re = 1.0 / r_e
    for n in n_list:
        sigma = inv_re + n * inv_r1 + inv_r2
        kappa_eff = (kappa / r_e) / sigma
        lambda_eff_um = 1.0 / np.sqrt(kappa_eff) * 1e6
        
        # Physical transverse cleft leakage conductance per unit length
        # kappa = r_e * g_e => g_e = kappa / r_e  (S/m)
        g_e_S_per_m = kappa / r_e
        
        rows.append({
            "w_cleft_nm": w * 1e9,
            "n_abeta": n,
            "kappa_m2": kappa,
            "lambda_kappa_um": lambda_kappa_um,
            "r_e_Mohm_per_m": r_e / 1e6,
            "g_e_mS_per_m": g_e_S_per_m * 1e3,
            "inv_re_m_per_ohm": inv_re,
            "inv_r1_m_per_ohm": inv_r1,
            "inv_r2_m_per_ohm": inv_r2,
            "sum_inv_r_m_per_ohm": sigma,
            "ratio_inv_re_to_sigma": inv_re / sigma,
            "kappa_eff_m2": kappa_eff,
            "lambda_eff_um": lambda_eff_um,
            "notes": "lambda_eff is the numerical decay scale of the reduced 1D operator, not the physical cleft decay length"
        })

df_kappa = pd.DataFrame(rows)
out_csv = os.path.join(out_dir, "kappa_effective_table.csv")
df_kappa.to_csv(out_csv, index=False)
print(f"Saved {out_csv}")

if __name__ == "__main__":
    for w_val in [20.0, 50.0]:
        print(f"\n--- KAPPA & EFFECTIVE DECAY LENGTH TABLE (w_cleft = {w_val:.0f} nm) ---")
        sub = df_kappa[df_kappa["w_cleft_nm"] == w_val]
        print(f"{'n':>4} | {'kappa(m^-2)':>12} | {'lambda_kappa(um)':>17} | {'kappa_eff(m^-2)':>16} | {'lambda_eff(um)':>15} | {'inv_re/sigma':>13}")
        print("-" * 88)
        for _, r in sub.iterrows():
            print(f"{int(r['n_abeta']):4d} | {r['kappa_m2']:12.2e} | {r['lambda_kappa_um']:17.2f} | {r['kappa_eff_m2']:16.4e} | {r['lambda_eff_um']:15.2f} | {r['ratio_inv_re_to_sigma']:13.4f}")
