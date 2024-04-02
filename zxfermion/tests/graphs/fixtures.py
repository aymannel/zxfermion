import pytest
from pyzx import VertexType

from zxfermion import BaseGraph


@pytest.fixture
def additional_padding():
    return 1


@pytest.fixture
def zzz() -> BaseGraph:
    graph = BaseGraph(num_qubits=3, num_rows=1)
    hub_ref = graph.add_vertex(ty=VertexType.X, row=2, qubit=4)
    phase_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=5, phase=1/2)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in zip(graph.inputs(), graph.outputs())])
    m1 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=0)
    m2 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=1)
    m3 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=2)
    graph.add_edges([(graph.inputs()[0], m1), (m1, graph.outputs()[0])])
    graph.add_edges([(graph.inputs()[1], m2), (m2, graph.outputs()[1])])
    graph.add_edges([(graph.inputs()[2], m3), (m3, graph.outputs()[2])])
    graph.add_edge((hub_ref, phase_ref))
    graph.add_edge((m1, hub_ref))
    graph.add_edge((m2, hub_ref))
    graph.add_edge((m3, hub_ref))
    return graph


@pytest.fixture
def yzx() -> BaseGraph:
    graph = BaseGraph(num_qubits=3, num_rows=3)
    hub_ref = graph.add_vertex(ty=VertexType.X, row=3, qubit=4)
    phase_ref = graph.add_vertex(ty=VertexType.Z, row=3, qubit=5, phase=1/2)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in zip(graph.inputs(), graph.outputs())])
    l1 = graph.add_vertex(ty=VertexType.X, row=1, qubit=0, phase=1/2)
    m1 = graph.add_vertex(ty=VertexType.Z, row=2, qubit=0)
    r1 = graph.add_vertex(ty=VertexType.X, row=3, qubit=0, phase=-1/2)
    m2 = graph.add_vertex(ty=VertexType.Z, row=2, qubit=1)
    l3 = graph.add_vertex(ty=VertexType.H_BOX, row=1, qubit=2)
    m3 = graph.add_vertex(ty=VertexType.Z, row=2, qubit=2)
    r3 = graph.add_vertex(ty=VertexType.H_BOX, row=3, qubit=2)
    graph.add_edges([(graph.inputs()[0], l1), (l1, m1), (m1, r1), (r1, graph.outputs()[0])])
    graph.add_edges([(graph.inputs()[1], m2), (m2, graph.outputs()[1])])
    graph.add_edges([(graph.inputs()[2], l3), (l3, m3), (m3, r3), (r3, graph.outputs()[2])])
    graph.add_edge((hub_ref, phase_ref))
    graph.add_edge((m1, hub_ref))
    graph.add_edge((m2, hub_ref))
    graph.add_edge((m3, hub_ref))
    return graph


@pytest.fixture
def izzzi() -> BaseGraph:
    graph = BaseGraph(num_qubits=5, num_rows=1)
    hub_ref = graph.add_vertex(ty=VertexType.X, row=2, qubit=5)
    phase_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=6, phase=1/2)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in list(zip(graph.inputs(), graph.outputs()))[1:-1]])
    m1 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=1)
    m2 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=2)
    m3 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=3)
    graph.add_edges([(graph.inputs()[1], m1), (m1, graph.outputs()[1])])
    graph.add_edges([(graph.inputs()[2], m2), (m2, graph.outputs()[2])])
    graph.add_edges([(graph.inputs()[3], m3), (m3, graph.outputs()[3])])
    graph.add_edge((hub_ref, phase_ref))
    graph.add_edge((m1, hub_ref))
    graph.add_edge((m2, hub_ref))
    graph.add_edge((m3, hub_ref))
    return graph


@pytest.fixture
def zzz_padded(additional_padding) -> BaseGraph:
    graph = BaseGraph(num_qubits=3, num_rows=1 + 2 * additional_padding)
    hub_ref = graph.add_vertex(ty=VertexType.X, row=2 + additional_padding, qubit=4)
    phase_ref = graph.add_vertex(ty=VertexType.Z, row=2 + additional_padding, qubit=5, phase=1/2)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in zip(graph.inputs(), graph.outputs())])
    m1 = graph.add_vertex(ty=VertexType.Z, row=1 + additional_padding, qubit=0)
    m2 = graph.add_vertex(ty=VertexType.Z, row=1 + additional_padding, qubit=1)
    m3 = graph.add_vertex(ty=VertexType.Z, row=1 + additional_padding, qubit=2)
    graph.add_edges([(graph.inputs()[0], m1), (m1, graph.outputs()[0])])
    graph.add_edges([(graph.inputs()[1], m2), (m2, graph.outputs()[1])])
    graph.add_edges([(graph.inputs()[2], m3), (m3, graph.outputs()[2])])
    graph.add_edge((hub_ref, phase_ref))
    graph.add_edge((m1, hub_ref))
    graph.add_edge((m2, hub_ref))
    graph.add_edge((m3, hub_ref))
    return graph


