from pyzx.graph.graph_s import GraphS

from zxfermion.gadgets import Gadget, CX, CZ
from zxfermion.helpers import pair_list
from zxfermion.types import LegType, VertexType, Node


class BaseGraph(GraphS):
    def __init__(self, num_qubits: int, num_rows: int = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    def add_node(self, node) -> int:
        return self.add_vertex(ty=node.type, row=node.row, qubit=node.qubit, phase=node.phase)

    def remove_wire(self, qubit: int):
        if self.connected(self.inputs()[qubit], self.outputs()[qubit]):
            self.remove_edge((self.inputs()[qubit], self.outputs()[qubit]))

    def connect_nodes(self, qubit: int, node_refs: list[int]):
        self.add_edges(pair_list([self.inputs()[qubit], *node_refs, self.outputs()[qubit]]))

    def add_gadget(self, gadget: Gadget):
        graph = BaseGraph(num_qubits=self.num_qubits, num_rows=3)
        if legs := {qubit: leg for qubit, leg in gadget.legs.items() if leg.type != LegType.I}:
            hub_ref = graph.add_node(node=Node(type=VertexType.X, row=3, qubit=self.num_qubits + 1))
            phase_ref = graph.add_node(node=Node(type=VertexType.Z, row=3, qubit=self.num_qubits + 2, phase=gadget.phase))
            graph.add_edge((hub_ref, phase_ref))

            for qubit, leg in legs.items():
                node_refs = [graph.add_node(node) for node in leg.nodes]
                middle_ref = node_refs[1] if leg.left else node_refs[0]
                graph.connect_nodes(qubit=leg.qubit, node_refs=node_refs)
                graph.add_edge((middle_ref, hub_ref))
                graph.remove_wire(qubit=qubit)
        self.compose(graph)

    def add_cx(self, cx: CX):
        graph = BaseGraph(num_qubits=self.num_qubits)
        graph.connect_nodes(qubit=cx.control.qubit, node_refs=[(control_ref := graph.add_node(node=cx.control))])
        graph.connect_nodes(qubit=cx.target.qubit, node_refs=[(target_ref := graph.add_node(node=cx.target))])
        graph.add_edge((control_ref, target_ref))
        graph.remove_wire(cx.control.qubit)
        graph.remove_wire(cx.target.qubit)
        self.compose(graph)

    def add_cz(self, cz: CZ):
        graph = BaseGraph(num_qubits=self.num_qubits)
        graph.connect_nodes(qubit=cz.control.qubit, node_refs=[(control_ref := graph.add_node(node=cz.control))])
        graph.connect_nodes(qubit=cz.target.qubit, node_refs=[(target_ref := graph.add_node(node=cz.target))])
        graph.add_edge((control_ref, target_ref))
        graph.remove_wire(cz.control.qubit)
        graph.remove_wire(cz.target.qubit)
        self.compose(graph)

    def add_cx_gadget(self, cx: CX):
        hub_node = Node(type=VertexType.X, qubit=self.num_qubits + 1, row=2)
        phase_node = Node(type=VertexType.Z, qubit=self.num_qubits + 2, row=2, phase=-1/2)
        control_node = Node(type=VertexType.Z, qubit=cx.control.qubit, row=1, phase=1/2)
        target_node = Node(type=VertexType.Z, qubit=cx.target.qubit, row=1, phase=1/2)

        graph = BaseGraph(num_qubits=self.num_qubits, num_rows=3)
        graph.connect_nodes(qubit=cx.control.qubit, node_refs=[(control_ref := graph.add_node(node=control_node))])
        graph.connect_nodes(qubit=cx.target.qubit, node_refs=[
            (graph.add_node(Node(type=VertexType.H, row=0, qubit=cx.target.qubit))),
            (target_ref := graph.add_node(node=target_node)),
            (graph.add_node(Node(type=VertexType.H, row=2, qubit=cx.target.qubit))),
        ])
        graph.remove_wire(cx.control.qubit)
        graph.remove_wire(cx.target.qubit)
        graph.add_edges((
            (hub_ref := graph.add_node(hub_node), graph.add_node(phase_node)),
            (hub_ref, control_ref),
            (hub_ref, target_ref)))
        self.compose(graph)

    def add_cz_gadget(self, cz: CZ):
        hub_node = Node(type=VertexType.X, qubit=self.num_qubits + 1, row=2)
        phase_node = Node(type=VertexType.Z, qubit=self.num_qubits + 2, row=2, phase=-1/2)
        control_node = Node(type=VertexType.Z, qubit=cz.control.qubit, row=1, phase=1/2)
        target_node = Node(type=VertexType.Z, qubit=cz.target.qubit, row=1, phase=1/2)

        graph = BaseGraph(num_qubits=self.num_qubits, num_rows=3)
        graph.connect_nodes(qubit=cz.control.qubit, node_refs=[(control_ref := graph.add_node(node=control_node))])
        graph.connect_nodes(qubit=cz.target.qubit, node_refs=[(target_ref := graph.add_node(node=target_node))])
        graph.remove_wire(cz.control.qubit)
        graph.remove_wire(cz.target.qubit)
        graph.add_edges((
            (hub_ref := graph.add_node(hub_node), graph.add_node(phase_node)),
            (hub_ref, control_ref),
            (hub_ref, target_ref)))
        self.compose(graph)


