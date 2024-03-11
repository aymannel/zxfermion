from __future__ import annotations

import logging
from copy import deepcopy
from typing import Optional
from itertools import groupby

import pyzx as zx
from zxfermion.exceptions import IncompatibleQubitDimension, IncompatibleAdditionType
from zxfermion.gates import CX, CZ, X, Z
from zxfermion.types import Node, VertexType, LegType, GateType
from zxfermion.rules import cx_rules, cz_rules, x_rules, z_rules
from zxfermion.graph import BaseGraph

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.ERROR)
logger = logging.getLogger('zxfermion_logger')
logger.setLevel(logging.DEBUG)


class Gadget:
    def __init__(self, pauli_str: str, phase: Optional[float] = None, num_qubits: Optional[int] = None):
        self.phase = phase
        self.type = GateType.GADGET
        self.num_qubits = num_qubits if num_qubits else len(pauli_str)
        if len(pauli_str) != self.num_qubits:
            raise IncompatibleQubitDimension('Length of Pauli string differs from specified number of qubits.')

        self.hub_node = Node(type=VertexType.X, row=3, qubit=self.num_qubits + 1)
        self.phase_node = Node(type=VertexType.Z, row=3, qubit=self.num_qubits + 2, phase=self.phase)
        self.legs = {qubit: LegType.return_object(pauli, qubit) for qubit, pauli in enumerate(pauli_str)}

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        try:
            assert hasattr(other, 'type')
            if (is_gadget := (other.type == GateType.GADGET)) or other.type == GateType.GADGET_CIRCUIT:
                try:
                    assert self.num_qubits == other.num_qubits
                    gadget_list = [self, other] if is_gadget else [self] + other.gadgets
                    gadgets = [key for key, group in groupby(gadget_list) if len(list(group)) % 2]
                    return GadgetCircuit(num_qubits=self.num_qubits, gadgets=gadgets)
                except AssertionError:
                    raise IncompatibleQubitDimension(f'{self.num_qubits} and {other.num_qubits}')
            else:
                raise IncompatibleAdditionType(f'Cannot add Gadget and {type(other)}')
        except AssertionError:
            raise IncompatibleAdditionType(f'Cannot add Gadget and {type(other)}')

    def conjugate_single(self, qubit: int, rules: dict):
        leg_type, multiplier = rules[self.legs[qubit].type]
        self.legs[qubit] = LegType.return_object(type=leg_type, qubit=qubit)
        self.phase_node.phase *= multiplier

    def conjugate_multi(self, control_qubit: int, target_qubit: int, rules: dict):
        control_type, target_type = rules[(self.legs[control_qubit].type, self.legs[target_qubit].type)]
        self.legs[control_qubit] = LegType.return_object(qubit=control_qubit, type=control_type)
        self.legs[target_qubit] = LegType.return_object(qubit=target_qubit, type=target_type)

    def conjugate_x(self, qubit: int):
        self.conjugate_single(qubit=qubit, rules=x_rules)

    def conjugate_z(self, qubit: int):
        self.conjugate_single(qubit=qubit, rules=z_rules)

    def conjugate_cx(self, control: int, target: int):
        self.conjugate_multi(control_qubit=control, target_qubit=target, rules=cx_rules)

    def conjugate_cz(self, control: int, target: int):
        self.conjugate_multi(control_qubit=control, target_qubit=target, rules=cz_rules)

    def graph(self, num_qubits: Optional[int]) -> zx.Graph:
        try:
            num_qubits = num_qubits if num_qubits else self.num_qubits
            assert self.num_qubits == num_qubits
        except AssertionError:
            raise IncompatibleQubitDimension(f'Incompatible qubit dimensions {self.num_qubits} and {num_qubits}')

        graph = BaseGraph(num_qubits=self.num_qubits, num_rows=3)
        if non_identity_legs := {qubit: leg for qubit, leg in self.legs.items() if leg.type != LegType.I}:
            hub_ref = graph.add_node(node=self.hub_node)
            phase_ref = graph.add_node(node=self.phase_node)
            graph.add_edge((hub_ref, phase_ref))

            for qubit, leg in non_identity_legs.items():
                node_refs = [graph.add_node(node) for node in leg.nodes]
                middle_ref = node_refs[1] if leg.left else node_refs[0]
                graph.connect_nodes(qubit=leg.qubit, node_refs=node_refs)
                graph.add_edge((middle_ref, hub_ref))
                graph.remove_wire(qubit=qubit)
        return graph

    def draw(self):
        zx.draw(self.graph(self.num_qubits))


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget], num_qubits: int):
        self.num_qubits = num_qubits
        self.type = GateType.GADGET_CIRCUIT
        self.gadgets = [key for key, group in groupby(deepcopy(gadgets)) if len(list(group)) % 2]
        try:
            assert all(self.num_qubits == gadget.num_qubits for gadget in self.gadgets)
        except AssertionError:
            raise IncompatibleQubitDimension

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        try:
            assert hasattr(other, 'type')
            if (is_gadget := (other.type == GateType.GADGET)) or other.type == GateType.GADGET_CIRCUIT:
                try:
                    assert self.num_qubits == other.num_qubits
                    gadget_list = self.gadgets + [other] if is_gadget else self.gadgets + other.gadgets
                    gadgets = [key for key, group in groupby(gadget_list) if len(list(group)) % 2]
                    return GadgetCircuit(num_qubits=self.num_qubits, gadgets=gadgets)
                except AssertionError:
                    raise IncompatibleQubitDimension(f'{self.num_qubits} and {other.num_qubits}')
            else:
                raise IncompatibleAdditionType(f'Cannot add GadgetCircuit and {type(other)}')
        except AssertionError:
            raise IncompatibleAdditionType(f'Cannot add GadgetCircuit and {type(other)}')

    def surround_cx(
            self,
            control: int,
            target: int,
            left: Optional[int] = None,
            right: Optional[int] = None,
            draw: Optional[bool] = True
    ):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_cx(control=control, target=target)
        self.gadgets.insert(left, CX(control=control, target=target))
        self.gadgets.insert(right, CX(control=control, target=target))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        if draw:
            self.draw()

    def surround_cz(
            self,
            control: int,
            target: int,
            left: Optional[int] = None,
            right: Optional[int] = None,
            draw: Optional[bool] = True
    ):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_cz(control=control, target=target)
        self.gadgets.insert(left, CZ(control=control, target=target))
        self.gadgets.insert(right, CZ(control=control, target=target))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        if draw:
            self.draw()

    def surround_x(self, qubit: int, left: Optional[int] = None, right: Optional[int] = None):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_x(qubit=qubit)
        self.gadgets.insert(left, X(qubit=qubit))
        self.gadgets.insert(right, X(qubit=qubit))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        self.draw()

    def surround_z(self, qubit: int, left: Optional[int] = None, right: Optional[int] = None):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_z(qubit=qubit)
        self.gadgets.insert(left, Z(qubit=qubit))
        self.gadgets.insert(right, Z(qubit=qubit))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        self.draw()

    def graph(self) -> zx.Graph:
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        graph = BaseGraph(num_qubits=self.num_qubits)
        for gadget in self.gadgets:
            gadget.num_qubits = gadget.num_qubits if gadget.num_qubits else self.num_qubits
            graph += gadget.graph(num_qubits=self.num_qubits)
        return graph

    def draw(self):
        zx.draw(self.graph())
