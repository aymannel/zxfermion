from copy import deepcopy

from zxfermion.commutations import cx_rules, cz_rules, cliff_x_rules, x_rules, z_rules, cliff_x_minus_rules, \
    cliff_z_rules, cliff_z_minus_rules
from zxfermion.gadgets import PauliGate, CliffordGate, Gadget, CX, CZ, XPlus, X, Z, ZPlus, XMinus, ZMinus
from zxfermion.types import LegType


class CliffordTableau:
    def __init__(self, gate: CliffordGate):
        self.gate = gate

    def apply(self, gadget: Gadget) -> Gadget:
        new_gadget = deepcopy(gadget)
        if isinstance(self.gate, CX):
            pauli_control = new_gadget.legs.get(self.gate.control, LegType.I)
            pauli_target = new_gadget.legs.get(self.gate.target, LegType.I)
            pauli_control, pauli_target = cx_rules[(pauli_control, pauli_target)]
            new_gadget.legs[self.gate.control] = pauli_control
            new_gadget.legs[self.gate.target] = pauli_target
            return new_gadget
        elif isinstance(self.gate, CZ):
            pauli_control = new_gadget.legs.get(self.gate.control, LegType.I)
            pauli_target = new_gadget.legs.get(self.gate.target, LegType.I)
            pauli_control, pauli_target = cz_rules[(pauli_control, pauli_target)]
            new_gadget.legs[self.gate.control] = pauli_control
            new_gadget.legs[self.gate.target] = pauli_target
            return new_gadget
        elif isinstance(self.gate, XPlus):
            pauli = new_gadget.legs.get(self.gate.qubit, LegType.I)
            new_gadget.legs[self.gate.qubit] = cliff_x_rules[pauli]
            return new_gadget
        elif isinstance(self.gate, ZPlus):
            pauli = new_gadget.legs.get(self.gate.qubit, LegType.I)
            new_gadget.legs[self.gate.qubit] = cliff_z_rules[pauli]
            return new_gadget
        elif isinstance(self.gate, XMinus):
            pauli = new_gadget.legs.get(self.gate.qubit, LegType.I)
            new_gadget.legs[self.gate.qubit] = cliff_x_minus_rules[pauli]
            return new_gadget
        elif isinstance(self.gate, ZMinus):
            pauli = new_gadget.legs.get(self.gate.qubit, LegType.I)
            new_gadget.legs[self.gate.qubit] = cliff_z_minus_rules[pauli]
            return new_gadget
        else:
            return gadget


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

