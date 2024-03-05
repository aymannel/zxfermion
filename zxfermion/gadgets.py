from __future__ import annotations

import logging
from copy import deepcopy
from typing import Optional

import pyzx as zx

from zxfermion.cliffords import CZ, CX, X
from zxfermion.types import Node, VertexType, LegType
from zxfermion.rules import cx_rules, cz_rules, x_rules, z_rules, hadamard_rules
from zxfermion.graphs import BaseGraph

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.ERROR)
logger = logging.getLogger('zxfermion_logger')
logger.setLevel(logging.DEBUG)

# implement LegI! will get rid of so many issues like finding the 'type' of a leg


class Gadget:
    def __init__(self, pauli_str: str, num_qubits: Optional[int] = None, phase: Optional[float] = None):
        self.phase = phase
        self.num_qubits = num_qubits if num_qubits else len(pauli_str)

        if len(pauli_str) > self.num_qubits:
            raise ValueError('Length of Pauli string exceeds specified number of qubits.')

        self.legs = {
            qubit: LegType.get_object(pauli, qubit)
            for qubit, pauli in enumerate(pauli_str)
        }

        if [leg for leg in self.legs.values()]:
            self.hub_node = Node(type=VertexType.X, row=3, qubit=self.num_qubits + 1)
            self.phase_node = Node(type=VertexType.Z, row=3, qubit=self.num_qubits + 2, phase=self.phase)

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(
            num_qubits=self.num_qubits,
            gadgets=[self] + other.gadgets if other.gadgets else [self, other]
        )

    def conjugate(self, qubit: int, rules: dict):
        leg_type, multiplier = rules[self.legs[qubit].type]
        self.legs[qubit] = LegType.get_object(type=leg_type, qubit=qubit)
        self.phase = self.phase * multiplier

    def conjugate_multi(self, control_qubit: int, target_qubit: int, rules: dict):
        control_type, target_type = rules[(self.legs[control_qubit].type, self.legs[target_qubit].type)]
        self.legs[control_qubit] = LegType.get_object(qubit=control_qubit, type=control_type)
        self.legs[target_qubit] = LegType.get_object(qubit=target_qubit, type=target_type)

    def conjugate_x(self, qubit: int):
        self.conjugate(qubit=qubit, rules=x_rules)

    def conjugate_z(self, qubit: int):
        self.conjugate(qubit=qubit, rules=z_rules)

    def conjugate_hadamard(self, qubit: int):
        self.conjugate(qubit=qubit, rules=hadamard_rules)

    def conjugate_cx(self, control: int, target: int):
        self.conjugate_multi(control_qubit=control, target_qubit=target, rules=cx_rules)

    def conjugate_cz(self, control: int, target: int):
        self.conjugate_multi(control_qubit=control, target_qubit=target, rules=cz_rules)

    def graph(self) -> zx.Graph:
        from zxfermion.graphs import GadgetGraph
        return GadgetGraph(self)

    def draw(self):
        zx.draw(self.graph())


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget], num_qubits: Optional[int] = None):
        if not num_qubits and all((qubits := gadget.num_qubits) == gadgets[0].num_qubits for gadget in gadgets):
            self.num_qubits = qubits
        self.num_qubits = num_qubits if num_qubits else qubits
        self.gadgets = deepcopy(gadgets)
        self.cliffords = []

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(
            num_qubits=self.num_qubits,
            gadgets=self.gadgets + other.gadgets if other.gadgets else self.gadgets + [other]
        )

    def apply_cx(self, control: int, target: int):
        for gadget in self.gadgets:
            gadget.conjugate_cx(control=control, target=target)
        self.cliffords.append(CX(control=control, target=target))
        self.draw()

    def apply_cz(self, control: int, target: int):
        for gadget in self.gadgets:
            gadget.conjugate_cz(control=control, target=target)
        self.cliffords.append(CZ(control=control, target=target))
        self.draw()

    def apply_x(self, qubit: int):
        for gadget in self.gadgets:
            gadget.conjugate_x(qubit)
        self.cliffords.append(X(qubit))
        self.draw()

    def graph(self) -> zx.Graph:
        gadget_graph = BaseGraph(num_qubits=self.num_qubits)
        for gadget in self.gadgets:
            gadget_graph += gadget.graph()

        clifford_left, clifford_right = BaseGraph(num_qubits=self.num_qubits), BaseGraph(num_qubits=self.num_qubits)
        for left, right in zip(self.cliffords, self.cliffords[::-1]):
            clifford_left += left.graph(self.num_qubits)
            clifford_right += right.graph(self.num_qubits)

        return clifford_left + gadget_graph + clifford_right if self.cliffords else gadget_graph

    def draw(self):
        zx.draw(self.graph())
