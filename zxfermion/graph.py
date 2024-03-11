from pyzx.graph.graph_s import GraphS
from zxfermion.helpers import pair_list


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
