from copy import deepcopy
import cirq

from zxfermion.gadgets import Gadget
from zxfermion.types import PauliType, GateType
from zxfermion.clifford_tableau import CliffordTableau


class Tableau:
    def __init__(self, gate):
        self.gate = gate
        self.line_qubits = cirq.LineQubit.range(max(gate.qubits) + 1)
        self.tableau = self.build_tableau()

    def build_tableau(self):
        cirq_gate = {GateType.CX: cirq.CNOT, GateType.CZ: cirq.CZ, GateType.H: cirq.H}[self.gate.type]
        circuit = cirq.Circuit(cirq_gate(*[self.line_qubits[qubit] for qubit in self.gate.qubits]))
        return CliffordTableau(circuit)

    def __call__(self, gadget: Gadget) -> Gadget:
        pauli_map = {PauliType.I: cirq.I, PauliType.X: cirq.X, PauliType.Y: cirq.Y, PauliType.Z: cirq.Z}
        inverse_pauli_map = {v: k for k, v in pauli_map.items()}

        paulis = {qubit: pauli_map[gadget.paulis.get(qubit.x, PauliType.I)] for qubit in self.line_qubits}
        pauli_string = self.tableau(cirq.PauliString(gadget.phase, paulis))
        cirq_dict = {qubit: pauli_string.get(self.line_qubits[qubit]) for qubit in self.gate.qubits}

        new_gadget = deepcopy(gadget)
        new_gadget.phase = pauli_string.coefficient.real
        new_gadget.paulis.update({
            qubit: inverse_pauli_map.get(pauli)
            if pauli else PauliType.I
            for qubit, pauli in cirq_dict.items()})
        return new_gadget

        # return Gadget.from_paulis({
        #     qubit: inverse_pauli_map.get(pauli)
        #     if pauli else PauliType.I
        #     for qubit, pauli in cirq_dict.items()
        # }, pauli_string.coefficient.real)
