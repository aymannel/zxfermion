import pytest
from pyzx import VertexType, EdgeType

from zxfermion.gadgets import Gadget, CX, CZ, X, Z
from zxfermion.graph import BaseGraph
from zxfermion.types import GateType, LegType, GadgetLeg


def test_gadget():
    gadget = Gadget(pauli_str='XYZ')
    assert gadget.type == GateType.GADGET
    assert not gadget.phase
    assert len(gadget.legs) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert all(isinstance(leg, GadgetLeg) for leg in gadget.legs.values())


def test_gadget_phase():
    gadget = Gadget('XYZ', phase=1/2)
    assert gadget.type == GateType.GADGET
    assert gadget.phase == 1/2
    assert len(gadget.legs) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert all(isinstance(leg.type, LegType) for leg in gadget.legs.values())


def test_gadget_equality():
    gadget1 = Gadget(pauli_str='XYZ')
    gadget2 = Gadget(pauli_str='XYZ')
    gadget3 = Gadget(pauli_str='ZXY')
    gadget4 = Gadget(pauli_str='XYZ', phase=1/2)

    assert gadget1 == gadget2
    assert gadget1 != gadget3
    assert gadget1 != gadget4


def test_gadget_draw():
    gadget = Gadget(pauli_str='XYZ', phase=1/2)
    circuit = gadget.draw()
    assert isinstance(circuit, BaseGraph)
    assert circuit.num_qubits == gadget.max_qubit + 1
    assert circuit.num_vertices() == 15
    assert circuit.num_edges() == 14
    assert circuit.num_inputs() == 3
    assert circuit.num_outputs() == 3
    assert list(circuit.inputs()) == [0, 1, 2]
    assert list(circuit.outputs()) == [3, 4, 5]
    assert circuit.type(6) == VertexType.X
    assert circuit.type(7) == VertexType.Z
    assert circuit.type(8) == VertexType.H_BOX
    assert circuit.type(9) == VertexType.Z
    assert circuit.type(10) == VertexType.H_BOX
    assert circuit.type(11) == VertexType.X
    assert circuit.type(12) == VertexType.Z
    assert circuit.type(13) == VertexType.X
    assert circuit.type(14) == VertexType.Z
    assert circuit.phase(7) == 1/2


def test_cx():
    cx = CX(control=0, target=1)
    assert cx.type == GateType.CX
    assert cx.control == 0
    assert cx.target == 1
    assert cx.min_qubit == 0
    assert cx.max_qubit == 1

    with pytest.raises(AssertionError):
        CX(control=1, target=1)


def test_cx_equality():
    cx1 = CX(control=0, target=1)
    cx2 = CX(control=0, target=1)
    cx3 = CX(control=1, target=2)
    assert cx1 == cx2
    assert cx1 != cx3


def test_cx_draw():
    cx = CX(control=0, target=1)
    circuit = cx.draw()
    assert isinstance(circuit, BaseGraph)
    assert circuit.num_qubits == cx.max_qubit + 1
    assert circuit.num_vertices() == 6
    assert circuit.num_edges() == 5
    assert circuit.num_inputs() == 2
    assert circuit.num_outputs() == 2
    assert list(circuit.inputs()) == [0, 1]
    assert list(circuit.outputs()) == [2, 3]
    assert circuit.type(4) == VertexType.Z
    assert circuit.type(5) == VertexType.X


def test_cz():
    cz = CZ(control=0, target=1)
    assert cz.type == GateType.CZ
    assert cz.control == 0
    assert cz.target == 1
    assert cz.min_qubit == 0
    assert cz.max_qubit == 1

    with pytest.raises(AssertionError):
        CZ(control=1, target=1)


def test_cz_equality():
    cz1 = CZ(control=0, target=1)
    cz2 = CZ(control=0, target=1)
    cz3 = CZ(control=1, target=0)
    cz4 = CZ(control=1, target=2)
    assert cz1 == cz2
    assert cz1 == cz3
    assert cz1 != cz4


def test_cz_draw():
    cz = CZ(control=0, target=1)
    circuit = cz.draw()
    assert isinstance(circuit, BaseGraph)
    assert circuit.num_qubits == cz.max_qubit + 1
    assert circuit.num_vertices() == 6
    assert circuit.num_edges() == 5
    assert circuit.num_inputs() == 2
    assert circuit.num_outputs() == 2
    assert list(circuit.inputs()) == [0, 1]
    assert list(circuit.outputs()) == [2, 3]
    assert circuit.type(4) == VertexType.Z
    assert circuit.type(5) == VertexType.Z
    assert circuit.edge_type((4, 5)) == EdgeType.HADAMARD


def test_x():
    x = X(qubit=0)
    assert x.type == GateType.X
    assert x.phase == 1
    assert x.qubit == 0
    assert x.min_qubit == 0
    assert x.max_qubit == 0


def test_x_equality():
    x1 = X(qubit=0)
    x2 = X(qubit=0)
    x3 = X(qubit=1)
    assert x1 == x2
    assert x1 != x3


def test_x_draw():
    x = X(qubit=0)
    circuit = x.draw()
    assert isinstance(circuit, BaseGraph)
    assert circuit.num_qubits == 1
    assert circuit.num_vertices() == 3
    assert circuit.num_edges() == 2
    assert circuit.num_inputs() == 1
    assert circuit.num_outputs() == 1
    assert list(circuit.inputs()) == [0]
    assert list(circuit.outputs()) == [1]
    assert circuit.type(2) == VertexType.X
    assert circuit.phase(2) == 1


def test_z():
    z = Z(qubit=0)
    assert z.type == GateType.Z
    assert z.phase == 1
    assert z.qubit == 0
    assert z.min_qubit == 0
    assert z.max_qubit == 0


def test_z_equality():
    z1 = Z(qubit=0)
    z2 = Z(qubit=0)
    z3 = Z(qubit=1)
    assert z1 == z2
    assert z1 != z3


def test_z_draw():
    z = Z(qubit=0)
    circuit = z.draw()
    assert isinstance(circuit, BaseGraph)
    assert circuit.num_qubits == 1
    assert circuit.num_vertices() == 3
    assert circuit.num_edges() == 2
    assert circuit.num_inputs() == 1
    assert circuit.num_outputs() == 1
    assert list(circuit.inputs()) == [0]
    assert list(circuit.outputs()) == [1]
    assert circuit.type(2) == VertexType.Z
    assert circuit.phase(2) == 1
