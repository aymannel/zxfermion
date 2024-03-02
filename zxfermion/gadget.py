from __future__ import annotations

from typing import Literal, Optional

import pyzx as zx
from openfermion import jordan_wigner, FermionOperator, QubitOperator

from zxfermion.helpers import ref_tuples

LegType = Literal['X', 'Y', 'Z']


class Node:
    def __init__(self, graph: zx.Graph, qubit: int, row: int, node_type: zx.VertexType, phase: Optional[float] = None):
        self.ref = graph.add_vertex(ty=node_type, qubit=qubit, row=row, phase=phase)
        self.phase = phase
        self.qubit = qubit
        self.row = row
        self.ty = node_type
        graph.set_vdata(self.ref, key='ref', val=self.ref)  # keep track of vertices when composing graphs


class GadgetLeg:
    def __init__(self, graph: zx.Graph, leg_type: LegType, qubit: int):
        self.qubit = qubit
        self.leg_type = leg_type
        self.in_ref = graph.inputs()[qubit]
        self.out_ref = graph.outputs()[qubit]

        match self.leg_type:
            case 'X':
                self.middle = Node(graph=graph, node_type=zx.VertexType.Z, qubit=self.qubit, row=2)
                self.cliff_left = Node(graph=graph, node_type=zx.VertexType.H_BOX, qubit=self.qubit, row=1)
                self.cliff_right = Node(graph=graph, node_type=zx.VertexType.H_BOX, qubit=self.qubit, row=3)
            case 'Y':
                self.middle = Node(graph=graph, node_type=zx.VertexType.Z, qubit=self.qubit, row=2)
                self.cliff_left = Node(graph=graph, node_type=zx.VertexType.X, qubit=self.qubit, row=1, phase=1 / 2)
                self.cliff_right = Node(graph=graph, node_type=zx.VertexType.X, qubit=self.qubit, row=3, phase=-1 / 2)
            case 'Z':
                self.middle = Node(graph=graph, node_type=zx.VertexType.Z, qubit=self.qubit, row=2)
                self.cliff_left = None
                self.cliff_right = None

        self.nodes = tuple(node for node in (self.cliff_left, self.middle, self.cliff_right) if node)


