from __future__ import annotations

import pyzx as zx
from typing import Optional
from copy import deepcopy, copy

from zxfermion import Gadget, BaseGraph
from zxfermion.graphs.gadget_graph import GadgetGraph
from zxfermion.tableaus.tableau import Tableau
from zxfermion.types import GateType
from zxfermion.utils import settings


class GadgetCircuit:
    def __init__(self, gates: list[Gadget], num_qubits: Optional[int] = 0):
        self.type = GateType.GADGET_CIRCUIT
        self.gates = deepcopy(gates)
        self.num_qubits = max(num_qubits, max([
            max(gate.paulis) + 1
            if gate.type == GateType.GADGET
            else max(gate.qubits) + 1
            for gate in self.gates]))

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gates=self.simplify(self.gates + other.gates))

    def apply(self, gate, start: int = 0, end: int = None, draw=False):
        assert max(gate.qubits) < self.num_qubits  # update num qubits instead / think about edge cases
        end = len(self.gates) if end is None else end
        tableau = Tableau(gate)
        new_gadgets = [
            tableau(gadget)
            if gadget.type == GateType.GADGET else gadget
            for gadget in self.gates[start:end]]
        self.gates[start:end] = [copy(gate), *new_gadgets, copy(gate.inverse)]
        if draw:
            zx.draw(self.graph())
        # self.gates[start:end] = new_gadgets

    def graph(self, as_gadgets: bool = None, stack: bool = settings.stack) -> GadgetGraph:
        graph = GadgetGraph(num_qubits=self.num_qubits)
        for gate in self.gates:
            gate.as_gadget = gate.as_gadget if as_gadgets is None else as_gadgets
            graph.compose(gate.graph, stack=gate.stack if stack is None else stack)
        return graph

    def simplify(self, gates: Optional[list] = None) -> list:
        """Needs work. Use __add__ methods to do this"""
        # return [key for key, group in groupby(gates if gates else self.gates) if len(list(group)) % 2]
        return gates if gates else self.gates

    def matrix(self, return_latex=False, override_max=False):
        return self.graph().matrix(return_latex=return_latex, override_max=override_max)

    def draw(self, as_gadgets: bool = None, stack: bool = settings.stack, labels: bool = False):
        zx.draw(self.graph(as_gadgets=as_gadgets, stack=stack), labels=labels)

    def tikz(self, name: Optional[str] = None, scale: float = settings.tikz_scale, **kwargs):
        return self.graph(**kwargs).tikz(name=name, scale=scale)

    def pdf(self, name: str, scale: float = settings.tikz_scale, **kwargs):
        return self.graph(**kwargs).pdf(name=name, scale=scale)

    def to_dict(self) -> list[dict[str, str | int | float]]:
        return {
            'num_qubits': self.num_qubits,
            'gates': [gadget.to_dict() for gadget in self.gates],
        }

    @classmethod
    def from_dict(cls, circuit_dict: dict):
        gates = []
        for gate in circuit_dict['gates']:
            name = next(iter(gate))
            assert name in GateType.NAMES
            gates.append(eval(name)(**gate[name]))
        return cls(gates=gates, num_qubits=circuit_dict.get('num_qubits'))


class CircuitCollection:
    def __init__(self, circuit1: GadgetCircuit, circuit2: GadgetCircuit):
        self.circuit1 = deepcopy(circuit1)
        self.circuit2 = deepcopy(circuit2)

    def graph(self, as_gadgets=None, stack=None, padding: Optional[int] = 2) -> BaseGraph:
        graph = BaseGraph(num_qubits=max(self.circuit1.num_qubits, self.circuit2.num_qubits))
        graph1 = self.circuit1.graph(as_gadgets=as_gadgets, stack=stack)
        graph2 = self.circuit2.graph(as_gadgets=as_gadgets, stack=stack)
        graph.compose(graph1)

        vertex_dict = {
            vertex: graph.add_vertex(
                graph2.type(vertex),
                phase=graph2.phase(vertex),
                qubit=graph2.qubit(vertex),
                row=graph2.row(vertex) + graph1.output_row + padding)
            for vertex in graph2.vertices()
        }

        for edge in graph2.edges():
            source, target = graph2.edge_st(edge)
            graph.add_edge(graph2.edge(
                vertex_dict[source],
                vertex_dict[target]
            ), edgetype=graph2.edge_type(edge))

        return graph

    def draw(self, as_gadgets=None, stack=None, padding: Optional[int] = 2, labels: Optional[bool] = True):
        graph = self.graph(as_gadgets=as_gadgets, stack=stack, padding=padding)
        zx.draw(graph, labels=labels)
