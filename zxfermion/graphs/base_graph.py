from __future__ import annotations

import os
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Optional

import pyzx as zx
from IPython.core.display import Markdown
from IPython.core.display_functions import display
# from pdflatex import PDFLaTeX
from pyzx.graph.graph_s import GraphS

from zxfermion.utils import pair_list, settings

#### PDFLATEX STUFF MAKE IT LIGHTER


class BaseGraph(GraphS):
    def __init__(self, num_qubits: Optional[int] = 1, num_rows: Optional[int] = 1, boundary_padding: Optional[int] = 1):
        super().__init__()
        self.num_qubits = num_qubits
        self.boundary_padding = boundary_padding
        self.set_inputs([self.add_vertex(qubit=qubit, row=0) for qubit in range(self.num_qubits)])
        self.set_outputs([self.add_vertex(qubit=qubit, row=num_rows + 1) for qubit in range(self.num_qubits)])
        self.add_edges([(self.inputs()[qubit], self.outputs()[qubit]) for qubit in range(self.num_qubits)])

    def __eq__(self, other):
        # ADD VDATA
        other_data = other.rows(), other.qubits(), other.types()
        self_data = self.rows(), self.qubits(), self.types()
        return self_data == other_data

    def __add__(self, other):
        new = deepcopy(self)
        new.compose(other, stack=False)
        return new

    @property
    def min_qubit(self) -> int:
        return min((self.qubit(vertex) for vertex in self.bounded_vertices), default=0)

    @property
    def max_qubit(self) -> int:
        return max((self.qubit(vertex) for vertex in self.bounded_vertices), default=self.num_qubits - 1)

    @property
    def input_row(self) -> int:
        return self.row(self.inputs()[0])

    @property
    def output_row(self) -> int:
        return self.row(self.outputs()[0])

    @property
    def left_row(self) -> int:
        return min((self.row(vertex) for vertex in self.bounded_vertices), default=self.output_row)

    @property
    def right_row(self) -> int:
        return max((self.row(vertex) for vertex in self.bounded_vertices), default=self.input_row)

    @property
    def left_padding(self) -> int:
        return self.left_row - self.input_row

    @property
    def right_padding(self) -> int:
        return self.output_row - self.right_row

    @property
    def boundaries(self) -> list[int]:
        return self.inputs() + self.outputs()

    @property
    def graph_rows(self) -> list[int]:
        return [row for row in range(self.left_row, self.right_row + 1)]

    @property
    def graph_depth(self) -> int:
        return len(self.graph_rows)

    def left_end(self, qubit: int) -> int:
        default = self.outputs()[qubit] if qubit < self.num_qubits else None
        return self.vertices_on_qubit(qubit)[0] if self.vertices_on_qubit(qubit) else default

    def right_end(self, qubit: int) -> int:
        default = self.inputs()[qubit] if qubit < self.num_qubits else None
        return self.vertices_on_qubit(qubit)[-1] if self.vertices_on_qubit(qubit) else default

    def left_row_within(self, top: int, bottom: int) -> int:
        return min(self.row(self.left_end(q)) for q in range(top, bottom + 1))

    def right_row_within(self, top: int, bottom: int) -> int:
        return max(self.row(self.right_end(q)) for q in range(top, bottom + 1))

    @property
    def bounded_vertices(self) -> list[int]:
        return [
            vertex
            for vertex
            in self.vertices()
            if vertex not in self.boundaries
            and 0 <= self.qubit(vertex) <= self.num_qubits - 1
        ]

    @property
    def unbounded_vertices(self) -> list[int]:
        return [
            vertex
            for vertex
            in self.vertices()
            if vertex not in self.boundaries
            and vertex not in self.bounded_vertices
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

    def connect_vertices(self, vertices: list[int]):
        self.add_edges(pair_list(vertices))

    def set_input_row(self, row):
        for vertex in self.inputs():
            self.set_row(vertex, row)

    def set_output_row(self, row):
        for vertex in self.outputs():
            self.set_row(vertex, row)

    def set_left_padding(self, padding: Optional[int] = None):
        padding = self.boundary_padding if padding is None else padding
        offset = self.input_row - self.left_row + padding
        for vertex in [vertex for vertex in self.vertices() if vertex not in self.inputs()]:
            self.set_row(vertex, self.row(vertex) + offset)

    def set_right_padding(self, padding: Optional[int] = None):
        padding = self.boundary_padding if padding is None else padding
        self.set_output_row(self.right_row + padding)

    def set_num_qubits(self, num_qubits: int):
        assert num_qubits >= self.num_qubits
        graph = BaseGraph(num_qubits=num_qubits)
        graph.compose(self)
        self.__dict__.update(graph.__dict__)

    def update_num_qubits(self, num_qubits):
        if num_qubits > self.num_qubits:
            self.set_num_qubits(num_qubits)

    def compose(self, other: BaseGraph, stack: bool = False):
        other = deepcopy(other)
        out_refs = [self.right_end(qubit) for qubit in range(self.num_qubits)]
        self.update_num_qubits(max(self.num_qubits, other.num_qubits))

        row = self.right_row_within(other.min_qubit, other.max_qubit) if stack else self.right_row
        vertex_dict = {
            vertex: self.add_vertex(
                other.type(vertex),
                phase=other.phase(vertex),
                qubit=other.qubit(vertex),
                row=other.row(vertex) + row)
            for vertex in other.vertices()
            if vertex not in other.boundaries
        }

        for edge in other.edges():
            source, target = other.edge_st(edge)
            if source not in other.boundaries and target not in other.boundaries:
                self.add_edge(self.edge(
                    vertex_dict[source],
                    vertex_dict[target]
                ), edgetype=other.edge_type(edge))

        for vertex, new_vertex in vertex_dict.items():
            for key in [key for key in other.vdata_keys(vertex) if key]:
                self.set_vdata(new_vertex, key, other.vdata(vertex, key, None))

        for qubit in [qubit for qubit in range(other.num_qubits) if other.vertices_on_qubit(qubit)]:
            self.remove_edge((out_refs[qubit], self.outputs()[qubit]))
            self.add_edge((out_refs[qubit], vertex_dict[other.left_end(qubit)]))
            self.add_edge((vertex_dict[other.right_end(qubit)], self.outputs()[qubit]))

        for vertex in other.unbounded_vertices:
            vertical_offset = self.num_qubits - other.num_qubits
            self.set_qubit(vertex_dict[vertex], other.qubit(vertex) + vertical_offset)

        self.set_left_padding()
        self.set_right_padding()

    def matrix(self, return_latex=False, override_max=False):
        if self.num_qubits < 5 or override_max:
            latex_string = zx.matrix_to_latex(self.to_matrix())
            display(Markdown(latex_string))
            return latex_string if return_latex else None
        else:
            print(f'{2 ** self.num_qubits} x {2 ** self.num_qubits} matrix too large to compute.')

    def tikz(self, name: Optional[str] = None, scale: float = settings.tikz_scale):
        from zxfermion.graphs import to_tikz
        Path('output/').mkdir(parents=True, exist_ok=True)
        tikz_content = to_tikz(self, scale=scale)
        if name is not None:
            with open(f'output/{name}.tikz', 'w') as file:
                file.write(tikz_content)
        else:
            return tikz_content

    def tex(self, name: str, scale: float = settings.tikz_scale):
        Path('output/').mkdir(parents=True, exist_ok=True)
        tikz_content = self.tikz(scale=scale)
        with open('tikz/template.tex', 'r') as template_file:
            tex_output = template_file.read().replace('TIKZ_PICTURE', tikz_content.strip())
        with open(f'output/{name}_temp.tex', 'w') as file:
            file.write(tex_output)

    def pdf(self, name: str, scale: float = settings.tikz_scale):
        self.tex(name=name, scale=scale)
        #pdf = PDFLaTeX.from_texfile(f'output/{name}_temp.tex')
        #pdf.set_pdf_filename(f'{name}')
        #pdf.set_output_directory('output/')
        #pdf.create_pdf(keep_pdf_file=True, keep_log_file=False)
        #if os.path.exists(f'output/{name}_temp.tex'):
        #    os.remove(f'output/{name}_temp.tex')

    def clipboard(self):
        subprocess.run('pbcopy', text=True, input=self.tikz())

    def draw(self, labels: bool = settings.labels):
        zx.draw(self, labels=labels)

    def html(self, name: str):
        with open(f'output/{name}_temp.html', 'w') as file:
            file.write(zx.draw(self))
