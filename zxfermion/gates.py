from typing import Optional, Union

from zxfermion.graph import BaseGraph
from zxfermion.types import Node, VertexType, EdgeType, GateType


class CX:
    def __init__(self, control: int, target: int, num_qubits: Optional[int] = None):
        assert control != target
        self.type = GateType.CX
        self.num_qubits = num_qubits
        self.control = Node(type=VertexType.Z, qubit=control, row=1)
        self.target = Node(type=VertexType.X, qubit=target, row=1)

    def conjugate_x(self, **kwargs):
        """Need to rethink this business..."""
        pass

    def conjugate_z(self, **kwargs):
        pass

    def conjugate_cx(self, **kwargs):
        pass

    def conjugate_cz(self, **kwargs):
        pass

    def graph(self, num_qubits: int) -> BaseGraph:
        graph = BaseGraph(num_qubits=num_qubits)
        graph.connect_nodes(qubit=self.control.qubit, node_refs=[(control_ref := graph.add_node(node=self.control))])
        graph.connect_nodes(qubit=self.target.qubit, node_refs=[(target_ref := graph.add_node(node=self.target))])
        graph.add_edge((control_ref, target_ref))
        graph.remove_wire(self.control.qubit)
        graph.remove_wire(self.target.qubit)
        return graph

    def gadget(self, num_qubits: int) -> BaseGraph:
        hub_node = Node(type=VertexType.X, qubit=num_qubits + 1, row=2)
        phase_node = Node(type=VertexType.Z, qubit=num_qubits + 2, row=2, phase=-1/2)
        control_node = Node(type=VertexType.Z, qubit=self.control.qubit, row=1, phase=1/2)
        target_node = Node(type=VertexType.Z, qubit=self.target.qubit, row=1, phase=1/2)

        graph = BaseGraph(num_qubits=num_qubits, num_rows=3)
        graph.connect_nodes(qubit=self.control.qubit, node_refs=[(control_ref := graph.add_node(node=control_node))])
        graph.connect_nodes(qubit=self.target.qubit, node_refs=[
            (graph.add_node(Node(type=VertexType.H, row=0, qubit=self.target.qubit))),
            (target_ref := graph.add_node(node=target_node)),
            (graph.add_node(Node(type=VertexType.H, row=2, qubit=self.target.qubit))),
        ])
        graph.remove_wire(self.control.qubit)
        graph.remove_wire(self.target.qubit)
        graph.add_edges((
            (hub_ref := graph.add_node(hub_node), graph.add_node(phase_node)),
            (hub_ref, control_ref),
            (hub_ref, target_ref)))
        return graph

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control.qubit, self.target.qubit) == (other.control.qubit, other.target.qubit)
        else:
            return False


class CZ:
    def __init__(self, control: int, target: int, num_qubits: Optional[int] = None):
        assert control != target
        self.type = GateType.CZ
        self.num_qubits = num_qubits
        self.control = Node(type=VertexType.Z, qubit=control, row=1)
        self.target = Node(type=VertexType.Z, qubit=target, row=1)

    def conjugate_x(self, **kwargs):
        pass

    def conjugate_z(self, **kwargs):
        pass

    def conjugate_cx(self, **kwargs):
        pass

    def conjugate_cz(self, **kwargs):
        pass

    def graph(self, num_qubits: int) -> BaseGraph:
        graph = BaseGraph(num_qubits=num_qubits)
        graph.connect_nodes(qubit=self.control.qubit, node_refs=[(control_ref := graph.add_node(node=self.control))])
        graph.connect_nodes(qubit=self.target.qubit, node_refs=[(target_ref := graph.add_node(node=self.target))])
        graph.add_edge((control_ref, target_ref), edgetype=EdgeType.H)
        graph.remove_wire(self.control.qubit)
        graph.remove_wire(self.target.qubit)
        return graph

    def gadget(self, num_qubits: int) -> BaseGraph:
        hub_node = Node(type=VertexType.X, qubit=num_qubits + 1, row=2)
        phase_node = Node(type=VertexType.Z, qubit=num_qubits + 2, row=2, phase=-1/2)
        control_node = Node(type=VertexType.Z, qubit=self.control.qubit, row=1, phase=1/2)
        target_node = Node(type=VertexType.Z, qubit=self.target.qubit, row=1, phase=1/2)

        graph = BaseGraph(num_qubits=num_qubits, num_rows=3)
        graph.connect_nodes(qubit=self.control.qubit, node_refs=[(control_ref := graph.add_node(node=control_node))])
        graph.connect_nodes(qubit=self.target.qubit, node_refs=[(target_ref := graph.add_node(node=target_node))])
        graph.remove_wire(self.control.qubit)
        graph.remove_wire(self.target.qubit)
        graph.add_edges((
            (hub_ref := graph.add_node(hub_node), graph.add_node(phase_node)),
            (hub_ref, control_ref),
            (hub_ref, target_ref)))
        return graph

    def __eq__(self, other):
        if self.type == other.type:
            return (self.control.qubit, self.target.qubit) == (other.control.qubit, other.target.qubit)
        else:
            return False


class Z(Node):
    def __init__(self, qubit: int, num_qubits: Optional[int] = None):
        self.num_qubits = num_qubits
        super().__init__(
            row=1,
            qubit=qubit,
            type=VertexType.Z,
            phase=1
        )


class X(Node):
    def __init__(self, qubit: int, num_qubits: Optional[int] = None):
        self.num_qubits = num_qubits
        super().__init__(
            row=1,
            qubit=qubit,
            type=VertexType.X,
            phase=1
        )

    def conjugate_x(self, qubit: int):
        pass


class S(Node):
    def __init__(self, qubit: int, num_qubits: Optional[int] = None):
        self.num_qubits = num_qubits
        super().__init__(
            row=1,
            qubit=qubit,
            type=VertexType.X,
            phase=1/2
        )
