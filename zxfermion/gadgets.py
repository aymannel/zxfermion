from __future__ import annotations

import math
from typing import Optional

import pyzx as zx

from zxfermion import config
from zxfermion.exceptions import IncompatibleGatesException
from zxfermion.types import GateType, LegType, VertexType


class Identity:
    def __init__(self):
        self.type = GateType.IDENTITY

    def __add__(self, other):
        return other

    def __eq__(self, other):
        return True if other.type == GateType.IDENTITY else other.identity if hasattr(other, 'identity') else False


class BaseGadget:
    def matrix(self, return_latex=False):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).matrix(return_latex=return_latex)

    def graph(self, expand_gadget=None, as_gadget=None):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(expand_gadgets=expand_gadget, gadgets_only=as_gadget)

    def tikz(self, name: str, expand_gadget=None, as_gadget=None):
        self.graph(expand_gadget=expand_gadget, as_gadget=as_gadget).tikz(name=name)

    def draw(self, expand_gadget=None, as_gadget=None):
        zx.draw(self.graph(expand_gadget=expand_gadget, as_gadget=as_gadget))


class Gadget(BaseGadget):
    def __init__(self, pauli_string: str, phase: Optional[int | float] = None, expand_gadget=None):
        self.type = GateType.GADGET
        self.phase = 0 if phase is None else round(phase % 2, 15)
        self.legs = {qubit: LegType(pauli) for qubit, pauli in enumerate(pauli_string)}
        self.min_qubit = min([qubit for qubit in self.legs])
        self.max_qubit = max([qubit for qubit in self.legs])
        self.expand_gadget = expand_gadget if expand_gadget is not None else config.expand_gadgets
        self.phase_gadget = all(leg == LegType.Z or leg == LegType.I for leg in self.legs.values())
        self.identity = self.phase_gadget and math.isclose(self.phase, 0)

    def __repr__(self):
        return f'Gadget(pauli_string="{"".join(self.legs.values())}", phase={self.phase})'

    def __eq__(self, other):
        if self.identity and other.type == GateType.IDENTITY:
            return True
        elif other.type == GateType.GADGET:
            return self.legs == other.legs and math.isclose(self.phase, other.phase)
        else:
            raise IncompatibleGatesException(f'Cannot assert equality between f{self.type} and {other.type}.')

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif other.type == GateType.GADGET and self.legs == other.legs:
            pauli_string = ''.join(leg for leg in self.legs.values())
            return Gadget(pauli_string, self.phase + other.phase)
        else:
            raise IncompatibleGatesException


class SingleQubitGate(BaseGadget):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        self.type = GateType.SINGLE_QUBIT_GATE
        self.qubit = 0 if qubit is None else qubit
        self.min_qubit = self.qubit
        self.max_qubit = self.qubit
        self.as_gadget = as_gadget if as_gadget is not None else config.gadgets_only


class PhaseGate(SingleQubitGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, as_gadget=None):
        super().__init__(qubit=qubit, as_gadget=as_gadget)
        self.type = GateType.PHASE_GATE
        self.phase = 0 if phase is None else round(phase % 2, 15)
        self.identity = math.isclose(self.phase, 0)

    def __repr__(self):
        return f'{self.__class__.__name__}(qubit={self.qubit}, phase={self.phase})'


class XPhase(PhaseGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=phase, as_gadget=as_gadget)
        self.type = GateType.X_PHASE
        self.vertex_type = VertexType.X

    def __eq__(self, other):
        if other.type == GateType.IDENTITY:
            return self.phase == 0
        else:
            return (self.qubit, self.phase) == (other.qubit, other.phase) if isinstance(other, XPhase) else False

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif isinstance(other, XPhase) and self.qubit == other.qubit:
            return XPhase(qubit=self.qubit, phase=round(self.phase + other.phase, 15))
        else:
            raise IncompatibleGatesException(f'Cannot add {self.type} and {other.type}')


class ZPhase(PhaseGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=phase, as_gadget=as_gadget)
        self.type = GateType.Z_PHASE
        self.vertex_type = VertexType.Z

    def __eq__(self, other):
        if other.type == GateType.IDENTITY:
            return self.phase == 0
        else:
            return (self.qubit, self.phase) == (other.qubit, other.phase) if isinstance(other, ZPhase) else False

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif isinstance(other, ZPhase) and self.qubit == other.qubit:
            return ZPhase(qubit=self.qubit, phase=round(self.phase + other.phase, 15))
        else:
            raise IncompatibleGatesException(f'Cannot add {self.type} and {other.type}')


class X(XPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1, as_gadget=as_gadget)
        self.type = GateType.X

    def __add__(self, other):
        return Identity() if other.type == GateType.X and self.qubit == other.qubit else super().__add__(other)


class Z(ZPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1, as_gadget=as_gadget)
        self.type = GateType.Z

    def __add__(self, other):
        return Identity() if other.type == GateType.Z and self.qubit == other.qubit else super().__add__(other)


class XPlus(XPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1/2, as_gadget=as_gadget)
        self.type = GateType.X_PLUS


class XMinus(XPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=3/2, as_gadget=as_gadget)
        self.type = GateType.X_MINUS


class ZPlus(ZPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1/2, as_gadget=as_gadget)
        self.type = GateType.Z_PLUS


class ZMinus(ZPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=3/2, as_gadget=as_gadget)
        self.type = GateType.Z_MINUS


class H(SingleQubitGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, as_gadget=as_gadget)
        self.type = GateType.H
        self.vertex_type = VertexType.H
        self.phase = None

    def __repr__(self):
        return f'H(qubit={self.qubit})'

    def __eq__(self, other):
        return self.qubit == other.qubit if other.type == GateType.H else False

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif other.type == GateType.H:
            return Identity()
        else:
            raise IncompatibleGatesException


class ControlledGate(BaseGadget):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None):
        control = 0 if control is None else control
        target = 1 if target is None else target
        assert control != target
        self.type = GateType.CONTROLLED_GATE
        self.control = control
        self.target = target
        self.min_qubit = min(self.control, self.target)
        self.max_qubit = max(self.control, self.target)
        self.as_gadget = as_gadget if as_gadget is not None else config.gadgets_only

    def __repr__(self):
        return f'{self.__class__.__name__}(control={self.control}, target={self.target})'

    def __eq__(self, other):
        return (self.control, self.target) == (other.control, other.target) if self.type == other.type else False

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif self.type == other.type:
            return Identity()
        else:
            raise IncompatibleGatesException


class CX(ControlledGate):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None):
        super().__init__(control=control, target=target, as_gadget=as_gadget)
        self.type = GateType.CX


class CZ(ControlledGate):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None):
        super().__init__(control=control, target=target, as_gadget=as_gadget)
        self.type = GateType.CZ
        if self.control > self.target:
            self.control, self.target = self.target, self.control
