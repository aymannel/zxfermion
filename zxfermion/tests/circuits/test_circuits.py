import pytest
from zxfermion.types import GateType
from zxfermion.gates.gates import Gadget
from zxfermion.circuits.gadget_circuit import GadgetCircuit


# test num_qubits > max(gadget.num_qubits...) vs num_qubits < max(gadget.num_qubits...)


def test_circuit():
    gates = [Gadget(pauli_string='XYZ')]
    circuit = GadgetCircuit(gates)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.gates == gates
    assert circuit.num_qubits == 3

    gates = [Gadget(pauli_string='XYZ'), Gadget(pauli_string='IYXZ'), Gadget(pauli_string='ZYX')]
    circuit = GadgetCircuit(gates)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.gates == gates
    assert circuit.num_qubits == 4


def test_add_circuits():
    circuit1 = GadgetCircuit([Gadget(pauli_string='XYZ')])
    circuit2 = GadgetCircuit([Gadget(pauli_string='ZYX')])
    circuit = circuit1 + circuit2
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 3
    assert len(circuit.gates) == 2


def test_add_incompatible_circuits():
    circuit1 = GadgetCircuit([Gadget(pauli_string='XYZ')])
    circuit2 = GadgetCircuit([Gadget(pauli_string='IZYX')])
    with pytest.raises(AssertionError):
        circuit1 + circuit2


def test_stack_gates():
    pass


def test_circuit_draw():
    pass


def test_circuit_tikz():
    pass


def test_circuit_matrix():
    pass
