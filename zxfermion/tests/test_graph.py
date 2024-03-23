from pyzx import VertexType, EdgeType

from zxfermion.gadgets import Gadget, CX, CZ, X, Z
from zxfermion.graph import BaseGraph


# test update_num_rows()
# test remove_wire()


def test_gadget():
    gadget = Gadget(pauli_str='XYZ', phase=1/2)
    graph = gadget.graph(expand=False)
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == gadget.max_qubit + 1
    assert graph.num_vertices() == 15
    assert graph.num_edges() == 14
    assert graph.num_inputs() == 3
    assert graph.num_outputs() == 3
    assert list(graph.inputs()) == [0, 1, 2]
    assert list(graph.outputs()) == [3, 4, 5]
    assert graph.type(6) == VertexType.X
    assert graph.type(7) == VertexType.Z
    assert graph.type(8) == VertexType.H_BOX
    assert graph.type(9) == VertexType.Z
    assert graph.type(10) == VertexType.H_BOX
    assert graph.type(11) == VertexType.X
    assert graph.type(12) == VertexType.Z
    assert graph.type(13) == VertexType.X
    assert graph.type(14) == VertexType.Z
    assert graph.phase(7) == 1/2


def test_expanded_gadget():
    gadget = Gadget(pauli_str='XYZ', phase=1/2)
    graph = gadget.graph(expand=True)
    assert isinstance(graph, BaseGraph)
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


def test_cx():
    cx = CX(control=0, target=1)
    graph = cx.graph()
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == cx.max_qubit + 1
    assert graph.num_vertices() == 6
    assert graph.num_edges() == 5
    assert graph.num_inputs() == 2
    assert graph.num_outputs() == 2
    assert list(graph.inputs()) == [0, 1]
    assert list(graph.outputs()) == [2, 3]
    assert graph.type(4) == VertexType.Z
    assert graph.type(5) == VertexType.X


def test_cz():
    cz = CZ(control=0, target=1)
    graph = cz.graph()
    assert isinstance(graph, BaseGraph)
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


def test_x():
    x = X(qubit=0)
    graph = x.graph()
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.X
    assert graph.phase(2) == 1


def test_z():
    z = Z(qubit=0)
    graph = z.graph()
    assert isinstance(graph, BaseGraph)
    assert graph.num_qubits == 1
    assert graph.num_vertices() == 3
    assert graph.num_edges() == 2
    assert graph.num_inputs() == 1
    assert graph.num_outputs() == 1
    assert list(graph.inputs()) == [0]
    assert list(graph.outputs()) == [1]
    assert graph.type(2) == VertexType.Z
    assert graph.phase(2) == 1
