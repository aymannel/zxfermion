import math

import pytest
from pyzx import VertexType

from zxfermion.types import GateType, PauliType
from zxfermion.exceptions import IncompatibleGatesException
from zxfermion.gadgets import Identity, Gadget, CX, CZ, X, Z, XPhase, ZPhase, ZPlus, XPlus, XMinus, ZMinus, H, \
    PauliGate, CliffordGate, ControlledGate, FixedPhaseGate


# kwargs for drawing
# kwargs for graphs
# kwargs for tikz

# test stack_gadgets gadget feature (multiple test cases, think of clever ones?)
# test expand_gadget feature (multiple test cases! pauli vs phase gadget, gadgets skipping paulis, etc)
# some weird behaviour with stack_gadgets gadgets where XPlus is commuting through CZ

# test graphing in all different modes
# test expanded CX and CZ
# test Gadget.from_gate()
# assert XPhase.gadget() method returns Gadget.from_single_gate(self)

# update Gadget tests to assert Gadget('XI') == Gadget('X')

def test_inheritance():
    assert all(isinstance(gate, PauliGate) for gate in [X(), Z()])
    assert all(isinstance(gate, CliffordGate) for gate in [CX(), CZ()])
    assert all(isinstance(gate, CliffordGate) for gate in [XPlus(), ZPlus(), XMinus(), ZMinus()])
    assert all(isinstance(gate, FixedPhaseGate) for gate in [XPlus(), ZPlus(), XMinus(), ZMinus()])
    assert all(isinstance(gate, ControlledGate) for gate in [CX(), CZ()])
    with pytest.raises(IncompatibleGatesException):
        XPhase() + ZPhase()
    with pytest.raises(IncompatibleGatesException):
        ZPhase() + XPhase()


# Gadget tests
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
    assert len(gadget.paulis) == 3
    assert repr(gadget) == "Gadget(pauli_string='XYZ', phase=0)"
    assert all(isinstance(pauli, PauliType) for pauli in gadget.paulis.values())
    assert all((gadget.paulis[0] == PauliType.X, gadget.paulis[1] == PauliType.Y, gadget.paulis[2] == PauliType.Z))
    assert gadget.to_dict() == {'Gadget': {'pauli_string': 'XYZ', 'phase': 0}}


def test_phase_gadget():
    gadget = Gadget('ZZZ')
    assert gadget.type == GateType.GADGET
    assert gadget.phase_gadget
    assert not gadget.phase
    assert len(gadget.paulis) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert repr(gadget) == "Gadget(pauli_string='ZZZ', phase=0)"
    assert all(pauli == PauliType.Z for pauli in gadget.paulis.values())
    assert gadget.to_dict() == {'Gadget': {'pauli_string': 'ZZZ', 'phase': 0}}


# @formatter:off
@pytest.mark.parametrize(['pauli_string', 'paulis'],
                         [['ZZZ',   {0: PauliType.Z, 1: PauliType.Z, 2: PauliType.Z}],
                          ['YZX',   {0: PauliType.Y, 1: PauliType.Z, 2: PauliType.X}],
                          ['ZIZ',   {0: PauliType.Z, 1: PauliType.I, 2: PauliType.Z}],
                          ['IIZ',   {0: PauliType.I, 1: PauliType.I, 2: PauliType.Z}],
                          ['ZZZII', {0: PauliType.Z, 1: PauliType.Z, 2: PauliType.Z}],
                          ['ZIZII', {0: PauliType.Z, 1: PauliType.I, 2: PauliType.Z}]])  # @formatter:on
def test_gadget_pauli_string(pauli_string, paulis):
    gadget = Gadget(pauli_string)
    assert gadget.paulis == paulis
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2


# @formatter:off
@pytest.mark.parametrize(['phase', 'expected'],
[[None, 0], [0, 0], [1, 1], [2, 0], [3, 1], [1/4, 1/4], [3/2, 3/2], [5.5, 1.5], [12/5, 2/5]])  # @formatter:on
def test_gadget_phase(phase, expected):
    phase_gadget = Gadget('ZZZ', phase=phase)
    pauli_gadget = Gadget('YZX', phase=phase)
    assert phase_gadget.type == GateType.GADGET
    assert pauli_gadget.type == GateType.GADGET
    assert math.isclose(phase_gadget.phase, expected)
    assert math.isclose(pauli_gadget.phase, expected)


