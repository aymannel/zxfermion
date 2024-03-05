from zxfermion.helpers import pair_list
from pyzx.graph.graph_s import GraphS

from zxfermion.types import Node, EdgeType, VertexType, LegType


class BaseGraph(GraphS):
    def __init__(self, num_qubits: int, num_rows: int = 0):
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


class GadgetGraph(BaseGraph):
    def __init__(self, gadget):
        super().__init__(num_qubits=gadget.num_qubits, num_rows=3)
        self.num_qubits = gadget.num_qubits
        self.gadget = gadget

        if non_identity_legs := {qubit: leg for qubit, leg in self.gadget.legs.items() if leg.type != LegType.I}:
            self.hub_ref = self.add_node(node=gadget.hub_node)
            self.phase_ref = self.add_node(node=gadget.phase_node)
            self.add_edge((self.hub_ref, self.phase_ref))

            for qubit, leg in non_identity_legs.items():
                node_refs = [self.add_node(node) for node in leg.nodes]
                middle_ref = node_refs[1] if leg.left else node_refs[0]
                self.connect_nodes(qubit=leg.qubit, node_refs=node_refs)
                self.add_edge((middle_ref, self.hub_ref))
                self.remove_wire(qubit=qubit)


class CliffordGraph(BaseGraph):
    def __init__(self, num_qubits: int, clifford: Node):
        super().__init__(num_qubits=num_qubits, num_rows=1)
        self.connect_nodes(qubit=clifford.qubit, node_refs=[self.add_node(node=clifford)])
        self.remove_wire(clifford.qubit)


class CliffordMultiQubit(BaseGraph):
    def __init__(self, num_qubits: int, control: Node, target: Node, edge_type: EdgeType):
        super().__init__(num_qubits=num_qubits, num_rows=1)
        self.connect_nodes(qubit=control.qubit, node_refs=[(control_ref := self.add_node(node=control))])
        self.connect_nodes(qubit=target.qubit, node_refs=[(target_ref := self.add_node(node=target))])
        self.add_edge((control_ref, target_ref), edgetype=edge_type)
        self.remove_wire(control.qubit)
        self.remove_wire(target.qubit)


class CXGraph(CliffordMultiQubit):
    def __init__(self, num_qubits: int, control_qubit: int, target_qubit: int):
        control = Node(type=VertexType.Z, row=1, qubit=control_qubit)
        target = Node(type=VertexType.X, row=1, qubit=target_qubit)
        super().__init__(num_qubits=num_qubits, control=control, target=target, edge_type=EdgeType.S)


class CZGraph(CliffordMultiQubit):
    def __init__(self, num_qubits: int, control_qubit: int, target_qubit: int):
        control = Node(type=VertexType.Z, row=1, qubit=control_qubit)
        target = Node(type=VertexType.Z, row=1, qubit=target_qubit)
        super().__init__(num_qubits=num_qubits, control=control, target=target, edge_type=EdgeType.H)
