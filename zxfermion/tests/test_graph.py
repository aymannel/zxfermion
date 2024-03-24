import pytest
from zxfermion.gadgets import XPhase, ZPhase, X, Z, ZPlus, XMinus, XPlus, ZMinus
from zxfermion.graph import BaseGraph


def test_graph():
    graph = BaseGraph(num_qubits=4)
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert list(graph.edges()) == [(0, 4), (1, 5), (2, 6), (3, 7)]
    assert graph.depth() == 1


@pytest.mark.parametrize('num_qubits', [1, 3, 5, 15, 50])
def test_graph_num_qubits(num_qubits):
    graph = BaseGraph(num_qubits=num_qubits)
    assert graph.num_qubits == num_qubits
    assert list(graph.inputs()) == list(range(num_qubits))
    assert list(graph.outputs()) == list(range(num_qubits, 2 * num_qubits))
    assert all(graph.connected(graph.inputs()[qubit], graph.outputs()[qubit]) for qubit in range(num_qubits))


@pytest.mark.parametrize('num_rows', range(1, 11))
def test_graph_num_rows(num_rows):
    graph = BaseGraph(num_qubits=4, num_rows=num_rows)
    assert graph.depth() == num_rows


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
def test_graph_remove_wire(qubit):
    graph = BaseGraph(num_qubits=4)
    graph.remove_wire(qubit=qubit)
    edges = [(0, 4), (1, 5), (2, 6), (3, 7)]
    edges.pop(qubit)
    assert list(graph.edges()) == edges


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize('num_nodes', range(10))
def test_graph_connect_nodes(qubit, num_nodes):
    graph = BaseGraph(num_qubits=4, num_rows=num_nodes)
    graph.remove_wire(qubit=qubit)
    node_refs = [graph.add_vertex(qubit=qubit, row=num + 1) for num in range(num_nodes)]
    graph.connect_nodes(qubit=qubit, node_refs=node_refs)
    assert graph.num_vertices() == num_nodes + 8
    assert graph.num_edges() == num_nodes + 4


@pytest.mark.parametrize('num_rows', range(10))
def test_graph_update_num_rows(num_rows):
    graph = BaseGraph(num_qubits=4, num_rows=1)
    assert graph.depth() == 1

    graph.update_num_rows(num_rows=num_rows)
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert list(graph.edges()) == [(0, 4), (1, 5), (2, 6), (3, 7)]
    assert graph.depth() == num_rows


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize(['gate', 'phase'], [[XPhase, 1/2], [XPhase, None], [ZPhase, 3/2], [ZPhase, None]])
def test_graph_add_phase_nodes(qubit, gate, phase):
    graph = BaseGraph(num_qubits=4)
    gate = gate(qubit=qubit, phase=phase)
    ref = graph.add_single(gate=gate)
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
@pytest.mark.parametrize('gate', [X, XPlus, XMinus, Z, ZPlus, ZMinus])
def test_graph_add_single_qubit_gates(qubit, gate):
    graph = BaseGraph(num_qubits=4)
    ref = graph.add_single(gate=gate(qubit=qubit))
    assert graph.depth() == 1
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert all(graph.connected(graph.inputs()[q], graph.outputs()[q]) for q in range(4) if qubit != qubit)
    assert graph.connected(graph.inputs()[qubit], ref)
    assert graph.connected(ref, graph.outputs()[qubit])


def test_graph_add_gadget():
    pass


def test_graph_add_expanded_gadget():
    pass


def test_graph_add_cx():
    pass


def test_graph_add_cz():
    pass


def test_graph_add_cx_gadget():
    pass


def test_graph_add_cz_gadget():
    pass


def test_graph_add_x_gadget():
    pass


def test_graph_add_z_gadget():
    pass


