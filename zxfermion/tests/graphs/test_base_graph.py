from copy import copy

import pytest
from zxfermion.graphs.gadget_graph import GadgetGraph
from zxfermion.graphs.base_graph import BaseGraph
from .fixtures import (
    zzz, yzx, izzzi, zzz_padded, additional_padding,
    zzz_expanded, izzzi_expanded, zzz_expanded_unstacked,
)


def test0_base_graph_empty():
    graph = BaseGraph()
    assert graph.num_qubits == 1
    assert graph.num_edges() == 1
    assert graph.num_vertices() == 2
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.connected(0, 1)
    assert graph.boundaries == [0, 1]
    assert graph.min_qubit == 0
    assert graph.max_qubit == 0
    assert graph.input_row == 0
    assert graph.output_row == 2
    assert graph.left_row == 2
    assert graph.right_row == 0
    assert graph.graph_rows == []
    assert graph.graph_depth == 0
    assert graph.left_end(0) == 1
    assert graph.right_end(0) == 0
    assert len(graph.bounded_vertices) == 0
    assert len(graph.unbounded_vertices) == 0
    assert graph.vertices_on_qubit(0) == []


@pytest.mark.parametrize('num_rows', range(1, 11))
@pytest.mark.parametrize('num_qubits', [1, 3, 5, 15, 50])
def test1_base_graph_empty(num_rows, num_qubits):
    graph = BaseGraph(num_qubits=num_qubits, num_rows=num_rows)
    assert graph.num_qubits == num_qubits
    assert graph.num_edges() == num_qubits
    assert graph.num_vertices() == 2 * num_qubits
    assert list(graph.inputs()) == list(range(num_qubits))
    assert list(graph.outputs()) == list(range(num_qubits, 2 * num_qubits))
    assert all(graph.connected(in_ref, out_ref) for in_ref, out_ref in zip(graph.inputs(), graph.outputs()))
    assert graph.boundaries == list(range(2 * num_qubits))
    assert graph.min_qubit == 0
    assert graph.max_qubit == num_qubits - 1
    assert graph.input_row == 0
    assert graph.output_row == num_rows + 1
    assert graph.left_row == num_rows + 1
    assert graph.right_row == 0
    assert graph.graph_rows == []
    assert graph.graph_depth == 0
    assert all(graph.left_end(qubit) == graph.outputs()[qubit] for qubit in range(num_qubits))
    assert all(graph.right_end(qubit) == graph.inputs()[qubit] for qubit in range(num_qubits))
    assert len(graph.bounded_vertices) == 0
    assert len(graph.unbounded_vertices) == 0
    assert all(graph.vertices_on_qubit(qubit) == [] for qubit in range(num_qubits))


def test2_base_graph(zzz):
    graph = zzz
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 3
    assert graph.num_edges() == 10
    assert graph.num_vertices() == 11
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.boundaries == [0, 1, 2, 3, 4, 5]
    assert graph.min_qubit == 0
    assert graph.max_qubit == 2
    assert graph.input_row == 0
    assert graph.output_row == 2
    assert graph.left_row == 1
    assert graph.right_row == 1
    assert graph.left_padding == 1
    assert graph.right_padding == 1
    assert graph.graph_rows == [1]
    assert graph.graph_depth == 1
    assert graph.left_end(0) == 8
    assert graph.left_end(1) == 9
    assert graph.left_end(2) == 10
    assert graph.right_end(0) == 8
    assert graph.right_end(1) == 9
    assert graph.right_end(2) == 10
    assert len(graph.bounded_vertices) == 3
    assert len(graph.unbounded_vertices) == 2
    assert graph.vertices_on_qubit(0) == [8]
    assert graph.vertices_on_qubit(1) == [9]
    assert graph.vertices_on_qubit(2) == [10]


