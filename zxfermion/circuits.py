from __future__ import annotations

from copy import deepcopy, copy
from itertools import groupby
from typing import Optional

import pyzx as zx
from IPython.display import display, Markdown

from zxfermion import config
from zxfermion.gadgets import Gadget, SingleQubitGate, FixedPhaseGate
from zxfermion.graph import GadgetGraph
from zxfermion.tableaus import Tableau
from zxfermion.types import GateType, PauliType
from zxfermion.utilities import matrix_to_latex


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget], num_qubits: Optional[int] = 0):
        self.type = GateType.GADGET_CIRCUIT
        self.gadgets = deepcopy(gadgets)
        self.num_qubits = max(num_qubits, max([gadget.max_qubit for gadget in self.gadgets]) + 1)

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gadgets=self.cancel_gadgets(self.gadgets + other.gadgets))

    def apply(self, gate, start: int = 0, end: int = None):
        assert gate.max_qubit < self.num_qubits
        end = len(self.gadgets) if end is None else end

        tableau = Tableau(gate)
        new_gadgets = [
            tableau(gadget)
            if gadget.type == GateType.GADGET else gadget
            for gadget in self.gadgets[start:end]
        ]

        ## NOT SURE ABOUT THIS BUSINESS...
        first_type = self.gadgets[start].paulis.get(gate.qubit) if self.gadgets[start].type == GateType.GADGET else None
        last_type = self.gadgets[end - 1].paulis.get(gate.qubit) if self.gadgets[end - 1].type == GateType.GADGET else None
        if (first_type == last_type == PauliType.Z or first_type == last_type == PauliType.X) and gate.type == GateType.H:
            self.gadgets[start:end] = new_gadgets
        elif first_type == last_type == PauliType.Y and gate.type == GateType.X_MINUS:
            self.gadgets[start:end] = new_gadgets
        else:
            self.gadgets[start:end] = [copy(gate), *new_gadgets, copy(gate.inverse)]

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
                elif gadget.type == GateType.CX:
                    layer.add_cx_gadget(gadget) if gadget.as_gadget else layer.add_cx(gadget)
                elif gadget.type == GateType.CZ:
                    layer.add_cz_gadget(gadget) if gadget.as_gadget else layer.add_cz(gadget)
                elif gadget.type == GateType.H:
                    layer.add_single_gate(gadget)
                elif isinstance(gadget, SingleQubitGate):
                    layer.add_gadget(Gadget.from_single(gadget)) if gadget.as_gadget else layer.add_single_gate(gadget)
            circuit.compose(layer)
        return circuit

    def cancel_gadgets(self, gadgets: Optional[list] = None) -> list:
        """Needs work. Use __add__() to do this"""
        # return [key for key, group in groupby(gadgets if gadgets else self.gadgets) if len(list(group)) % 2]
        return gadgets if gadgets else self.gadgets

    def cancel_cnots(self):
        pass

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

    def draw(self, labels=False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

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
        gadgets = []
        for gadget in circuit_dict['gadgets']:
            name = next(iter(gadget))
            assert name in GateType.NAMES
            gadgets.append(eval(name)(**gadget[name]))
        return cls(gadgets=gadgets, num_qubits=circuit_dict.get('num_qubits'))
