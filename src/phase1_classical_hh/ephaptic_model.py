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
# Geometry / discretization (Nominal 10 um grid, L = 10 mm)
# ---------------------------------------------------------------
L = 10e-3                 # total length, m (10 mm)
dz = 10e-6                # compartment size, m (10 um)
N = int(round(L / dz))    # number of compartments

d1 = 10e-6                # Abeta fiber diameter, m
d2 = 1.0e-6               # C-fiber diameter, m

internode_spacing = 1e-3  # 1 mm node spacing
node_width = 10e-6        # 10 um node compartment
node_mask = (np.arange(N) * dz) % internode_spacing < 1e-9
node_mask[0] = True

# Physical node of Ranvier dimensions:
l_node = 1.0e-6           # 1.0 um physical node length
f_node = l_node / dz      # 0.10: fraction of nodal compartment occupied by bare active node

# ---------------------------------------------------------------
# Resistivities (Sweeney et al. 1987: rho_i = 54.7 ohm*cm for mammalian myelinated axon)
# ---------------------------------------------------------------
rho_i = 54.7 * ohm_cm_to_ohm_m     # axoplasmic resistivity, ohm*m (Sweeney 1987: 54.7 ohm*cm)
rho_e_bulk = 100.0 * ohm_cm_to_ohm_m  # bulk extracellular resistivity, ohm*m
d1_axon = 0.7 * d1                 # axoplasmic core diameter (g-ratio 0.7: explicit modeling assumption, not Sweeney's 0.6)

def r_e_from_cleft(w_cleft):
    """Longitudinal extracellular resistance per unit length (ohm/m)."""
    r_outer = (d1 + d2) / 2.0 + w_cleft
    A_eff = np.pi * (r_outer**2 - (d1/2.0)**2 - (d2/2.0)**2)
    return rho_e_bulk / A_eff   # ohm/m

# ---------------------------------------------------------------
# Membrane parameters
# ---------------------------------------------------------------
Cm = 1.0 * uF_cm2_to_F_m2   # F/m^2
E_Na = 35.64e-3             # Na+ reversal potential, V (Sweeney et al. 1987: +35.64 mV)
E_K = -77e-3
E_leak_1 = -80.0e-3         # CRRSS leak reversal, V (rounded approximation of Sweeney's -80.01 mV to enforce -80.0 mV rest)
E_leak_2 = -54.4e-3   # standard HH leak reversal (not -70; keeps HH near -65 rest)

# Physical bare nodal membrane: Cm_node = 2.0 uF/cm^2 (retained modeling choice / Chiu-MRG lineage; not Sweeney's 2.5 uF/cm^2)
# Physical nodal conductances: g_Na = 1445 mS/cm^2 (Sweeney 1987), g_leak = 128.0 mS/cm^2 (Sweeney 1987)
# Internodal compact myelin: Cm_internode = 0.005 uF/cm^2, g_leak_internode = 0.006 mS/cm^2 (explicit modeling assumptions)
Cm_node_comp = (2.0 * f_node + 0.005 * (1.0 - f_node)) * uF_cm2_to_F_m2
Cm_internode = 0.005 * uF_cm2_to_F_m2
Cm1_arr = np.where(node_mask, Cm_node_comp, Cm_internode)

g_Na_CRRSS = 1445.0 * f_node * mS_cm2_to_S_m2  # effective nodal Na+ conductance density (physical 1445 scaled by f_node)
g_leak_CRRSS = 128.0 * mS_cm2_to_S_m2         # bare nodal leak conductance (Sweeney 1987)
g_leak_internode = 0.006 * mS_cm2_to_S_m2     # compact myelin leak conductance (explicit modeling assumption)
g_leak_node_comp = g_leak_CRRSS * f_node + g_leak_internode * (1.0 - f_node)
g_leak1_arr = np.where(node_mask, g_leak_node_comp, g_leak_internode)

g_Na_HH = 120.0 * mS_cm2_to_S_m2
g_K_HH = 36.0 * mS_cm2_to_S_m2
g_leak_HH = 0.3 * mS_cm2_to_S_m2

dt = 2.5e-6   # 0.0025 ms in seconds (2.5 us for numerical precision and stability)
phi_CRRSS = 1.0  # Sweeney 1987 mammalian rates are natively formulated at 37 deg C (k=1.0)

# ---------------------------------------------------------------
# CRRSS gating kinetics (Sweeney et al. 1987; Chiu et al. 1979), rates in 1/s
# v in volts (SI) -> Y = vmV + 80.0 is deviation from -80 mV resting potential
# ---------------------------------------------------------------
def crrss_rates(v, phi=phi_CRRSS):
    vmV = v * 1e3
    Y = vmV + 80.0
    alpha_m = (97.0 + 0.363 * Y) / (1.0 + np.exp((31.0 - Y) / 5.3)) * 1e3 * phi
    beta_m = alpha_m / np.exp((Y - 23.8) / 4.17)
    beta_h = 15.6 / (1.0 + np.exp((24.0 - Y) / 10.0)) * 1e3 * phi
    alpha_h = beta_h / np.exp((Y - 5.5) / 5.0)
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


