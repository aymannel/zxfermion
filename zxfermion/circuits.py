from __future__ import annotations

import json
from random import getrandbits

import numpy as np
import pyzx as zx
from copy import deepcopy
from typing import Optional
from itertools import groupby

from IPython.display import display, Markdown

from zxfermion.config import mapping
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

    def matrix(self, return_latex = False):
        latex_str = r'\begin{pmatrix}'
        for row in self.graph().to_matrix():
            for elem in row:
                real_part = np.real(elem)
                imag_part = np.imag(elem)
                if np.isclose(imag_part, 0):
                    latex_str += f'{real_part:.0f}'
                elif np.isclose(real_part, 0):
                    latex_str += f'{imag_part:.0f}i'
                else:
                    latex_str += f'({real_part:.0f}{"+" if imag_part > 0 else ""}{imag_part:.0f}i)'
                latex_str += ' & '
            latex_str = latex_str[:-2] + r'\\'
        latex_str = latex_str[:-2] + r'\end{pmatrix}'
        display(Markdown(latex_str))
        return latex_str if return_latex else None

    def fuse_gadgets(self, gadgets: Optional[list] = None) -> list:
        return [key for key, group in groupby(gadgets if gadgets else self.gadgets) if len(list(group)) % 2]

    def stack_gadgets(self, gadgets: Optional[list] = None) -> list[list]:
        layers = []
        for gadget in gadgets if gadgets else self.fuse_gadgets():
            placed = False
            for layer in layers:
                if all(gadget.max_qubit < other.min_qubit or gadget.min_qubit > other.max_qubit for other in layer):
                    layer.append(gadget)
                    placed = True
                    break
            if not placed:
                layers.append([gadget])
        return layers

    def draw(self, labels = False, **kwargs):
        zx.draw(self.graph(**kwargs), labels=labels)

    def graph(self, gadgets_only: bool = False, stack: bool = True, expand: bool = False) -> BaseGraph:
        gadget_layers = self.stack_gadgets() if stack else [[gadget] for gadget in self.gadgets]

        circuit = BaseGraph(num_qubits=self.num_qubits)
        for gadget_layer in gadget_layers:
            layer = BaseGraph(num_qubits=self.num_qubits)
            for gadget in gadget_layer:
                if gadget.type == GateType.GADGET:
                    layer.add_expanded_gadget(gadget) if expand else layer.add_gadget(gadget)
                elif gadget.type == GateType.CX:
                    layer.add_cx_gadget(gadget) if gadgets_only else layer.add_cx(gadget)
                elif gadget.type == GateType.CZ:
                    layer.add_cz_gadget(gadget) if gadgets_only else layer.add_cz(gadget)
                elif gadget.type == GateType.X:
                    layer.add_x_gadget(gadget) if gadgets_only else layer.add_node(gadget)
                elif gadget.type == GateType.Z:
                    layer.add_z_gadget(gadget) if gadgets_only else layer.add_node(gadget)
            circuit.compose(layer)
        return circuit

    def to_tikz(self, name: str, **kwargs):
        content = self.graph(**kwargs).to_tikz()
        labels = {
            r'$\frac{\pi}{2}$': r'$+$',
            r'$\frac{3\pi}{2}$': r'$-$',
        }
        for key in mapping:
            content = content.replace(f'style={key}', f'style={mapping[key]}')
        for key in labels:
            content = content.replace(f'{key}', f'{labels[key]}')
        with open(f'{name}.tikz', 'w') as file:
            file.write(content)