@pytest.fixture
def zzz_expanded() -> BaseGraph:
    graph = BaseGraph(num_qubits=3, num_rows=5)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in zip(graph.inputs(), graph.outputs())])
    c1 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=0)
    t1 = graph.add_vertex(ty=VertexType.X, row=1, qubit=1)
    c2 = graph.add_vertex(ty=VertexType.Z, row=2, qubit=1)
    t2 = graph.add_vertex(ty=VertexType.X, row=2, qubit=2)
    c3 = graph.add_vertex(ty=VertexType.Z, row=4, qubit=1)
    t3 = graph.add_vertex(ty=VertexType.X, row=4, qubit=2)
    c4 = graph.add_vertex(ty=VertexType.Z, row=5, qubit=0)
    t4 = graph.add_vertex(ty=VertexType.X, row=5, qubit=1)
    hub = graph.add_vertex(ty=VertexType.Z, row=3, qubit=2, phase=1/2)

    graph.add_edges([
        (graph.inputs()[0], c1), (graph.inputs()[1], t1), (graph.inputs()[2], t2),
        (t3, graph.outputs()[2]), (t4, graph.outputs()[1]), (c4, graph.outputs()[0]),
        (t2, hub), (hub, t3), (c1, c4), (c2, c3), (c1, t1), (t1, c2), (c2, t2), (t3, c3), (c3, t4), (t4, c4)
    ])
    return graph


@pytest.fixture
def izzzi_expanded() -> BaseGraph:
    graph = BaseGraph(num_qubits=5, num_rows=5)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in list(zip(graph.inputs(), graph.outputs()))[1:-1]])
    c1 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=1)
    t1 = graph.add_vertex(ty=VertexType.X, row=1, qubit=2)
    c2 = graph.add_vertex(ty=VertexType.Z, row=2, qubit=2)
    t2 = graph.add_vertex(ty=VertexType.X, row=2, qubit=3)
    c3 = graph.add_vertex(ty=VertexType.Z, row=4, qubit=2)
    t3 = graph.add_vertex(ty=VertexType.X, row=4, qubit=3)
    c4 = graph.add_vertex(ty=VertexType.Z, row=5, qubit=1)
    t4 = graph.add_vertex(ty=VertexType.X, row=5, qubit=2)
    hub = graph.add_vertex(ty=VertexType.Z, row=3, qubit=3, phase=1/2)

    graph.add_edges([
        (graph.inputs()[1], c1), (graph.inputs()[2], t1), (graph.inputs()[3], t2),
        (t3, graph.outputs()[3]), (t4, graph.outputs()[2]), (c4, graph.outputs()[1]),
        (t2, hub), (hub, t3), (c1, c4), (c2, c3), (c1, t1), (t1, c2), (c2, t2), (t3, c3), (c3, t4), (t4, c4),
    ])
    return graph


@pytest.fixture
def zzz_expanded_unstacked():
    graph = BaseGraph(num_qubits=6, num_rows=10)
    graph.remove_edges([(in_ref, out_ref) for in_ref, out_ref in zip(graph.inputs(), graph.outputs())])
    c1 = graph.add_vertex(ty=VertexType.Z, row=1, qubit=0)
    t1 = graph.add_vertex(ty=VertexType.X, row=1, qubit=1)
    c2 = graph.add_vertex(ty=VertexType.Z, row=2, qubit=1)
    t2 = graph.add_vertex(ty=VertexType.X, row=2, qubit=2)
    c3 = graph.add_vertex(ty=VertexType.Z, row=4, qubit=1)
    t3 = graph.add_vertex(ty=VertexType.X, row=4, qubit=2)
    c4 = graph.add_vertex(ty=VertexType.Z, row=5, qubit=0)
    t4 = graph.add_vertex(ty=VertexType.X, row=5, qubit=1)
    hub = graph.add_vertex(ty=VertexType.Z, row=3, qubit=2, phase=1/2)

    graph.add_edges([
        (graph.inputs()[0], c1), (graph.inputs()[1], t1), (graph.inputs()[2], t2),
        (t3, graph.outputs()[2]), (t4, graph.outputs()[1]), (c4, graph.outputs()[0]),
        (t2, hub), (hub, t3), (c1, c4), (c2, c3), (c1, t1), (t1, c2), (c2, t2), (t3, c3), (c3, t4), (t4, c4)
    ])

    c1 = graph.add_vertex(ty=VertexType.Z, row=6, qubit=3)
    t1 = graph.add_vertex(ty=VertexType.X, row=6, qubit=4)
    c2 = graph.add_vertex(ty=VertexType.Z, row=7, qubit=4)
    t2 = graph.add_vertex(ty=VertexType.X, row=7, qubit=5)
    c3 = graph.add_vertex(ty=VertexType.Z, row=9, qubit=4)
    t3 = graph.add_vertex(ty=VertexType.X, row=9, qubit=5)
    c4 = graph.add_vertex(ty=VertexType.Z, row=10, qubit=3)
    t4 = graph.add_vertex(ty=VertexType.X, row=10, qubit=4)
    hub = graph.add_vertex(ty=VertexType.Z, row=8, qubit=5, phase=1/2)

    graph.add_edges([
        (graph.inputs()[3], c1), (graph.inputs()[4], t1), (graph.inputs()[5], t2),
        (t3, graph.outputs()[5]), (t4, graph.outputs()[4]), (c4, graph.outputs()[3]),
        (t2, hub), (hub, t3), (c1, c4), (c2, c3), (c1, t1), (t1, c2), (c2, t2), (t3, c3), (c3, t4), (t4, c4)
    ])
    return graph
