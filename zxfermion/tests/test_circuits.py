import pytest

from zxfermion.gadgets import Gadget
from zxfermion.circuits import GadgetCircuit
from zxfermion.types import GateType


# you need way more test cases
# test tikz output
# test matrix()


def test_gadgetcircuit():
    gadgets = [Gadget(pauli_string='XYZ')]
    circuit = GadgetCircuit(gadgets)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.gadgets == gadgets
    assert circuit.num_qubits == 3

    gadgets = [Gadget(pauli_string='XYZ'), Gadget(pauli_string='IYXZ'), Gadget(pauli_string='ZYX')]
    circuit = GadgetCircuit(gadgets)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.gadgets == gadgets
    assert circuit.num_qubits == 4


def test_add_gadgetcircuit():
    circuit1 = GadgetCircuit([Gadget(pauli_string='XYZ')])
    circuit2 = GadgetCircuit([Gadget(pauli_string='ZYX')])
    circuit = circuit1 + circuit2
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 3
    assert len(circuit.gadgets) == 2


def test_add_incompatible_gadgetcircuit():
    circuit1 = GadgetCircuit([Gadget(pauli_string='XYZ')])
    circuit2 = GadgetCircuit([Gadget(pauli_string='IZYX')])

    with pytest.raises(AssertionError):
        circuit1 + circuit2


def test_stack_gadgets():
    pass


def test_gadgetcircuit_draw():
    pass
