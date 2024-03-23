from __future__ import annotations

import pyzx as zx
from typing import Optional
from zxfermion.types import LegType, GateType, VertexType


class Gadget:
    def __init__(self, pauli_str: str, phase: Optional[float] = None):
        self.type = GateType.GADGET
        self.phase = phase
        self.legs = {qubit: LegType(pauli) for qubit, pauli in enumerate(pauli_str)}
        self.min_qubit = min([qubit for qubit in self.legs])
        self.max_qubit = max([qubit for qubit in self.legs])

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.phase, self.legs) == (other.phase, other.legs)
        else:
            return False

    def draw(self, labels = False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(**kwargs)


class CX:
    def __init__(self, control: int, target: int):
        assert control != target
        self.type = GateType.CX
        self.control = control
        self.target = target
        self.min_qubit = min(self.control, self.target)
        self.max_qubit = max(self.control, self.target)

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control, self.target) == (other.control, other.target)
        else:
            return False

    def draw(self, labels = False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(**kwargs)


class CZ:
    def __init__(self, control: int, target: int):
        assert control != target
        self.type = GateType.CZ
        self.control = min(control, target)
        self.target = max(control, target)
        self.min_qubit = self.control
        self.max_qubit = self.target

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control, self.target) == (other.control, other.target)
        else:
            return False

    def draw(self, labels = False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(**kwargs)


class Single:
    def __init__(self, type: GateType, qubit: int, phase: Optional[float] = None):
        self.type = type
        self.phase = phase
        self.qubit = qubit
        self.min_qubit = qubit
        self.max_qubit = qubit

    def __eq__(self, other):
        if self.type == other.type:
            return (self.qubit, self.phase) == (other.qubit, self.phase)
        else:
            return False

    def draw(self, labels = False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(**kwargs)


class XPhase(Single):
    def __init__(self, qubit: int, phase: Optional[float] = None):
        super().__init__(type=GateType.X_PHASE, qubit=qubit, phase=phase)
        self.vertex_type = VertexType.X


class ZPhase(Single):
    def __init__(self, qubit: int, phase: Optional[float] = None):
        super().__init__(type=GateType.Z_PHASE, qubit=qubit, phase=phase)
        self.vertex_type = VertexType.Z


class H(Single):
    def __init__(self, qubit: int):
        super().__init__(type=GateType.H, qubit=qubit)
        self.vertex_type = VertexType.H


class X(XPhase):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, phase=1)
        self.type = GateType.X


class Z(ZPhase):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, phase=1)
        self.type = GateType.Z


class XPlus(XPhase):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, phase=1/2)
        self.type = GateType.X_PLUS


class XMinus(XPhase):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, phase=-1/2)
        self.type = GateType.X_MINUS


class ZPlus(ZPhase):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, phase=1/2)
        self.type = GateType.Z_PLUS


class ZMinus(ZPhase):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, phase=-1/2)
        self.type = GateType.Z_MINUS
