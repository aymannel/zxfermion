from __future__ import annotations

from copy import deepcopy, copy
from typing import Optional

import pyzx as zx
from IPython.display import display, Markdown

from zxfermion.gates import Gadget, SingleQubitGate
from zxfermion.graph import GadgetGraph
from zxfermion.tableau import Tableau
from zxfermion.types import GateType
from zxfermion.utilities import matrix_to_latex


# phase out stack gadget / layer stuff
# impl add() method that takes gate as input and adds to gadgets. maybe. isn't GadgetCircuit supposed to be immutable?


class GadgetCircuit:
    def __init__(self, gates: list[Gadget], num_qubits: Optional[int] = 0):
        self.type = GateType.GADGET_CIRCUIT
        self.gates = deepcopy(gates)
        self.num_qubits = max(num_qubits, max([gadget.max_qubit for gadget in self.gates]) + 1)

    def __add__(self, other: GadgetCircuit) -> GadgetCircuit:
        assert self.num_qubits == other.num_qubits
        return GadgetCircuit(gates=self.simplify(self.gates + other.gates))

    def apply(self, gate, start: int = 0, end: int = None):
        assert gate.max_qubit < self.num_qubits
        end = len(self.gates) if end is None else end
        tableau = Tableau(gate)
        new_gadgets = [
            tableau(gadget)
            if gadget.type == GateType.GADGET else gadget
            for gadget in self.gates[start:end]]
        self.gates[start:end] = [copy(gate), *new_gadgets, copy(gate.inverse)]

    def graph(self, gadgets_only=None, expand_gadgets=None) -> GadgetGraph:
        circuit = GadgetGraph(num_qubits=self.num_qubits)
        for gate in self.gates:
            if gate.type == GateType.GADGET:
                gate.expand_gadget = gate.expand_gadget if expand_gadgets is None else expand_gadgets
            else:
                gate.as_gadget = gate.as_gadget if gadgets_only is None else gadgets_only
            if gate.type == GateType.GADGET:
                circuit.add_expanded_gadget(gate) if gate.expand_gadget else circuit.add_gadget(gate)
            elif gate.type == GateType.CX:
                circuit.add_cx_gadget(gate) if gate.as_gadget else circuit.add_cx(gate)
            elif gate.type == GateType.CZ:
                circuit.add_cz_gadget(gate) if gate.as_gadget else circuit.add_cz(gate)
            elif gate.type == GateType.H:
                circuit.add(gate)
            elif isinstance(gate, SingleQubitGate):
                circuit.add_gadget(Gadget.from_single(gate)) if gate.as_gadget else circuit.add(gate)
        return circuit

    def simplify(self, gates: Optional[list] = None) -> list:
        """Needs work. Use __add__ methods to do this"""
        # return [key for key, group in groupby(gates if gates else self.gates) if len(list(group)) % 2]
        return gates if gates else self.gates

    def matrix(self, return_latex=False, override_max=False):  # use pyzx matrix_to_latex() method here
        if self.num_qubits <= 5 or override_max:
            matrix = self.graph(expand_gadgets=False, gadgets_only=False).to_matrix()
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
