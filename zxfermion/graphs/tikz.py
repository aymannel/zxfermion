from typing import Optional

from zxfermion.graphs.base_graph import BaseGraph
from zxfermion.utils import settings
from pyzx.utils import VertexType, EdgeType

tikz_template = r"""
    \begin{{tikzpicture}}[scale={scale}]
        \begin{{pgfonlayer}}{{nodelayer}}
    {vertices}
        \end{{pgfonlayer}}
        \begin{{pgfonlayer}}{{edgelayer}}
    {edges}
        \end{{pgfonlayer}}
    \end{{tikzpicture}}
"""


def to_tikz(graph: BaseGraph, scale: float) -> str:
    max_index = 0
    vertices = []
    for vertex in graph.vertices():
        type = graph.type(vertex)
        phase = graph.phase(vertex)
        if type == VertexType.BOUNDARY:
            style = settings.tikz_classes['boundary']
        elif type == VertexType.H_BOX:
            style = settings.tikz_classes['hadamard']
        else:
            if phase != 0:
                if type == VertexType.Z:
                    style = settings.tikz_classes['z_phase']
                else:
                    style = settings.tikz_classes['x_phase']
            else:
                if type == VertexType.Z:
                    style = settings.tikz_classes['z_node']
                else:
                    style = settings.tikz_classes['x_node']

        if (type == VertexType.H_BOX and phase == 1) or (type != VertexType.H_BOX and phase == 0):
            phase = ''
        else:
            var = settings.tikz_var if (vdata_var := graph.vdata(vertex, 'var', default=None)) is None else vdata_var
            numerator = '' if phase.numerator == 1 else str(phase.numerator)
            denominator = '' if phase.denominator == 1 else str(phase.denominator)
            phase = rf'$\frac{{{numerator}{var}}}{{{denominator}}}$' if denominator else rf'${numerator}{var}$'
            if phase == r'$\frac{\pi}{2}$':
                phase = r'$+$'
            elif phase == r'$\frac{3\pi}{2}$':
                phase = r'$-$'

        x = graph.row(vertex)
        y = - graph.qubit(vertex)
        s = '        \\node [style={}] ({:d}) at ({:.2f}, {:.2f}) {{{:s}}};'.format(style, vertex, x, y, phase)
        vertices.append(s)
        max_index = vertex

    edges = []
    for edge in graph.edges():
        source, target = graph.edge_st(edge)
        type = graph.edge_type(edge)
        s = '        \\draw '
        if type == EdgeType.HADAMARD:
            if graph.type(source) != VertexType.BOUNDARY and graph.type(target) != VertexType.BOUNDARY:
                style = settings.tikz_classes['hadamard_edge']
                if style:
                    s += f'[style={style}] '
            else:
                x = (graph.row(source) + graph.row(target)) / 2.0
                y = -(graph.qubit(source) + graph.qubit(target)) / 2.0
                t = '        \\node [style={:s}] ({:d}) at ({:.2f}, {:.2f}) {{}};'.format(
                    settings.tikz_classes['hadamard'], 1, x, y)
                vertices.append(t)
                max_index += 1
        else:
            style = settings.tikz_classes['edge']
            if style:
                s += "[style={:s}] ".format(style)
        s += "({:d}) to ({:d});".format(source, target)
        edges.append(s)

    return tikz_template.format(scale=scale, vertices='\n'.join(vertices), edges='\n'.join(edges))
