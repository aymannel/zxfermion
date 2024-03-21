from zxfermion.exceptions import IncompatibleQubitDimension, IncompatibleType
from zxfermion.gadgets import Gadget
from zxfermion.circuits import GadgetCircuit
from zxfermion.types import GateType


def test_instantiate_gadgetcircuit():
    # assert graph
    # assert hub node
    # assert phase node
    # assert legs
    pass


# test num qubits asserts max gadget dimension


def test_incompatible_num_qubits():
    try:
        GadgetCircuit([Gadget('YYXXII'), Gadget('XXYY')])
    except IncompatibleQubitDimension:
        pass


def test_add_gadgetcircuit_gadget():
    gadget = Gadget('XXIIYY')
    gadget_circuit = GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')])
    circuit = gadget_circuit + gadget
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 6
    assert len(circuit.gadgets) == 3
    assert circuit.graph().depth() == 10


def test_add_gadgetcircuit_gadgetcircuit():
    circuit1 = GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')])
    circuit2 = GadgetCircuit([Gadget('YYIIXX'), Gadget('XXIIYY')])
    circuit = circuit1 + circuit2
    assert isinstance(circuit, GadgetCircuit)
    assert circuit.type == GateType.GADGET_CIRCUIT
    assert circuit.num_qubits == 6
    assert len(circuit.gadgets) == 4
    assert circuit.graph().depth() == 13


def test_add_gadgetcircuit_incompatible():
    try:
        GadgetCircuit([Gadget('YYXXII'), Gadget('IIXXYY')]) + None
    except IncompatibleType:
        pass


def test_add_gadgetcircuit_gadget_incompatible_qubits():
    try:
        GadgetCircuit([Gadget('IIXXYY')]) + Gadget('YYXX')
    except IncompatibleQubitDimension:
        pass


def test_add_gadgetcircuit_gadgetcircuit_incompatible_qubits():
    try:
        GadgetCircuit([Gadget('IIXXYY')]) + GadgetCircuit([Gadget('YYXX')])
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
