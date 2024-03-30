from __future__ import annotations

import math
from copy import deepcopy
from typing import Optional

import pyzx as zx
from pyzx import VertexType

from zxfermion import config
from zxfermion.types import GateType, PauliType
from zxfermion.exceptions import IncompatibleGatesException


class Identity:
    def __init__(self):
        self.type = GateType.IDENTITY

    def __add__(self, other):
        return other

    def __eq__(self, other):
        return True if other.type == GateType.IDENTITY else other.identity if hasattr(other, 'identity') else False

    @property
    def inverse(self) -> Identity:
        return Identity()


class FixedPhaseGate:
    qubit: int


class SelfInverse:
    @property
    def inverse(self) -> X:
        return deepcopy(self)


class CliffordGate(FixedPhaseGate):
    pass


class PauliGate(SelfInverse, FixedPhaseGate):
    pass


class BaseGate:
    def matrix(self, return_latex=False):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).matrix(return_latex=return_latex)

    def graph(self, expand_gadget=None, as_gadget=None):
        from zxfermion.circuits import GadgetCircuit
        return GadgetCircuit([self]).graph(expand_gadgets=expand_gadget, gadgets_only=as_gadget)

    def tikz(self, name: str, expand_gadget=None, as_gadget=None):
        self.graph(expand_gadget=expand_gadget, as_gadget=as_gadget).tikz(name=name)

    def draw(self, expand_gadget=None, as_gadget=None, labels=False):
        zx.draw(self.graph(expand_gadget=expand_gadget, as_gadget=as_gadget), labels=labels)


class SingleQubitGate(BaseGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None, phase: Optional[int | float] = None):
        self.type = GateType.SINGLE_QUBIT_GATE
        self.qubit = 0 if qubit is None else qubit
        self.phase = 0 if phase is None else round(phase % 2, 15)
        self.min_qubit = self.qubit
        self.max_qubit = self.qubit
        self.qubits = [self.qubit]
        self.as_gadget = as_gadget if as_gadget is not None else config.gadgets_only

    def __repr__(self):
        if isinstance(self, FixedPhaseGate):
            return f'{self.__class__.__name__}(qubit={self.qubit})'
        else:
            return f'{self.__class__.__name__}(qubit={self.qubit}, phase={self.phase})'

    def to_dict(self) -> dict:
        return {self.__class__.__name__: {
            'qubit': self.qubit
        } if isinstance(self, FixedPhaseGate) else {
            'qubit': self.qubit,
            'phase': self.phase
        }}

    @property
    def inverse(self) -> SingleQubitGate:
        inverse = deepcopy(self)
        inverse.phase *= -1
        return inverse


class ControlledGate(BaseGate, SelfInverse):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None):
        control = 0 if control is None else control
        target = 1 if target is None else target
        assert control != target
        self.type = GateType.CONTROLLED_GATE
        self.control = control
        self.target = target
        self.qubits = control, target
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


class Gadget(BaseGate):
    def __init__(self, pauli_string: str, phase: Optional[int | float] = None, expand_gadget=None):
        self.type = GateType.GADGET
        self.phase = 0 if phase is None else round(phase % 2, 15)
        self.paulis = {q: PauliType(p) for q, p in enumerate(pauli_string.rstrip('I'))}
        self.expand_gadget = expand_gadget if expand_gadget is not None else config.expand_gadgets
        self.phase_gadget = all(pauli == PauliType.Z or pauli == PauliType.I for pauli in self.paulis.values())
        self.identity = self.phase_gadget and math.isclose(self.phase, 0)

    def __repr__(self):
        return f"Gadget(pauli_string='{self.pauli_string}', phase={self.phase})"

    def __eq__(self, other):
        if self.identity and other.type == GateType.IDENTITY:
            return True
        elif other.type == GateType.GADGET:
            return self.paulis == other.paulis and math.isclose(self.phase, other.phase)
        else:
            return False

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif other.type == GateType.GADGET and self.paulis == other.paulis:
            return Gadget(self.pauli_string, self.phase + other.phase)
        else:
            raise IncompatibleGatesException

    @property
    def pauli_string(self) -> str:
        return ''.join(self.paulis.get(pauli, 'I') for pauli in range(self.max_qubit + 1))

    @property
    def min_qubit(self) -> int:  # handle PauliType.I before
        return min(qubit for qubit, pauli in self.paulis.items() if pauli != PauliType.I)

    @property
    def max_qubit(self) -> int:  # handle PauliType.I after
        return max(qubit for qubit, pauli in self.paulis.items() if pauli != PauliType.I)

    @property
    def inverse(self) -> Gadget:
        inverse = deepcopy(self)
        inverse.phase *= -1
        return inverse

    @classmethod
    def from_single(cls, gate: ZPhase) -> Gadget:
        return cls(pauli_string='I' * gate.qubit + 'Z', phase=gate.phase)

    def to_dict(self) -> dict:
        return {'Gadget': {'pauli_string': self.pauli_string, 'phase': self.phase}}