def test_gadget_identity():
    gadget1 = Gadget('ZZZ')
    gadget2 = Gadget('XYZ')
    gadget3 = Gadget('ZZZ', phase=1)
    gadget4 = Gadget('XYZ', phase=1)
    assert gadget1.identity
    assert not gadget2.identity
    assert not gadget3.identity
    assert not gadget4.identity


# @formatter:off
@pytest.mark.parametrize(['control', 'target', 'expected_control', 'expected_target'],
[[None, None, 0, 1], [0, 1, 0, 1], [0, 4, 0, 4], [3, 6, 3, 6], [6, 12, 6, 12]])  # @formatter:on
def test_cx(control, target, expected_control, expected_target):
    cx = CX(control=control, target=target)
    assert cx.type == GateType.CX
    assert cx.control == expected_control
    assert cx.target == expected_target
    assert repr(cx) == f'CX(control={expected_control}, target={expected_target})'
    with pytest.raises(AssertionError):
        CX(control=1, target=1)


# @formatter:off
@pytest.mark.parametrize(['control', 'target', 'min_qubit', 'max_qubit'],
[[0, 1, 0, 1], [0, 4, 0, 4], [6, 3, 3, 6], [12, 6, 6, 12], [2, 15, 2, 15]])  # @formatter:on
def test_cx_min_max(control, target, min_qubit, max_qubit):
    cx = CX(control=control, target=target)
    assert cx.type == GateType.CX
    assert cx.control == control
    assert cx.target == target
    assert cx.min_qubit == min_qubit
    assert cx.max_qubit == max_qubit


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


# @formatter:off
@pytest.mark.parametrize(['control', 'target', 'min_qubit', 'max_qubit'],
[[0, 1, 0, 1], [0, 4, 0, 4], [6, 3, 3, 6], [12, 6, 6, 12], [2, 15, 2, 15]])  # @formatter:on
def test_cz_min_max(control, target, min_qubit, max_qubit):
    cz = CZ(control=control, target=target)
    assert cz.type == GateType.CZ
    assert cz.control == min_qubit
    assert cz.target == max_qubit
    assert cz.min_qubit == min_qubit
    assert cz.max_qubit == max_qubit


# @formatter:off
@pytest.mark.parametrize(['phase', 'expected'],
[[None, 0], [0, 0], [1, 1], [1/4, 1/4], [5/7, 5/7], [2, 0], [3, 1], [5.5, 1.5], [12/5, 2/5]])  # @formatter:on
def test_x_phase(phase, expected):
    x_phase = XPhase(phase=phase)
    assert x_phase.type == GateType.X_PHASE
    assert x_phase.vertex_type == VertexType.X
    assert x_phase.qubit == 0
    assert x_phase.min_qubit == 0
    assert x_phase.max_qubit == 0
    assert math.isclose(x_phase.phase, expected)

    x_phase_dict = x_phase.to_dict()
    assert next(iter(x_phase_dict)) == 'XPhase'
    assert x_phase_dict['XPhase']['qubit'] == x_phase.qubit
    assert math.isclose(x_phase_dict['XPhase']['phase'], x_phase.phase)


# @formatter:off
@pytest.mark.parametrize(['phase', 'expected'],
[[None, 0], [0, 0], [1, 1], [1/4, 1/4], [5/7, 5/7], [2, 0], [3, 1], [5.5, 1.5], [12/5, 2/5]])  # @formatter:on
def test_z_phase(phase, expected):
    z_phase = ZPhase(phase=phase)
    assert z_phase.type == GateType.Z_PHASE
    assert z_phase.vertex_type == VertexType.Z
    assert z_phase.qubit == 0
    assert z_phase.min_qubit == 0
    assert z_phase.max_qubit == 0
    assert math.isclose(z_phase.phase, expected)

    z_phase_dict = z_phase.to_dict()
    assert next(iter(z_phase_dict)) == 'ZPhase'
    assert z_phase_dict['ZPhase']['qubit'] == z_phase.qubit
    assert math.isclose(z_phase_dict['ZPhase']['phase'], z_phase.phase)


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
    assert repr(x) == 'X(qubit=0)'
    assert x.to_dict() == {'X': {'qubit': 0}}