def test3_base_graph(yzx):
    assert isinstance(yzx, BaseGraph)
    graph = yzx
    assert graph.num_qubits == 3
    assert graph.num_edges() == 14
    assert graph.num_vertices() == 15
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.boundaries == [0, 1, 2, 3, 4, 5]
    assert graph.min_qubit == 0
    assert graph.max_qubit == 2
    assert graph.input_row == 0
    assert graph.output_row == 4
    assert graph.left_row == 1
    assert graph.right_row == 3
    assert graph.left_padding == 1
    assert graph.right_padding == 1
    assert graph.graph_rows == [1, 2, 3]
    assert graph.graph_depth == 3
    assert graph.left_end(0) == 8
    assert graph.left_end(1) == 11
    assert graph.left_end(2) == 12
    assert graph.right_end(0) == 10
    assert graph.right_end(1) == 11
    assert graph.right_end(2) == 14
    assert len(graph.bounded_vertices) == 7
    assert len(graph.unbounded_vertices) == 2
    assert graph.vertices_on_qubit(0) == [8, 9, 10]
    assert graph.vertices_on_qubit(1) == [11]
    assert graph.vertices_on_qubit(2) == [12, 13, 14]


def test4_base_graph(izzzi):
    graph = izzzi
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 5
    assert graph.num_edges() == 12
    assert graph.num_vertices() == 15
    assert list(graph.inputs()) == [0, 1, 2, 3, 4]
    assert list(graph.outputs()) == [5, 6, 7, 8, 9]
    assert graph.boundaries == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert graph.min_qubit == 1
    assert graph.max_qubit == 3
    assert graph.input_row == 0
    assert graph.output_row == 2
    assert graph.left_row == 1
    assert graph.right_row == 1
    assert graph.left_padding == 1
    assert graph.right_padding == 1
    assert graph.graph_rows == [1]
    assert graph.graph_depth == 1
    assert graph.left_end(0) == 5
    assert graph.left_end(1) == 12
    assert graph.left_end(2) == 13
    assert graph.left_end(3) == 14
    assert graph.left_end(4) == 9
    assert graph.right_end(0) == 0
    assert graph.right_end(1) == 12
    assert graph.right_end(2) == 13
    assert graph.right_end(3) == 14
    assert graph.right_end(4) == 4
    assert graph.left_row_within(0, 0) == 2
    assert graph.left_row_within(1, 3) == 1
    assert graph.left_row_within(4, 4) == 2
    assert graph.right_row_within(0, 0) == 0
    assert graph.right_row_within(1, 3) == 1
    assert graph.right_row_within(4, 4) == 0
    assert len(graph.bounded_vertices) == 3
    assert len(graph.unbounded_vertices) == 2
    assert graph.vertices_on_qubit(0) == []
    assert graph.vertices_on_qubit(1) == [12]
    assert graph.vertices_on_qubit(2) == [13]
    assert graph.vertices_on_qubit(3) == [14]
    assert graph.vertices_on_qubit(4) == []


@pytest.mark.parametrize('additional_padding', [1, 3, 5, 10, 15, 50], indirect=True)
def test5_base_graph(zzz_padded, additional_padding):
    graph = zzz_padded
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 3
    assert graph.num_edges() == 10
    assert graph.num_vertices() == 11
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.boundaries == [0, 1, 2, 3, 4, 5]
    assert graph.min_qubit == 0
    assert graph.max_qubit == 2
    assert graph.input_row == 0
    assert graph.output_row == 2 + 2 * additional_padding
    assert graph.left_row == 1 + additional_padding
    assert graph.right_row == 1 + additional_padding
    assert graph.left_padding == additional_padding + 1
    assert graph.right_padding == additional_padding + 1
    assert graph.graph_rows == [1 + additional_padding]
    assert graph.graph_depth == 1
    assert graph.left_end(0) == 8
    assert graph.left_end(1) == 9
    assert graph.left_end(2) == 10
    assert graph.right_end(0) == 8
    assert graph.right_end(1) == 9
    assert graph.right_end(2) == 10
    assert len(graph.bounded_vertices) == 3
    assert len(graph.unbounded_vertices) == 2
    assert graph.vertices_on_qubit(0) == [8]
    assert graph.vertices_on_qubit(1) == [9]
    assert graph.vertices_on_qubit(2) == [10]


