from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union
from pdflatex import PDFLaTeX

import pyzx as zx
from pyzx import VertexType, EdgeType
from pyzx.graph.graph_s import GraphS

from zxfermion.types import LegType
from zxfermion.utilities import tex_parse_tikz
from zxfermion.gadgets import Gadget, XPhase, ZPhase, XPlus, XMinus, CZ, CX, H


class BaseGraph(GraphS):
    def __init__(self, num_qubits: int, num_rows: int = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    def depth(self) -> int:
        return self.row(self.outputs()[0]) - 1  # disregards phase hub

    def update_num_rows(self, num_rows: int):
        self.remove_vertices(self.outputs())
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    def remove_wire(self, qubit: int):
        if self.connected(self.inputs()[qubit], self.outputs()[qubit]):
            self.remove_edge((self.inputs()[qubit], self.outputs()[qubit]))

    def connect_nodes(self, qubit: int, node_refs: list[int]):
        def pair_list(items: list[int]) -> list[tuple[int, int]]:
            return [(items[idx], items[idx + 1]) for idx in range(len(items) - 1)]
        self.add_edges(pair_list([self.inputs()[qubit], *node_refs, self.outputs()[qubit]]))

    def tikz(self, name: Optional[str] = None, symbol: Optional[str] = None, scale: Optional[float] = None):
        Path('output/').mkdir(parents=True, exist_ok=True)
        tex_output = tex_parse_tikz(content=self.to_tikz(), phase_row=self.num_qubits + 2, symbol=symbol, scale=scale)
        if name:
            with open(f'output/{name}.tex', 'w') as file: file.write(tex_output)
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
    def __init__(self, num_qubits: int, num_rows: int = 1):
        super().__init__(num_qubits=num_qubits, num_rows=num_rows)

    def add_single_gate(self, gate: Union[XPhase, ZPhase, H]):
        ref = self.add_vertex(ty=gate.vertex_type, row=1, qubit=gate.qubit, phase=gate.phase)
        self.connect_nodes(qubit=gate.qubit, node_refs=[ref])
        self.remove_wire(gate.qubit)
        return ref

    def add_gadget(self, gadget: Gadget):
        gadget_depth = 1 if gadget.phase_gadget else 3
        if gadget_depth > self.depth():
            self.update_num_rows(gadget_depth)

        if not all(leg == LegType.I for leg in gadget.legs.values()):
            hub_row = 2 if gadget.phase_gadget else 3
            hub_ref = self.add_vertex(ty=VertexType.X, row=hub_row, qubit=self.num_qubits + 1)
            phase_ref = self.add_vertex(ty=VertexType.Z, row=hub_row, qubit=self.num_qubits + 2, phase=gadget.phase)
            for qubit, leg in gadget.legs.items():
                if leg == LegType.X:
                    left_ref = self.add_vertex(ty=VertexType.H_BOX, row=1, qubit=qubit)
                    middle_ref = self.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                    right_ref = self.add_vertex(ty=VertexType.H_BOX, row=3, qubit=qubit)
                    self.connect_nodes(qubit=qubit, node_refs=[left_ref, middle_ref, right_ref])
                    self.add_edge((middle_ref, hub_ref))
                    self.remove_wire(qubit=qubit)
                elif leg == LegType.Y:
                    left_ref = self.add_vertex(ty=VertexType.X, row=1, qubit=qubit, phase=1/2,)
                    middle_ref = self.add_vertex(ty=VertexType.Z, row=2, qubit=qubit)
                    right_ref = self.add_vertex(ty=VertexType.X, row=3, qubit=qubit, phase=-1/2)
                    self.connect_nodes(qubit=qubit, node_refs=[left_ref, middle_ref, right_ref])
                    self.add_edge((middle_ref, hub_ref))
                    self.remove_wire(qubit=qubit)
                elif leg == LegType.Z:
                    middle_ref = self.add_vertex(ty=VertexType.Z, row=1 if gadget.phase_gadget else 2, qubit=qubit)
                    self.connect_nodes(qubit=qubit, node_refs=[middle_ref])
                    self.add_edge((middle_ref, hub_ref))
                    self.remove_wire(qubit=qubit)
            self.add_edge((hub_ref, phase_ref))

    def add_expanded_gadget(self, gadget: Gadget):
        qubits = [qubit for qubit, leg in gadget.legs.items() if leg != LegType.I]
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
        for qubit, leg in gadget.legs.items():
            if leg == LegType.X:
                clifford_left.add_single_gate(H(qubit=qubit))
                clifford_right.add_single_gate(H(qubit=qubit))
            elif leg == LegType.Y:
                clifford_left.add_single_gate(XPlus(qubit=qubit))
                clifford_right.add_single_gate(XMinus(qubit=qubit))

        ladder_middle = GadgetGraph(num_qubits=self.num_qubits)
        ladder_middle.add_single_gate(ZPhase(qubit=max(qubits), phase=gadget.phase))

        for graph in clifford_left, ladder_left, ladder_middle, ladder_right, clifford_right:
            self.compose(graph)

    def add_cx(self, cx: CX):
        control_ref = self.add_vertex(ty=VertexType.Z, row=1, qubit=cx.control)
        target_ref = self.add_vertex(ty=VertexType.X, row=1, qubit=cx.target)

        self.connect_nodes(qubit=cx.control, node_refs=[control_ref])
        self.connect_nodes(qubit=cx.target, node_refs=[target_ref])
        self.add_edge((control_ref, target_ref))
        self.remove_wire(cx.control)
        self.remove_wire(cx.target)

    def add_cz(self, cz: CZ):
        control_ref = self.add_vertex(ty=VertexType.Z, row=1, qubit=cz.control)
        target_ref = self.add_vertex(ty=VertexType.Z, row=1, qubit=cz.target)

        self.connect_nodes(qubit=cz.control, node_refs=[control_ref])
        self.connect_nodes(qubit=cz.target, node_refs=[target_ref])
        self.add_edge((control_ref, target_ref), edgetype=EdgeType.HADAMARD)
        self.remove_wire(cz.control)
        self.remove_wire(cz.target)

    def add_cx_gadget(self, cx: CX):
        if self.depth() < 3:
            self.update_num_rows(3)

        hub_ref = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=3)
        phase_ref = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=3, phase=-1/2)
        control_ref = self.add_vertex(ty=VertexType.Z, qubit=cx.control, row=2, phase=1/2)
        target_ref = self.add_vertex(ty=VertexType.Z, qubit=cx.target, row=2, phase=1/2)
        left_had_ref = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=1)
        right_had_ref = self.add_vertex(ty=VertexType.H_BOX, qubit=cx.target, row=3)

        self.connect_nodes(qubit=cx.control, node_refs=[control_ref])
        self.connect_nodes(qubit=cx.target, node_refs=[left_had_ref, target_ref, right_had_ref])
        self.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        self.remove_wire(cx.control)
        self.remove_wire(cx.target)

    def add_cz_gadget(self, cz: CZ):
        hub_ref = self.add_vertex(ty=VertexType.X, qubit=self.num_qubits + 1, row=2)
        phase_ref = self.add_vertex(ty=VertexType.Z, qubit=self.num_qubits + 2, row=2, phase=-1/2)
        control_ref = self.add_vertex(ty=VertexType.Z, qubit=cz.control, row=1, phase=1/2)
        target_ref = self.add_vertex(ty=VertexType.Z, qubit=cz.target, row=1, phase=1/2)

        self.connect_nodes(qubit=cz.control, node_refs=[control_ref])
        self.connect_nodes(qubit=cz.target, node_refs=[target_ref])
        self.add_edges(((hub_ref, phase_ref), (hub_ref, control_ref), (hub_ref, target_ref)))
        self.remove_wire(cz.control)
        self.remove_wire(cz.target)
