from __future__ import annotations

from typing import Optional
from pyzx.graph.graph_s import GraphS
from zxfermion.gadgets import Gadget, CZ, CX, Z, X, ZPhase, XPlus, H, XMinus
from zxfermion.types import LegType, VertexType, EdgeType


class BaseGraph(GraphS):
    def __init__(self, num_qubits: int, num_rows: int = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    def remove_wire(self, qubit: int):
        if self.connected(self.inputs()[qubit], self.outputs()[qubit]):
            self.remove_edge((self.inputs()[qubit], self.outputs()[qubit]))

    def connect_nodes(self, qubit: int, node_refs: list[int]):
        def pair_list(items: list[int]) -> list[tuple[int, int]]:
            return [(items[idx], items[idx + 1]) for idx in range(len(items) - 1)]
        self.add_edges(pair_list([self.inputs()[qubit], *node_refs, self.outputs()[qubit]]))

    def add_node(self, node, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits)
        ref = graph.add_vertex(ty=node.vertex_type, row=1, qubit=node.qubit, phase=node.phase)
        graph.connect_nodes(qubit=node.qubit, node_refs=[ref])
        graph.remove_wire(node.qubit)
        return graph

    def add_gadget(self, gadget: Gadget, graph: Optional[BaseGraph] = None):
        identity_only = all(leg.type == LegType.I for leg in gadget.legs.values())
        phase_only = all(leg.type == LegType.Z or leg.type == LegType.I for leg in gadget.legs.values())

        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits, num_rows=2 if phase_only else 3)
        if not identity_only:
            hub_ref = graph.add_vertex(ty=VertexType.X, row=3, qubit=self.num_qubits + 1)
            phase_ref = graph.add_vertex(ty=VertexType.Z, row=3, qubit=self.num_qubits + 2, phase=gadget.phase)
            for qubit, leg in gadget.legs.items():
                match leg.type:
                    case LegType.X:
                        left_ref = graph.add_vertex(ty=VertexType.H, row=1, qubit=qubit)
                        middle_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                        right_ref = graph.add_vertex(ty=VertexType.H, row=3, qubit=qubit)
                        graph.connect_nodes(qubit=leg.qubit, node_refs=[left_ref, middle_ref, right_ref])
                        graph.add_edge((middle_ref, hub_ref))
                        graph.remove_wire(qubit=qubit)
                    case LegType.Y:
                        left_ref = graph.add_vertex(ty=VertexType.X, row=1, qubit=qubit, phase=1/2,)
                        middle_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                        right_ref = graph.add_vertex(ty=VertexType.X, row=3, qubit=qubit, phase=-1/2)
                        graph.connect_nodes(qubit=leg.qubit, node_refs=[left_ref, middle_ref, right_ref])
                        graph.add_edge((middle_ref, hub_ref))
                        graph.remove_wire(qubit=qubit)
                    case LegType.Z:
                        middle_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                        graph.connect_nodes(qubit=leg.qubit, node_refs=[middle_ref])
                        graph.add_edge((middle_ref, hub_ref))
                        graph.remove_wire(qubit=qubit)
            graph.add_edge((hub_ref, phase_ref))
        return graph

    def add_expanded_gadget(self, gadget: Gadget, graph: BaseGraph):
        clifford_left = BaseGraph(num_qubits=self.num_qubits)
        clifford_right = BaseGraph(num_qubits=self.num_qubits)

        for qubit, leg in gadget.legs.items():
            if leg.type == LegType.X:
                clifford_left = self.add_node(node=H(qubit), graph=clifford_left)
                clifford_right = self.add_node(node=H(qubit), graph=clifford_right)
            elif leg.type == LegType.Y:
                clifford_left = self.add_node(node=XPlus(qubit), graph=clifford_left)
                clifford_right = self.add_node(node=XMinus(qubit), graph=clifford_right)

        qubits = [qubit for qubit, leg in gadget.legs.items() if leg.type != LegType.I]
        ladder_left = BaseGraph(num_qubits=self.num_qubits)
        ladder_right = BaseGraph(num_qubits=self.num_qubits)
        ladder_middle = self.add_node(ZPhase(qubit=max(qubits), phase=gadget.phase))

        for left, right in zip(range(len(qubits) - 1), reversed(range(len(qubits) - 1))):
            ladder_left.compose(ladder_left.add_cx(CX(qubits[left], qubits[left + 1])))
            ladder_right.compose(ladder_right.add_cx(CX(qubits[right], qubits[right + 1])))

        graph = BaseGraph(num_qubits=self.num_qubits) if graph is None else graph
        graph.compose(clifford_left + ladder_left + ladder_middle + ladder_right + clifford_right)
        return graph

    def add_x_gadget(self, x: X, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits)
        ref = graph.add_vertex(ty=VertexType.X, row=1, qubit=x.qubit)
        hub_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=self.num_qubits + 1)
        phase_ref = graph.add_vertex(ty=VertexType.X, row=2, qubit=self.num_qubits + 2, phase=1)

        graph.remove_wire(qubit=x.qubit)
        graph.connect_nodes(qubit=x.qubit, node_refs=[ref])
        graph.add_edge((hub_ref, phase_ref))
        graph.add_edge((ref, hub_ref))
        return graph

    def add_z_gadget(self, z: Z, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits)
        ref = graph.add_vertex(ty=VertexType.Z, row=1, qubit=z.qubit)
        hub_ref = graph.add_vertex(ty=VertexType.X, row=2, qubit=self.num_qubits + 1)
        phase_ref = graph.add_vertex(ty=VertexType.Z, row=2, qubit=self.num_qubits + 2, phase=1)

        graph.remove_wire(qubit=z.qubit)
        graph.connect_nodes(qubit=z.qubit, node_refs=[ref])
        graph.add_edge((hub_ref, phase_ref))
        graph.add_edge((ref, hub_ref))
        return graph

    def add_cx(self, cx: CX, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits)
        control_ref = graph.add_vertex(ty=VertexType.Z, row=1, qubit=cx.control)
        target_ref = graph.add_vertex(ty=VertexType.X, row=1, qubit=cx.target)

        graph.connect_nodes(qubit=cx.control, node_refs=[control_ref])
        graph.connect_nodes(qubit=cx.target, node_refs=[target_ref])
        graph.add_edge((control_ref, target_ref))
        graph.remove_wire(cx.control)
        graph.remove_wire(cx.target)
        return graph

    def add_cz(self, cz: CZ, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits)
        control_ref = graph.add_vertex(ty=VertexType.Z, row=1, qubit=cz.control)
        target_ref = graph.add_vertex(ty=VertexType.Z, row=1, qubit=cz.target)

        graph.connect_nodes(qubit=cz.control, node_refs=[control_ref])
        graph.connect_nodes(qubit=cz.target, node_refs=[target_ref])
        graph.add_edge((control_ref, target_ref), edgetype=EdgeType.H)
        graph.remove_wire(cz.control)
        graph.remove_wire(cz.target)
        return graph

    def add_cx_gadget(self, cx: CX, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits, num_rows=2)
        hub_ref = graph.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=2)
        phase_ref = graph.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=2, phase=-1/2)
        control_ref = graph.add_vertex(ty=VertexType.Z, qubit=cx.control, row=1, phase=1/2)
        target_ref = graph.add_vertex(ty=VertexType.Z, qubit=cx.target, row=1, phase=1/2)
        left_had_ref = graph.add_vertex(ty=VertexType.H, qubit=cx.target, row=0)
        right_had_ref = graph.add_vertex(ty=VertexType.H, qubit=cx.target, row=2)

        graph.connect_nodes(qubit=cx.control, node_refs=[control_ref])
        graph.connect_nodes(qubit=cx.target, node_refs=[left_had_ref, target_ref, right_had_ref])
        graph.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        graph.remove_wire(cx.control)
        graph.remove_wire(cx.target)
        return graph

    def add_cz_gadget(self, cz: CZ, graph: Optional[BaseGraph] = None):
        graph = graph if graph else BaseGraph(num_qubits=self.num_qubits, num_rows=1)
        hub_ref = graph.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=2)
        phase_ref = graph.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=2, phase=-1/2)
        control_ref = graph.add_vertex(ty=VertexType.Z, qubit=cz.control, row=1, phase=1/2)
        target_ref = graph.add_vertex(ty=VertexType.Z, qubit=cz.target, row=1, phase=1/2)

        graph.connect_nodes(qubit=cz.control, node_refs=[control_ref])
        graph.connect_nodes(qubit=cz.target, node_refs=[target_ref])
        graph.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        graph.remove_wire(cz.control)
        graph.remove_wire(cz.target)
        return graph


