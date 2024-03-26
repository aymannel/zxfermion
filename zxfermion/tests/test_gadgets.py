import math

import pytest
from pyzx import VertexType, EdgeType

from zxfermion.exceptions import IncompatibleGatesException
from zxfermion.graph import GadgetGraph
from zxfermion.gadgets import Gadget, CX, CZ, X, Z, XPhase, ZPhase, ZPlus, XPlus, XMinus, ZMinus, Identity, H
from zxfermion.types import GateType, LegType


# test kwarg business
# kwargs for drawing
# kwargs for graphs
# kwargs for tikz

# test stack_gadgets gadget feature (multiple test cases, think of clever ones?)
# test expand_gadget feature (multiple test cases! pauli vs phase gadget, gadgets skipping legs, etc)
# some weird behaviour with stack_gadgets gadgets where XPlus is commuting through CZ
# test graphing in all different modes
# test expanded CX and CZ
# assert graph depth doesn't change when graph is larger than gadget size

# rethink mixed equality stuff. possibly use for lop
# go through all __repr__, __add__, __eq__ for all GateType classes and write tests for expected behaviour + edge cases


# GADGET TESTS
def test_identity():
    identity = Identity()
    assert identity.type == GateType.IDENTITY


def test_gadget():
    gadget = Gadget('XYZ')
    assert gadget.type == GateType.GADGET
    assert not gadget.phase_gadget
    assert not gadget.phase
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert len(gadget.legs) == 3
    assert repr(gadget) == 'Gadget(pauli_string="XYZ", phase=0)'
    assert all(isinstance(leg, LegType) for leg in gadget.legs.values())
    assert all((gadget.legs[0] == LegType.X, gadget.legs[1] == LegType.Y, gadget.legs[2] == LegType.Z))


def test_phase_gadget():
    gadget = Gadget('ZZZ')
    assert gadget.type == GateType.GADGET
    assert gadget.phase_gadget
    assert not gadget.phase
    assert len(gadget.legs) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert repr(gadget) == 'Gadget(pauli_string="ZZZ", phase=0)'
    assert all(leg == LegType.Z for leg in gadget.legs.values())


@pytest.mark.parametrize('pauli_string', ['YZX', 'ZZZ'])
@pytest.mark.parametrize(['phase', 'expected'],
    [[None, 0], [0, 0], [1, 1], [1/4, 1/4], [3/4, 3/4], [5/7, 5/7], [2, 0], [3, 1], [5.5, 1.5], [12/5, 2/5]])
def test_gadget_phase(phase, expected, pauli_string):
    gadget = Gadget(pauli_string, phase=phase)
    assert gadget.type == GateType.GADGET
    assert math.isclose(gadget.phase, expected)


def test_identity_gadget():
    gadget1 = Gadget('ZZZ')
    gadget2 = Gadget('XYZ')
    gadget3 = Gadget('ZZZ', phase=1)
    gadget4 = Gadget('XYZ', phase=1)
    assert gadget1.identity
    assert not gadget2.identity
    assert not gadget3.identity
    assert not gadget4.identity


@pytest.mark.parametrize(['control', 'target'], [[None, None], [0, 1]])
def test_cx(control, target):
    cx = CX(control=control, target=target)
    assert cx.type == GateType.CX
    assert cx.control == 0
    assert cx.target == 1
    assert cx.min_qubit == 0
    assert cx.max_qubit == 1
    assert repr(cx) == f'CX(control={0 if control is None else control}, target={1 if target is None else target})'
    with pytest.raises(AssertionError):
        CX(control=1, target=1)


@pytest.mark.parametrize(['control', 'target'], [[None, None], [0, 1]])
def test_cz(control, target):
    cz = CZ(control=control, target=target)
    assert cz.type == GateType.CZ
    assert cz.control == 0
    assert cz.target == 1
    assert cz.min_qubit == 0
    assert cz.max_qubit == 1
    assert repr(cz) == f'CZ(control={0 if control is None else control}, target={1 if target is None else target})'
    with pytest.raises(AssertionError):
        CZ(control=1, target=1)


@pytest.mark.parametrize(['phase', 'expected'],
    [[None, 0], [0, 0], [1, 1], [1/4, 1/4], [3/4, 3/4], [5/7, 5/7], [2, 0], [3, 1], [5.5, 1.5], [12/5, 2/5]])