class Gadget:
    def __init__(self, num_qubits: int, phase: float, pauli_str: Optional[str] = None):
        self.phase = phase
        self.num_qubits = num_qubits
        self.leg_types = list(pauli_str + 'I' * (num_qubits - len(pauli_str))) if pauli_str else list('I' * num_qubits)
        self.nodes = []

        # initialise graph
        self.graph = zx.Graph()
        self.graph.set_inputs([self.graph.add_vertex(qubit=qubit, row=0) for qubit in range(num_qubits)])
        self.graph.set_outputs([self.graph.add_vertex(qubit=qubit, row=4) for qubit in range(num_qubits)])
        self.graph.add_edges([  # create edges between boundaries in absence of a leg
            (self.graph.inputs()[qubit], self.graph.outputs()[qubit])
            for qubit, leg_type
            in enumerate(self.leg_types)
            if leg_type == 'I'
        ])

        # add gadget hub
        self.hub_node = Node(graph=self.graph, node_type=zx.VertexType.X, qubit=self.num_qubits + 1, row=3)
        self.phase_node = Node(graph=self.graph, node_type=zx.VertexType.Z, qubit=self.num_qubits + 2, row=3, phase=self.phase)
        self.graph.add_edge((self.hub_node.ref, self.phase_node.ref))
        self.nodes += [self.hub_node, self.phase_node]

        # add gadget legs
        self.legs = [
            None if leg_type == 'I'
            else self.add_leg(qubit=qubit, leg_type=leg_type)
            for qubit, leg_type in enumerate(self.leg_types)
        ]

    def add_leg(self, qubit: int, leg_type: LegType) -> GadgetLeg:
        gadget_leg = GadgetLeg(graph=self.graph, leg_type=leg_type, qubit=qubit)
        node_refs = [node.ref for node in gadget_leg.nodes if node]
        if self.graph.connected(gadget_leg.in_ref, gadget_leg.out_ref):
            self.graph.remove_edge((gadget_leg.in_ref, gadget_leg.out_ref))

        self.graph.add_edge((gadget_leg.middle.ref, self.hub_node.ref))
        self.graph.add_edges(ref_tuples([gadget_leg.in_ref, *node_refs, gadget_leg.out_ref]))
        self.nodes += [*gadget_leg.nodes]
        return gadget_leg

    def remove_leg(self, qubit: int):
        gadget_leg = next(filter(lambda leg: leg.qubit == qubit, [leg for leg in self.legs if leg]), None)
        self.nodes = [node for node in self.nodes if node not in gadget_leg.nodes]
        self.graph.remove_vertices([node.ref for node in gadget_leg.nodes if node])
        self.graph.add_edge((gadget_leg.in_ref, gadget_leg.out_ref))
        self.legs.remove(gadget_leg)
        del gadget_leg

    def replace_leg(self, qubit: int, leg_type: LegType) -> GadgetLeg:
        self.remove_leg(qubit=qubit)
        return self.add_leg(qubit=qubit, leg_type=leg_type)

    def draw(self):
        zx.draw(self.graph)


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget], num_qubits: int = 8):
        self.gadgets = gadgets
        self.num_qubits = num_qubits
        self.nodes = [node for gadget in self.gadgets for node in gadget.nodes]
        self.graph = self._build_graph()
        self._update_refs()

    def __add__(self, other) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gadgets=self.gadgets + other.gadgets, num_qubits=self.num_qubits)

    def _build_graph(self):
        graph = zx.Graph()
        graph.set_inputs([graph.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        graph.set_outputs([graph.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        graph.add_edges(list(zip(graph.inputs(), graph.outputs())))
        for gadget in self.gadgets:
            graph += gadget.graph
        return graph

    def _update_refs(self):
        for idx, gadget in enumerate(self.gadgets):
            for node in gadget.nodes:
                node.row = node.row + (3 * idx)
                node.ref = self.find_node(row=node.row, qubit=node.qubit)

        # for gadget in self.gadgets:
        #     for leg in [leg for leg in gadget.legs if leg]:
        #         leg.in_ref = self.get_left_of_node(leg.nodes[0]).ref
        #         leg.out_ref = self.get_right_of_node(leg.nodes[-1]).ref
        #         pass

    def find_node(self, row: int, qubit: int) -> int:
        row_refs = self.graph.rows()
        qubit_refs = self.graph.qubits()
        all_refs = self.graph.vertices()
        return {(qubit_refs.get(ref), row_refs.get(ref)): ref for ref in all_refs}.get((qubit, row))

    def node_by_ref(self, ref: int):
        return next(filter(lambda node: node.ref == ref, self.nodes))

    def get_left_of_node(self, node: Node) -> Node:
        incident_edges = self.graph.incident_edges(node.ref)
        # incident_nodes = [self.node_by_ref(ref) for edge in incident_edges for ref in edge if ref != node.ref]
        incident_nodes = [ref for edge in incident_edges for ref in edge if ref != node.ref]
        print(incident_nodes)
        # return next(filter(lambda n: n.row < node.row and n.qubit == node.qubit, incident_nodes))
        return None

    def get_right_of_node(self, node: Node) -> Node:
        incident_edges = self.graph.incident_edges(node.ref)
        incident_nodes = [self.node_by_ref(ref) for edge in incident_edges for ref in edge if ref != node.ref]
        return next(filter(lambda n: n.row > node.row and n.qubit == node.qubit, incident_nodes))

    def get_leg(self, gadget_num: int, leg_num: int) -> GadgetLeg:  # where gadget_num/leg_num = 1 for first gadget/leg
        gadget = self.gadgets[gadget_num - 1]
        return [leg for leg in gadget.legs if leg][leg_num - 1]

    def draw(self):
        zx.draw(self.graph)

    @staticmethod
    def from_operator(operator: QubitOperator, num_qubits: int = 8) -> GadgetCircuit:
        gadgets = []
        for gadget_tuple, phase in operator.terms.items():
            paulis = ['I'] * num_qubits
            for pauli in gadget_tuple:
                paulis[pauli[0]] = pauli[1]
            gadgets.append(Gadget(num_qubits=num_qubits, pauli_str=''.join(paulis), phase=phase))
        return GadgetCircuit(gadgets=gadgets, num_qubits=num_qubits)

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
    def from_fermion_operator(operator: FermionOperator, num_qubits: int = 8) -> GadgetCircuit:
        return GadgetCircuit.from_operator(operator=jordan_wigner(operator), num_qubits=num_qubits)
