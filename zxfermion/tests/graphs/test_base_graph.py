import pytest
from pyzx import VertexType

from zxfermion.graphs.gadget_graph import GadgetGraph
from zxfermion.graphs.base_graph import BaseGraph


# fixtures
@pytest.fixture
def zzz_base_graph() -> BaseGraph:
    graph = BaseGraph(num_qubits=3, num_rows=1)
    hub_ref = graph.add_vertex(ty=VertexType.X, row=2, qubit=4)
    phase_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=5, phase=1/2)
    graph.add_edge((hub_ref, phase_ref))

    graph.remove_wire(0)
    m = graph.add_vertex(ty=VertexType.Z, row=1, qubit=0)
    graph.add_edges([(graph.inputs()[0], m), (m, graph.outputs()[0])])
    graph.add_edge((m, hub_ref))

    graph.remove_wire(1)
    m = graph.add_vertex(ty=VertexType.Z, row=1, qubit=1)
    graph.add_edges([(graph.inputs()[1], m), (m, graph.outputs()[1])])
    graph.add_edge((m, hub_ref))

    graph.remove_wire(2)
    m = graph.add_vertex(ty=VertexType.Z, row=1, qubit=2)
    graph.add_edges([(graph.inputs()[2], m), (m, graph.outputs()[2])])
    graph.add_edge((m, hub_ref))
    return graph


@pytest.fixture
def yzx_base_graph() -> BaseGraph:
    graph = BaseGraph(num_qubits=3, num_rows=3)
    hub_ref = graph.add_vertex(ty=VertexType.X, row=3, qubit=4)
    phase_ref = graph.add_vertex(ty=VertexType.Z, row=3, qubit=5, phase=1/2)
    graph.add_edge((hub_ref, phase_ref))

    graph.remove_wire(0)
    l = graph.add_vertex(ty=VertexType.X, row=1, qubit=0, phase=1/2)
    m = graph.add_vertex(ty=VertexType.Z, row=2, qubit=0)
    r = graph.add_vertex(ty=VertexType.X, row=3, qubit=0, phase=-1/2)
    graph.add_edges([(graph.inputs()[0], l), (l, m), (m, r), (r, graph.outputs()[0])])
    graph.add_edge((m, hub_ref))

    graph.remove_wire(1)
    m = graph.add_vertex(ty=VertexType.Z, row=2, qubit=1)
    graph.add_edges([(graph.inputs()[1], m), (m, graph.outputs()[1])])
    graph.add_edge((m, hub_ref))

    graph.remove_wire(2)
    l = graph.add_vertex(ty=VertexType.H_BOX, row=1, qubit=2)
    m = graph.add_vertex(ty=VertexType.Z, row=2, qubit=2)
    r = graph.add_vertex(ty=VertexType.H_BOX, row=3, qubit=2)
    graph.add_edges([(graph.inputs()[2], l), (l, m), (m, r), (r, graph.outputs()[2])])
    graph.add_edge((m, hub_ref))
    return graph


# BaseGraph tests
def test_default_empty_base_graph_dimensions():
    graph = BaseGraph()
    assert graph.input_row == 0
    assert graph.output_row == 2
    assert graph.graph_depth == 1
    assert graph.graph_rows == [1]
    assert graph.left_end(0) == 1
    assert graph.right_end(0) == 0
    assert graph.num_qubits == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.connected(0, 1)


@pytest.mark.parametrize('num_rows', range(1, 11))
@pytest.mark.parametrize('num_qubits', [1, 3, 5, 15, 50])
def test_empty_base_graph_dimensions(num_rows, num_qubits):
    graph = BaseGraph(num_qubits=num_qubits, num_rows=num_rows)
    assert graph.input_row == 0
    assert graph.output_row == num_rows + 1
    assert graph.graph_depth == num_rows
    assert graph.graph_rows == list(range(1, num_rows + 1))
    assert graph.left_end(0) == num_qubits
    assert graph.right_end(0) == 0
    assert graph.num_qubits == num_qubits
    assert list(graph.inputs()) == list(range(num_qubits))
    assert list(graph.outputs()) == list(range(num_qubits, 2 * num_qubits))
    assert all(graph.connected(graph.inputs()[qubit], graph.outputs()[qubit]) for qubit in range(num_qubits))


def test_zzz_base_graph_dimensions(zzz_base_graph):
    assert isinstance(zzz_base_graph, BaseGraph)
    assert zzz_base_graph.input_row == 0
    assert zzz_base_graph.output_row == 2
    assert zzz_base_graph.graph_depth == 1
    assert zzz_base_graph.graph_rows == [1]
    assert zzz_base_graph.num_qubits == 3
    assert list(zzz_base_graph.inputs()) == [0, 1, 2]
    assert list(zzz_base_graph.outputs()) == [3, 4, 5]


def test_yzx_base_graph_dimensions(yzx_base_graph):
    assert isinstance(yzx_base_graph, BaseGraph)
    assert yzx_base_graph.input_row == 0
    assert yzx_base_graph.output_row == 4
    assert yzx_base_graph.graph_depth == 3
    assert yzx_base_graph.graph_rows == [1, 2, 3]
    assert yzx_base_graph.num_qubits == 3
    assert list(yzx_base_graph.inputs()) == [0, 1, 2]
    assert list(yzx_base_graph.outputs()) == [3, 4, 5]


def test_base_graph_plugs():
    """Test left and right plugs using graph fixture with some empty wires."""
    pass


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
def test_base_graph_remove_wire(qubit):
    graph = GadgetGraph(num_qubits=4)
    graph.remove_wire(qubit=qubit)
    edges = [(0, 4), (1, 5), (2, 6), (3, 7)]
    edges.pop(qubit)
    assert list(graph.edges()) == edges


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize('num_vertices', range(10))
def test_base_graph_connect_vertices(qubit, num_vertices):
    graph = GadgetGraph(num_qubits=4, num_rows=num_vertices)
    graph.remove_wire(qubit=qubit)
    vertex_refs = [graph.add_vertex(qubit=qubit, row=num + 1) for num in range(num_vertices)]
    graph.connect_vertices([graph.inputs()[qubit], *vertex_refs, graph.outputs()[qubit]])
    assert graph.num_vertices() == num_vertices + 8
    assert graph.num_edges() == num_vertices + 4