class XPhase(SingleQubitGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=phase, as_gadget=as_gadget)
        self.type = GateType.X_PHASE
        self.vertex_type = VertexType.X
        self.identity = math.isclose(self.phase, 0)

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


class ZPhase(SingleQubitGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=phase, as_gadget=as_gadget)
        self.type = GateType.Z_PHASE
        self.vertex_type = VertexType.Z
        self.identity = math.isclose(self.phase, 0)

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

    def gadget(self) -> Gadget:
        return Gadget.from_single(self)


class X(PauliGate, XPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget: Optional[bool] = None):
        super().__init__(qubit=qubit, phase=1, as_gadget=as_gadget)
        self.type = GateType.X

    def __add__(self, other):
        if other.type == GateType.X and self.qubit == other.qubit:
            return Identity()
        elif other.type == GateType.X_PLUS and self.qubit == other.qubit:
            return XMinus(qubit=self.qubit)
        elif other.type == GateType.X_MINUS and self.qubit == other.qubit:
            return XPlus(qubit=self.qubit)
        else:
            return super().__add__(other)


class Z(PauliGate, ZPhase):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1, as_gadget=as_gadget)
        self.type = GateType.Z

    def __add__(self, other):
        if other.type == GateType.Z and self.qubit == other.qubit:
            return Identity()
        elif other.type == GateType.Z_PLUS and self.qubit == other.qubit:
            return ZMinus(qubit=self.qubit)
        elif other.type == GateType.Z_MINUS and self.qubit == other.qubit:
            return ZPlus(qubit=self.qubit)
        else:
            return super().__add__(other)


class XPlus(XPhase, CliffordGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1/2, as_gadget=as_gadget)
        self.type = GateType.X_PLUS

    def __add__(self, other):
        if other.type == GateType.X_PLUS and self.qubit == other.qubit:
            return X(qubit=self.qubit)
        elif other.type == GateType.X_MINUS and self.qubit == other.qubit:
            return Identity()
        elif other.type == GateType.X and self.qubit == other.qubit:
            return XMinus(qubit=self.qubit)
        else:
            return super().__add__(other)

    @property
    def inverse(self) -> XMinus:
        return XMinus(qubit=self.qubit)


class XMinus(XPhase, CliffordGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=3/2, as_gadget=as_gadget)
        self.type = GateType.X_MINUS

    def __add__(self, other):
        if other.type == GateType.X_MINUS and self.qubit == other.qubit:
            return X(qubit=self.qubit)
        elif other.type == GateType.X_PLUS and self.qubit == other.qubit:
            return Identity()
        elif other.type == GateType.X and self.qubit == other.qubit:
            return XPlus(qubit=self.qubit)
        else:
            return super().__add__(other)

    @property
    def inverse(self) -> XPlus:
        return XPlus(qubit=self.qubit)


class ZPlus(ZPhase, CliffordGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=1/2, as_gadget=as_gadget)
        self.type = GateType.Z_PLUS

    def __add__(self, other):
        if other.type == GateType.Z_PLUS and self.qubit == other.qubit:
            return Z(qubit=self.qubit)
        elif other.type == GateType.Z_MINUS and self.qubit == other.qubit:
            return Identity()
        elif other.type == GateType.Z and self.qubit == other.qubit:
            return ZMinus(qubit=self.qubit)
        else:
            return super().__add__(other)

    @property
    def inverse(self) -> ZMinus:
        return ZMinus(qubit=self.qubit)


class ZMinus(ZPhase, CliffordGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, phase=3/2, as_gadget=as_gadget)
        self.type = GateType.Z_MINUS

    def __add__(self, other):
        if other.type == GateType.Z_MINUS and self.qubit == other.qubit:
            return Z(qubit=self.qubit)
        elif other.type == GateType.Z_PLUS and self.qubit == other.qubit:
            return Identity()
        elif other.type == GateType.Z and self.qubit == other.qubit:
            return ZPlus(qubit=self.qubit)
        else:
            return super().__add__(other)

    @property
    def inverse(self) -> ZPlus:
        return ZPlus(qubit=self.qubit)


class H(SelfInverse, SingleQubitGate, CliffordGate):
    def __init__(self, qubit: Optional[int] = None, as_gadget=None):
        super().__init__(qubit=qubit, as_gadget=as_gadget)
        self.type = GateType.H
        self.vertex_type = VertexType.H_BOX
        self.phase = None

    def __repr__(self):
        return f'H(qubit={self.qubit})'

    def __eq__(self, other):
        return self.qubit == other.qubit if other.type == GateType.H else False

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif other.type == GateType.H and self.qubit == other.qubit:
            return Identity()
        else:
            raise IncompatibleGatesException


class CX(ControlledGate, CliffordGate):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None):
        super().__init__(control=control, target=target, as_gadget=as_gadget)
        self.type = GateType.CX


class CZ(ControlledGate, CliffordGate):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None):
        super().__init__(control=control, target=target, as_gadget=as_gadget)
        self.type = GateType.CZ
        if self.control > self.target:
            self.control, self.target = self.target, self.control