def test_x_phase(phase, expected):
    x_phase = XPhase(phase=phase)
    assert x_phase.type == GateType.X_PHASE
    assert x_phase.vertex_type == VertexType.X
    assert x_phase.qubit == 0
    assert x_phase.min_qubit == 0
    assert x_phase.max_qubit == 0
    assert math.isclose(x_phase.phase, expected)


@pytest.mark.parametrize(
    ['phase', 'expected'],
    [[None, 0], [0, 0], [1, 1], [1/4, 1/4], [3/4, 3/4], [5/7, 5/7], [2, 0], [3, 1], [5.5, 1.5], [12/5, 2/5]])
def test_z_phase(phase, expected):
    z_phase = ZPhase(phase=phase)
    assert z_phase.type == GateType.Z_PHASE
    assert z_phase.vertex_type == VertexType.Z
    assert z_phase.qubit == 0
    assert z_phase.min_qubit == 0
    assert z_phase.max_qubit == 0
    assert math.isclose(z_phase.phase, expected)


def test_phase_gates_repr():
    assert repr(XPhase()) == f'XPhase(qubit=0, phase=0)'
    assert repr(ZPhase()) == f'ZPhase(qubit=0, phase=0)'
    assert repr(XPhase(qubit=1)) == f'XPhase(qubit=1, phase=0)'
    assert repr(ZPhase(qubit=1, phase=1)) == f'ZPhase(qubit=1, phase=1)'
    assert repr(XPhase(qubit=1, phase=1)) == f'XPhase(qubit=1, phase=1)'


def test_x():
    x = X()
    assert x.type == GateType.X
    assert x.vertex_type == VertexType.X
    assert x.phase == 1
    assert x.qubit == 0
    assert x.min_qubit == 0
    assert x.max_qubit == 0
    assert repr(x) == 'X(qubit=0, phase=1)'


def test_z():
    z = Z()
    assert z.type == GateType.Z
    assert z.vertex_type == VertexType.Z
    assert z.phase == 1
    assert z.qubit == 0
    assert z.min_qubit == 0
    assert z.max_qubit == 0
    assert repr(z) == 'Z(qubit=0, phase=1)'


def test_x_plus():
    x_plus = XPlus()
    assert x_plus.type == GateType.X_PLUS
    assert x_plus.vertex_type == VertexType.X
    assert x_plus.phase == 1/2
    assert x_plus.qubit == 0
    assert x_plus.min_qubit == 0
    assert x_plus.max_qubit == 0
    assert repr(x_plus) == 'XPlus(qubit=0, phase=0.5)'


def test_z_plus():
    z_plus = ZPlus()
    assert z_plus.type == GateType.Z_PLUS
    assert z_plus.vertex_type == VertexType.Z
    assert z_plus.phase == 1/2
    assert z_plus.qubit == 0
    assert z_plus.min_qubit == 0
    assert z_plus.max_qubit == 0
    assert repr(z_plus) == 'ZPlus(qubit=0, phase=0.5)'


def test_x_minus():
    x_minus = XMinus()
    assert x_minus.type == GateType.X_MINUS
    assert x_minus.vertex_type == VertexType.X
    assert x_minus.phase == 3/2
    assert x_minus.qubit == 0
    assert x_minus.min_qubit == 0
    assert x_minus.max_qubit == 0
    assert repr(x_minus) == 'XMinus(qubit=0, phase=1.5)'


def test_z_minus():
    z_minus = ZMinus()
    assert z_minus.type == GateType.Z_MINUS
    assert z_minus.vertex_type == VertexType.Z
    assert z_minus.phase == 3/2
    assert z_minus.qubit == 0
    assert z_minus.min_qubit == 0
    assert z_minus.max_qubit == 0
    assert repr(z_minus) == 'ZMinus(qubit=0, phase=1.5)'


def test_hadamard():
    hadamard1 = H()
    hadamard2 = H(qubit=1)
    assert hadamard1.type == GateType.H
    assert hadamard1.vertex_type == VertexType.H_BOX
    assert not hadamard1.phase
    assert hadamard1.qubit == 0
    assert hadamard2.qubit == 1
    assert hadamard1.min_qubit == 0
    assert hadamard1.max_qubit == 0
    assert repr(hadamard1) == 'H(qubit=0)'
    assert repr(hadamard2) == 'H(qubit=1)'


