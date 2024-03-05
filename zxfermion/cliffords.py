from pydantic import BaseModel

from zxfermion.graphs import CZGraph, CXGraph, CliffordGraph
from zxfermion.types import Node, VertexType


class CX(BaseModel):
    control: int
    target: int

    def graph(self, num_qubits: int) -> CXGraph:
        return CXGraph(num_qubits=num_qubits, control_qubit=self.control, target_qubit=self.target)


class CZ(BaseModel):
    control: int
    target: int

    def graph(self, num_qubits: int) -> CZGraph:
        return CZGraph(num_qubits=num_qubits, control_qubit=self.control, target_qubit=self.target)


class X(Node):
    def __init__(self, qubit: int):
        super().__init__(qubit=qubit, row=1, type=VertexType.X, phase=1)

    def graph(self, num_qubits: int) -> CliffordGraph:
        return CliffordGraph(clifford=self, num_qubits=num_qubits)
