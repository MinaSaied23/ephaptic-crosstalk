"""Regression and invariant tests for the coupled model.

Run:  python -m pytest -q tests        (about 2-3 minutes)
      python -m pytest -q tests -m "not slow"   (about 30 s)
"""
import csv
import math
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from ephaptic import (AbetaParams, HHParams, NavCParams, CleftParams, Protocol, CoupledModel,  # noqa: E402
                      abeta_threshold, A_REF, equivalent_gap)
from ephaptic.params import ABETA_THRESHOLD, a_eff_pair  # noqa: E402
from ephaptic.model import run_lagged, c_fiber_equilibria  # noqa: E402
from ephaptic.metrics import summarize  # noqa: E402

DATA = os.path.join(ROOT, "results", "data")


def rows(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------------------
# Parameter sets: one Abeta model, one cable convention, two C-fiber membranes
# ----------------------------------------------------------------------------
def test_parameter_sets_are_the_documented_ones():
    ab, hh, nc = AbetaParams(), HHParams(), NavCParams()
    assert ab.ENa == pytest.approx(35.64e-3) and ab.EL == pytest.approx(-80e-3)
    assert ab.rho_i == pytest.approx(0.547) and ab.phi == 1.0
    assert ab.d_axon == pytest.approx(7e-6)
    assert hh.ENa == pytest.approx(50e-3) and hh.EK == pytest.approx(-77e-3) and hh.EL == pytest.approx(-54.4e-3)
    assert hh.temperature == 6.3 and hh.phi == pytest.approx(1.0)
    assert nc.ENa == pytest.approx(50e-3) and nc.tau_m8 == pytest.approx(1.5e-3)
    # the two C-fiber models share the same cable, and its axoplasm equals the Abeta axoplasm
    assert hh.cable == nc.cable
    assert hh.cable.rho_i == ab.rho_i
    assert Protocol().dt == pytest.approx(1e-6) and Protocol().dz == pytest.approx(5e-6)
    assert CleftParams().kappa == 1e9 and CleftParams().A_e == pytest.approx(a_eff_pair(20e-9))
    assert A_REF * 1e12 == pytest.approx(16.40, abs=0.01)


def test_hh_temperature_scaling():
    assert HHParams(temperature=16.3).phi == pytest.approx(3.0)


def test_resting_potentials():
    assert c_fiber_equilibria(HHParams())[0]["v"] * 1e3 == pytest.approx(-65.0, abs=0.01)
    assert c_fiber_equilibria(NavCParams())[0]["v"] * 1e3 == pytest.approx(-66.82, abs=0.01)
    # The coupled steady state is not exactly uniform: resting Na+ conductance holds the
    # Abeta nodes a fraction of a microvolt above the internodes, which drives a tiny
    # standing extracellular potential.  Both are far below any reported quantity.
    m = CoupledModel(NavCParams(), Protocol(dz=10e-6))
    v1, v2, ue = m.resting_state()
    assert np.ptp(v2) < 1e-6 and np.abs(ue).max() < 1e-6


def test_equivalent_gap_roundtrip():
    from ephaptic.params import sleeve_area
    for w in (5e-9, 20e-9, 500e-9):
        assert equivalent_gap(sleeve_area(10e-6, w)) == pytest.approx(w, rel=1e-9)
    assert equivalent_gap(A_REF / 25) * 1e9 == pytest.approx(20.8, abs=0.1)


# ----------------------------------------------------------------------------
# Numerics
# ----------------------------------------------------------------------------
def test_monolithic_scheme_conserves_current():
    r = rows("e02_kcl.csv")
    assert max(float(x["relative"]) for x in r) < 1e-9


def test_lagged_scheme_error_is_reproduced_and_monolithic_is_dt_robust():
    """The earlier lagged scheme underestimates the n = 25 response ~2.5x at dt = 2.5 us;
    the monolithic scheme is within 1 % of its fine-dt value already at 2.5 us."""
    hh = HHParams(ENa=35.64e-3)
    cl = CleftParams(config="full", stim_current_returns_via_cleft=False)

    def dv(scheme, dt):
        m = CoupledModel(hh, Protocol(n_abeta=25, dt=dt, dz=10e-6, T=1.5e-3, stim_amp=100e-9,
                                      stop_on_spike=False, quiet_after=1.0), cl)
        r = run_lagged(m) if scheme == "lagged" else m.run()
        w = (r["z"] >= 3e-3 - 1e-9) & (r["z"] <= 8e-3 + 1e-9)
        return ((r["v2_max"] - r["v2_rest"])[w]).max() * 1e3
    lag, mono, mono_fine = dv("lagged", 2.5e-6), dv("mono", 2.5e-6), dv("mono", 0.5e-6)
    assert 5.5 < lag < 6.5
    assert mono == pytest.approx(mono_fine, rel=0.01)
    assert 15.0 < mono_fine < 16.0


def test_explicit_and_implicit_ionic_variants_agree():
    out = []
    for ionic in ("explicit", "implicit"):
        pr = Protocol(n_abeta=10, dz=10e-6, dt=0.5e-6, T=3e-3, ionic=ionic)
        out.append(summarize(CoupledModel(NavCParams(), pr).run())["dv_lesion_mV"])
    assert out[0] == pytest.approx(out[1], rel=0.01)


def test_cross_section_per_fiber_scaling():
    """Dividing the shared cross-section by n is almost the same as adding n-1 more Abeta
    fibers to it: the extracellular compartment sees both as a smaller area per fiber.
    The mapping is not exact, because the C-fiber's own axial conductance g_2 enters the
    compartment equation unscaled and is therefore over-weighted n-fold in the
    single-fiber version; the deviation grows with n and is bounded here."""
    dev = {}
    for n in (2, 10, 50):
        a = summarize(CoupledModel(NavCParams(), Protocol(n_abeta=n, dz=10e-6, T=6e-3)).run())
        b = summarize(CoupledModel(NavCParams(), Protocol(n_abeta=1, dz=10e-6, T=6e-3),
                                   CleftParams(A_e=A_REF / n)).run())
        dev[n] = abs(a["dv_lesion_mV"] / b["dv_lesion_mV"] - 1)
    assert dev[2] < 0.02
    assert dev[2] < dev[10] < dev[50] < 0.20


# ----------------------------------------------------------------------------
# Regression against the stored results (regenerated quickly)
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("model,n", [("NavC", 1), ("NavC", 10), ("HH", 25)])
def test_n_sweep_regression(model, n):
    C = NavCParams() if model == "NavC" else HHParams()
    s = summarize(CoupledModel(C, Protocol(n_abeta=n, T=25e-3)).run())
    ref = [r for r in rows("e03_n_sweep.csv") if r["model"] == model and int(r["n_abeta"]) == n][0]
    assert s["dv_lesion_mV"] == pytest.approx(float(ref["dv_lesion_mV"]), rel=1e-4)
    assert s["c_spike"] == (ref["c_spike"] == "True")
    assert s["ab_conducts"] == (ref["ab_conducts"] == "True")


@pytest.mark.slow
def test_abeta_threshold_constant():
    assert abeta_threshold(AbetaParams(), Protocol()) == pytest.approx(ABETA_THRESHOLD, rel=2e-3)


# ----------------------------------------------------------------------------
# Scheme variants
# ----------------------------------------------------------------------------
def test_c_only_implicit_variant_matches_explicit():
    """The 'implicit_c' treatment (C-fiber ionic current implicit, Abeta explicit) used for
    the fast kinetic variants agrees with the fully explicit scheme at a finer step."""
    out = {}
    for ionic, dt in (("implicit_c", 1e-6), ("explicit", 0.25e-6)):
        pr = Protocol(n_abeta=25, dz=10e-6, dt=dt, T=3e-3, ionic=ionic)
        out[ionic] = summarize(CoupledModel(NavCParams(), pr).run())["dv_lesion_mV"]
    assert out["implicit_c"] == pytest.approx(out["explicit"], rel=0.01)


def test_resting_state_is_a_fixed_point():
    """Running from the computed steady state without stimulus leaves it unchanged."""
    pr = Protocol(n_abeta=25, dz=20e-6, T=2e-3, stim_amp=0.0, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(NavCParams(), pr)
    r = m.run()
    assert np.abs(r["v2_max"] - r["v2_rest"]).max() < 1e-7
    assert np.abs(r["v1_max"] - r["v1_rest"]).max() < 1e-7


def test_c_fiber_does_not_load_the_compartment():
    """Removing the C-fiber's axial conductance from the compartment changes the drive by
    <1 %, which is why the open-loop safety factor is meaningful."""
    from ephaptic.openloop import run_c_driven
    pr = Protocol(n_abeta=25, dz=10e-6, T=2e-3, stop_on_spike=False, quiet_after=1.0)
    m = CoupledModel(NavCParams(), pr)
    r = m.run(record=["ue"], record_stride=1)
    closed = ((r["v2_max"] - r["v2_rest"]) * 1e3)[m.geo.cleft].max()
    o = run_c_driven(NavCParams(), r["ue"], pr.dt, pr.dz, T=2e-3, stop_on_spike=False)
    opened = ((o["v_max"] - o["v_rest"]) * 1e3)[m.geo.cleft].max()
    assert opened == pytest.approx(closed, rel=0.01)
