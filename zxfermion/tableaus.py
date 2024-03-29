from copy import deepcopy
import cirq

from zxfermion.gadgets import Gadget
from zxfermion.types import LegType, GateType
from zxfermion.clifford_tableau import CliffordTableau


class Tableau:
    def __init__(self, gate):
        self.gate = gate
        self.line_qubits = cirq.LineQubit.range(max(gate.qubits) + 1)
        self.tableau = self.build_tableau()

    def build_tableau(self):
        cirq_gate = {
            GateType.CX: cirq.CNOT,
            GateType.CZ: cirq.CZ,
        }[self.gate.type]
        circuit = cirq.Circuit(cirq_gate(*[self.line_qubits[qubit] for qubit in self.gate.qubits]))
        return CliffordTableau(circuit)

    def apply_tableau(self, gadget: Gadget) -> Gadget:
        cirq_map = {
                LegType.I: cirq.I,
                LegType.X: cirq.X,
                LegType.Y: cirq.Y,
                LegType.Z: cirq.Z,
            }

        pauli_string = cirq.PauliString(gadget.phase, {
            qubit: cirq_map[gadget.legs.get(qubit.x, LegType.I)]
            for qubit in self.line_qubits
        })

        pauli_string = self.tableau(pauli_string)
        cirq_map_inverse = {v: k for k, v in cirq_map.items()}
        cirq_dict = {qubit: pauli_string.get(self.line_qubits[qubit]) for qubit in self.gate.qubits}

        new_gadget = deepcopy(gadget)
        new_gadget.phase = pauli_string.coefficient.real
        new_gadget.legs.update({
            qubit: cirq_map_inverse.get(pauli)
            if pauli else LegType.I
            for qubit, pauli in cirq_dict.items()
        })
        return new_gadget
