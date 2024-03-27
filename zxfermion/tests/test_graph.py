from typing import Union

import pytest
from pyzx import VertexType, EdgeType
from zxfermion.graph import GadgetGraph
from zxfermion.gadgets import Gadget, XPhase, ZPhase, X, Z, ZPlus, XMinus, XPlus, ZMinus, H, CX, CZ


# assert graph depth doesn't change when graph is larger than gadget size
# test increasingly large expanded gadgets. test expanded gadget that skips qubits

# tikz / pdf
# assert tex file is deleted after pdf generation


def test_graph():
    graph = GadgetGraph(num_qubits=4)
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert list(graph.edges()) == [(0, 4), (1, 5), (2, 6), (3, 7)]
    assert graph.depth() == 1


@pytest.mark.parametrize('num_qubits', [1, 3, 5, 15, 50])
def test_graph_num_qubits(num_qubits):
    graph = GadgetGraph(num_qubits=num_qubits)
    assert graph.num_qubits == num_qubits
    assert list(graph.inputs()) == list(range(num_qubits))
    assert list(graph.outputs()) == list(range(num_qubits, 2 * num_qubits))
    assert all(graph.connected(graph.inputs()[qubit], graph.outputs()[qubit]) for qubit in range(num_qubits))


@pytest.mark.parametrize('num_rows', range(1, 11))
def test_graph_num_rows(num_rows):
    graph = GadgetGraph(num_qubits=4, num_rows=num_rows)
    assert graph.depth() == num_rows


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
def test_graph_remove_wire(qubit):
    graph = GadgetGraph(num_qubits=4)
    graph.remove_wire(qubit=qubit)
    edges = [(0, 4), (1, 5), (2, 6), (3, 7)]
    edges.pop(qubit)
    assert list(graph.edges()) == edges


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize('num_nodes', range(10))
def test_graph_connect_nodes(qubit, num_nodes):
    graph = GadgetGraph(num_qubits=4, num_rows=num_nodes)
    graph.remove_wire(qubit=qubit)
    node_refs = [graph.add_vertex(qubit=qubit, row=num + 1) for num in range(num_nodes)]
    graph.connect_nodes(qubit=qubit, node_refs=node_refs)
    assert graph.num_vertices() == num_nodes + 8
    assert graph.num_edges() == num_nodes + 4


@pytest.mark.parametrize('num_rows', range(10))
def test_graph_update_num_rows(num_rows):
    graph = GadgetGraph(num_qubits=4, num_rows=1)
    assert graph.depth() == 1

    graph.update_num_rows(num_rows=num_rows)
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert list(graph.edges()) == [(0, 4), (1, 5), (2, 6), (3, 7)]
    assert graph.depth() == num_rows


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize(['gate', 'phase'], [[XPhase, 1/2], [XPhase, None], [ZPhase, 3/2], [ZPhase, None]])
def test_graph_add_phase_nodes(qubit, gate: Union[type[XPhase], type[ZPhase]], phase):
    graph = GadgetGraph(num_qubits=4)
    gate = gate(qubit=qubit, phase=phase)
    ref = graph.add_single_gate(gate=gate)
    assert graph.depth() == 1
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert all(graph.connected(graph.inputs()[q], graph.outputs()[q]) for q in range(4) if qubit != qubit)
    assert graph.connected(graph.inputs()[qubit], ref)
    assert graph.connected(ref, graph.outputs()[qubit])
    assert graph.type(8) == gate.vertex_type
    assert graph.phase(8) == 0 if phase is None else phase


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize('gate', [X, XPlus, XMinus, Z, ZPlus, ZMinus, H])
def test_graph_add_single_qubit_gates(qubit, gate):
    graph = GadgetGraph(num_qubits=4)
    ref = graph.add_single_gate(gate=gate(qubit=qubit))
    assert graph.depth() == 1
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert all(graph.connected(graph.inputs()[q], graph.outputs()[q]) for q in range(4) if qubit != qubit)
    assert graph.connected(graph.inputs()[qubit], ref)
    assert graph.connected(ref, graph.outputs()[qubit])


