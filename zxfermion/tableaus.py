from copy import deepcopy

import stim
from zxfermion.gadgets import Gadget
from zxfermion.types import PauliType, GateType


class Tableau:
    def __init__(self, gate):
        self.gate = gate
        self.tableau = stim.Tableau.from_named_gate({
            GateType.X: 'X',
            GateType.Z: 'Z',
            GateType.CX: 'CNOT',
            GateType.CZ: 'CZ',
            GateType.H: 'H',
            GateType.X_PLUS: 'SQRT_X_DAG',
            GateType.Z_PLUS: 'SQRT_Z_DAG',
            GateType.X_MINUS: 'SQRT_X',
            GateType.Z_MINUS: 'SQRT_Z',
        }.get(gate.type))

    def __call__(self, gadget: Gadget) -> Gadget:
        gadget = deepcopy(gadget)
        qubits = self.gate.qubits
        stim_result = self.tableau(stim.PauliString([gadget.paulis.get(qubit, 'I') for qubit in qubits]))
        pauli_string = str(stim_result)[1:].replace('_', 'I')
        gadget.paulis.update({qubit: PauliType(pauli) for qubit, pauli in zip(qubits, pauli_string)})
        return Gadget(gadget.pauli_string, stim_result.sign.real * gadget.phase)
