from __future__ import annotations

from typing import Optional
from zxfermion.types import LegType, GateType, GadgetLeg


class Gadget:
    def __init__(self, pauli_str: str, phase: Optional[float] = None):
        self.type = GateType.GADGET
        self.phase = phase
        self.legs = {qubit: GadgetLeg(type=LegType(pauli), qubit=qubit) for qubit, pauli in enumerate(pauli_str)}
        self.min_qubit = min([qubit for qubit in self.legs])
        self.max_qubit = max([qubit for qubit in self.legs])

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.phase, self.legs) == (other.phase, other.legs)
        else:
            return False

    def draw(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).draw(**kwargs)


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

    def draw(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).draw(**kwargs)


class CZ:
    def __init__(self, control: int, target: int):
        assert control != target
        self.type = GateType.CZ
        self.control = control
        self.target = target
        self.min_qubit = min(self.control, self.target)
        self.max_qubit = max(self.control, self.target)

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control, self.target) == (other.control, other.target)
        else:
            return False

    def draw(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).draw(**kwargs)


class X:
    def __init__(self, qubit: int):
        self.type = GateType.X
        self.phase = 1
        self.qubit = qubit
        self.min_qubit = qubit
        self.max_qubit = qubit

    def __eq__(self, other):
        if self.type == other.type:
            return (self.qubit, self.phase) == (other.qubit, self.phase)
        else:
            return False

    def draw(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).draw(**kwargs)


class Z:
    def __init__(self, qubit: int):
        self.type = GateType.Z
        self.phase = 1
        self.qubit = qubit
        self.min_qubit = qubit
        self.max_qubit = qubit

    def __eq__(self, other):
        if self.type == other.type:
            return (self.qubit, self.phase) == (other.qubit, self.phase)
        else:
            return False

    def draw(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).draw(**kwargs)
