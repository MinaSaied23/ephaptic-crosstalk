"""Coupled Abeta / C-fiber ephaptic core-conductor model (monolithic implicit solver)."""
from .params import (AbetaParams, CCable, HHParams, NavCParams, CleftParams, Protocol,
                     a_eff_pair, sleeve_area, equivalent_gap, A_REF)
from .model import CoupledModel, abeta_threshold

__all__ = ["AbetaParams", "CCable", "HHParams", "NavCParams", "CleftParams", "Protocol",
           "a_eff_pair", "sleeve_area", "equivalent_gap", "A_REF", "CoupledModel", "abeta_threshold"]
