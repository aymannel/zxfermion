from zxfermion.exceptions import IncompatibleQubitDimension, IncompatibleAdditionType
from zxfermion.gadget import Gadget, GadgetCircuit
from zxfermion.types import GateType


def test_instantiate_gadgetcircuit():
    # assert graph
    # assert hub node
    # assert phase node
    # assert legs
    pass


def test_incompatible_num_qubits():
    try:
        GadgetCircuit([Gadget('YYXXII'), Gadget('XXYY')], num_qubits=6)
    except IncompatibleQubitDimension:
        pass


def test_add_gadgetcircuit_gadget():
    gadget = Gadget('XXIIYY')
    gadget_circuit = GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')], num_qubits=6)
    circuit = gadget_circuit + gadget
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 6
    assert len(circuit.gadgets) == 3
    assert circuit.graph().depth() == 10


def test_add_gadgetcircuit_gadgetcircuit():
    circuit1 = GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')], num_qubits=6)
    circuit2 = GadgetCircuit([Gadget('YYIIXX'), Gadget('XXIIYY')], num_qubits=6)
    circuit = circuit1 + circuit2
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 6
    assert len(circuit.gadgets) == 4
    assert circuit.graph().depth() == 13


def test_add_gadgetcircuit_incompatible():
    try:
        GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')], num_qubits=6) + None
    except IncompatibleAdditionType:
        pass


def test_add_gadgetcircuit_gadget_incompatible_qubits():
    try:
        GadgetCircuit([Gadget('IIXXYY')], num_qubits=6) + Gadget('YYXX')
    except IncompatibleQubitDimension:
        pass


def test_add_gadgetcircuit_gadgetcircuit_incompatible_qubits():
    try:
        GadgetCircuit([Gadget('IIXXYY')], num_qubits=6) + GadgetCircuit([Gadget('YYXX')], num_qubits=4)
    except IncompatibleQubitDimension:
        pass


def test_surround_x():
    pass


def test_surround_z():
    pass


def test_surround_cx():
    pass


def test_surround_cz():
    pass
