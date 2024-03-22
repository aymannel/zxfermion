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
    CX = 'CX'
    CZ = 'CZ'
    X = 'Y'
    Z = 'Z'


class GadgetLeg(BaseModel):
    type: LegType
    qubit: int
