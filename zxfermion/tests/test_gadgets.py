import pytest
from pyzx import VertexType, EdgeType

from zxfermion.graph import BaseGraph
from zxfermion.gadgets import Gadget, CX, CZ, X, Z, XPhase, ZPhase, ZPlus, XPlus, XMinus, ZMinus
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
# test vertex type for all SingleQubitGate children


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


def test_gadget():
    gadget = Gadget('XYZ')
    assert gadget.type == GateType.GADGET
    assert not gadget.phase_gadget
    assert not gadget.phase
    assert len(gadget.legs) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert all(isinstance(leg, LegType) for leg in gadget.legs.values())


def test_phase_gadget():
    gadget = Gadget('ZZZ')
    assert gadget.type == GateType.GADGET
    assert gadget.phase_gadget
    assert not gadget.phase
    assert len(gadget.legs) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert all(leg == LegType.Z for leg in gadget.legs.values())


def test_gadget_phase():
    gadget = Gadget('XYZ', phase=1/2)
    assert gadget.type == GateType.GADGET
    assert not gadget.phase_gadget
    assert gadget.phase == 1/2
    assert len(gadget.legs) == 3
    assert gadget.min_qubit == 0
    assert gadget.max_qubit == 2
    assert all(isinstance(leg, LegType) for leg in gadget.legs.values())


def test_gadget_equality():
    gadget1 = Gadget('XYZ')
    gadget2 = Gadget('XYZ')
    gadget3 = Gadget('ZXY')
    gadget4 = Gadget('XYZ', 1/2)
    assert gadget1 == gadget2
    assert gadget1 != gadget3
    assert gadget1 != gadget4


def test_gadget_graph():
    gadget = Gadget('XYZ', 1 / 2)
    graph = gadget.graph(expand_gadget=False)
    assert isinstance(graph, BaseGraph)
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
    assert isinstance(graph, BaseGraph)
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


@pytest.mark.parametrize(['control', 'target'], [[None, None], [0, 1]])
def test_cx(control, target):
    cx = CX(control=control, target=target)
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


def test_cx_graph():
    cx = CX(control=0, target=1)
    graph = cx.graph()
    assert isinstance(graph, BaseGraph)
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


@pytest.mark.parametrize(['control', 'target'], [[None, None], [0, 1]])
def test_cz(control, target):
    cz = CZ(control=control, target=target)
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


def test_cz_graph():
    cz = CZ(control=0, target=1)
    graph = cz.graph()
    assert isinstance(graph, BaseGraph)
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


@pytest.mark.parametrize('phase', [None, 0, 1/4, 2/2, 3/4, 1, 5/4, 6/4, 7/4, 2, 3, 15])
def test_x_phase(phase):
    x_phase = XPhase(phase=phase)
    assert x_phase.type == GateType.X_PHASE
    assert x_phase.vertex_type == VertexType.X
    assert x_phase.phase == phase
    assert x_phase.qubit == 0
    assert x_phase.min_qubit == 0
    assert x_phase.max_qubit == 0


def test_x_phase_equality():
    x_phase1 = XPhase()
    x_phase2 = XPhase()
    x_phase3 = XPhase(qubit=1)
    x_phase4 = XPhase(phase=1)
    assert x_phase1 == x_phase2
    assert x_phase1 != x_phase3
    assert x_phase1 != x_phase4


def test_x_phase_graph():
    x_phase = XPhase(phase=3/4)
    graph = x_phase.graph()
    assert isinstance(graph, BaseGraph)
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


@pytest.mark.parametrize('phase', [None, 0, 1/4, 2/2, 3/4, 1, 5/4, 6/4, 7/4, 2, 3, 15])
def test_z_phase(phase):
    z_phase = ZPhase(phase=phase)
    assert z_phase.type == GateType.Z_PHASE
    assert z_phase.vertex_type == VertexType.Z
    assert z_phase.phase == phase
    assert z_phase.qubit == 0
    assert z_phase.min_qubit == 0
    assert z_phase.max_qubit == 0


def test_z_phase_equality():
    z_phase1 = ZPhase()
    z_phase2 = ZPhase()
    z_phase3 = ZPhase(qubit=1)
    z_phase4 = ZPhase(phase=1)
    assert z_phase1 == z_phase2
    assert z_phase1 != z_phase3
    assert z_phase1 != z_phase4


