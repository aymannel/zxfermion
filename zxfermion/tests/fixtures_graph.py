import pytest
from pyzx import VertexType

from zxfermion.gates import Gadget
from zxfermion.graph import BaseGraph, GadgetGraph


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
