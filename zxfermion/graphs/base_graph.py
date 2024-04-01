from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Optional

import pyzx as zx
from pdflatex import PDFLaTeX
from pyzx import VertexType
from pyzx.graph.graph_s import GraphS

from zxfermion.utilities import pair_list, tex_parse_tikz


class BaseGraph(GraphS):
    def __init__(self, num_qubits: Optional[int] = 1, num_rows: Optional[int] = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    @property
    def min_qubit(self) -> int:
        return min((self.qubit(vertex) for vertex in self.bounded_vertices), default=0)

    @property
    def max_qubit(self) -> int:
        return max((self.qubit(vertex) for vertex in self.bounded_vertices), default=self.num_qubits - 1)

    @property
    def boundaries(self) -> list[int]:
        return self.inputs() + self.outputs()

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
        return min((self.row(vertex) for vertex in self.bounded_vertices), default=self.output_row)

    @property
    def right_row(self) -> int:
        return max((self.row(vertex) for vertex in self.bounded_vertices), default=self.input_row)

    def left_end(self, qubit: int) -> int:
        default = self.outputs()[qubit] if qubit < self.num_qubits else None
        return self.vertices_on_qubit(qubit)[0] if self.vertices_on_qubit(qubit) else default

    def right_end(self, qubit: int) -> int:
        default = self.inputs()[qubit] if qubit < self.num_qubits else None
        return self.vertices_on_qubit(qubit)[-1] if self.vertices_on_qubit(qubit) else default

    @property
    def left_ends(self) -> list[int]:
        return [self.left_end(qubit) for qubit in range(self.num_qubits)]

    @property
    def right_ends(self) -> list[int]:
        return [self.right_end(qubit) for qubit in range(self.num_qubits)]

    def left_row_between(self, left: int, right: int) -> int:
        return min(self.row(self.left_end(q)) for q in range(left, right + 1))

    def right_row_between(self, left: int, right: int) -> int:
        return max(self.row(self.right_end(q)) for q in range(left, right + 1))

    @property
    def bounded_vertices(self) -> list[int]:
        return [
            vertex
            for vertex
            in self.vertices()
            if self.type(vertex) != VertexType.BOUNDARY
            and self.qubit(vertex) in range(self.num_qubits)
        ]

    @property
    def unbounded_vertices(self) -> list[int]:
        return [
            vertex
            for vertex
            in self.vertices()
            if vertex not in self.bounded_vertices
            and self.type(vertex) != VertexType.BOUNDARY
        ]

    def vertices_on_qubit(self, qubit: int) -> list[int]:
        return sorted([
            vertex
            for vertex
            in self.bounded_vertices
            if self.qubit(vertex) == qubit
        ], key=lambda vertex: self.row(vertex))

    def remove_wire(self, qubit: int):
        self.remove_edge((self.inputs()[qubit], self.outputs()[qubit]))

    def connect_vertices(self, vertex_refs: list[int]):
        self.add_edges(pair_list(vertex_refs))

    def update_output_row(self):
        if self.right_row + 1 > self.output_row:
            for output in self.outputs():
                self.set_row(output, self.right_row + 1)

    def update_input_row(self):
        if (offset := self.left_row - self.input_row) > 1:
            for vertex in [vertex for vertex in self.vertices() if vertex not in self.inputs()]:
                self.set_row(vertex, self.row(vertex) - offset + 1)

    def update_boundaries(self):
        self.update_output_row()
        self.update_input_row()

    def update_num_qubits(self, num_qubits):
        if num_qubits > self.num_qubits:
            self.set_num_qubits(num_qubits)

    def set_num_qubits(self, num_qubits: int):
        assert num_qubits >= self.num_qubits
        graph = BaseGraph(num_qubits=num_qubits)

        self_refs = {
            vertex: graph.add_vertex(
                self.type(vertex),
                phase=self.phase(vertex),
                qubit=self.qubit(vertex),
                row=self.row(vertex))
            for vertex in self.vertices()
            if vertex not in self.boundaries
        }

        for edge in self.edges():
            source, target = self.edge_st(edge)
            if source not in self.boundaries and target not in self.boundaries:
                graph.add_edge(graph.edge(
                    self_refs[source],
                    self_refs[target]
                ), edgetype=self.edge_type(edge))

        for qubit in [qubit for qubit in range(self.num_qubits) if self.vertices_on_qubit(qubit)]:
            graph.remove_wire(qubit)
            graph.add_edge((graph.inputs()[qubit], self_refs[self.left_end(qubit)]))
            graph.add_edge((self_refs[self.right_end(qubit)], graph.outputs()[qubit]))

        for vertex in self.unbounded_vertices:
            vertical_offset = graph.num_qubits - self.num_qubits
            graph.set_qubit(self_refs[vertex], self.qubit(vertex) + vertical_offset)

        graph.update_boundaries()
        self.__dict__.update(graph.__dict__)

    def compose(self, other: BaseGraph, stack: Optional[bool] = False):
        self.update_num_qubits(max(self.num_qubits, other.num_qubits))
        out_refs = self.right_ends
        other = deepcopy(other)

        row = self.right_row_between(other.min_qubit, other.max_qubit) if stack else self.right_row
        other_refs = {
            vertex: self.add_vertex(
                other.type(vertex),
                phase=other.phase(vertex),
                qubit=other.qubit(vertex),
                row=row + other.row(vertex))
            for vertex in other.vertices()
            if vertex not in other.boundaries
        }

        for edge in other.edges():
            source, target = other.edge_st(edge)
            if source not in other.boundaries and target not in other.boundaries:
                self.add_edge(self.edge(
                    other_refs[source],
                    other_refs[target]
                ), edgetype=other.edge_type(edge))

        # should be iterating over left_ends
        for qubit in [qubit for qubit in range(other.num_qubits) if other.vertices_on_qubit(qubit)]:
            self.remove_edge((out_refs[qubit], self.outputs()[qubit]))
            self.add_edge((out_refs[qubit], other_refs[other.left_end(qubit)]))
            self.add_edge((other_refs[other.right_end(qubit)], self.outputs()[qubit]))

        for vertex in other.unbounded_vertices:
            vertical_offset = self.num_qubits - other.num_qubits
            self.set_qubit(other_refs[vertex], other.qubit(vertex) + vertical_offset)

        self.update_boundaries()

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