def test_z():
    z = Z()
    assert z.type == GateType.Z
    assert z.vertex_type == VertexType.Z
    assert z.phase == 1
    assert z.qubit == 0
    assert z.min_qubit == 0
    assert z.max_qubit == 0
    assert repr(z) == 'Z(qubit=0)'
    assert z.to_dict() == {'Z': {'qubit': 0}}


def test_x_plus():
    x_plus = XPlus()
    assert x_plus.type == GateType.X_PLUS
    assert x_plus.vertex_type == VertexType.X
    assert x_plus.phase == 1/2
    assert x_plus.qubit == 0
    assert x_plus.min_qubit == 0
    assert x_plus.max_qubit == 0
    assert repr(x_plus) == 'XPlus(qubit=0)'
    assert x_plus.to_dict() == {'XPlus': {'qubit': 0}}


def test_z_plus():
    z_plus = ZPlus()
    assert z_plus.type == GateType.Z_PLUS
    assert z_plus.vertex_type == VertexType.Z
    assert z_plus.phase == 1/2
    assert z_plus.qubit == 0
    assert z_plus.min_qubit == 0
    assert z_plus.max_qubit == 0
    assert repr(z_plus) == 'ZPlus(qubit=0)'
    assert z_plus.to_dict() == {'ZPlus': {'qubit': 0}}


def test_x_minus():
    x_minus = XMinus()
    assert x_minus.type == GateType.X_MINUS
    assert x_minus.vertex_type == VertexType.X
    assert x_minus.phase == 3/2
    assert x_minus.qubit == 0
    assert x_minus.min_qubit == 0
    assert x_minus.max_qubit == 0
    assert repr(x_minus) == 'XMinus(qubit=0)'
    assert x_minus.to_dict() == {'XMinus': {'qubit': 0}}


def test_z_minus():
    z_minus = ZMinus()
    assert z_minus.type == GateType.Z_MINUS
    assert z_minus.vertex_type == VertexType.Z
    assert z_minus.phase == 3/2
    assert z_minus.qubit == 0
    assert z_minus.min_qubit == 0
    assert z_minus.max_qubit == 0
    assert repr(z_minus) == 'ZMinus(qubit=0)'
    assert z_minus.to_dict() == {'ZMinus': {'qubit': 0}}


def test_hadamard():
    hadamard1 = H()
    hadamard2 = H(qubit=1)
    assert hadamard1.type == GateType.H
    assert hadamard1.vertex_type == VertexType.H_BOX
    assert hadamard1.qubit == 0
    assert hadamard2.qubit == 1
    assert hadamard1.min_qubit == 0
    assert hadamard1.max_qubit == 0
    assert repr(hadamard1) == 'H(qubit=0)'
    assert repr(hadamard2) == 'H(qubit=1)'
    assert hadamard1.to_dict() == {'H': {'qubit': 0}}
    assert hadamard2.to_dict() == {'H': {'qubit': 1}}


# Equality tests
x_gates = [XPhase(), XMinus(), XPlus(), X()]
z_gates = [ZPhase(), ZMinus(), ZPlus(), Z()]


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
    assert all(Gadget('ZZZ') != gate for gate in x_gates)
    assert all(Gadget('ZZZ') != gate for gate in z_gates)
    assert Gadget('ZZZ') != H()


def test_x_phase_equality():
    assert XPhase() == XPhase()
    assert XPhase() == XPhase(phase=0)
    assert XPhase() != XPhase(qubit=1)
    assert XPhase() != XPhase(phase=1)
    assert XPhase(phase=-1/2) == XMinus()
    assert XPhase(phase=1/2) == XPlus()
    assert XPhase(phase=1) == X()
    assert all(XPhase() != gate for gate in z_gates)
    assert all(XPhase(qubit=1) != gate for gate in x_gates)
    assert XPhase() == Identity()
    assert XPhase() != H()


