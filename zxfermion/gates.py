from typing import Optional

from zxfermion.types import Node, VertexType


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
