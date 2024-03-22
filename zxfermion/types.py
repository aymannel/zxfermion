from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class EdgeType:
    S: int = 1
    H: int = 2


class VertexType:
    Z: int = 1
    X: int = 2
    H: int = 3


class LegType(str, Enum):
    I = 'I'
    X = 'X'
    Y = 'Y'
    Z = 'Z'


class GateType(str, Enum):
    GADGET_CIRCUIT = 'GADGET_CIRCUIT'
    GADGET = 'GADGET'
    X_PHASE = 'X_PHASE'
    Z_PHASE = 'Z_PHASE'
    X = 'X'
    Z = 'Z'
    CX = 'CX'
    CZ = 'CZ'
    X_PLUS = 'X_PLUS'
    Z_PLUS = 'Z_PLUS'
    X_MINUS = 'X_MINUS'
    Z_MINUS = 'Z_MINUS'


class GadgetLeg(BaseModel):
    type: LegType
    qubit: int
