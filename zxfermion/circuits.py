from __future__ import annotations

from copy import deepcopy
from typing import Optional

import pyzx as zx
from IPython.display import display, Markdown

from zxfermion import config
from zxfermion.gadgets import Gadget, XPhase, ZPhase, X, Z, XPlus, ZPlus, XMinus, ZMinus, H
from zxfermion.graph import GadgetGraph
from zxfermion.types import GateType
from zxfermion.utilities import matrix_to_latex


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget], num_qubits: Optional[int] = 0):
        self.type = GateType.GADGET_CIRCUIT
        self.gadgets = deepcopy(gadgets)
        self.num_qubits = max(num_qubits, max([gadget.max_qubit for gadget in self.gadgets]) + 1)

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gadgets=self.cancel_gadgets(self.gadgets + other.gadgets))

    def draw(self, labels=False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, gadgets_only=None, stack_gadgets=None, expand_gadgets=None) -> GadgetGraph:
        stack_gadgets = stack_gadgets if stack_gadgets is not None else config.stack_gadgets
        gadget_layers = self.stack_gadgets() if stack_gadgets else [[gadget] for gadget in self.gadgets]
        circuit = GadgetGraph(num_qubits=self.num_qubits)
        for gadget_layer in gadget_layers:
            layer = GadgetGraph(num_qubits=self.num_qubits)
            for gadget in gadget_layer:
                if gadget.type == GateType.GADGET:
                    gadget.expand_gadget = gadget.expand_gadget if expand_gadgets is None else expand_gadgets
                else:
                    gadget.as_gadget = gadget.as_gadget if gadgets_only is None else gadgets_only
                if gadget.type == GateType.GADGET:
                    layer.add_expanded_gadget(gadget) if gadget.expand_gadget else layer.add_gadget(gadget)
                elif gadget.type in [GateType.X_PHASE, GateType.X, GateType.X_PLUS, GateType.X_MINUS]:
                    layer.add_single_gate(gadget)
                elif gadget.type in [GateType.Z_PHASE, GateType.Z, GateType.Z_PLUS, GateType.Z_MINUS]:
                    layer.add_gadget(Gadget.from_gate(gadget)) if gadget.as_gadget else layer.add_single_gate(gadget)
                elif gadget.type == GateType.CX:
                    layer.add_cx_gadget(gadget) if gadget.as_gadget else layer.add_cx(gadget)
                elif gadget.type == GateType.CZ:
                    layer.add_cz_gadget(gadget) if gadget.as_gadget else layer.add_cz(gadget)
                elif gadget.type == GateType.H:
                    layer.add_single_gate(gadget)
            circuit.compose(layer)
        return circuit

    def cancel_gadgets(self, gadgets: Optional[list] = None) -> list:
        """Needs work. Use __add__() to do this"""
        # return [key for key, group in groupby(gadgets if gadgets else self.gadgets) if len(list(group)) % 2]
        return gadgets if gadgets else self.gadgets

    def stack_gadgets(self, gadgets: Optional[list] = None) -> list[list]:
        layers = []
        for gadget in gadgets if gadgets else self.cancel_gadgets():
            placed = False
            for layer in layers:
                if all(gadget.max_qubit < other.min_qubit or gadget.min_qubit > other.max_qubit for other in layer):
                    layer.append(gadget)
                    placed = True
                    break
            if not placed:
                layers.append([gadget])
        return layers

    def matrix(self, return_latex=False, override_max=False):
        if self.num_qubits <= 5 or override_max:
            matrix = self.graph(expand_gadgets=False, gadgets_only=False, stack_gadgets=False).to_matrix()
            latex_string = matrix_to_latex(matrix)
            display(Markdown(latex_string))
            return latex_string if return_latex else None
        else:
            print(f'{2 ** self.num_qubits} x {2 ** self.num_qubits} matrix too large to compute.')

    def tikz(self, name: Optional[str] = None, symbol: Optional[str] = None, scale: Optional[float] = None, **kwargs):
        return self.graph(**kwargs).tikz(name=name, symbol=symbol, scale=scale)

    def pdf(self, name: str, symbol: Optional[str] = None, scale: Optional[float] = 0.5, **kwargs):
        return self.graph(**kwargs).pdf(name=name, symbol=symbol, scale=scale)

    def to_dict(self) -> list[dict[str, str | int | float]]:
        return {
            'num_qubits': self.num_qubits,
            'gadgets': [gadget.to_dict() for gadget in self.gadgets],
        }

    @classmethod
    def from_dict(cls, circuit_dict: dict):
        gadgets = [eval(gadget_dict['gate_type'])(**gadget_dict['params']) for gadget_dict in circuit_dict['gadgets']]
        return cls(gadgets=gadgets, num_qubits=circuit_dict.get('num_qubits'))
