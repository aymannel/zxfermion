from __future__ import annotations

import pyzx as zx
from typing import Optional

from zxfermion import config
from zxfermion.types import GateType, LegType, VertexType


class BaseGadget:
    def draw(self, labels=False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(**kwargs)

    def matrix(self, return_latex=False):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).matrix(return_latex)

    def tikz(self, name: str, **kwargs):
        from zxfermion.circuits import GadgetCircuit
        GadgetCircuit([self]).tikz(name=name, **kwargs)


class Gadget(BaseGadget):
    def __init__(self, pauli_string: str, phase: Optional[float] = None, expand_gadget=config.expand_gadgets):
        self.type = GateType.GADGET
        self.phase = phase
        self.legs = {qubit: LegType(pauli) for qubit, pauli in enumerate(pauli_string)}
        self.min_qubit = min([qubit for qubit in self.legs])
        self.max_qubit = max([qubit for qubit in self.legs])
        self.expand_gadget = expand_gadget

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.phase, self.legs) == (other.phase, other.legs)
        else:
            return False


class CX(BaseGadget):
    def __init__(self, control: int, target: int, as_gadget=config.gadgets_only):
        assert control != target
        self.type = GateType.CX
        self.control = control
        self.target = target
        self.min_qubit = min(self.control, self.target)
        self.max_qubit = max(self.control, self.target)
        self.as_gadget = as_gadget

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control, self.target) == (other.control, other.target)
        else:
            return False


class CZ(BaseGadget):
    def __init__(self, control: int, target: int, as_gadget=config.gadgets_only):
        assert control != target
        self.type = GateType.CZ
        self.control = min(control, target)
        self.target = max(control, target)
        self.min_qubit = self.control
        self.max_qubit = self.target
        self.as_gadget = as_gadget

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control, self.target) == (other.control, other.target)
        else:
            return False


class Single(BaseGadget):
    def __init__(self, type: GateType, qubit: Optional[int] = 0, phase: Optional[float] = None, as_gadget=config.gadgets_only):
        self.type = type
        self.phase = phase
        self.qubit = qubit
        self.min_qubit = self.qubit
        self.max_qubit = self.qubit
        self.as_gadget = as_gadget

    def __eq__(self, other):
        if self.type == other.type:
            return (self.qubit, self.phase) == (other.qubit, self.phase)
        else:
            return False


class XPhase(Single):
    def __init__(self, **kwargs):
        super().__init__(type=GateType.X_PHASE, **kwargs)
        self.vertex_type = VertexType.X


class ZPhase(Single):
    def __init__(self, **kwargs):
        super().__init__(type=GateType.Z_PHASE, **kwargs)
        self.vertex_type = VertexType.Z


class H(Single):
    def __init__(self, **kwargs):
        super().__init__(type=GateType.H, **kwargs)
        self.vertex_type = VertexType.H


class X(XPhase):
    def __init__(self, **kwargs):
        super().__init__(phase=1, **kwargs)
        self.type = GateType.X


class Z(ZPhase):
    def __init__(self, **kwargs):
        super().__init__(phase=1, **kwargs)
        self.type = GateType.Z


class XPlus(XPhase):
    def __init__(self, **kwargs):
        super().__init__(phase=1/2, **kwargs)
        self.type = GateType.X_PLUS


class XMinus(XPhase):
    def __init__(self, **kwargs):
        super().__init__(phase=-1/2, **kwargs)
        self.type = GateType.X_MINUS


class ZPlus(ZPhase):
    def __init__(self, **kwargs):
        super().__init__(phase=1/2, **kwargs)
        self.type = GateType.Z_PLUS


class ZMinus(ZPhase):
    def __init__(self, **kwargs):
        super().__init__(phase=-1/2, **kwargs)
        self.type = GateType.Z_MINUS
