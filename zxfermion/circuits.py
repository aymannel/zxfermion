from __future__ import annotations

from copy import deepcopy, copy
from itertools import groupby
from typing import Optional

import pyzx as zx
from IPython.display import display, Markdown

from zxfermion import config
from zxfermion.gates import Gadget, SingleQubitGate, FixedPhaseGate
from zxfermion.graph import GadgetGraph
from zxfermion.tableau import Tableau
from zxfermion.types import GateType, PauliType
from zxfermion.utilities import matrix_to_latex


class GadgetCircuit:
    def __init__(self, gates: list[Gadget], num_qubits: Optional[int] = 0):
        self.type = GateType.GADGET_CIRCUIT
        self.gates = deepcopy(gates)
        self.num_qubits = max(num_qubits, max([gadget.max_qubit for gadget in self.gates]) + 1)

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gates=self.cancel_gates(self.gates + other.gates))

    def apply(self, gate, start: int = 0, end: int = None):
        assert gate.max_qubit < self.num_qubits
        end = len(self.gates) if end is None else end

        tableau = Tableau(gate)
        new_gadgets = [
            tableau(gadget)
            if gadget.type == GateType.GADGET else gadget
            for gadget in self.gates[start:end]
        ]

        self.gates[start:end] = [copy(gate), *new_gadgets, copy(gate.inverse)]

    def graph(self, gadgets_only=None, stack_gates=None, expand_gadgets=None) -> GadgetGraph:
        stack_gates = stack_gates if stack_gates is not None else config.stack_gadgets
        gate_layers = self.stack_gates() if stack_gates else [[gadget] for gadget in self.gates]
        circuit = GadgetGraph(num_qubits=self.num_qubits)
        for gate_layer in gate_layers:
            layer = GadgetGraph(num_qubits=self.num_qubits)
            for gadget in gate_layer:
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
                    layer.add_single_qubit_gate(gadget)
                elif isinstance(gadget, SingleQubitGate):
                    layer.add_gadget(Gadget.from_single(gadget)) if gadget.as_gadget else layer.add_single_qubit_gate(gadget)
            circuit.compose(layer)
        return circuit

    def cancel_gates(self, gates: Optional[list] = None) -> list:
        """Needs work. Use __add__() to do this"""
        # return [key for key, group in groupby(gates if gates else self.gates) if len(list(group)) % 2]
        return gates if gates else self.gates

    def cancel_cnots(self):
        pass

    def stack_gates(self, gates: Optional[list] = None) -> list[list]:
        layers = []
        for gadget in gates if gates else self.cancel_gates():
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
            matrix = self.graph(expand_gadgets=False, gadgets_only=False, stack_gates=False).to_matrix()
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
