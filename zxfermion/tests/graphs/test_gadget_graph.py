from typing import Union

import pytest
from pyzx import VertexType

from zxfermion.graphs.gadget_graph import GadgetGraph
from zxfermion import Gadget
from zxfermion.gates.gates import XPlus, XMinus, ZPlus, ZMinus, CX, CZ
from zxfermion.gates import X, Z, XPhase, ZPhase


# assert graph depth doesn't change when graph is larger than gadget size
# test pdf()
# test tikz()
# assert tex file is deleted after pdf generation
# test qubit_vertices()

# test cases
# various gadgets / missing legs / different paulis etc
# expanded analogues of above
# circuit consisting of various single qubit and controlled gates to check stacking
# single qubit excitation operators + two qubit excitation operators
# test vdata


# GadgetGraph tests
@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize(['gate', 'phase'], [[XPhase, 1/2], [XPhase, None], [ZPhase, 3/2], [ZPhase, None]])
def test_graph_add_phase_gate(qubit, gate: Union[type[XPhase], type[ZPhase]], phase):
    graph = GadgetGraph(num_qubits=4)
    gate = gate(qubit=qubit, phase=phase)
    graph.add(gate=gate)
    assert graph.graph_depth == 1
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert all(graph.connected(graph.inputs()[q], graph.outputs()[q]) for q in range(4) if qubit != qubit)
    assert graph.connected(graph.inputs()[qubit], 8)
    assert graph.connected(8, graph.outputs()[qubit])
    assert graph.type(8) == gate.vertex_type
    assert graph.phase(8) == 0 if phase is None else phase


def test_graph_add_gadget():
    gadget = Gadget('XYZ', 1/2)
    graph = GadgetGraph(num_qubits=3)
    graph.add_gadget(gadget)
    assert graph.graph_depth == 3
    assert graph.num_qubits == max(gadget.paulis) + 1
    assert graph.num_vertices() == 15
    assert graph.num_edges() == 14
    assert graph.num_inputs() == 3
    assert graph.num_outputs() == 3
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.phase(6) == 1/2
    assert graph.type(6) == VertexType.Z
    assert graph.type(7) == VertexType.X
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
    assert graph.connected(7, 9)
    assert graph.connected(7, 12)
    assert graph.connected(7, 14)


def test_graph_add_expanded_gadget_zzz():
    gadget = Gadget('ZZZ', 1/2)
    graph = GadgetGraph(num_qubits=3)
    graph.add_expanded_gadget(gadget)
    assert graph.num_qubits == 3
    assert graph.graph_depth == 5
    assert graph.num_edges() == 16
    assert graph.num_vertices() == 15
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.type(6) == VertexType.Z
    assert graph.type(7) == VertexType.X
    assert graph.type(8) == VertexType.Z
    assert graph.type(9) == VertexType.X
    assert graph.type(10) == VertexType.Z
    assert graph.type(11) == VertexType.Z
    assert graph.type(12) == VertexType.X
    assert graph.type(13) == VertexType.Z
    assert graph.type(14) == VertexType.X
    assert graph.phase(10) == 1/2


def test_graph_add_expanded_gadget_yzx():
    gadget = Gadget('YZX', 1/2)
    graph = GadgetGraph(num_qubits=3)
    graph.add_expanded_gadget(gadget)
    assert graph.num_qubits == 3
    assert graph.graph_depth == 7
    assert graph.num_edges() == 20
    assert graph.num_vertices() == 19
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.type(6) == VertexType.X
    assert graph.type(7) == VertexType.H_BOX
    assert graph.type(8) == VertexType.Z
    assert graph.type(9) == VertexType.X
    assert graph.type(10) == VertexType.Z
    assert graph.type(11) == VertexType.X
    assert graph.type(12) == VertexType.Z
    assert graph.type(13) == VertexType.Z
    assert graph.type(14) == VertexType.X
    assert graph.type(15) == VertexType.Z
    assert graph.type(16) == VertexType.X
    assert graph.type(18) == VertexType.H_BOX
    assert graph.phase(6) == 1/2
    assert graph.phase(12) == 1/2
    assert graph.phase(17) == 3/2


