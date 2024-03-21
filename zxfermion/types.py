from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel

from zxfermion.graph import BaseGraph


class EdgeType:
    S: int = 1
    H: int = 2


class VertexType:
    Z: int = 1
    X: int = 2
    H: int = 3


class LegType(str, Enum):
    I = 'I'
    X = 'X'
    Y = 'Y'
    Z = 'Z'


class GateType(str, Enum):
    GADGET_CIRCUIT = 'GADGET_CIRCUIT'
    GADGET = 'GADGET'
    CX = 'CX'
    CZ = 'CZ'
    X = 'Y'
    Z = 'Z'


class Node(BaseModel):
    row: int
    qubit: Optional[int] = None
    type: Optional[int] = None
    phase: Optional[float] = None

    def graph(self, num_qubits: int) -> BaseGraph:
        graph = BaseGraph(num_qubits=num_qubits)
        graph.connect_nodes(qubit=self.qubit, node_refs=[graph.add_node(node=self)])
        graph.remove_wire(self.qubit)
        return graph

    def gadget(self, num_qubits: int) -> BaseGraph:
        if self.type == VertexType.X or self.type == VertexType.Z:
            opposite_type = VertexType.X if self.type == VertexType.Z else VertexType.Z

            leg = Node(type=self.type, row=1, qubit=self.qubit)
            hub_node = Node(type=opposite_type, row=2, qubit=num_qubits + 1)
            phase_node = Node(type=self.type, row=2, qubit=num_qubits + 2, phase=self.phase)

            graph = BaseGraph(num_qubits=num_qubits, num_rows=1)
            graph.connect_nodes(qubit=self.qubit, node_refs=[ref := graph.add_node(leg)])
            graph.remove_wire(qubit=self.qubit)

            hub_ref = graph.add_node(hub_node)
            phase_ref = graph.add_node(phase_node)
            graph.add_edge((hub_ref, phase_ref))
            graph.add_edge((ref, hub_ref))
            return graph
        else:
            print(f'Not yet implemented gadget for {self.type}')


class LegI:
    def __init__(self, qubit):
        self.type = LegType.I
        self.qubit = qubit
        self.left = None
        self.middle = None
        self.right = None
        self.nodes = []


class LegX:
    def __init__(self, qubit):
        self.type = LegType.X
        self.qubit = qubit
        self.left = Node(row=1, qubit=qubit, type=VertexType.H)
        self.middle = Node(row=2, qubit=qubit, type=VertexType.Z)
        self.right = Node(row=3, qubit=qubit, type=VertexType.H)
        self.nodes = [self.left, self.middle, self.right]


class LegY:
    def __init__(self, qubit):
        self.type = LegType.Y
        self.qubit = qubit
        self.left = Node(row=1, qubit=qubit, type=VertexType.X, phase=1/2)
        self.middle = Node(row=2, qubit=qubit, type=VertexType.Z)
        self.right = Node(row=3, qubit=qubit, type=VertexType.X, phase=-1/2)
        self.nodes = [self.left, self.middle, self.right]


class LegZ:
    def __init__(self, qubit):
        self.type = LegType.Z
        self.qubit = qubit
        self.middle = Node(row=2, qubit=qubit, type=VertexType.Z)
        self.left = None
        self.right = None
        self.nodes = [self.middle]
