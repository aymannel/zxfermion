from __future__ import annotations

from copy import deepcopy
from typing import Optional

from zxfermion.exceptions import IncompatibleGatesException

from zxfermion.types import GateType


class Identity:
    def __init__(self):
        self.type = GateType.IDENTITY

    def __add__(self, other):
        return other

    def __mul__(self, other):
        return other

    def __eq__(self, other):
        return True if other.type == GateType.IDENTITY else other.identity if hasattr(other, 'identity') else False

    @property
    def inverse(self) -> Identity:
        return Identity()


class FixedPhaseGate:
    qubit: int


class SelfInverse:
    qubits: list[int]
    type: GateType

    def __add__(self, other):
        if other.type == GateType.IDENTITY:
            return self
        elif self.type == other.type and self.qubits == other.qubits:
            return Identity()
        else:
            raise IncompatibleGatesException

    @property
    def inverse(self) -> BaseGate:
        return deepcopy(self)


class CliffordGate(FixedPhaseGate):
    pass


class PauliGate(SelfInverse, FixedPhaseGate):
    pass


class BaseGate:
    stack: Optional[bool] = False
    as_gadget: Optional[bool]


class SingleQubitGate(BaseGate):
    def __init__(self, qubit: Optional[int] = None, phase: Optional[int | float] = None, as_gadget=None, stack=None):
        self.type = GateType.SINGLE_QUBIT_GATE
        self.qubit = 0 if qubit is None else qubit
        self.phase = 0 if phase is None else round(phase % 2, 15)
        self.qubits = [self.qubit]
        self.stack = stack if stack else self.stack
        self.as_gadget = as_gadget if as_gadget else False

    def __repr__(self):
        if isinstance(self, FixedPhaseGate):
            return f'{self.__class__.__name__}(qubit={self.qubit})'
        else:
            return f'{self.__class__.__name__}(qubit={self.qubit}, phase={self.phase})'

    def __eq__(self, other):
        return self.qubit == other.qubit if self.type == other.type else False

    @property
    def inverse(self) -> SingleQubitGate:
        inverse = deepcopy(self)
        inverse.phase *= -1
        return inverse

    @property
    def graph(self):
        from zxfermion.gates.gates import Gadget
        from zxfermion.graphs.gadget_graph import GadgetGraph
        graph = GadgetGraph(num_qubits=self.qubit + 1)
        graph.add(self) if not self.as_gadget else graph.add_gadget(Gadget.from_gate(self))
        return graph

    def to_dict(self) -> dict:
        return {self.__class__.__name__: {
            'qubit': self.qubit
        } if isinstance(self, FixedPhaseGate) else {
            'qubit': self.qubit,
            'phase': self.phase
        }}


class ControlledGate(BaseGate, SelfInverse):
    def __init__(self, control: Optional[int] = None, target: Optional[int] = None, as_gadget=None, stack=None):
        control = 0 if control is None else control
        target = 1 if target is None else target
        assert control != target
        self.type = GateType.CONTROLLED_GATE
        self.control = control
        self.target = target
        self.qubits = control, target
        self.stack = stack if stack else self.stack
        self.as_gadget = as_gadget if as_gadget else False

    def __repr__(self):
        return f'{self.__class__.__name__}(control={self.control}, target={self.target})'

    def __eq__(self, other):
        return (self.control, self.target) == (other.control, other.target) if self.type == other.type else False
