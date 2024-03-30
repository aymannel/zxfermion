from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union, TypeVar

import pyzx as zx
from pdflatex import PDFLaTeX
from pyzx import VertexType, EdgeType
from pyzx.graph.graph_s import GraphS

from zxfermion.gates import Gadget, XPhase, ZPhase, XPlus, XMinus, CZ, CX, H, ZMinus, ZPlus
from zxfermion.types import PauliType, GateType
from zxfermion.utilities import tex_parse_tikz, pair_list


class BaseGraph(GraphS):
    def __init__(self, num_qubits: Optional[int] = 1, num_rows: Optional[int] = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    @property
    def graph_qubits(self) -> list[int]:
        return [self.qubit(v) for v in self.inputs()]

    @property
    def graph_rows(self) -> list[int]:
        return list(range(self.input_row + 1, self.output_row))

    @property
    def input_row(self) -> int:
        return self.row(self.inputs()[0])

    @property
    def output_row(self) -> int:
        return self.row(self.outputs()[0])

    @property
    def first_qubit(self) -> int:
        return self.qubit(self.inputs()[0])

    @property
    def last_qubit(self) -> int:
        return self.qubit(self.inputs()[-1])

    @property
    def graph_depth(self) -> int:
        return self.output_row - self.input_row - 1

    @property
    def left_plugs(self) -> list[int]:
        return [leftmost for q in self.graph_qubits if (leftmost := self.leftmost_vertex(q)) >= 0]

    @property
    def right_plugs(self) -> list[int]:
        return [rightmost for q in self.graph_qubits if (rightmost := self.rightmost_vertex(q)) >= 0]

    @property
    def leftmost_row(self) -> int:
        return min((
            self.row(v)
            for v in self.vertices()
            if self.type(v) != VertexType.BOUNDARY
            and self.qubit(v) <= self.last_qubit
        ), default=-1)

    @property
    def rightmost_row(self) -> int:
        return max((
            self.row(v)
            for v in self.vertices()
            if self.type(v) != VertexType.BOUNDARY
            and self.qubit(v) <= self.last_qubit
        ), default=-1)

    def leftmost_vertex(self, qubit: int) -> int:
        return min((
            v for v in self.vertices()
            if self.type(v) != VertexType.BOUNDARY
            and self.qubit(v) == qubit
        ), default=-1)

    def rightmost_vertex(self, qubit: int) -> int:
        return max((
            v for v in self.vertices()
            if self.type(v) != VertexType.BOUNDARY
            and self.qubit(v) == qubit
        ), default=-1)

    def set_output_row(self, row: int):
        for output in self.outputs():
            self.set_row(output, row)

    def remove_wire(self, qubit: int):
        if self.connected(self.inputs()[qubit], self.outputs()[qubit]):
            self.remove_edge((self.inputs()[qubit], self.outputs()[qubit]))

    def remove_wires(self, qubits: list[int]):
        for qubit in qubits:
            self.remove_wire(qubit)

    def connect_vertices(self, qubit: int, vertex_refs: list[int]):
        self.add_edges(pair_list([self.inputs()[qubit], *vertex_refs, self.outputs()[qubit]]))

    def tikz(self, name: Optional[str] = None, symbol: Optional[str] = None, scale: Optional[float] = None):
        Path('output/').mkdir(parents=True, exist_ok=True)
        tex_output = tex_parse_tikz(content=self.to_tikz(), phase_row=self.num_qubits + 2, symbol=symbol, scale=scale)
        if name:
            with open(f'output/{name}.tex', 'w') as file:
                file.write(tex_output)
        else:
            return tex_output

    def pdf(self, name: Optional[str] = None, symbol: Optional[str] = None, scale: Optional[float] = None):
        self.tikz(name=f'{name}_temp', symbol=symbol, scale=scale)
        pdf = PDFLaTeX.from_texfile(f'output/{name}_temp.tex')
        pdf.set_pdf_filename(f'{name}.pdf')
        pdf.set_output_directory('output/')
        pdf.create_pdf(keep_pdf_file=True, keep_log_file=False)
        if os.path.exists(f'output/{name}_temp.tex'):
            os.remove(f'output/{name}_temp.tex')

    def draw(self, labels=False):
        zx.draw(self, labels=labels)


class GadgetGraph(BaseGraph):
    def __init__(self, num_qubits: Optional[int] = 1, num_rows: Optional[int] = 1):
        super().__init__(num_qubits=num_qubits, num_rows=num_rows)

    def add_single_gate(self, gate: Union[XPhase, ZPhase, XPlus, XMinus, ZPlus, ZMinus, H]):
        ref = self.add_vertex(
            ty=gate.vertex_type,
            row=1, qubit=gate.qubit,
            phase=None if gate.type == GateType.H else gate.phase
        )
        self.connect_vertices(qubit=gate.qubit, vertex_refs=[ref])
        self.remove_wire(gate.qubit)
        return ref

    def add_gadget(self, gadget: Gadget):
        gadget_depth = 1 if gadget.phase_gadget else 3
        if gadget_depth > self.graph_depth:
            self.set_output_row(gadget_depth + 1)

        if not all(pauli == PauliType.I for pauli in gadget.paulis.values()):
            hub_row = 2 if gadget.phase_gadget else 3
            hub_ref = self.add_vertex(ty=VertexType.X, row=hub_row, qubit=self.num_qubits + 1)
            phase_ref = self.add_vertex(ty=VertexType.Z, row=hub_row, qubit=self.num_qubits + 2, phase=gadget.phase)
            for qubit, pauli in gadget.paulis.items():
                if pauli == PauliType.X:
                    left_ref = self.add_vertex(ty=VertexType.H_BOX, row=1, qubit=qubit)
                    middle_ref = self.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                    right_ref = self.add_vertex(ty=VertexType.H_BOX, row=3, qubit=qubit)
                    self.connect_vertices(qubit=qubit, vertex_refs=[left_ref, middle_ref, right_ref])
                    self.add_edge((middle_ref, hub_ref))
                    self.remove_wire(qubit=qubit)
                elif pauli == PauliType.Y:
                    left_ref = self.add_vertex(ty=VertexType.X, row=1, qubit=qubit, phase=1 / 2, )
                    middle_ref = self.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                    right_ref = self.add_vertex(ty=VertexType.X, row=3, qubit=qubit, phase=-1 / 2)
                    self.connect_vertices(qubit=qubit, vertex_refs=[left_ref, middle_ref, right_ref])
                    self.add_edge((middle_ref, hub_ref))
                    self.remove_wire(qubit=qubit)
                elif pauli == PauliType.Z:
                    middle_ref = self.add_vertex(ty=VertexType.Z, row=1 if gadget.phase_gadget else 2, qubit=qubit)
                    self.connect_vertices(qubit=qubit, vertex_refs=[middle_ref])
                    self.add_edge((middle_ref, hub_ref))
                    self.remove_wire(qubit=qubit)
            self.add_edge((hub_ref, phase_ref))

    def add_expanded_gadget(self, gadget: Gadget):
        qubits = [qubit for qubit, pauli in gadget.paulis.items() if pauli != PauliType.I]
        ladder_left = GadgetGraph(num_qubits=self.num_qubits)
        ladder_right = GadgetGraph(num_qubits=self.num_qubits)
        for left, right in zip(range(len(qubits) - 1), reversed(range(len(qubits) - 1))):
            left_cx = GadgetGraph(num_qubits=self.num_qubits)
            left_cx.add_cx(CX(qubits[left], qubits[left + 1]))
            ladder_left.compose(left_cx)

            right_cx = GadgetGraph(num_qubits=self.num_qubits)
            right_cx.add_cx(CX(qubits[right], qubits[right + 1]))
            ladder_right.compose(right_cx)

        clifford_left = GadgetGraph(num_qubits=self.num_qubits)
        clifford_right = GadgetGraph(num_qubits=self.num_qubits)
        for qubit, pauli in gadget.paulis.items():
            if pauli == PauliType.X:
                clifford_left.add_single_gate(H(qubit=qubit))
                clifford_right.add_single_gate(H(qubit=qubit))
            elif pauli == PauliType.Y:
                clifford_left.add_single_gate(XPlus(qubit=qubit))
                clifford_right.add_single_gate(XMinus(qubit=qubit))

        ladder_middle = GadgetGraph(num_qubits=self.num_qubits)
        ladder_middle.add_single_gate(ZPhase(qubit=max(qubits), phase=gadget.phase))

        for graph in clifford_left, ladder_left, ladder_middle, ladder_right, clifford_right:
            self.compose(graph)

    def add_cx(self, cx: CX):
        control_ref = self.add_vertex(ty=VertexType.Z, row=1, qubit=cx.control)
        target_ref = self.add_vertex(ty=VertexType.X, row=1, qubit=cx.target)

        self.connect_vertices(qubit=cx.control, vertex_refs=[control_ref])
        self.connect_vertices(qubit=cx.target, vertex_refs=[target_ref])
        self.add_edge((control_ref, target_ref))
        self.remove_wire(cx.control)
        self.remove_wire(cx.target)

    def add_cz(self, cz: CZ):
        control_ref = self.add_vertex(ty=VertexType.Z, row=1, qubit=cz.control)
        target_ref = self.add_vertex(ty=VertexType.Z, row=1, qubit=cz.target)

        self.connect_vertices(qubit=cz.control, vertex_refs=[control_ref])
        self.connect_vertices(qubit=cz.target, vertex_refs=[target_ref])
        self.add_edge((control_ref, target_ref), edgetype=EdgeType.HADAMARD)
        self.remove_wire(cz.control)
        self.remove_wire(cz.target)

    def add_cx_gadget(self, cx: CX):
        if self.graph_depth < 3:
            self.set_output_row(4)

        hub_ref = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=3)
        phase_ref = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=3, phase=-1 / 2)
        control_ref = self.add_vertex(ty=VertexType.Z, qubit=cx.control, row=2, phase=1 / 2)
        target_ref = self.add_vertex(ty=VertexType.Z, qubit=cx.target, row=2, phase=1 / 2)
        left_had_ref = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=1)
        right_had_ref = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=3)

        self.connect_vertices(qubit=cx.control, vertex_refs=[control_ref])
        self.connect_vertices(qubit=cx.target, vertex_refs=[left_had_ref, target_ref, right_had_ref])
        self.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        self.remove_wire(cx.control)
        self.remove_wire(cx.target)

    def add_cz_gadget(self, cz: CZ):
        hub_ref = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=2)
        phase_ref = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=2, phase=-1 / 2)
        control_ref = self.add_vertex(ty=VertexType.Z, qubit=cz.control, row=1, phase=1 / 2)
        target_ref = self.add_vertex(ty=VertexType.Z, qubit=cz.target, row=1, phase=1 / 2)

        self.connect_vertices(qubit=cz.control, vertex_refs=[control_ref])
        self.connect_vertices(qubit=cz.target, vertex_refs=[target_ref])
        self.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        self.remove_wire(cz.control)
        self.remove_wire(cz.target)
