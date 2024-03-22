from __future__ import annotations

import pyzx as zx
from copy import deepcopy
from typing import Optional
from itertools import groupby

from zxfermion.types import GateType
from zxfermion.gadgets import Gadget
from zxfermion.graph import BaseGraph


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget]):
        self.type = GateType.GADGET_CIRCUIT
        self.gadgets = deepcopy(gadgets)
        self.num_qubits = max([gadget.max_qubit for gadget in self.gadgets]) + 1

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gadgets=self.fuse_gadgets(self.gadgets + other.gadgets))

    def fuse_gadgets(self, gadgets: Optional[list] = None) -> list:
        return [key for key, group in groupby(gadgets if gadgets else self.gadgets) if len(list(group)) % 2]

    def stack_gadgets(self):
        layers = []
        for gadget in self.fuse_gadgets():
            placed = False
            for layer in layers:
                if all(gadget.max_qubit < other.min_qubit or gadget.min_qubit > other.max_qubit for other in layer):
                    layer.append(gadget)
                    placed = True
                    break
            if not placed:
                layers.append([gadget])
        return layers

    def draw(self, gadgets_only: bool = False, stack: bool = True, expand: bool = False) -> BaseGraph:
        layers = self.stack_gadgets() if stack else [[gadget] for gadget in self.gadgets]

        circuit = BaseGraph(num_qubits=self.num_qubits)
        for layer in layers:
            graph = None
            for gadget in layer:
                match gadget.type:
                    case GateType.GADGET:
                        graph = circuit.add_expanded_gadget(gadget, graph) if expand else circuit.add_gadget(gadget, graph)
                    case GateType.CX:
                        graph = circuit.add_cx_gadget(gadget, graph) if gadgets_only else circuit.add_cx(gadget, graph)
                    case GateType.CZ:
                        graph = circuit.add_cz_gadget(gadget, graph) if gadgets_only else circuit.add_cz(gadget, graph)
                    case GateType.X:
                        graph = circuit.add_x_gadget(gadget, graph) if gadgets_only else circuit.add_node(gadget, graph)
                    case GateType.Z:
                        graph = circuit.add_z_gadget(gadget, graph) if gadgets_only else circuit.add_node(gadget, graph)
            circuit.compose(graph)
        zx.draw(circuit)  ## , labels=True)
        return circuit
