from __future__ import annotations

import math
import re
from copy import deepcopy
from typing import Optional

from pyzx import VertexType

from zxfermion.exceptions import IncompatibleGatesException
from zxfermion.gates.gate_types import Identity, SelfInverse, CliffordGate, PauliGate, BaseGate, SingleQubitGate, \
    ControlledGate
from zxfermion.types import GateType, PauliType


class Gadget(BaseGate):
    def __init__(self, pauli_string: str, phase: Optional[int | float] = None, as_gadget=True, stack=None):
        pauli_string = re.sub(r'^I+|I+$', lambda match: '_' * len(match.group()), pauli_string)
        self.type = GateType.GADGET
        self.phase = 0 if phase is None else round(phase % 2, 15)
        self.paulis = {q: PauliType(p) for q, p in enumerate(pauli_string) if p != '_'}
        self.phase_gadget = all(pauli == PauliType.Z or pauli == PauliType.I for pauli in self.paulis.values())
        self.identity = self.phase_gadget and math.isclose(self.phase, 0)
        self.stack = stack if stack else self.stack
        self.as_gadget = as_gadget

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
        return ''.join(self.paulis.get(pauli, 'I') for pauli in range(max(self.paulis) + 1))

    @property
    def inverse(self) -> Gadget:
        inverse = deepcopy(self)
        inverse.phase *= -1
        return inverse

    @property
    def graph(self):
        from zxfermion.graphs.gadget_graph import GadgetGraph
        graph = GadgetGraph(max(self.paulis) + 1)
        graph.add_gadget(self) if self.as_gadget else graph.add_expanded_gadget(self)
        return graph

    @classmethod
    def from_gate(cls, gate: ZPhase) -> Gadget:
        return cls(pauli_string='I' * gate.qubit + 'Z', phase=gate.phase)

    def to_dict(self) -> dict:
        return {'Gadget': {'pauli_string': self.pauli_string, 'phase': self.phase}}


class XPhase(SingleQubitGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, **kwargs):
        super().__init__(qubit=qubit, phase=phase, **kwargs)
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
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, **kwargs):
        super().__init__(qubit=qubit, phase=phase, **kwargs)
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

    @property
    def gadget(self) -> Gadget:
        return Gadget.from_gate(self)


class X(XPhase, PauliGate):
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, phase=1, **kwargs)
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


class Z(ZPhase, PauliGate):
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, phase=1, **kwargs)
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
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, phase=1/2, **kwargs)
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
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, phase=3/2, **kwargs)
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
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, phase=1/2, **kwargs)
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
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, phase=3/2, **kwargs)
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
    def __init__(self, qubit: Optional[int] = None, **kwargs):
        super().__init__(qubit=qubit, as_gadget=False, **kwargs)
        self.type = GateType.H
        self.vertex_type = VertexType.H_BOX
        self.phase = None

    def __repr__(self):
        return f'H(qubit={self.qubit})'

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif other.type == GateType.H and self.qubit == other.qubit:
            return Identity()
        else:
            raise IncompatibleGatesException


class CX(ControlledGate, CliffordGate):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, **kwargs):
        super().__init__(control=control, target=target, **kwargs)
        self.type = GateType.CX

    @property
    def graph(self):
        from zxfermion.graphs.gadget_graph import GadgetGraph
        graph = GadgetGraph(num_qubits=max(self.qubits) + 1)
        graph.add_cx_gadget(self) if self.as_gadget else graph.add_cx(self)
        return graph


class CZ(ControlledGate, CliffordGate):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, **kwargs):
        super().__init__(control=control, target=target, **kwargs)
        self.type = GateType.CZ
        if self.control > self.target:
            self.control, self.target = self.target, self.control

    @property
    def graph(self):
        from zxfermion.graphs.gadget_graph import GadgetGraph
        graph = GadgetGraph(num_qubits=max(self.qubits) + 1)
        graph.add_cz_gadget(self) if self.as_gadget else graph.add_cz(self)
        return graph