def test_graph_add_gadget():
    gadget = Gadget('XYZ', 1/2)
    graph = GadgetGraph(num_qubits=3)
    graph.add_gadget(gadget)
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


def test_graph_add_expanded_gadget():
    gadget = Gadget('YZX', 1/2)
    graph = GadgetGraph(num_qubits=3)
    graph.add_expanded_gadget(gadget)
    assert graph.depth() == 7
    assert graph.num_qubits == gadget.max_qubit + 1
    assert graph.num_vertices() == 19
    assert graph.num_edges() == 20
    assert graph.num_inputs() == 3
    assert graph.num_outputs() == 3
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [26, 27, 28]
    assert graph.type(6) == VertexType.X
    assert graph.type(7) == VertexType.H_BOX
    assert graph.type(8) == VertexType.Z
    assert graph.type(9) == VertexType.X
    assert graph.type(13) == VertexType.Z
    assert graph.type(14) == VertexType.X
    assert graph.type(18) == VertexType.Z
    assert graph.type(19) == VertexType.Z
    assert graph.type(20) == VertexType.X
    assert graph.type(24) == VertexType.Z
    assert graph.type(25) == VertexType.X
    assert graph.type(29) == VertexType.X
    assert graph.type(30) == VertexType.H_BOX
    assert graph.phase(18) == 1/2


def test_graph_add_cx():
    cx = CX(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cx(cx)
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


def test_graph_add_cz():
    cz = CZ(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cz(cz)
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


def test_graph_add_cx_gadget():
    cx = CX(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cx_gadget(cx)
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 3
    assert graph.num_qubits == cx.max_qubit + 1
    assert graph.num_vertices() == 10
    assert graph.num_edges() == 9
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.X
    assert graph.type(5) == VertexType.Z
    assert graph.type(6) == VertexType.Z
    assert graph.type(7) == VertexType.Z
    assert graph.type(8) == VertexType.H_BOX
    assert graph.type(9) == VertexType.H_BOX
    assert graph.phase(5) == 3/2
    assert graph.phase(6) == 1/2
    assert graph.phase(7) == 1/2
    assert graph.connected(4, 6)
    assert graph.connected(4, 7)
    assert graph.connected(7, 8)
    assert graph.connected(7, 9)
    assert graph.connected(graph.inputs()[0], 6)
    assert graph.connected(graph.inputs()[1], 8)
    assert graph.connected(6, graph.outputs()[0])
    assert graph.connected(9, graph.outputs()[1])


def test_graph_add_cz_gadget():
    cz = CZ(control=0, target=1)
    graph = GadgetGraph(num_qubits=2)
    graph.add_cz_gadget(cz)
    assert isinstance(graph, GadgetGraph)
    assert graph.depth() == 1
    assert graph.num_qubits == cz.max_qubit + 1
    assert graph.num_vertices() == 8
    assert graph.num_edges() == 7
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.X
    assert graph.type(5) == VertexType.Z
    assert graph.type(6) == VertexType.Z
    assert graph.type(7) == VertexType.Z
    assert graph.phase(5) == 3/2
    assert graph.phase(6) == 1/2
    assert graph.phase(7) == 1/2
    assert graph.connected(4, 6)
    assert graph.connected(4, 7)
    assert graph.connected(graph.inputs()[0], 6)
    assert graph.connected(graph.inputs()[1], 7)
    assert graph.connected(6, graph.outputs()[0])
    assert graph.connected(7, graph.outputs()[1])


def test_graph_add_x_phase():
    x_phase = XPhase(phase=3/4)
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(x_phase)
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


def test_graph_add_z_phase():
    z_phase = ZPhase(phase=3/4)
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(z_phase)
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
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(X())
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
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(Z())
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
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(XPlus())
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
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(ZPlus())
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
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(XMinus())
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
    graph = GadgetGraph(num_qubits=1)
    graph.add_single_gate(ZMinus())
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