def test_z_phase_graph():
    z_phase = ZPhase(phase=3/4)
    graph = z_phase.graph()
    assert isinstance(graph, BaseGraph)
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


def test_x():
    x = X()
    assert x.type == GateType.X
    assert x.vertex_type == VertexType.X
    assert x.phase == 1
    assert x.qubit == 0
    assert x.min_qubit == 0
    assert x.max_qubit == 0


def test_x_equality():
    x1 = X()
    x2 = X()
    x3 = X(qubit=1)
    assert x1 == x2
    assert x1 != x3


def test_x_graph():
    x = X()
    graph = x.graph()
    assert isinstance(graph, BaseGraph)
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


def test_z():
    z = Z()
    assert z.type == GateType.Z
    assert z.vertex_type == VertexType.Z
    assert z.phase == 1
    assert z.qubit == 0
    assert z.min_qubit == 0
    assert z.max_qubit == 0


def test_z_equality():
    z1 = Z()
    z2 = Z()
    z3 = Z(qubit=1)
    assert z1 == z2
    assert z1 != z3


def test_z_graph():
    z = Z()
    graph = z.graph()
    assert isinstance(graph, BaseGraph)
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


def test_x_plus():
    x_plus = XPlus()
    assert x_plus.type == GateType.X_PLUS
    assert x_plus.vertex_type == VertexType.X
    assert x_plus.phase == 1/2
    assert x_plus.qubit == 0
    assert x_plus.min_qubit == 0
    assert x_plus.max_qubit == 0


def test_x_plus_equality():
    x_plus1 = XPlus()
    x_plus12 = XPlus()
    x_plus13 = XPlus(qubit=1)
    assert x_plus1 == x_plus12
    assert x_plus1 != x_plus13


def test_x_plus_graph():
    x_plus = XPlus()
    graph = x_plus.graph()
    assert isinstance(graph, BaseGraph)
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


def test_z_plus():
    z_plus = ZPlus()
    assert z_plus.type == GateType.Z_PLUS
    assert z_plus.vertex_type == VertexType.Z
    assert z_plus.phase == 1/2
    assert z_plus.qubit == 0
    assert z_plus.min_qubit == 0
    assert z_plus.max_qubit == 0


def test_z_plus_equality():
    z_plus1 = ZPlus()
    z_plus2 = ZPlus()
    z_plus3 = ZPlus(qubit=1)
    assert z_plus1 == z_plus2
    assert z_plus1 != z_plus3


def test_z_plus_graph():
    z_plus = ZPlus()
    graph = z_plus.graph()
    assert isinstance(graph, BaseGraph)
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


def test_x_minus():
    x_minus = XMinus()
    assert x_minus.type == GateType.X_MINUS
    assert x_minus.vertex_type == VertexType.X
    assert x_minus.phase == -1/2
    assert x_minus.qubit == 0
    assert x_minus.min_qubit == 0
    assert x_minus.max_qubit == 0


def test_x_minus_equality():
    x_minus1 = XMinus()
    x_minus2 = XMinus()
    x_minus3 = XMinus(qubit=1)
    assert x_minus1 == x_minus2
    assert x_minus1 != x_minus3


def test_x_minus_graph():
    x_minus = XMinus()
    graph = x_minus.graph()
    assert isinstance(graph, BaseGraph)
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


def test_z_minus():
    z_minus = ZMinus()
    assert z_minus.type == GateType.Z_MINUS
    assert z_minus.vertex_type == VertexType.Z
    assert z_minus.phase == -1/2
    assert z_minus.qubit == 0
    assert z_minus.min_qubit == 0
    assert z_minus.max_qubit == 0


def test_z_minus_equality():
    z_minus1 = ZMinus()
    z_minus2 = ZMinus()
    z_minus3 = ZMinus(qubit=1)
    assert z_minus1 == z_minus2
    assert z_minus1 != z_minus3


def test_z_minus_graph():
    z_minus = ZMinus()
    graph = z_minus.graph()
    assert isinstance(graph, BaseGraph)
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
