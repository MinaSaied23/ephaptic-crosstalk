"""
Parameter sets for the coupled Abeta / C-fiber core-conductor model.

Every simulation in the study is configured from the dataclasses in this module.
There is exactly ONE Abeta model, ONE cable/stimulus/time-step convention and two
C-fiber membrane models (classical Hodgkin-Huxley, "HH", and a phenomenological,
calibrated TTX-resistant Nav1.8/Nav1.9 model, "NavC").  The two C-fiber models
share the same cable properties (diameter, axoplasmic resistivity, capacitance),
so Phase 1 vs Phase 2 comparisons differ only in C-fiber membrane kinetics.

Units: SI throughout (V, s, m, A, F, S, Ohm).  Conversion helpers are provided for
values quoted in the conventional cm/mV/ms units.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace, asdict
import math

# ----------------------------------------------------------------------------
# Unit helpers
# ----------------------------------------------------------------------------
uF_cm2 = 1e-2          # 1 uF/cm^2 = 1e-2 F/m^2
mS_cm2 = 10.0          # 1 mS/cm^2 = 10 S/m^2
ohm_cm = 1e-2          # 1 Ohm*cm  = 1e-2 Ohm*m
mV = 1e-3
ms = 1e-3
um = 1e-6
nm = 1e-9
nA = 1e-9


# ----------------------------------------------------------------------------
# Myelinated Abeta fiber (CRRSS nodal kinetics, Sweeney et al. 1987)
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class AbetaParams:
    D_outer: float = 10.0 * um            # outer (myelinated) fiber diameter
    g_ratio: float = 0.7                  # modelling assumption (Sweeney used 0.6)
    rho_i: float = 54.7 * ohm_cm          # axoplasmic resistivity (Sweeney et al. 1987)
    internode: float = 1.0e-3             # node spacing (m)
    l_node: float = 1.0 * um              # physical node length
    Cm_node: float = 2.0 * uF_cm2         # modelling choice (Sweeney used 2.5 uF/cm^2)
    Cm_internode: float = 0.005 * uF_cm2  # compact myelin (modelling assumption)
    gNa: float = 1445.0 * mS_cm2          # Sweeney et al. 1987
    gL_node: float = 128.0 * mS_cm2       # Sweeney et al. 1987
    gL_internode: float = 0.006 * mS_cm2  # compact myelin (modelling assumption)
    ENa: float = 35.64 * mV               # Sweeney et al. 1987 (115 mV above -80 mV rest, rounded as in CRRSS)
    EL: float = -80.0 * mV                # leak reversal (Sweeney: -80.01 mV)
    phi: float = 1.0                      # CRRSS rates used as published for 37 degC; no extra scaling

    @property
    def d_axon(self) -> float:
        return self.g_ratio * self.D_outer


# ----------------------------------------------------------------------------
# Unmyelinated C-fiber: shared cable properties
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class CCable:
    d: float = 1.0 * um                   # C-fiber diameter
    rho_i: float = 54.7 * ohm_cm          # same axoplasm as the Abeta fiber (one value for all fibers)
    Cm: float = 1.0 * uF_cm2


@dataclass(frozen=True)
class HHParams:
    """Classical Hodgkin-Huxley (1952) membrane.  Rates are the 6.3 degC squid rates
    multiplied by phi = q10 ** ((temperature - 6.3) / 10)."""
    kind: str = "HH"
    cable: CCable = field(default_factory=CCable)
    gNa: float = 120.0 * mS_cm2
    gK: float = 36.0 * mS_cm2
    gL: float = 0.3 * mS_cm2
    ENa: float = 50.0 * mV
    EK: float = -77.0 * mV
    EL: float = -54.4 * mV
    temperature: float = 6.3              # degC
    q10: float = 3.0
    gating_shift: float = 0.0             # uniform shift of all rate functions (V); used only in sensitivity tests

    @property
    def phi(self) -> float:
        return self.q10 ** ((self.temperature - 6.3) / 10.0)


@dataclass(frozen=True)
class NavCParams:
    """Phenomenological, calibrated TTX-resistant nociceptor membrane:
    Nav1.8 (m^3 h) + persistent Nav1.9 (m) + HH delayed rectifier (n^4) + leak.
    Time constants of the Na gates are voltage independent (simplification).
    h8 midpoint (-42 mV) and tau_h8 (2 ms) were calibrated (literature-range values
    of about -30 mV / 17 ms gave a non-repolarizing state in this reduced model)."""
    kind: str = "NavC"
    cable: CCable = field(default_factory=CCable)
    g18: float = 2000.0 * mS_cm2
    g19: float = 0.2 * mS_cm2
    gK: float = 60.0 * mS_cm2
    gL: float = 0.3 * mS_cm2
    ENa: float = 50.0 * mV
    EK: float = -77.0 * mV
    EL: float = -55.0 * mV
    V8m: float = -25.0 * mV
    k8m: float = 6.0 * mV
    tau_m8: float = 1.5 * ms
    V8h: float = -42.0 * mV
    k8h: float = 6.0 * mV
    tau_h8: float = 2.0 * ms
    V9m: float = -50.0 * mV
    k9m: float = 5.0 * mV
    tau_m9: float = 10.0 * ms
    phi_K: float = 1.0                    # scaling of the HH n-gate rates


# ----------------------------------------------------------------------------
# Extracellular compartment
# ----------------------------------------------------------------------------
RHO_E = 100.0 * ohm_cm

# Stimulation threshold of the uncoupled Abeta fiber (0.2-ms pulse at node 0, dz = 5 um,
# dt = 1 us), from ephaptic.model.abeta_threshold(); verified by tests/test_model.py.
ABETA_THRESHOLD = 1.511 * nA


def a_eff_pair(w_cleft: float, D1: float = 10.0 * um, d2: float = 1.0 * um) -> float:
    """Cross-section used in the earlier version of the study: a circle circumscribing
    both fibers, enlarged by w_cleft, minus the two fiber cross-sections (m^2)."""
    r_outer = (D1 + d2) / 2.0 + w_cleft
    return math.pi * (r_outer ** 2 - (D1 / 2.0) ** 2 - (d2 / 2.0) ** 2)


def sleeve_area(D: float, w: float) -> float:
    """Area of a uniform periaxonal sleeve of thickness w around a fiber of diameter D."""
    return math.pi * ((D / 2.0 + w) ** 2 - (D / 2.0) ** 2)


def equivalent_gap(area_per_fiber: float, D: float = 10.0 * um) -> float:
    """Thickness of the uniform sleeve around a fiber of diameter D whose area equals area_per_fiber."""
    return math.sqrt((D / 2.0) ** 2 + area_per_fiber / math.pi) - D / 2.0


A_REF = a_eff_pair(20.0 * nm)   # 16.4 um^2: the single-pair compartment of the earlier version


@dataclass(frozen=True)
class CleftParams:
    """Shared extracellular compartment.

    area_model:
      "fixed"      A_e is the total extracellular cross-section shared by all fibers,
                   independent of n (A_e defaults to A_REF = 16.4 um^2).
      "per_fiber"  each Abeta fiber (and the C-fiber) brings its own periaxonal sleeve of
                   thickness w_sleeve, so A_e = n * sleeve(D1) + sleeve(d2) grows with n.
    kappa:   r_e * G_e (m^-2), with G_e the transverse leak conductance per unit length from the
             compartment to grounded bulk tissue; lambda_e = 1/sqrt(kappa) is the passive length
             constant of the extracellular compartment.
    config:
      "lesion"     the shared compartment occupies z in [lesion_start, lesion_end]; elsewhere the
                   fibers lie in grounded bulk fluid (u_e = 0).  Default.
      "full"       the shared compartment spans the whole cable (sealed ends), as in the earlier
                   version of the study; the Abeta stimulation site then lies inside the cleft.
    """
    area_model: str = "fixed"
    A_e: float = A_REF
    w_sleeve: float = 20.0 * nm
    rho_e: float = RHO_E
    kappa: float = 1.0e9
    config: str = "lesion"
    lesion_start: float = 2.5e-3
    lesion_end: float = 7.5e-3
    stim_current_returns_via_cleft: bool = True


# ----------------------------------------------------------------------------
# Protocol / numerics
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Protocol:
    L: float = 10.0e-3
    dz: float = 5.0 * um
    dt: float = 1.0e-6
    T: float = 20.0e-3
    n_abeta: float = 1.0                  # number of synchronously stimulated Abeta fibers
    stim_amp: float = None                # A; None -> stim_factor x ABETA_THRESHOLD
    stim_factor: float = 2.0
    stim_dur: float = 0.2e-3
    pulse_times: tuple = (0.0,)
    jitter: float = 0.0                   # width of the uniform onset-dispersion window (s)
    jitter_phases: int = 21
    c_bias: float = 0.0                   # uniform depolarizing current density on the C-fiber (A/m^2)
    c_stim_amp: float = 0.0               # optional direct C-fiber stimulus (A) at c_stim_z
    c_stim_z: float = 0.0
    c_stim_dur: float = 1.0e-3
    ionic: str = "explicit"               # "explicit" (factorize once), "implicit" (both fibers
                                          # conductance-implicit) or "implicit_c" (C-fiber only)
    stop_on_spike: bool = True
    quiet_after: float = 4.0e-3           # stop early once quiescent after this time
    quiet_tol: float = 0.25 * mV


def as_dict(obj) -> dict:
    return asdict(obj)


__all__ = [
    "AbetaParams", "CCable", "HHParams", "NavCParams", "CleftParams", "Protocol",
    "a_eff_pair", "sleeve_area", "equivalent_gap", "A_REF", "RHO_E", "ABETA_THRESHOLD", "replace",
    "uF_cm2", "mS_cm2", "ohm_cm", "mV", "ms", "um", "nm", "nA",
]
