"""
Coupled Aβ (myelinated, CRRSS) / C-fiber (unmyelinated, HH) ephaptic model.
Pure NumPy/SciPy implementation (no Brian2 dependency).

Units: SI internally (volts, seconds, meters, amps, farads, siemens),
converted from the biophysical cm/mV/ms convention at input time.
"""

import numpy as np
from scipy.linalg import solve_banded

# ---------------------------------------------------------------
# Physical constants (converted to SI)
# ---------------------------------------------------------------
cm2_to_m2 = 1e-4          # cm^2 -> m^2
uF_cm2_to_F_m2 = 1e-6 / cm2_to_m2   # uF/cm^2 -> F/m^2
mS_cm2_to_S_m2 = 1e-3 / cm2_to_m2   # mS/cm^2 -> S/m^2
ohm_cm_to_ohm_m = 1e-2    # ohm*cm -> ohm*m

# ---------------------------------------------------------------
# Geometry / discretization
# ---------------------------------------------------------------
L = 10e-3                 # total length, m (10 mm)
dz = 10e-6                # compartment size, m (10 um)
N = int(round(L / dz))    # number of compartments

d1 = 10e-6                # Abeta fiber diameter, m
d2 = 1.0e-6               # C-fiber diameter, m

internode_spacing = 1e-3  # 1 mm node spacing
node_mask = (np.arange(N) * dz) % internode_spacing < dz
node_mask[0] = True

# ---------------------------------------------------------------
# Resistivities (corrected: rho_i from Hodgkin & Huxley 1952 table entry)
# ---------------------------------------------------------------
rho_i = 35.4 * ohm_cm_to_ohm_m     # axoplasmic resistivity, ohm*m
rho_e_bulk = 100.0 * ohm_cm_to_ohm_m  # bulk extracellular resistivity, ohm*m

def r_e_from_cleft(w_cleft):
    """Longitudinal extracellular resistance per unit length (ohm/m)."""
    r_outer = (d1 + d2) / 2.0 + w_cleft
    A_eff = np.pi * (r_outer**2 - (d1/2.0)**2 - (d2/2.0)**2)
    return rho_e_bulk / A_eff   # ohm/m

# ---------------------------------------------------------------
# Membrane parameters
# ---------------------------------------------------------------
Cm = 1.0 * uF_cm2_to_F_m2   # F/m^2
E_Na = 50e-3
E_K = -77e-3
E_leak_1 = -70e-3
E_leak_2 = -54.4e-3   # standard HH leak reversal (not -70; keeps HH near -65 rest)

g_Na_CRRSS = 150.0 * mS_cm2_to_S_m2
g_leak_CRRSS = 1.5 * mS_cm2_to_S_m2

# Myelin insulation factor: real myelin (~100-300 wraps) reduces effective
# internodal capacitance and leak conductance by roughly two orders of
# magnitude relative to bare (nodal) membrane. Without this, saltatory
# conduction fails because the internode leaks charge instead of passing it
# passively to the next node (see CRRSS 1979; Halter & Clark 1991).
MYELIN_FACTOR = 250.0
Cm_internode = Cm / MYELIN_FACTOR
g_leak_internode = g_leak_CRRSS / MYELIN_FACTOR

g_Na_HH = 120.0 * mS_cm2_to_S_m2
g_K_HH = 36.0 * mS_cm2_to_S_m2
g_leak_HH = 0.3 * mS_cm2_to_S_m2

dt = 5e-6   # 0.005 ms in seconds

# ---------------------------------------------------------------
# CRRSS gating kinetics (v in volts -> convert to mV for formulas), rates in 1/s
# ---------------------------------------------------------------
def crrss_rates(v):
    vmV = v * 1e3
    denom = (1.0 - np.exp(-(vmV + 49.0) / 5.3))
    denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
    alpha_m = 0.363 * (vmV + 49.0) / denom * 1e3   # /s
    beta_m = alpha_m / np.exp((vmV + 56.2) / 4.17)
    alpha_h = 15.6 / (1.0 + np.exp(-(vmV + 56.0) / 10.0)) * 1e3
    beta_h = alpha_h / np.exp((vmV + 74.5) / 5.0)
    return alpha_m, beta_m, alpha_h, beta_h

# ---------------------------------------------------------------
# HH gating kinetics, rates in 1/s
# ---------------------------------------------------------------
def hh_rates(v):
    vmV = v * 1e3
    def safe_div(num, denom):
        denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
        return num / denom
    alpha_m = safe_div(0.1 * (vmV + 40.0), (1.0 - np.exp(-(vmV + 40.0) / 10.0))) * 1e3
    beta_m = 4.0 * np.exp(-(vmV + 65.0) / 18.0) * 1e3
    alpha_h = 0.07 * np.exp(-(vmV + 65.0) / 20.0) * 1e3
    beta_h = 1.0 / (1.0 + np.exp(-(vmV + 35.0) / 10.0)) * 1e3
    alpha_n = safe_div(0.01 * (vmV + 55.0), (1.0 - np.exp(-(vmV + 55.0) / 10.0))) * 1e3
    beta_n = 0.125 * np.exp(-(vmV + 65.0) / 80.0) * 1e3
    return alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n

# ---------------------------------------------------------------
# Laplacian with sealed-end (Neumann) boundary conditions
# ---------------------------------------------------------------
def laplacian_1d(x, dz):
    d2x = np.zeros_like(x)
    d2x[1:-1] = (x[2:] - 2*x[1:-1] + x[:-2]) / dz**2
    d2x[0] = (x[1] - x[0]) / dz**2 * 2   # reflecting boundary (mirror ghost point)
    d2x[-1] = (x[-2] - x[-1]) / dz**2 * 2
    return d2x

def build_banded_laplacian(N, dz):
    """Tridiagonal Laplacian with Neumann BCs, banded form for solve_banded."""
    A = np.zeros((3, N))
    A[0, 1:] = 1.0          # upper diag
    A[1, :] = -2.0          # main diag
    A[2, :-1] = 1.0         # lower diag
    # Neumann: first and last row use ghost-point reflection => coefficient -2 stays,
    # but the "missing" neighbor is replaced by the mirror, giving effectively
    # row0: -2*u0 + 2*u1 = dz^2 * r_e * I0   (already captured since A[0,1]=1 gives u1 once;
    # need factor 2 on that single neighbor)
    A[0, 1] = 2.0
    A[2, -2] = 2.0
    return A / dz**2

def solve_ue(I_total, r_e, dz, N, A_banded_unit):
    """Solve A u_e = B for extracellular potential given total current density I_total (A/m)."""
    B = r_e * I_total
    u_e = solve_banded((1, 1), A_banded_unit, B)
    return u_e

if __name__ == "__main__":
    print(f"N compartments: {N}")
    print(f"Number of nodes of Ranvier: {node_mask.sum()}")
    print(f"rho_i = {rho_i} ohm*m, rho_e_bulk = {rho_e_bulk} ohm*m")
    for w in [5e-6, 100e-9, 20e-9]:
        print(f"w_cleft={w*1e9:.0f} nm -> r_e = {r_e_from_cleft(w):.3e} ohm/m")
