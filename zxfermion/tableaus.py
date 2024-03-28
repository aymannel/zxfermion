from collections import OrderedDict
from copy import deepcopy

import cirq

from zxfermion.clifford_tableau import CliffordTableau
from zxfermion.commutations import cx_rules, x_rules, z_rules, cz_rules, x_plus_rules, z_plus_rules
from zxfermion.exceptions import IncompatibleGatesException
from zxfermion.gadgets import PauliGate, CliffordGate, Gadget, X, Z, ControlledGate, SingleQubitGate
from zxfermion.types import LegType, GateType


class Tableau:
    def __init__(self, gate):
        self.gate = gate
        self.line_qubits = cirq.LineQubit.range(len(gate.qubits))
        if gate.type == GateType.CX:
            cirq_gate = cirq.CNOT(*self.line_qubits)
        elif gate.type == GateType.CZ:
            cirq_gate = cirq.CZ(*self.line_qubits)
        self.tableau = CliffordTableau(cirq.Circuit(cirq_gate))

    def apply(self, gadget: Gadget) -> Gadget:
        gadget = deepcopy(gadget)
        paulis = cirq.I(self.line_qubits[0])
        for qubit, line_qubit in zip(self.gate.qubits, self.line_qubits):
            pauli = gadget.legs.get(qubit, LegType.I)
            if pauli == LegType.X:
                paulis *= cirq.X(line_qubit)
            elif pauli == LegType.Y:
                paulis *= cirq.Y(line_qubit)
            elif pauli == LegType.Z:
                paulis *= cirq.Z(line_qubit)

        gadget.legs.update({
            qubit: LegType(str(pauli)) if pauli else LegType.I
            for qubit, pauli in zip(self.gate.qubits, [self.tableau(paulis).get(qubit) for qubit in self.line_qubits])})
        return gadget

        # if self.gate.type == GateType.CX:
        #     pauli_dict = self.apply_cx(paulis)
        # elif self.gate.type == GateType.CZ:
        #     return self.apply_cz(paulis)
        # elif self.gate.type == GateType.X_PLUS:
        #     return self.apply_xplus(paulis, phase)
        # elif self.gate.type == GateType.Z_PLUS:
        #     return self.apply_zplus(paulis, phase)
        # gadget.legs.update(pauli_dict)
        # return gadget

    def apply_single(self, gadget: Gadget, rules: dict):
        self.gate: SingleQubitGate
        gadget.legs[self.gate.qubit], gadget.phase = rules[(gadget.legs.get(self.gate.qubit, LegType.I))]
        return gadget

    def apply_controlled_gate(self, gadget: Gadget, rules: dict):
        self.gate: ControlledGate
        control, target = self.gate.control, self.gate.target
        gadget.legs[control], gadget.legs[target] = rules[(
            gadget.legs.get(control, LegType.I),
            gadget.legs.get(target, LegType.I))]
        return gadget

    def apply_cx(self, gadget: Gadget) -> Gadget:
        return self.apply_controlled_gate(gadget, cx_rules)

    def apply_cz(self, gadget: Gadget) -> Gadget:
        return self.apply_controlled_gate(gadget, cz_rules)

    def apply_xplus(self, gadget: Gadget) -> Gadget:
        return self.apply_single(gadget, x_plus_rules)

    def apply_zplus(self, gadget: Gadget) -> Gadget:
        return self.apply_single(gadget, z_plus_rules)


class PauliTableau:
    def __init__(self, gate: PauliGate):
        self.gate = gate

    def apply(self, gadget: Gadget) -> Gadget:
        new_gadget = deepcopy(gadget)
        if isinstance(self.gate, X):
            pauli = new_gadget.legs.get(self.gate.qubit, LegType.I)
            new_gadget.legs[self.gate.qubit] = x_rules[pauli]
            return gadget
        elif isinstance(self.gate, Z):
            pauli = new_gadget.legs.get(self.gate.qubit, LegType.I)
            new_gadget.legs[self.gate.qubit] = z_rules[pauli]
            return gadget

