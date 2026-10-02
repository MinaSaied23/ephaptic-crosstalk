"""Named C-fiber membrane variants used in the sensitivity analysis."""
import math
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ephaptic.params import HHParams, NavCParams


def hh(temperature=6.3, speed=1.0, gscale=1.0, **kw):
    """HH membrane at `temperature` (rates x 3^((T-6.3)/10)).
    speed:  multiplies all rates AND maximal conductances (time-compressed HH: equivalent to
            dividing the membrane capacitance and every time scale by `speed`).
    gscale: multiplies the maximal conductances only (rates unchanged)."""
    p = HHParams(temperature=temperature, **kw)
    f = speed * gscale
    if f != 1.0:
        p = replace(p, gNa=p.gNa * f, gK=p.gK * f, gL=p.gL * f)
    if speed != 1.0:
        p = replace(p, temperature=temperature + 10.0 * math.log(speed, 3.0))
    return p


def navc(tau_m8_ms=1.5, speed=1.0, **kw):
    """NavC membrane; speed divides all gate time constants (and multiplies the HH n-gate
    rates) and multiplies all maximal conductances (time-compressed NavC)."""
    p = NavCParams(tau_m8=tau_m8_ms * 1e-3, **kw)
    if speed != 1.0:
        p = replace(p, tau_m8=p.tau_m8 / speed, tau_h8=p.tau_h8 / speed, tau_m9=p.tau_m9 / speed,
                    phi_K=p.phi_K * speed, g18=p.g18 * speed, g19=p.g19 * speed,
                    gK=p.gK * speed, gL=p.gL * speed)
    return p


def label(p):
    if isinstance(p, HHParams):
        return f"HH_phi{p.phi:.3g}_gNa{p.gNa/10:.0f}"
    return f"NavC_tm8_{p.tau_m8*1e3:.3g}ms_g18_{p.g18/10:.0f}"


def ionic_for(p):
    """Ionic-current treatment for a C-fiber variant.  Variants whose maximal conductances
    exceed the standard values have membrane time constants close to the 1-us step; their
    C-fiber ionic current is treated conductance-implicitly ("implicit_c") while the Abeta
    fiber keeps the validated explicit treatment (checked against dt = 0.25 us in E02b)."""
    if isinstance(p, HHParams):
        return "implicit_c" if p.gNa > HHParams().gNa * 1.0001 else "explicit"
    return "implicit_c" if p.g18 > NavCParams().g18 * 1.0001 else "explicit"
