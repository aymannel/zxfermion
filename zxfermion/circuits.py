from __future__ import annotations

from copy import deepcopy
from itertools import groupby
from typing import Optional

import pyzx as zx

from zxfermion.exceptions import IncompatibleQubitDimension, IncompatibleType
from zxfermion.gadgets import Gadget, CX, CZ
from zxfermion.gates import X, Z
from zxfermion.graph import BaseGraph
from zxfermion.tableau import Tableau
from zxfermion.types import GateType, LegType


class GadgetCircuit:
    def __init__(self, gadgets: list[Gadget]):
        self.num_qubits = max([gadget.num_qubits for gadget in gadgets]) + 1
        self.num_qubits = 6
        self.type = GateType.GADGET_CIRCUIT
        self.gadgets = [key for key, group in groupby(deepcopy(gadgets)) if len(list(group)) % 2]

    def __add__(self, other: Gadget | GadgetCircuit) -> GadgetCircuit:
        try:
            assert hasattr(other, 'type')
            if (is_gadget := (other.type == GateType.GADGET)) or other.type == GateType.GADGET_CIRCUIT:
                try:
                    assert self.num_qubits == other.num_qubits
                    gadget_list = self.gadgets + [other] if is_gadget else self.gadgets + other.gadgets
                    gadgets = [key for key, group in groupby(gadget_list) if len(list(group)) % 2]
                    return GadgetCircuit(gadgets=gadgets)
                except AssertionError:
                    raise IncompatibleQubitDimension(f'{self.num_qubits} and {other.num_qubits}')
            else:
                raise IncompatibleType(f'Cannot add GadgetCircuit and {type(other)}')
        except AssertionError:
            raise IncompatibleType(f'Cannot add GadgetCircuit and {type(other)}')

    def swap(self, start: int, finish: int):
        self.gadgets[start], self.gadgets[finish] = Tableau(self.gadgets[start], self.gadgets[finish])

    def surround_cx(
            self,
            control: int,
            target: int,
            left: Optional[int] = None,
            right: Optional[int] = None,
            draw: Optional[bool] = True
    ):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_cx(control=control, target=target)
        self.gadgets.insert(left, CX(control=control, target=target))
        self.gadgets.insert(right, CX(control=control, target=target))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        if draw:
            self.draw()

    def surround_cz(
            self,
            control: int,
            target: int,
            left: Optional[int] = None,
            right: Optional[int] = None,
            draw: Optional[bool] = True
    ):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_cz(control=control, target=target)
        self.gadgets.insert(left, CZ(control=control, target=target))
        self.gadgets.insert(right, CZ(control=control, target=target))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        if draw:
            self.draw()

    def surround_x(self, qubit: int, left: Optional[int] = None, right: Optional[int] = None):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_x(qubit=qubit)
        self.gadgets.insert(left, X(qubit=qubit))
        self.gadgets.insert(right, X(qubit=qubit))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        self.draw()

    def surround_z(self, qubit: int, left: Optional[int] = None, right: Optional[int] = None):
        left, right = left if left else 0, right if right else len(self.gadgets) + 1
        for gadget in self.gadgets[left:right - 1]:
            gadget.conjugate_z(qubit=qubit)
        self.gadgets.insert(left, Z(qubit=qubit))
        self.gadgets.insert(right, Z(qubit=qubit))
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        self.draw()

    def controlled_rotation(self, control_top: Optional[bool] = True, draw: Optional[bool] = False):
        qubits = [qubit for qubit, leg in self.gadgets[0].legs.items() if leg.type != LegType.I]
        if control_top:
            self.surround_cx(qubits[0], qubits[3], draw=False)
            self.surround_cx(qubits[0], qubits[2], draw=False)
            self.surround_cx(qubits[0], qubits[1], draw=draw)
        else:
            self.surround_cx(qubits[3], qubits[0], draw=False)
            self.surround_cx(qubits[3], qubits[1], draw=False)
            self.surround_cx(qubits[3], qubits[2], draw=draw)

    def graph(self) -> zx.Graph:
        self.gadgets = [key for key, group in groupby(self.gadgets) if len(list(group)) % 2]
        graph = BaseGraph(num_qubits=self.num_qubits)
        for gadget in self.gadgets:
            match gadget.type:
                case GateType.GADGET:
                    graph.add_gadget(gadget)
                case GateType.CX:
                    graph.add_cx_gadget(gadget)
                case GateType.CZ:
                    graph.add_cz_gadget(gadget)
        return graph

    def draw(self):
        zx.draw(self.graph())