def test6_base_graph(zzz_expanded):
    graph = zzz_expanded
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 3
    assert graph.num_edges() == 16
    assert graph.num_vertices() == 15
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.boundaries == [0, 1, 2, 3, 4, 5]
    assert graph.min_qubit == 0
    assert graph.max_qubit == 2
    assert graph.input_row == 0
    assert graph.output_row == 6
    assert graph.left_row == 1
    assert graph.right_row == 5
    assert graph.left_padding == 1
    assert graph.right_padding == 1
    assert graph.graph_rows == [1, 2, 3, 4, 5]
    assert graph.graph_depth == 5
    assert graph.left_end(0) == 6
    assert graph.left_end(1) == 7
    assert graph.left_end(2) == 9
    assert graph.right_end(0) == 12
    assert graph.right_end(1) == 13
    assert graph.right_end(2) == 11
    assert len(graph.bounded_vertices) == 9
    assert len(graph.unbounded_vertices) == 0
    assert graph.vertices_on_qubit(0) == [6, 12]
    assert graph.vertices_on_qubit(1) == [7, 8, 10, 13]
    assert graph.vertices_on_qubit(2) == [9, 14, 11]


def test7_base_graph(izzzi_expanded):
    graph = izzzi_expanded
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 5
    assert graph.num_edges() == 18
    assert graph.num_vertices() == 19
    assert list(graph.inputs()) == [0, 1, 2, 3, 4]
    assert list(graph.outputs()) == [5, 6, 7, 8, 9]
    assert graph.boundaries == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert graph.min_qubit == 1
    assert graph.max_qubit == 3
    assert graph.input_row == 0
    assert graph.output_row == 6
    assert graph.left_row == 1
    assert graph.right_row == 5
    assert graph.left_padding == 1
    assert graph.right_padding == 1
    assert graph.graph_rows == [1, 2, 3, 4, 5]
    assert graph.graph_depth == 5
    assert graph.left_end(0) == 5
    assert graph.left_end(1) == 10
    assert graph.left_end(2) == 11
    assert graph.left_end(3) == 13
    assert graph.left_end(4) == 9
    assert graph.right_end(0) == 0
    assert graph.right_end(1) == 16
    assert graph.right_end(2) == 17
    assert graph.right_end(3) == 15
    assert graph.right_end(4) == 4
    assert graph.left_row_within(0, 0) == 6
    assert graph.left_row_within(1, 3) == 1
    assert graph.left_row_within(4, 4) == 6
    assert graph.right_row_within(0, 0) == 0
    assert graph.right_row_within(1, 3) == 5
    assert graph.right_row_within(4, 4) == 0
    assert len(graph.bounded_vertices) == 9
    assert len(graph.unbounded_vertices) == 0
    assert graph.vertices_on_qubit(0) == []
    assert graph.vertices_on_qubit(1) == [10, 16]
    assert graph.vertices_on_qubit(2) == [11, 12, 14, 17]
    assert graph.vertices_on_qubit(3) == [13, 18, 15]
    assert graph.vertices_on_qubit(4) == []


def test8_base_graph(zzz_expanded_unstacked):
    graph = zzz_expanded_unstacked
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 6
    assert graph.num_edges() == 32
    assert graph.num_vertices() == 30
    assert graph.min_qubit == 0
    assert graph.max_qubit == 5
    assert graph.input_row == 0
    assert graph.output_row == 11
    assert graph.left_row == 1
    assert graph.right_row == 10
    assert graph.left_padding == 1
    assert graph.right_padding == 1
    assert graph.graph_rows == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert graph.graph_depth == 10
    assert graph.left_end(0) == 12
    assert graph.left_end(1) == 13
    assert graph.left_end(2) == 15
    assert graph.left_end(3) == 21
    assert graph.left_end(4) == 22
    assert graph.left_end(5) == 24
    assert graph.right_end(0) == 18
    assert graph.right_end(1) == 19
    assert graph.right_end(2) == 17
    assert graph.right_end(3) == 27
    assert graph.right_end(4) == 28
    assert graph.right_end(5) == 26
    assert graph.left_row_within(0, 2) == 1
    assert graph.left_row_within(2, 5) == 2
    assert graph.left_row_within(3, 5) == 6
    assert graph.right_row_within(0, 2) == 5
    assert graph.right_row_within(3, 5) == 10
    assert len(graph.bounded_vertices) == 18
    assert len(graph.unbounded_vertices) == 0
    assert graph.vertices_on_qubit(0) == [12, 18]
    assert graph.vertices_on_qubit(1) == [13, 14, 16, 19]
    assert graph.vertices_on_qubit(2) == [15, 20, 17]
    assert graph.vertices_on_qubit(3) == [21, 27]
    assert graph.vertices_on_qubit(4) == [22, 23, 25, 28]
    assert graph.vertices_on_qubit(5) == [24, 29, 26]


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
def test9_base_graph_remove_wire(qubit):
    graph = GadgetGraph(num_qubits=4)
    graph.remove_wire(qubit=qubit)
    edges = [(0, 4), (1, 5), (2, 6), (3, 7)]
    edges.pop(qubit)
    assert list(graph.edges()) == edges