# EQUALITY TESTS
def test_identity_equality():
    assert Identity() == Identity()
    assert Identity() == Gadget('ZZZ')
    assert Identity() == XPhase()
    assert Identity() == ZPhase()
    assert Identity() != XMinus()
    assert Identity() != ZMinus()
    assert Identity() != XPlus()
    assert Identity() != ZPlus()
    assert Identity() != X()
    assert Identity() != Z()
    assert Identity() != H()


def test_gadget_equality():
    assert Gadget('ZZZ') == Identity()
    assert Gadget('XYZ') == Gadget('XYZ')
    assert Gadget('XYZ') == Gadget('XYZ', 0)
    assert Gadget('XYZ') != Gadget('ZXY')
    assert Gadget('XYZ') != Gadget('XYZ', 1/2)
    assert Gadget('ZZZ') != XPhase()
    assert Gadget('ZZZ') != ZPhase()
    assert Gadget('ZZZ') != X()
    assert Gadget('ZZZ') != Z()


def test_x_phase_equality():
    assert XPhase() == XPhase()
    assert XPhase() == XPhase(phase=0)
    assert XPhase() != XPhase(qubit=1)
    assert XPhase() != XPhase(phase=1)
    assert XPhase(phase=-1/2) == XMinus()
    assert XPhase(phase=1/2) == XPlus()
    assert XPhase(phase=1) == X()
    assert XPhase() == Identity()
    assert XPhase() != ZPhase()


def test_z_phase_equality():
    assert ZPhase() == ZPhase()
    assert ZPhase() == ZPhase(phase=0)
    assert ZPhase() != ZPhase(qubit=1)
    assert ZPhase() != ZPhase(phase=1)
    assert ZPhase(phase=-1/2) == ZMinus()
    assert ZPhase(phase=1/2) == ZPlus()
    assert ZPhase(phase=1) == Z()
    assert ZPhase() == Identity()
    assert ZPhase() != XPhase()


def test_x_equality():
    assert X() == X()
    assert X() != X(qubit=1)
    assert X(qubit=1) == X(qubit=1)


def test_z_equality():
    assert Z() == Z()
    assert Z() != Z(qubit=1)
    assert Z(qubit=1) == Z(qubit=1)


def test_x_plus_equality():
    assert XPlus() == XPlus()
    assert XPlus() != XPlus(qubit=1)
    assert XPlus(qubit=1) == XPlus(qubit=1)


def test_z_plus_equality():
    assert ZPlus() == ZPlus()
    assert ZPlus() != ZPlus(qubit=1)
    assert ZPlus(qubit=1) == ZPlus(qubit=1)


def test_x_minus_equality():
    assert XMinus() == XMinus()
    assert XMinus() != XMinus(qubit=1)
    assert XMinus(qubit=1) == XMinus(qubit=1)


def test_z_minus_equality():
    assert ZMinus() == ZMinus()
    assert ZMinus() != ZMinus(qubit=1)
    assert ZMinus(qubit=1) == ZMinus(qubit=1)


def test_cx_equality():
    assert CX() == CX()
    assert CX() == CX(control=0, target=1)
    assert CX(control=0, target=1) == CX(control=0, target=1)
    assert CX(control=0, target=1) != CX(control=1, target=2)


def test_cz_equality():
    assert CZ() == CZ()
    assert CZ() == CZ(control=0, target=1)
    assert CZ(control=0, target=1) == CZ(control=0, target=1)
    assert CZ(control=0, target=1) == CZ(control=1, target=0)
    assert CZ(control=0, target=1) != CZ(control=1, target=2)


# ADDITION TESTS
def test_equality_addition():
    assert Identity() + Identity()
    assert Identity() + (gadget := Gadget('ZZZ')) is gadget
    assert Identity() + (x_phase := XPhase()) is x_phase
    assert Identity() + (z_phase := ZPhase()) is z_phase
    assert Identity() + (x_minus := XMinus()) is x_minus
    assert Identity() + (z_minus := ZMinus()) is z_minus
    assert Identity() + (x_plus := XPlus()) is x_plus
    assert Identity() + (z_plus := ZPlus()) is z_plus
    assert Identity() + (hadamard := H()) is hadamard
    assert Identity() + (x := X()) is x
    assert Identity() + (z := Z()) is z


