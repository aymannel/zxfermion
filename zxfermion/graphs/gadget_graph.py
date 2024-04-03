from __future__ import annotations

from typing import Optional

from pyzx import VertexType

from zxfermion.gates import XPhase, ZPhase
from zxfermion import Gadget
from zxfermion.gates.gates import XPlus, XMinus, H, CX, CZ, PhaseVar
from zxfermion.graphs.base_graph import BaseGraph
from zxfermion.types import PauliType, GateType


class GadgetGraph(BaseGraph):
    def __init__(self, num_qubits: Optional[int] = 1, num_rows: Optional[int] = 1):
        super().__init__(num_qubits=num_qubits, num_rows=num_rows)

    def add(self, gate: XPhase | ZPhase | H, row: Optional[int] = None):
        self.update_num_qubits(gate.qubit + 1)
        in_ref, out_ref = self.right_end(gate.qubit), self.outputs()[gate.qubit]
        ref = self.add_vertex(
            ty=gate.vertex_type,
            qubit=gate.qubit,
            phase=gate.phase,
            row=self.row(in_ref) + 1 if row is None else row)
        if gate.type in [GateType.X_PHASE, GateType.Z_PHASE] and gate.var is not None:
            self.set_vdata(ref, 'var', gate.var)
        self.remove_edge((in_ref, out_ref))
        self.connect_vertices([in_ref, ref, out_ref])
        self.set_left_padding()
        self.set_right_padding()
        return ref

    def add_cx(self, cx: CX, stack: Optional[bool] = None):
        self.update_num_qubits(max(cx.qubits) + 1)
        in_ref1, out_ref1 = self.right_end(cx.control), self.outputs()[cx.control]
        in_ref2, out_ref2 = self.right_end(cx.target), self.outputs()[cx.target]
        row = self.right_row_within(min(cx.qubits), max(cx.qubits)) + 1 if stack else self.right_row + 1
        control = self.add_vertex(ty=VertexType.Z, row=row, qubit=cx.control)
        target = self.add_vertex(ty=VertexType.X, row=row, qubit=cx.target)
        self.remove_edges(((in_ref1, out_ref1), (in_ref2, out_ref2)))
        self.connect_vertices([in_ref1, control, out_ref1])
        self.connect_vertices([in_ref2, target, out_ref2])
        self.connect_vertices([control, target])
        self.set_left_padding()
        self.set_right_padding()

    def add_cz(self, cz: CZ, stack: Optional[bool] = None):
        self.update_num_qubits(max(cz.qubits) + 1)
        in_ref1, out_ref1 = self.right_end(cz.control), self.outputs()[cz.control]
        in_ref2, out_ref2 = self.right_end(cz.target), self.outputs()[cz.target]
        row = self.right_row_within(min(cz.qubits), max(cz.qubits)) + 1 if stack else self.right_row + 1
        control = self.add_vertex(ty=VertexType.Z, row=row, qubit=cz.control)
        target = self.add_vertex(ty=VertexType.Z, row=row, qubit=cz.target)
        hadamard = self.add_vertex(ty=VertexType.H_BOX, row=row, qubit=(min(cz.qubits) + max(cz.qubits)) / 2)
        self.remove_edges(((in_ref1, out_ref1), (in_ref2, out_ref2)))
        self.connect_vertices([in_ref1, control, out_ref1])
        self.connect_vertices([in_ref2, target, out_ref2])
        self.connect_vertices((control, hadamard, target))
        self.set_left_padding()
        self.set_right_padding()

    def add_cx_gadget(self, cx: CX, stack: Optional[bool] = None):
        self.update_num_qubits(max(cx.qubits) + 1)
        in_ref1, out_ref1 = self.right_end(cx.control), self.outputs()[cx.control]
        in_ref2, out_ref2 = self.right_end(cx.target), self.outputs()[cx.target]
        row = self.right_row_within(min(cx.qubits), max(cx.qubits)) + 1 if stack else self.right_row + 1
        control = self.add_vertex(ty=VertexType.Z, qubit=cx.control, row=row + 1, phase=1/2)
        target = self.add_vertex(ty=VertexType.Z, qubit=cx.target, row=row + 1, phase=1/2)
        hadamard1 = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=row)
        hadamard2 = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=row + 2)
        phase = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=row + 2, phase=-1/2)
        hub = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=row + 2)
        self.remove_edges(((in_ref1, out_ref1), (in_ref2, out_ref2)))
        self.connect_vertices([in_ref2, hadamard1, target, hadamard2, out_ref2])
        self.add_edges(((hub, phase), (hub, control), (hub, target)))
        self.connect_vertices([in_ref1, control, out_ref1])
        self.set_left_padding()
        self.set_right_padding()

    def add_cz_gadget(self, cz: CZ, stack: Optional[bool] = None):
        self.update_num_qubits(max(cz.qubits) + 1)
        in_ref1, out_ref1 = self.right_end(cz.control), self.outputs()[cz.control]
        in_ref2, out_ref2 = self.right_end(cz.target), self.outputs()[cz.target]
        row = self.right_row_within(min(cz.qubits), max(cz.qubits)) + 2 if stack else self.right_row + 2
        control = self.add_vertex(ty=VertexType.Z, qubit=cz.control, row=row, phase=1 / 2)
        target = self.add_vertex(ty=VertexType.Z, qubit=cz.target, row=row, phase=1 / 2)
        phase = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=row + 1, phase=-1/2)
        hub = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=row + 1)
        self.remove_edges(((in_ref1, out_ref1), (in_ref2, out_ref2)))
        self.add_edges(((hub, phase), (hub, control), (hub, target)))
        self.connect_vertices([in_ref1, control, out_ref1])
        self.connect_vertices([in_ref2, target, out_ref2])
        self.set_left_padding()
        self.set_right_padding()

    def add_gadget(self, gadget: Gadget, stack: Optional[bool] = None):
        self.update_num_qubits(max(gadget.paulis) + 1)
        row = self.right_row_within(min(gadget.paulis), max(gadget.paulis)) + 1 if stack else self.right_row + 1
        offset = 0 if gadget.phase_gadget else 1
        phase = self.add_vertex(ty=VertexType.Z, row=row + offset + 1, qubit=self.num_qubits + 1, phase=gadget.phase)
        hub = self.add_vertex(ty=VertexType.X, row=row + offset + 1, qubit=self.num_qubits)
        self.add_edge((hub, phase))
        if gadget.var is not None:
            self.set_vdata(vertex=phase, key='var', val=gadget.var)

        for qubit, pauli in gadget.paulis.items():
            in_ref, out_ref = self.right_end(qubit), self.outputs()[qubit]
            if pauli == PauliType.X:
                left = self.add_vertex(ty=VertexType.H_BOX, row=row, qubit=qubit)
                middle = self.add_vertex(ty=VertexType.Z, row=row + 1, qubit=qubit)
                right = self.add_vertex(ty=VertexType.H_BOX, row=row + 2, qubit=qubit)
                self.remove_edge((in_ref, out_ref))
                self.add_edge((middle, hub))
                self.connect_vertices([in_ref, left, middle, right, out_ref])
            if pauli == PauliType.Y:
                left = self.add_vertex(ty=VertexType.X, row=row, qubit=qubit, phase=1/2)
                middle = self.add_vertex(ty=VertexType.Z, row=row + 1, qubit=qubit)
                right = self.add_vertex(ty=VertexType.X, row=row + 2, qubit=qubit, phase=3/2)
                self.remove_edge((in_ref, out_ref))
                self.add_edge((middle, hub))
                self.connect_vertices([in_ref, left, middle, right, out_ref])
            if pauli == PauliType.Z:
                middle = self.add_vertex(ty=VertexType.Z, row=row + offset, qubit=qubit)
                self.remove_edge((in_ref, out_ref))
                self.add_edge((middle, hub))
                self.connect_vertices([in_ref, middle, out_ref])
        self.set_left_padding()
        self.set_right_padding()

    def add_expanded_gadget(self, gadget: Gadget, stack: Optional[bool] = False):
        self.update_num_qubits(max(gadget.paulis) + 1)
        in_row = self.right_row_within(min(gadget.paulis), max(gadget.paulis)) + 1 if stack else self.right_row + 1
        gadget_qubits = [qubit for qubit, pauli in gadget.paulis.items() if pauli != PauliType.I]
        depth = 2 * len(gadget_qubits) - 1 if gadget.phase_gadget else 2 * len(gadget_qubits) + 1

        def add_cnots(num: list[int], reverse: bool):
            for left in reversed(range(num)) if reverse else range(num):
                self.add_cx(CX(gadget_qubits[left], gadget_qubits[left + 1]), stack=stack)

        def add_cliffords(row: int, reverse: bool):
            for qubit, pauli in gadget.paulis.items():
                if pauli == PauliType.X:
                    self.add(H(qubit), row=row)
                elif pauli == PauliType.Y:
                    self.add(XMinus(qubit) if reverse else XPlus(qubit), row=row)

        add_cliffords(in_row, reverse=False)
        add_cnots(len(gadget_qubits) - 1, reverse=False)

        phase_node = self.add(ZPhase(max(gadget_qubits), gadget.phase))
        if gadget.var is not None:
            self.set_vdata(vertex=phase_node, key='var', val=gadget.var)

        add_cnots(len(gadget_qubits) - 1, reverse=True)
        add_cliffords(in_row + depth - 1, reverse=True)
