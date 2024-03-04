from __future__ import annotations

import logging
from copy import deepcopy, copy
from typing import Optional

import pyzx as zx
from openfermion import jordan_wigner, FermionOperator, QubitOperator

from zxfermion.commutations import cx_rules, cz_rules
from zxfermion.helpers import pair_list
from zxfermion.types import Node, VertexType, LegType, LegX, LegY, LegZ

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.ERROR)
logger = logging.getLogger('zxfermion_logger')
logger.setLevel(logging.DEBUG)


class CX:
    def __init__(self, control: int, target: int, num_qubits: Optional[int] = None):
        self.num_qubits = num_qubits
        self.control = control
        self.target = target

    @property
    def graph(self) -> zx.Graph:
        def add_to_graph(node: Node) -> int:
            return graph.add_vertex(ty=node.type, row=node.row, qubit=node.qubit, phase=node.phase)

        assert self.num_qubits
        graph = zx.Graph()
        graph.set_inputs([graph.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        graph.set_outputs([graph.add_vertex(qubit=qubit, row=2) for qubit in range(self.num_qubits)])
        graph.add_edges([(graph.inputs()[qubit], graph.outputs()[qubit]) for qubit in range(self.num_qubits)])
        in_refs, out_refs = graph.inputs(), graph.outputs()

        if graph.connected((in_ref := in_refs[self.control]), (out_ref := out_refs[self.control])):
            graph.remove_edge((in_ref, out_ref))
        control_ref = add_to_graph(node=Node(type=VertexType.Z, row=1, qubit=self.control))
        graph.add_edges(pair_list([in_refs[self.control], control_ref, out_refs[self.control]]))

        if graph.connected((in_ref := in_refs[self.target]), (out_ref := out_refs[self.target])):
            graph.remove_edge((in_ref, out_ref))
        target_ref = add_to_graph(node=Node(type=VertexType.X, row=1, qubit=self.target))
        graph.add_edges(pair_list([in_refs[self.target], target_ref, out_refs[self.target]]))

        graph.add_edge((control_ref, target_ref))
        return graph


class CZ:
    def __init__(self, control: int, target: int, num_qubits: Optional[int] = None):
        self.num_qubits = num_qubits
        self.control = control
        self.target = target

    @property
    def graph(self) -> zx.Graph:
        def add_to_graph(node: Node) -> int:
            return graph.add_vertex(ty=node.type, row=node.row, qubit=node.qubit, phase=node.phase)

        assert self.num_qubits
        graph = zx.Graph()
        graph.set_inputs([graph.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        graph.set_outputs([graph.add_vertex(qubit=qubit, row=2) for qubit in range(self.num_qubits)])
        graph.add_edges([(graph.inputs()[qubit], graph.outputs()[qubit]) for qubit in range(self.num_qubits)])
        in_refs, out_refs = graph.inputs(), graph.outputs()

        if graph.connected((in_ref := in_refs[self.control]), (out_ref := out_refs[self.control])):
            graph.remove_edge((in_ref, out_ref))
        control_ref = add_to_graph(node=Node(type=VertexType.Z, row=1, qubit=self.control))
        graph.add_edges(pair_list([in_refs[self.control], control_ref, out_refs[self.control]]))

        if graph.connected((in_ref := in_refs[self.target]), (out_ref := out_refs[self.target])):
            graph.remove_edge((in_ref, out_ref))
        target_ref = add_to_graph(node=Node(type=VertexType.Z, row=1, qubit=self.target))
        graph.add_edges(pair_list([in_refs[self.target], target_ref, out_refs[self.target]]))

        graph.add_edge((control_ref, target_ref), edgetype=zx.EdgeType.HADAMARD)
        return graph


class Gadget:
    def __init__(self, pauli_str: Optional[str] = None, num_qubits: Optional[int] = None, phase: Optional[float] = None):
        num_qubits = len(pauli_str) if not num_qubits else num_qubits
        if len(pauli_str) > num_qubits:
            raise ValueError('Length of Pauli string exceeds specified number of qubits.')

        self.num_qubits = num_qubits
        self.phase = phase
        self.legs = dict()
        self.cliffords = []

        # add gadget legs
        for qubit, pauli in enumerate(pauli_str):
            self.leg(qubit=qubit, type=pauli)

        # add gadget hub
        if self.legs:
            self.hub_node = Node(type=VertexType.X, row=3, qubit=self.num_qubits + 1)
            self.phase_node = Node(type=VertexType.Z, row=3, qubit=self.num_qubits + 2, phase=self.phase)

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(
            num_qubits=self.num_qubits,
            gadgets=[self] + other.gadgets if other.gadgets else [self, other]
        )

    def remove_leg(self, qubit: int):
        self.legs.pop(qubit, None)

    def leg(self, qubit: int, type: LegType):
        match type:
            case LegType.X:
                self.legs[qubit] = LegX(qubit=qubit)
            case LegType.Y:
                self.legs[qubit] = LegY(qubit=qubit)
            case LegType.Z:
                self.legs[qubit] = LegZ(qubit=qubit)
            case LegType.I:
                self.remove_leg(qubit)
            case _:
                raise ValueError(f'Invalid Pauli {type}!')

    def apply_cx(self, control: int, target: int):
        assert control != target
        assert all((0 <= control < self.num_qubits, 0 <= target < self.num_qubits))
        control_start = control_type.type if (control_type := self.legs.get(control)) else LegType.I
        target_start = target_type.type if (target_type := self.legs.get(target)) else LegType.I
        control_end, target_end = cx_rules[(control_start, target_start)]
        self.leg(qubit=control, type=control_end)
        self.leg(qubit=target, type=target_end)

    def apply_cz(self, control: int, target: int):
        assert control != target
        assert all((0 <= control < self.num_qubits, 0 <= target < self.num_qubits))
        control_start = control_type.type if (control_type := self.legs.get(control)) else LegType.I
        target_start = target_type.type if (target_type := self.legs.get(target)) else LegType.I
        control_end, target_end = cz_rules[(control_start, target_start)]
        self.leg(qubit=control, type=control_end)
        self.leg(qubit=target, type=target_end)

    def conjugate_cx(self, control: int, target: int):
        self.apply_cx(control=control, target=target)
        self.cliffords.append(CX(control=control, target=target, num_qubits=self.num_qubits))
        self.draw()

    def conjugate_cz(self, control: int, target: int):
        self.apply_cz(control=control, target=target)
        self.cliffords.append(CZ(control=control, target=target, num_qubits=self.num_qubits))
        self.draw()

    def commutes_with(self, gadget: Gadget) -> bool:
        """Not implemented."""
        pass

    @property
    def gadget_graph(self) -> zx.Graph:
        def add_to_graph(node: Node) -> int:
            return graph.add_vertex(ty=node.type, row=node.row, qubit=node.qubit, phase=node.phase)

        graph = zx.Graph()
        graph.set_inputs([graph.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        graph.set_outputs([graph.add_vertex(qubit=qubit, row=4) for qubit in range(self.num_qubits)])
        graph.add_edges([(graph.inputs()[qubit], graph.outputs()[qubit]) for qubit in range(self.num_qubits)])
        in_refs, out_refs = graph.inputs(), graph.outputs()

        if self.legs:
            hub_ref = add_to_graph(node=self.hub_node)
            phase_ref = add_to_graph(node=self.phase_node)
            graph.add_edge((hub_ref, phase_ref))
            for qubit, leg in self.legs.items():
                if graph.connected(in_refs[qubit], out_refs[qubit]):
                    graph.remove_edge((in_refs[qubit], out_refs[qubit]))
                node_refs = [add_to_graph(node=node) for node in leg.nodes]
                graph.add_edges(pair_list([in_refs[leg.qubit], *node_refs, out_refs[leg.qubit]]))  # create edges across
                graph.add_edge((node_refs[1] if leg.left else node_refs[0], hub_ref))  # connect middle of leg to hub
        return graph

    @property
    def graph(self) -> zx.Graph:
        if not self.cliffords:
            return self.gadget_graph
        else:
            graph_conjugated = self.gadget_graph
            for clifford in self.cliffords:
                clifford_graph = clifford.graph
                graph_conjugated = clifford_graph + graph_conjugated + clifford_graph
            return graph_conjugated

    def draw(self):
        zx.draw(self.graph)


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget], num_qubits: Optional[int] = None):
        assert len(set([(qubits := gadget.num_qubits) for gadget in gadgets])) == 1
        self.num_qubits = num_qubits if num_qubits else qubits
        self.gadgets = deepcopy(gadgets)
        self.cliffords = []

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(
            num_qubits=self.num_qubits,
            gadgets=self.gadgets + other.gadgets if other.gadgets else self.gadgets + [other]
        )

    def conjugate_cx(self, control: int, target: int):
        for gadget in self.gadgets:
            gadget.apply_cx(control, target)
        self.cliffords.append(CX(control=control, target=target, num_qubits=self.num_qubits))
        self.draw()

    def conjugate_cz(self, control: int, target: int):
        for gadget in self.gadgets:
            gadget.apply_cz(control, target)
        self.cliffords.append(CZ(control=control, target=target, num_qubits=self.num_qubits))
        self.draw()

    def identify_controlled_rotations(self):
        """Not implemented."""
        pass

    @property
    def graph(self) -> zx.Graph:
        gadget_graph = copy(self.gadgets[0].graph)
        for gadget in self.gadgets[1:]:
            gadget_graph += gadget.graph

        if not self.cliffords:
            return gadget_graph
        else:
            graph_conjugated = gadget_graph
            for clifford in self.cliffords:
                clifford_graph = clifford.graph
                graph_conjugated = clifford_graph + graph_conjugated + clifford_graph
            return graph_conjugated

    def draw(self):
        zx.draw(self.graph)

    @staticmethod
    def from_operators(operators: list[QubitOperator], num_qubits: int = 8) -> GadgetCircuit:
        gadgets = []
        for operator in operators:
            for gadget_tuple, phase in operator.terms.items():
                paulis = ['I'] * num_qubits
                for pauli in gadget_tuple:
                    paulis[pauli[0]] = pauli[1]
                gadgets.append(Gadget(num_qubits=num_qubits, pauli_str=''.join(paulis), phase=phase))
        return GadgetCircuit(gadgets=gadgets, num_qubits=num_qubits)

    @staticmethod
    def from_operator(operator: QubitOperator, num_qubits: int = 8) -> GadgetCircuit:
        return GadgetCircuit.from_operators(operators=[operator], num_qubits=num_qubits)

    @staticmethod
    def from_fermion_operator(operator: FermionOperator, num_qubits: int = 8) -> GadgetCircuit:
        return GadgetCircuit.from_operator(operator=jordan_wigner(operator), num_qubits=num_qubits)
