"""
Membrane kinetics.  All functions take membrane potential in volts and return
rates in 1/s (or steady states and time constants in s).
"""
from __future__ import annotations

import numpy as np


def _vtrap(x, y):
    """x / (1 - exp(-x/y)), continuous at x = 0."""
    x = np.asarray(x, dtype=float)
    small = np.abs(x / y) < 1e-6
    out = np.empty_like(x)
    xs = x[~small]
    out[~small] = xs / (1.0 - np.exp(-xs / y))
    out[small] = y * (1.0 + x[small] / (2.0 * y))
    return out


# ----------------------------------------------------------------------------
# CRRSS (Chiu et al. 1979; Sweeney et al. 1987), rates at 37 degC
# ----------------------------------------------------------------------------
def crrss_rates(v, phi=1.0):
    vmV = np.asarray(v) * 1e3
    Y = vmV + 80.0
    alpha_m = (97.0 + 0.363 * Y) / (1.0 + np.exp((31.0 - Y) / 5.3)) * 1e3 * phi
    beta_m = alpha_m / np.exp((Y - 23.8) / 4.17)
    beta_h = 15.6 / (1.0 + np.exp((24.0 - Y) / 10.0)) * 1e3 * phi
    alpha_h = beta_h / np.exp((Y - 5.5) / 5.0)
    return alpha_m, beta_m, alpha_h, beta_h


def crrss_inf_tau(v, phi=1.0):
    am, bm, ah, bh = crrss_rates(v, phi)
    tm = 1.0 / (am + bm)
    th = 1.0 / (ah + bh)
    return am * tm, tm, ah * th, th


# ----------------------------------------------------------------------------
# Hodgkin-Huxley (1952), 6.3 degC rates multiplied by phi
# ----------------------------------------------------------------------------
def hh_rates(v, phi=1.0, shift=0.0):
    vmV = (np.asarray(v, dtype=float) + shift) * 1e3
    alpha_m = 0.1 * _vtrap(vmV + 40.0, 10.0)
    beta_m = 4.0 * np.exp(-(vmV + 65.0) / 18.0)
    alpha_h = 0.07 * np.exp(-(vmV + 65.0) / 20.0)
    beta_h = 1.0 / (1.0 + np.exp(-(vmV + 35.0) / 10.0))
    alpha_n = 0.01 * _vtrap(vmV + 55.0, 10.0)
    beta_n = 0.125 * np.exp(-(vmV + 65.0) / 80.0)
    k = 1e3 * phi
    return alpha_m * k, beta_m * k, alpha_h * k, beta_h * k, alpha_n * k, beta_n * k


def hh_inf_tau(v, phi=1.0, shift=0.0):
    am, bm, ah, bh, an, bn = hh_rates(v, phi, shift)
    tm, th, tn = 1.0 / (am + bm), 1.0 / (ah + bh), 1.0 / (an + bn)
    return am * tm, tm, ah * th, th, an * tn, tn


# ----------------------------------------------------------------------------
# Phenomenological Nav1.8 / Nav1.9 (voltage-independent time constants)
# ----------------------------------------------------------------------------
def navc_inf(v, p):
    v = np.asarray(v, dtype=float)
    m8 = 1.0 / (1.0 + np.exp(-(v - p.V8m) / p.k8m))
    h8 = 1.0 / (1.0 + np.exp((v - p.V8h) / p.k8h))
    m9 = 1.0 / (1.0 + np.exp(-(v - p.V9m) / p.k9m))
    return m8, h8, m9


def navc_n_inf_tau(v, p):
    _, _, _, _, an, bn = hh_rates(v, p.phi_K)
    tn = 1.0 / (an + bn)
    return an * tn, tn
