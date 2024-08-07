from __future__ import annotations
from enum import Enum


class PauliType(str, Enum):
    I = 'I'
    X = 'X'
    Y = 'Y'
    Z = 'Z'
    X_DAG = 'X_DAG'
    Y_DAG = 'Y_DAG'
    Z_DAG = 'Z_DAG'


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
    X_PLUS = 'X_PLUS'  # > S
    Z_PLUS = 'Z_PLUS'  # > SDag
    X_MINUS = 'X_MINUS'  # > V
    Z_MINUS = 'Z_MINUS'  # > VDag

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
