from __future__ import annotations
from enum import Enum


class LegType(str, Enum):
    I = 'I'
    X = 'X'
    Y = 'Y'
    Z = 'Z'


class GateType(str, Enum):
    IDENTITY = 'IDENTITY'
    SINGLE_QUBIT_GATE = 'SINGLE_QUBIT_GATE'
    CONTROLLED_GATE = 'CONTROLLED_GATE'
    GADGET_CIRCUIT = 'GADGET_CIRCUIT'
    GADGET = 'GADGET'
    PHASE_GATE = 'PHASE_GATE'
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

    NAMES = [
        'Gadget',
        'XPhase',
        'ZPhase',
        'X',
        'Z',
        'XPlus',
        'ZPlus',
        'XMinus',
        'ZMinus',
        'CX',
        'CZ',
        'H'
    ]
