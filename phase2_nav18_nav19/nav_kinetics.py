"""
Physiologically-grounded Nav1.8 / Nav1.9 kinetics for the C-fiber nociceptor,
replacing the classical squid-axon HH fast Na+ conductance.

Parameter sourcing (steady-state Boltzmann midpoints/slopes and time constants):
- Nav1.8 (TTX-resistant, slow-inactivating): activation V1/2 ~ -25 mV, inactivation
  V1/2 ~ -30 mV (dominant depolarized component of double-Boltzmann fits reported
  for TTX-R current in small DRG neurons; Rush/Cummins-type recordings), with
  activation/inactivation time constants ~1.5 ms / ~17 ms (consistent with reported
  tau_act ~1.6-1.7 ms and tau_inact ~18-19 ms at -10 mV for native Nav1.8 current).
- Nav1.9 (TTX-resistant, persistent): activation V1/2 ~ -50 mV, i.e. active at
  subthreshold potentials near rest, with negligible inactivation on the timescale
  of a single action potential (Cummins et al. 1999; Baker et al. 2003), modeled
  here as a single non-inactivating gate with tau_act ~10 ms.
Voltage-independent time constants are a deliberate simplification for tractability,
documented as such; K+ (delayed rectifier) and leak conductances are retained from
the classical HH C-fiber model unchanged.
"""

import numpy as np

# Nav1.8 parameters (mV, ms)
V8m_half, k8m, tau_m8 = -25.0, 6.0, 1.5
V8h_half, k8h, tau_h8 = -30.0, 6.0, 17.0

# Nav1.9 parameters (mV, ms) -- persistent, non-inactivating
V9m_half, k9m, tau_m9 = -50.0, 5.0, 10.0

def nav18_steady(vmV):
    m_inf = 1.0 / (1.0 + np.exp(-(vmV - V8m_half) / k8m))
    h_inf = 1.0 / (1.0 + np.exp((vmV - V8h_half) / k8h))
    return m_inf, h_inf

def nav19_steady(vmV):
    m_inf = 1.0 / (1.0 + np.exp(-(vmV - V9m_half) / k9m))
    return m_inf

def nav_c_fiber_rates(v):
    """v in volts (SI). Returns steady-states and time constants (in seconds) for
    Nav1.8 m,h and Nav1.9 m gates, ready for first-order relaxation dX/dt = (X_inf-X)/tau."""
    vmV = v * 1e3
    m8_inf, h8_inf = nav18_steady(vmV)
    m9_inf = nav19_steady(vmV)
    return (m8_inf, tau_m8 * 1e-3, h8_inf, tau_h8 * 1e-3, m9_inf, tau_m9 * 1e-3)
