# test update_num_rows()
# test remove_wire()
import pytest

from zxfermion.graph import BaseGraph


def test_graph():
    graph = BaseGraph(num_qubits=4)
    assert graph.num_qubits == 4
    assert list(graph.inputs()) == [0, 1, 2, 3]
    assert list(graph.outputs()) == [4, 5, 6, 7]
    assert list(graph.edges()) == [(0, 4), (1, 5), (2, 6), (3, 7)]
    assert graph.depth() == 2


@pytest.parametrize('num_rows', [1, 2, 3, 4])
def test_graph_num_rows(num_rows):
    graph = BaseGraph(num_qubits=4, num_rows=num_rows)
    assert graph.depth() == num_rows + 1