def test_gadget_addition():
    assert Gadget('ZZZ') + Gadget('ZZZ') == Gadget('ZZZ')
    assert Gadget('YZX', 1) + Gadget('YZX') == Gadget('YZX', 1)
    assert Gadget('ZZZ', 1/2) + Gadget('ZZZ', -1/2) == Gadget('ZZZ')
    assert Gadget('ZZZ', 1/2) + Gadget('ZZZ', -1/2) == Gadget('ZZZ', 0)
    assert Gadget('ZZZ', 1/2) + Gadget('ZZZ', 1/2) == Gadget('ZZZ', 1)
    assert Gadget('ZZZ', 1) + Gadget('ZZZ', 1) == Gadget('ZZZ')
    assert Gadget('ZZZ', 1) + Gadget('ZZZ', -1) == Identity()
    assert (gadget := Gadget('ZZZ')) + Identity() is gadget
    with pytest.raises(IncompatibleGatesException):
        Gadget('ZZZ') + Gadget('YZX')


def test_x_phase_addition():
    assert XPhase() == XPhase(phase=1/2) + XPhase(phase=-1/2)
    assert XPhase() + XPhase(phase=1/2) == XPhase(phase=1/2)
    assert XPhase(phase=1/2) + XPhase(phase=1/2) == XPhase(phase=1)
    assert XPhase(phase=1/2) + XPhase(phase=1/2) + XPhase(phase=1/2) == XPhase(phase=3/2)
    assert XPhase(phase=-1/2) + XPhase(phase=-1/2) + XPhase(phase=-1/2) == XPhase(phase=1/2)
    assert (x_phase := XPhase()) + Identity() is x_phase
    with pytest.raises(IncompatibleGatesException):
        XPhase() + XPhase(qubit=1)


def test_z_phase_addition():
    assert ZPhase() == ZPhase(phase=1/2) + ZPhase(phase=-1/2)
    assert ZPhase() + ZPhase(phase=1/2) == ZPhase(phase=1/2)
    assert ZPhase(phase=1/2) + ZPhase(phase=1/2) == ZPhase(phase=1)
    assert ZPhase(phase=1/2) + ZPhase(phase=1/2) + ZPhase(phase=1/2) == ZPhase(phase=3/2)
    assert ZPhase(phase=-1/2) + ZPhase(phase=-1/2) + ZPhase(phase=-1/2) == ZPhase(phase=1/2)
    assert (z_phase := ZPhase()) + Identity() is z_phase
    with pytest.raises(IncompatibleGatesException):
        ZPhase() + ZPhase(qubit=1)


