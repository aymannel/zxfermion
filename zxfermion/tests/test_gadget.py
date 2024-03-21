import pytest
from zxfermion.exceptions import IncompatibleType, IncompatibleQubitDimension
from zxfermion.gadgets import Gadget
from zxfermion.circuits import GadgetCircuit
from zxfermion.types import GateType, VertexType


# test graphing individual gadget

@pytest.mark.parametrize(['pauli_str', 'phase', 'num_qubits'], [['YIXYIIYX', 1/2, 8], ['YYIIYX', -1/2, 6]])
def test_gadget(pauli_str, phase, num_qubits):
    gadget = Gadget(pauli_str=pauli_str, phase=phase, num_qubits=num_qubits)
    assert gadget.phase == phase
    assert gadget.type == GateType.GADGET
    assert gadget.num_qubits == num_qubits

    assert gadget.hub_node
    assert gadget.phase_node
    assert not gadget.hub_node.phase
    assert gadget.phase_node.phase == phase
    assert gadget.hub_node.type == VertexType.X
    assert gadget.phase_node.type == VertexType.Z
    assert len(gadget.legs.values()) == num_qubits
    assert all([leg.type == pauli for leg, pauli in zip(gadget.legs.values(), list(pauli_str))])
    assert gadget.graph(num_qubits=num_qubits).depth() == 4


@pytest.mark.parametrize('pauli_str', ['YIXYIIYX', 'YYYYXXXX', 'ZZZIIIXXX', 'IIII'])
def test_gadget_from_defaults(pauli_str):
    gadget = Gadget(pauli_str=pauli_str)
    assert not gadget.phase
    assert gadget.type == GateType.GADGET
    assert gadget.num_qubits == len(pauli_str)

    assert gadget.hub_node
    assert gadget.phase_node
    assert not gadget.hub_node.phase
    assert not gadget.phase_node.phase
    assert gadget.hub_node.type == VertexType.X
    assert gadget.phase_node.type == VertexType.Z
    assert len(gadget.legs.values()) == gadget.num_qubits
    assert all([leg.type == pauli for leg, pauli in zip(gadget.legs.values(), list(pauli_str))])
    assert gadget.graph(num_qubits=len(pauli_str)).depth() == 4


def test_incompatible_num_qubits():
    try:
        Gadget(pauli_str='XYXYX', num_qubits=4)
    except IncompatibleQubitDimension as error:
        assert str(error) == 'Length of Pauli string differs from specified number of qubits.'


def test_add_gadget_gadget():
    circuit = Gadget('IIXXYY') + Gadget('YYXXII')
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 6
    assert len(circuit.gadgets) == 2
    assert circuit.graph().depth() == 7


def test_add_gadget_gadgetcircuit():
    gadget = Gadget('XXIIYY')
    gadget_circuit = GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')], num_qubits=6)
    circuit = gadget + gadget_circuit
    print(gadget_circuit.gadgets)
    print(circuit.gadgets)
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 6
    assert len(circuit.gadgets) == 3
    assert circuit.graph().depth() == 10


def test_add_gadget_incompatible():
    try:
        Gadget('IIXXYY') + None
    except IncompatibleType:
        pass


def test_add_gadget_gadget_incompatible_qubits():
    try:
        Gadget('IIXXYY') + Gadget('YYXX')
    except IncompatibleQubitDimension:
        pass


def test_add_gadget_gadgetcircuit_incompatible_qubits():
    try:
        Gadget('YYXX') + GadgetCircuit([Gadget('IIXXYY')], num_qubits=6)
    except IncompatibleQubitDimension:
        pass


def test_conjugate_x():
    pass


def test_conjugate_z():
    pass


def test_conjugate_cx():
    pass


def test_conjugate_cz():
    pass