@pytest.mark.parametrize('qubit', [0, 1, 2, 3])
@pytest.mark.parametrize('num_vertices', range(10))
def test10_base_graph_connect_vertices(qubit, num_vertices):
    graph = GadgetGraph(num_qubits=4, num_rows=num_vertices)
    graph.remove_wire(qubit=qubit)
    vertex_refs = [graph.add_vertex(qubit=qubit, row=num + 1) for num in range(num_vertices)]
    graph.connect_vertices([graph.inputs()[qubit], *vertex_refs, graph.outputs()[qubit]])
    assert graph.num_vertices() == num_vertices + 8
    assert graph.num_edges() == num_vertices + 4


@pytest.mark.parametrize('row', [-5, -1, 0, 1, 5])
def test11_base_graph_set_input_row(zzz, izzzi, zzz_expanded, izzzi_expanded, zzz_expanded_unstacked, row):
    for graph in [zzz, izzzi, zzz_expanded, izzzi_expanded, zzz_expanded_unstacked]:
        row_dict = {vertex: graph.row(vertex) for vertex in graph.bounded_vertices}
        qubit_dict = {vertex: graph.qubit(vertex) for vertex in graph.bounded_vertices}
        graph.set_input_row(row)
        assert all(graph.row(graph.inputs()[qubit]) == row for qubit in range(graph.num_qubits))
        assert {vertex: graph.row(vertex) for vertex in graph.bounded_vertices} == row_dict
        assert {vertex: graph.qubit(vertex) for vertex in graph.bounded_vertices} == qubit_dict


@pytest.mark.parametrize('row', [-5, -1, 0, 1, 5])
def test12_base_graph_set_output_row(zzz, izzzi, zzz_expanded, izzzi_expanded, zzz_expanded_unstacked, row):
    for graph in [zzz, izzzi, zzz_expanded, izzzi_expanded, zzz_expanded_unstacked]:
        row_dict = {vertex: graph.row(vertex) for vertex in graph.bounded_vertices}
        qubit_dict = {vertex: graph.qubit(vertex) for vertex in graph.bounded_vertices}
        graph.set_output_row(row)
        assert all(graph.row(graph.outputs()[qubit]) == row for qubit in range(graph.num_qubits))
        assert {vertex: graph.row(vertex) for vertex in graph.bounded_vertices} == row_dict
        assert {vertex: graph.qubit(vertex) for vertex in graph.bounded_vertices} == qubit_dict


@pytest.mark.parametrize('row', [5, -1, 0, 1, 5])
def test13_base_graph_set_graph_row(zzz, izzzi, zzz_expanded, izzzi_expanded, zzz_expanded_unstacked, row):
    for graph in [zzz, izzzi, zzz_expanded, izzzi_expanded, zzz_expanded_unstacked]:
        graph_depth = graph.graph_depth
        qubit_dict = {vertex: graph.qubit(vertex) for vertex in graph.vertices()}
        graph_rows = [r + row - 1 for r in copy(graph.graph_rows)]
        graph.set_graph_row(row)
        assert graph.left_row == row
        assert graph.graph_depth == graph_depth
        assert graph.right_row == row + graph_depth - 1
        assert graph.graph_rows == graph_rows
        assert {vertex: graph.qubit(vertex) for vertex in graph.vertices()} == qubit_dict


def test14_base_graph_set_left_padding():
    pass


def test15_base_graph_set_right_padding():
    pass


def test16_base_graph_set_num_qubits():
    pass


def test17_base_graph_set_update_num_qubits():
    pass


def test18_base_graph_compose():
    pass


def test19_base_graph_tikz():
    pass


def test20_base_graph_pdf():
    pass