def test_x_addition():
    assert isinstance(X() + X(), Identity)
    assert isinstance(X() + XPlus(), XMinus)
    assert isinstance(X() + XMinus(), XPlus)
    assert X(qubit=1) + X(qubit=1) == Identity()
    assert X(qubit=1) + XPlus(qubit=1) == XMinus(1)
    assert X(qubit=1) + XMinus(qubit=1) == XPlus(1)
    assert X() + XPhase(phase=0) == XPhase(phase=1)
    assert X() + XPhase(phase=1) == XPhase(phase=0)
    assert X() + X() + X() == X()
    assert (x := X()) + Identity() is x
    with pytest.raises(IncompatibleGatesException):
        X() + X(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        X() + Gadget('XXX')


def test_z_addition():
    assert isinstance(Z() + Z(), Identity)
    assert isinstance(Z() + ZPlus(), ZMinus)
    assert isinstance(Z() + ZMinus(), ZPlus)
    assert Z(qubit=1) + Z(qubit=1) == Identity()
    assert Z(qubit=1) + ZPlus(qubit=1) == ZMinus(1)
    assert Z(qubit=1) + ZMinus(qubit=1) == ZPlus(1)
    assert Z() + ZPhase(phase=0) == ZPhase(phase=1)
    assert Z() + ZPhase(phase=1) == ZPhase(phase=0)
    assert Z() + Z() + Z() == Z()
    assert (z := Z()) + Identity() is z
    with pytest.raises(IncompatibleGatesException):
        Z() + Z(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        Z() + Gadget('ZZZ')


def test_x_plus_addition():
    assert isinstance(XPlus() + XPlus(), X)
    assert isinstance(XPlus() + X(), XMinus)
    assert isinstance(XPlus() + XMinus(), Identity)
    assert XPlus(qubit=1) + XPlus(qubit=1) == X(qubit=1)
    assert XPlus(qubit=1) + X(qubit=1) == XMinus(qubit=1)
    assert XPlus(qubit=1) + XMinus(qubit=1) == Identity()
    assert XPlus() + XPhase(phase=0) == XPhase(phase=1/2)
    assert XPlus() + XPhase(phase=1) == XPhase(phase=3/2)
    assert (x_plus := XPlus()) + Identity() is x_plus
    with pytest.raises(IncompatibleGatesException):
        XPlus() + XPlus(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        XPlus() + Gadget('XXX')


def test_z_plus_addition():
    assert isinstance(ZPlus() + ZPlus(), Z)
    assert isinstance(ZPlus() + Z(), ZMinus)
    assert isinstance(ZPlus() + ZMinus(), Identity)
    assert ZPlus(qubit=1) + ZPlus(qubit=1) == Z(qubit=1)
    assert ZPlus(qubit=1) + Z(qubit=1) == ZMinus(qubit=1)
    assert ZPlus(qubit=1) + ZMinus(qubit=1) == Identity()
    assert ZPlus() + ZPhase(phase=0) == ZPhase(phase=1/2)
    assert ZPlus() + ZPhase(phase=1) == ZPhase(phase=3/2)
    assert (z_plus := ZPlus()) + Identity() is z_plus
    with pytest.raises(IncompatibleGatesException):
        ZPlus() + ZPlus(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        ZPlus() + Gadget('ZZZ')


def test_x_minus_addition():
    assert isinstance(XMinus() + X(), XPlus)
    assert isinstance(XMinus() + XMinus(), X)
    assert isinstance(XMinus() + XPlus(), Identity)
    assert XMinus(qubit=1) + XMinus(qubit=1) == X(qubit=1)
    assert XMinus(qubit=1) + X(qubit=1) == XPlus(qubit=1)
    assert XMinus(qubit=1) + XPlus(qubit=1) == Identity()
    assert XMinus() + XPhase(phase=0) == XPhase(phase=3/2)
    assert XMinus() + XPhase(phase=1) == XPhase(phase=1/2)
    assert (x_minus := XMinus()) + Identity() is x_minus
    with pytest.raises(IncompatibleGatesException):
        XMinus() + XMinus(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        XPlus() + Gadget('ZZZ')


def test_z_minus_addition():
    assert isinstance(ZMinus() + Z(), ZPlus)
    assert isinstance(ZMinus() + ZMinus(), Z)
    assert isinstance(ZMinus() + ZPlus(), Identity)
    assert ZMinus(qubit=1) + ZMinus(qubit=1) == Z(qubit=1)
    assert ZMinus(qubit=1) + Z(qubit=1) == ZPlus(qubit=1)
    assert ZMinus(qubit=1) + ZPlus(qubit=1) == Identity()
    assert ZMinus() + ZPhase(phase=0) == ZPhase(phase=3/2)
    assert ZMinus() + ZPhase(phase=1) == ZPhase(phase=1/2)
    assert (z_minus := ZMinus()) + Identity() is z_minus
    with pytest.raises(IncompatibleGatesException):
        ZMinus() + ZMinus(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        ZPlus() + Gadget('ZZZ')


def test_x_addition_mixed():
    assert XPhase() + X() == XPhase(phase=1)
    assert XPhase() + XPlus() == XPhase(phase=1/2)
    assert XPhase() + XMinus() == XPhase(phase=-1/2)


# CONFIG TESTS
@pytest.mark.parametrize('value', [True, False])
def test_expand_gadget(value, monkeypatch):
    monkeypatch.setattr('zxfermion.config.expand_gadgets', value)
    gadget1 = Gadget('ZZZ')
    gadget2 = Gadget('ZZZ', expand_gadget=value)
    assert gadget1.expand_gadget is value
    assert gadget2.expand_gadget is value


@pytest.mark.parametrize('value', [True, False])
def test_as_gadget(value, monkeypatch):
    monkeypatch.setattr('zxfermion.config.gadgets_only', value)
    gates = [CX, CZ, XPhase, ZPhase, XMinus, ZMinus, XPlus, ZPlus, X, Z]
    for gate_object in gates:
        gate1 = gate_object()
        gate2 = gate_object(as_gadget=value)
        assert gate1.as_gadget is value
        assert gate2.as_gadget is value


# GRAPH TESTS
def test_gadget_graph():
    gadget = Gadget('XYZ', 1 / 2)
    graph = gadget.graph(expand_gadget=False)
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 3
    assert graph.num_qubits == gadget.max_qubit + 1
    assert graph.num_vertices() == 15
    assert graph.num_edges() == 14
    assert graph.num_inputs() == 3
    assert graph.num_outputs() == 3
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.phase(7) == 1/2
    assert graph.type(6) == VertexType.X
    assert graph.type(7) == VertexType.Z
    assert graph.type(8) == VertexType.H_BOX
    assert graph.type(9) == VertexType.Z
    assert graph.type(10) == VertexType.H_BOX
    assert graph.type(11) == VertexType.X
    assert graph.type(12) == VertexType.Z
    assert graph.type(13) == VertexType.X
    assert graph.type(14) == VertexType.Z
    assert graph.connected(graph.inputs()[0], 8)
    assert graph.connected(graph.inputs()[1], 11)
    assert graph.connected(graph.inputs()[2], 14)
    assert graph.connected(10, graph.outputs()[0])
    assert graph.connected(13, graph.outputs()[1])
    assert graph.connected(14, graph.outputs()[2])
    assert graph.connected(6, 7)
    assert graph.connected(6, 9)
    assert graph.connected(6, 12)
    assert graph.connected(6, 14)


def test_expanded_gadget_graph():
    gadget = Gadget('XYZ', 1/2)
    graph = gadget.graph(expand_gadget=True)
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 7
    assert graph.num_qubits == gadget.max_qubit + 1
    assert graph.num_vertices() == 19
    assert graph.num_edges() == 20
    assert graph.num_inputs() == 3
    assert graph.num_outputs() == 3
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [14, 15, 16]
    assert graph.type(3) == VertexType.H_BOX
    assert graph.type(4) == VertexType.X
    assert graph.type(5) == VertexType.Z
    assert graph.type(6) == VertexType.X
    assert graph.type(7) == VertexType.Z
    assert graph.type(8) == VertexType.X
    assert graph.type(9) == VertexType.Z
    assert graph.type(10) == VertexType.Z
    assert graph.type(11) == VertexType.X
    assert graph.type(12) == VertexType.Z
    assert graph.type(13) == VertexType.X
    assert graph.type(17) == VertexType.H_BOX
    assert graph.type(18) == VertexType.X
    assert graph.phase(9) == 1/2


def test_cx_graph():
    cx = CX(control=0, target=1)
    graph = cx.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == cx.max_qubit + 1
    assert graph.num_vertices() == 6
    assert graph.num_edges() == 5
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.Z
    assert graph.type(5) == VertexType.X
    assert graph.connected(graph.inputs()[0], 4)
    assert graph.connected(graph.inputs()[1], 5)
    assert graph.connected(4, graph.outputs()[0])
    assert graph.connected(5, graph.outputs()[1])
    assert graph.connected(4, 5)


def test_cz_graph():
    cz = CZ(control=0, target=1)
    graph = cz.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == cz.max_qubit + 1
    assert graph.num_vertices() == 6
    assert graph.num_edges() == 5
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.Z
    assert graph.type(5) == VertexType.Z
    assert graph.edge_type((4, 5)) == EdgeType.HADAMARD
    assert graph.connected(graph.inputs()[0], 4)
    assert graph.connected(graph.inputs()[1], 5)
    assert graph.connected(4, graph.outputs()[0])
    assert graph.connected(5, graph.outputs()[1])
    assert graph.connected(4, 5)


def test_x_phase_graph():
    x_phase = XPhase(phase=3/4)
    graph = x_phase.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.X
    assert graph.phase(2) == 3/4
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_z_phase_graph():
    z_phase = ZPhase(phase=3/4)
    graph = z_phase.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.Z
    assert graph.phase(2) == 3/4
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_x_graph():
    x = X()
    graph = x.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.X
    assert graph.phase(2) == 1
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_z_graph():
    z = Z()
    graph = z.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.Z
    assert graph.phase(2) == 1
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_x_plus_graph():
    x_plus = XPlus()
    graph = x_plus.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.X
    assert graph.phase(2) == 1/2
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_z_plus_graph():
    z_plus = ZPlus()
    graph = z_plus.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.Z
    assert graph.phase(2) == 1/2
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_x_minus_graph():
    x_minus = XMinus()
    graph = x_minus.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.X
    assert graph.phase(2) == 3/2
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])


def test_z_minus_graph():
    z_minus = ZMinus()
    graph = z_minus.graph()
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.Z
    assert graph.phase(2) == 3/2
    assert graph.connected(graph.inputs()[0], 2)
    assert graph.connected(2, graph.outputs()[0])
