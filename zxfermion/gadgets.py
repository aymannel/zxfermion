from __future__ import annotations

import logging
import pyzx as zx
from typing import Optional

from zxfermion.circuits import GadgetCircuit
from zxfermion.graph import BaseGraph
from zxfermion.types import LegType, LegZ, LegY, LegX, LegI, GateType, Node, VertexType

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.ERROR)
logger = logging.getLogger('zxfermion_logger')
logger.setLevel(logging.DEBUG)


class Gadget:
    def __init__(self, pauli_str: str, phase: Optional[float] = None):
        self.type = GateType.GADGET
        self.phase = phase
        self.legs = self.build_legs(pauli_str)

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.phase, self.legs) == (other.phase, other.legs)
        else:
            return False

    @property
    def num_qubits(self) -> int:
        return max([qubit for qubit in self.legs])

    @staticmethod
    def build_legs(pauli_str):
        return {
            qubit: {
                LegType.I: LegI(qubit),
                LegType.X: LegX(qubit),
                LegType.Y: LegY(qubit),
                LegType.Z: LegZ(qubit),
            }[LegType(pauli)]
            for qubit, pauli in enumerate(pauli_str)
        }

    def draw(self) -> BaseGraph:
        circuit = GadgetCircuit([self])
        circuit.draw()
        return circuit.graph()

    # def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
    #     if (is_gadget := (other.type == GateType.GADGET)) or other.type == GateType.GADGET_CIRCUIT:
    #         try:
    #             assert self.num_qubits == other.num_qubits
    #             gadget_list = [self, other] if is_gadget else [self] + other.gadgets
    #             gadgets = [key for key, group in groupby(gadget_list) if len(list(group)) % 2]
    #             return GadgetCircuit(num_qubits=self.num_qubits, gadgets=gadgets)
    #         except AssertionError:
    #             raise IncompatibleQubitDimension(f'{self.num_qubits} and {other.num_qubits}')
    #     else:
    #         raise IncompatibleType(f'Cannot add Gadget and {type(other)}')


class CX:
    def __init__(self, control: int, target: int):
        assert control != target
        self.type = GateType.CX
        self.num_qubits = max(control, target)
        self.control = Node(type=VertexType.Z, qubit=control, row=1)
        self.target = Node(type=VertexType.X, qubit=target, row=1)

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control.qubit, self.target.qubit) == (other.control.qubit, other.target.qubit)
        else:
            return False


class CZ:
    def __init__(self, control: int, target: int):
        assert control != target
        self.type = GateType.CZ
        self.num_qubits = max(control, target)
        self.control = Node(type=VertexType.Z, qubit=control, row=1)
        self.target = Node(type=VertexType.Z, qubit=target, row=1)

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control.qubit, self.target.qubit) == (other.control.qubit, other.target.qubit)
        else:
            return False