def test_z_phase_equality():
    assert ZPhase() == ZPhase()
    assert ZPhase() == ZPhase(phase=0)
    assert ZPhase() != ZPhase(qubit=1)
    assert ZPhase() != ZPhase(phase=1)
    assert ZPhase(phase=-1/2) == ZMinus()
    assert ZPhase(phase=1/2) == ZPlus()
    assert ZPhase(phase=1) == Z()
    assert all(ZPhase() != gate for gate in x_gates)
    assert all(ZPhase(qubit=1) != gate for gate in z_gates)
    assert ZPhase() == Identity()
    assert ZPhase() != H()


def test_x_equality():
    assert X() == X()
    assert X() != X(qubit=1)
    assert X(qubit=1) == X(qubit=1)
    assert all(X() != gate for gate in z_gates)
    assert all(X(qubit=1) != gate for gate in x_gates)
    assert X() != Identity()
    assert X() != H()


def test_z_equality():
    assert Z() == Z()
    assert Z() != Z(qubit=1)
    assert Z(qubit=1) == Z(qubit=1)
    assert all(Z() != gate for gate in x_gates)
    assert all(Z(qubit=1) != gate for gate in z_gates)
    assert Z() != Identity()
    assert Z() != H()


def test_x_plus_equality():
    assert XPlus() == XPlus()
    assert XPlus() != XPlus(qubit=1)
    assert XPlus(qubit=1) == XPlus(qubit=1)
    assert all(XPlus() != gate for gate in z_gates)
    assert all(XPlus(qubit=1) != gate for gate in x_gates)
    assert XPlus() != Identity()
    assert XPlus() != H()


def test_z_plus_equality():
    assert ZPlus() == ZPlus()
    assert ZPlus() != ZPlus(qubit=1)
    assert ZPlus(qubit=1) == ZPlus(qubit=1)
    assert all(ZPlus() != gate for gate in x_gates)
    assert all(ZPlus(qubit=1) != gate for gate in z_gates)
    assert ZPlus() != Identity()
    assert ZPlus() != H()


def test_x_minus_equality():
    assert XMinus() == XMinus()
    assert XMinus() != XMinus(qubit=1)
    assert XMinus(qubit=1) == XMinus(qubit=1)
    assert all(XMinus() != gate for gate in z_gates)
    assert all(XMinus(qubit=1) != gate for gate in x_gates)
    assert XMinus() != Identity()
    assert XMinus() != H()


def test_z_minus_equality():
    assert ZMinus() == ZMinus()
    assert ZMinus() != ZMinus(qubit=1)
    assert ZMinus(qubit=1) == ZMinus(qubit=1)
    assert all(ZMinus() != gate for gate in x_gates)
    assert all(ZMinus(qubit=1) != gate for gate in z_gates)
    assert ZMinus() != Identity()
    assert ZMinus() != H()


def test_cx_equality():
    assert CX() == CX()
    assert CX() == CX(control=0, target=1)
    assert CX(control=0, target=1) == CX(control=0, target=1)
    assert CX(control=0, target=1) != CX(control=1, target=2)
    assert all(CX() != gate for gate in z_gates)
    assert all(CX() != gate for gate in x_gates)
    assert CX() != Identity()
    assert CX() != H()


def test_cz_equality():
    assert CZ() == CZ()
    assert CZ() == CZ(control=0, target=1)
    assert CZ(control=0, target=1) == CZ(control=0, target=1)
    assert CZ(control=0, target=1) == CZ(control=1, target=0)
    assert CZ(control=0, target=1) != CZ(control=1, target=2)
    assert all(CZ() != gate for gate in z_gates)
    assert all(CZ() != gate for gate in x_gates)
    assert CZ() != Identity()
    assert CZ() != H()


# Addition tests
def test_equality_addition():
    assert Identity() + Identity() == Identity()
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


def test_hadamard_addition():
    assert isinstance(H() + H(), Identity)
    assert Z(qubit=1) + Z(qubit=1) == Identity()
    assert (h := H()) + Identity() is h
    assert H() + H() + H() == H()
    with pytest.raises(IncompatibleGatesException):
        H() + H(qubit=1)
    with pytest.raises(IncompatibleGatesException):
        H() + Gadget('ZZZ')


# Config tests
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