def test_graph_add_expanded_gadget_z_z_z():
    gadget = Gadget('ZIZIZ', 1/2)
    graph = GadgetGraph(num_qubits=5)
    graph.add_expanded_gadget(gadget)
    assert graph.num_qubits == 5
    assert graph.graph_depth == 5
    assert graph.num_edges() == 18
    assert graph.num_vertices() == 19
    assert list(graph.inputs()) == [0, 1, 2, 3, 4]
    assert list(graph.outputs()) == [5, 6, 7, 8, 9]
    assert graph.type(10) == VertexType.Z
    assert graph.type(11) == VertexType.X
    assert graph.type(12) == VertexType.Z
    assert graph.type(13) == VertexType.X
    assert graph.type(14) == VertexType.Z
    assert graph.type(15) == VertexType.Z
    assert graph.type(16) == VertexType.X
    assert graph.type(17) == VertexType.Z
    assert graph.type(18) == VertexType.X
    assert graph.phase(14) == 1/2


def test_graph_add_cx():
    cx = CX(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cx(cx)
    assert graph.graph_depth == 1
    assert graph.num_qubits == 2
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


def test_graph_add_cz():
    cz = CZ(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cz(cz)
    assert isinstance(graph, GadgetGraph)
    assert graph.graph_depth == 1
    assert graph.num_qubits == 2
    assert graph.num_vertices() == 7
    assert graph.num_edges() == 6
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.Z
    assert graph.type(5) == VertexType.Z
    assert graph.connected(graph.inputs()[0], 4)
    assert graph.connected(graph.inputs()[1], 5)
    assert graph.connected(4, graph.outputs()[0])
    assert graph.connected(5, graph.outputs()[1])
    assert graph.connected(4, 6)
    assert graph.connected(5, 6)


def test_graph_add_cx_gadget():
    cx = CX(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cx_gadget(cx)
    assert isinstance(graph, GadgetGraph)
    assert graph.graph_depth == 3
    assert graph.num_qubits == max(cx.qubits) + 1
    assert graph.num_vertices() == 10
    assert graph.num_edges() == 9
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.Z
    assert graph.type(5) == VertexType.Z
    assert graph.type(6) == VertexType.H_BOX
    assert graph.type(7) == VertexType.H_BOX
    assert graph.type(8) == VertexType.Z
    assert graph.type(9) == VertexType.X
    assert graph.phase(8) == 3/2
    assert graph.phase(4) == 1/2
    assert graph.phase(5) == 1/2
    assert graph.connected(4, 9)
    assert graph.connected(5, 9)
    assert graph.connected(5, 6)
    assert graph.connected(5, 7)
    assert graph.connected(8, 9)
    assert graph.connected(graph.inputs()[0], 4)
    assert graph.connected(graph.inputs()[1], 6)
    assert graph.connected(4, graph.outputs()[0])
    assert graph.connected(7, graph.outputs()[1])


def test_graph_add_cz_gadget():
    cz = CZ(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cz_gadget(cz)
    assert isinstance(graph, GadgetGraph)
    assert graph.graph_depth == 1
    assert graph.num_qubits == max(cz.qubits) + 1
    assert graph.num_vertices() == 8
    assert graph.num_edges() == 7
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.Z
    assert graph.type(5) == VertexType.Z
    assert graph.type(6) == VertexType.Z
    assert graph.type(7) == VertexType.X
    assert graph.phase(6) == 3/2
    assert graph.phase(4) == 1/2
    assert graph.phase(5) == 1/2
    assert graph.connected(4, 7)
    assert graph.connected(5, 7)
    assert graph.connected(6, 7)
    assert graph.connected(graph.inputs()[0], 4)
    assert graph.connected(graph.inputs()[1], 5)
    assert graph.connected(4, graph.outputs()[0])
    assert graph.connected(5, graph.outputs()[1])


def test_graph_add_x_phase():
    x_phase = XPhase(phase=3/4)
    graph = GadgetGraph(num_qubits=1)
    graph.add(x_phase)
    assert graph.graph_depth == 1
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


def test_graph_add_z_phase():
    z_phase = ZPhase(phase=3/4)
    graph = GadgetGraph(num_qubits=1)
    graph.add(z_phase)
    assert graph.graph_depth == 1
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
    graph = GadgetGraph(num_qubits=1)
    graph.add(X())
    assert graph.graph_depth == 1
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
    graph = GadgetGraph(num_qubits=1)
    graph.add(Z())
    assert graph.graph_depth == 1
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
    graph = GadgetGraph(num_qubits=1)
    graph.add(XPlus())
    assert graph.graph_depth == 1
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
    graph = GadgetGraph(num_qubits=1)
    graph.add(ZPlus())
    assert graph.graph_depth == 1
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
    graph = GadgetGraph(num_qubits=1)
    graph.add(XMinus())
    assert graph.graph_depth == 1
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
    graph = GadgetGraph(num_qubits=1)
    graph.add(ZMinus())
    assert graph.graph_depth == 1
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
