from __future__ import annotations

import re
from copy import deepcopy
from typing import Optional
from itertools import groupby
from IPython.display import display, Markdown

import pyzx as zx
from zxfermion import config
from zxfermion.types import GateType
from zxfermion.gadgets import Gadget
from zxfermion.graph import BaseGraph
from zxfermion.utilities import matrix_to_latex


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget]):
        self.type = GateType.GADGET_CIRCUIT
        self.gadgets = deepcopy(gadgets)
        self.num_qubits = max([gadget.max_qubit for gadget in self.gadgets]) + 1

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gadgets=self.cancel_gadgets(self.gadgets + other.gadgets))

    def draw(self, labels=False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, gadgets_only=None, stack_gadgets=None, expand_gadgets=None) -> BaseGraph:
        stack_gadgets = stack_gadgets if stack_gadgets is not None else config.stack_gadgets
        gadget_layers = self.stack_gadgets() if stack_gadgets else [[gadget] for gadget in self.gadgets]
        circuit = BaseGraph(num_qubits=self.num_qubits)
        for gadget_layer in gadget_layers:
            layer = BaseGraph(num_qubits=self.num_qubits)
            for gadget in gadget_layer:

                if gadget.type == GateType.GADGET:
                    gadget.expand_gadget = expand_gadgets if expand_gadgets is not None else gadget.expand_gadget
                else:
                    gadget.as_gadget = gadgets_only if gadgets_only is not None else gadget.as_gadget

                if gadget.type == GateType.GADGET:
                    layer.add_expanded_gadget(gadget) if gadget.expand_gadget else layer.add_gadget(gadget)
                elif gadget.type == GateType.X_PHASE:
                    layer.add_single_gate(gadget)
                elif gadget.type == GateType.Z_PHASE:
                    layer.add_single_gate(gadget)
                elif gadget.type == GateType.X:
                    layer.add_x_gadget(gadget) if gadget.as_gadget else layer.add_single_gate(gadget)
                elif gadget.type == GateType.Z:
                    layer.add_z_gadget(gadget) if gadget.as_gadget else layer.add_single_gate(gadget)
                elif gadget.type == GateType.H:
                    layer.add_single_gate(gadget)
                elif gadget.type == GateType.CX:
                    layer.add_cx_gadget(gadget) if gadget.as_gadget else layer.add_cx(gadget)
                elif gadget.type == GateType.CZ:
                    layer.add_cz_gadget(gadget) if gadget.as_gadget else layer.add_cz(gadget)
                elif gadget.type == GateType.X_PLUS:
                    layer.add_single_gate(gadget)
                elif gadget.type == GateType.Z_PLUS:
                    layer.add_single_gate(gadget)
                elif gadget.type == GateType.X_MINUS:
                    layer.add_single_gate(gadget)
                elif gadget.type == GateType.Z_MINUS:
                    layer.add_single_gate(gadget)
            circuit.compose(layer)
        return circuit

    def cancel_gadgets(self, gadgets: Optional[list] = None) -> list:
        return [key for key, group in groupby(gadgets if gadgets else self.gadgets) if len(list(group)) % 2]

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

    def tikz(self, name: str, **kwargs):
        graph = self.graph(**kwargs)
        pattern = rf'\[style=Z phase dot\]\s*\((\d+)\)\s*at\s*\((.*?),\s*-{self.num_qubits + 2}\.00\)\s*{{\$(.*?)\$}};'
        content = '\n'.join([
            line.replace(r'\pi', r'\theta')
            if re.search(pattern, line) else line
            for line in graph.to_tikz().splitlines()
        ])

        labels = {r'$\frac{\pi}{2}$': r'$+$', r'$\frac{3\pi}{2}$': r'$-$'}
        from zxfermion.config import tikz_types
        for key in labels:
            content = content.replace(f'{key}', f'{labels[key]}')
        for key in tikz_types:
            content = content.replace(f'style={key}', f'style={tikz_types[key]}')
        with open(f'{name}.tikz', 'w') as file:
            file.write(content)

    def matrix(self, return_latex=False, override_max=False):
        if self.num_qubits <= 5 or override_max:
            matrix = self.graph(expand_gadgets=False, gadgets_only=False, stack_gadgets=False).to_matrix()
            latex_string = matrix_to_latex(matrix)
            display(Markdown(latex_string))
            return latex_string if return_latex else None
        else:
            print(f'{2 ** self.num_qubits} x {2 ** self.num_qubits} matrix too large to compute.')
