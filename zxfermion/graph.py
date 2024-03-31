from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from pdflatex import PDFLaTeX

import pyzx as zx
from pyzx import VertexType
from pyzx.graph.graph_s import GraphS

from zxfermion.types import PauliType
from zxfermion.utilities import tex_parse_tikz, pair_list
from zxfermion.gates import Gadget, XPhase, ZPhase, XPlus, XMinus, CZ, CX, H


class BaseGraph(GraphS):
    def __init__(self, num_qubits: Optional[int] = 1, num_rows: Optional[int] = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    @property
    def input_row(self) -> int:
        return self.row(self.inputs()[0])

    @property
    def output_row(self) -> int:
        return self.row(self.outputs()[0])

    @property
    def graph_rows(self) -> list[int]:
        return [row for row in range(self.input_row + 1, self.output_row)]

    @property
    def graph_depth(self) -> int:
        return self.output_row - self.input_row - 1

    @property
    def left_row(self) -> int:
        return min((self.row(vertex) for vertex in self.bounded_vertices), default=None)

    @property
    def right_row(self) -> int:
        return max((self.row(vertex) for vertex in self.bounded_vertices), default=None)

    def left_vertex(self, qubit: int) -> int:
        return self.vertices_along_qubit(qubit)[0] if self.vertices_along_qubit(qubit) else self.outputs()[qubit]

    def right_vertex(self, qubit: int) -> int:
        return self.vertices_along_qubit(qubit)[-1] if self.vertices_along_qubit(qubit) else self.inputs()[qubit]

    def left_vertex_row(self, qubit: int) -> int:
        return self.row(self.left_vertex(qubit))

    def right_vertex_row(self, qubit: int) -> int:
        return self.row(self.right_vertex(qubit))

    @property
    def bounded_vertices(self) -> list[int]:
        return [
            vertex
            for vertex
            in self.vertices()
            if self.type(vertex) != VertexType.BOUNDARY
            and self.qubit(vertex) in range(self.num_qubits)
        ]

    def vertices_along_qubit(self, qubit: int) -> list[int]:
        return sorted([
            vertex
            for vertex
            in self.bounded_vertices
            if self.qubit(vertex) == qubit
        ], key=lambda vertex: self.row(vertex))

    def update_boundaries(self):
        if self.right_row + 1 > self.output_row:
            for output in self.outputs():
                self.set_row(output, self.right_row + 1)
        if (offset := self.left_row - self.input_row) > 1:
            for vertex in [vertex for vertex in self.vertices() if vertex not in self.inputs()]:
                self.set_row(vertex, self.row(vertex) - offset + 1)

    def connect_vertices(self, vertex_refs: list[int]):
        self.add_edges(pair_list(vertex_refs))

    def tikz(self, name: Optional[str] = None, symbol: Optional[str] = None, scale: Optional[float] = None):
        Path('output/').mkdir(parents=True, exist_ok=True)
        tex_output = tex_parse_tikz(content=self.to_tikz(), phase_row=self.num_qubits + 2, symbol=symbol, scale=scale)
        if name is not None:
            with open(f'output/{name}.tex', 'w') as file: file.write(tex_output)
        return None if name is None else tex_output

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

    def add(self, gate: XPhase | ZPhase | H, row: Optional[int] = None):
        in_ref = self.right_vertex(gate.qubit)
        out_ref = self.outputs()[gate.qubit]
        ref = self.add_vertex(
            ty=gate.vertex_type,
            qubit=gate.qubit,
            phase=gate.phase,
            row=self.row(in_ref) + 1 if row is None else row)
        self.remove_edge((in_ref, out_ref))
        self.connect_vertices([in_ref, ref, out_ref])
        self.update_boundaries()

    def add_cx(self, cx: CX):
        row = max(self.right_vertex_row(q) for q in range(cx.min_qubit, cx.max_qubit + 1)) + 1
        control_in, control_out = self.right_vertex(cx.control), self.outputs()[cx.control]
        target_in, target_out = self.right_vertex(cx.target), self.outputs()[cx.target]
        control_ref = self.add_vertex(ty=VertexType.Z, row=row, qubit=cx.control)
        target_ref = self.add_vertex(ty=VertexType.X, row=row, qubit=cx.target)
        self.remove_edges(((control_in, control_out), (target_in, target_out)))
        self.connect_vertices([control_ref, target_ref])
        self.connect_vertices([control_in, control_ref, control_out])
        self.connect_vertices([target_in, target_ref, target_out])
        self.update_boundaries()

    def add_cz(self, cz: CZ):
        row = max(self.right_vertex_row(q) for q in range(cz.min_qubit, cz.max_qubit + 1)) + 1
        control_in, control_out = self.right_vertex(cz.control), self.outputs()[cz.control]
        target_in, target_out = self.right_vertex(cz.target), self.outputs()[cz.target]
        control_ref = self.add_vertex(ty=VertexType.Z, row=row, qubit=cz.control)
        target_ref = self.add_vertex(ty=VertexType.Z, row=row, qubit=cz.target)
        hadamard_ref = self.add_vertex(ty=VertexType.H_BOX, row=row, qubit=(cz.max_qubit + cz.min_qubit) / 2)
        self.remove_edges(((control_in, control_out), (target_in, target_out)))
        self.connect_vertices((control_ref, hadamard_ref, target_ref))
        self.connect_vertices([control_in, control_ref, control_out])
        self.connect_vertices([target_in, target_ref, target_out])
        self.update_boundaries()

    def add_cx_gadget(self, cx: CX):
        row = max(self.right_vertex_row(q) for q in range(cx.min_qubit, cx.max_qubit + 1)) + 1
        control_in, control_out = self.right_vertex(cx.control), self.outputs()[cx.control]
        target_in, target_out = self.right_vertex(cx.target), self.outputs()[cx.target]

        hub_ref = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=row + 2)
        phase_ref = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=row + 2, phase=-1/2)
        target_ref = self.add_vertex(ty=VertexType.Z, qubit=cx.target, row=row + 1, phase=1/2)
        control_ref = self.add_vertex(ty=VertexType.Z, qubit=cx.control, row=row + 1, phase=1/2)
        left_ref = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=row)
        right_ref = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=row + 2)

        self.remove_edges(((control_in, control_out), (target_in, target_out)))
        self.connect_vertices([target_in, left_ref, target_ref, right_ref, target_out])
        self.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        self.connect_vertices([control_in, control_ref, control_out])
        self.update_boundaries()

    def add_cz_gadget(self, cz: CZ):
        row = max(self.right_vertex_row(q) for q in range(cz.min_qubit, cz.max_qubit + 1)) + 1
        control_in, control_out = self.right_vertex(cz.control), self.outputs()[cz.control]
        target_in, target_out = self.right_vertex(cz.target), self.outputs()[cz.target]

        hub_ref = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=row + 1)
        phase_ref = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=row + 1, phase=-1/2)
        target_ref = self.add_vertex(ty=VertexType.Z, qubit=cz.target, row=row, phase=1 / 2)
        control_ref = self.add_vertex(ty=VertexType.Z, qubit=cz.control, row=row, phase=1 / 2)

        self.remove_edges(((control_in, control_out), (target_in, target_out)))
        self.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        self.connect_vertices([control_in, control_ref, control_out])
        self.connect_vertices([target_in, target_ref, target_out])
        self.update_boundaries()

    def add_gadget(self, gadget: Gadget):
        row = max(self.row(self.right_vertex(q)) for q in range(gadget.min_qubit, gadget.max_qubit + 1)) + 1
        offset = 0 if gadget.phase_gadget else 1
        hub_ref = self.add_vertex(ty=VertexType.X, row=row + offset + 1, qubit=self.num_qubits + 1)
        phase_ref = self.add_vertex(ty=VertexType.Z, row=row + offset + 1, qubit=self.num_qubits + 2, phase=gadget.phase)
        self.add_edge((hub_ref, phase_ref))
        for qubit, pauli in gadget.paulis.items():
            in_ref, out_ref = self.right_vertex(qubit), self.outputs()[qubit]
            if pauli == PauliType.X:
                left_ref = self.add_vertex(ty=VertexType.H_BOX, row=row, qubit=qubit)
                middle_ref = self.add_vertex(ty=VertexType.Z, row=row + 1, qubit=qubit)
                right_ref = self.add_vertex(ty=VertexType.H_BOX, row=row + 2, qubit=qubit)
                self.remove_edge((in_ref, out_ref))
                self.add_edge((middle_ref, hub_ref))
                self.connect_vertices([in_ref, left_ref, middle_ref, right_ref, out_ref])
            if pauli == PauliType.Y:
                left_ref = self.add_vertex(ty=VertexType.X, row=row, qubit=qubit, phase=1/2)
                middle_ref = self.add_vertex(ty=VertexType.Z, row=row + 1, qubit=qubit)
                right_ref = self.add_vertex(ty=VertexType.X, row=row + 2, qubit=qubit, phase=3/2)
                self.remove_edge((in_ref, out_ref))
                self.add_edge((middle_ref, hub_ref))
                self.connect_vertices([in_ref, left_ref, middle_ref, right_ref, out_ref])
            if pauli == PauliType.Z:
                middle_ref = self.add_vertex(ty=VertexType.Z, row=row + offset, qubit=qubit)
                self.remove_edge((in_ref, out_ref))
                self.add_edge((middle_ref, hub_ref))
                self.connect_vertices([in_ref, middle_ref, out_ref])
        self.update_boundaries()

    def add_expanded_gadget(self, gadget: Gadget):
        row = max(self.row(self.right_vertex(q)) for q in range(gadget.min_qubit, gadget.max_qubit + 1)) + 1
        gadget_qubits = [qubit for qubit, pauli in gadget.paulis.items() if pauli != PauliType.I]
        depth = 2 * len(gadget_qubits) - 1 if gadget.phase_gadget else 2 * len(gadget_qubits) + 1

        def add_cnots(num: list[int], reverse: bool):
            for left in reversed(range(num)) if reverse else range(num):
                self.add_cx(CX(gadget_qubits[left], gadget_qubits[left + 1]))

        def add_cliffords(row: int, reverse: bool):
            for qubit, pauli in gadget.paulis.items():
                if pauli == PauliType.X:
                    self.add(H(qubit), row=row)
                elif pauli == PauliType.Y:
                    self.add(XMinus(qubit) if reverse else XPlus(qubit), row=row)

        add_cliffords(row, reverse=False)
        add_cnots(len(gadget_qubits) - 1, reverse=False)
        self.add(ZPhase(max(gadget_qubits), gadget.phase))
        add_cnots(len(gadget_qubits) - 1, reverse=True)
        add_cliffords(row + depth - 1, reverse=True)
