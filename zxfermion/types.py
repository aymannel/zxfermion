from __future__ import annotations

from enum import Enum


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
    SINGLE_QUBIT_GATE = 'SINGLE_QUBIT_GATE'
    CONTROLLED_GATE = 'CONTROLLED_GATE'
    GADGET = 'GADGET'
    X_PHASE = 'X_PHASE'
    Z_PHASE = 'Z_PHASE'
    X = 'X'
    Z = 'Z'
    H = 'H'
    CX = 'CX'
    CZ = 'CZ'
    X_PLUS = 'X_PLUS'
    Z_PLUS = 'Z_PLUS'
    X_MINUS = 'X_MINUS'
    Z_MINUS = 'Z_MINUS'
