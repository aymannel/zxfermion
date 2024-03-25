import re
import numpy as np
from typing import Optional
from zxfermion.config import tikz_styles


def matrix_to_latex(array: np.array) -> str:
    latex_str = r'\begin{pmatrix}'
    for row in array:
        for elem in row:
            real_part = np.real(elem)
            imag_part = np.imag(elem)
            if np.isclose(imag_part, 0):
                latex_str += f'{real_part:.0f}'
            elif np.isclose(real_part, 0):
                latex_str += f'{imag_part:.0f}i'
            else:
                latex_str += f'({real_part:.0f}{"+" if imag_part > 0 else ""}{imag_part:.0f}i)'
            latex_str += ' & '
        latex_str = latex_str[:-2] + r'\\'
    latex_str = latex_str.replace('-0', '0')
    latex_str = latex_str[:-2] + r'\end{pmatrix}'
    return latex_str


def tex_parse_tikz(content: str, phase_row: int, symbol: Optional[str] = None, scale: Optional[float] = None):
    scale = 0.5 if symbol is None else scale
    symbol = r'\theta' if symbol is None else symbol
    pattern = rf'\[style=Z phase dot\]\s*\((\d+)\)\s*at\s*\((.*?),\s*-{phase_row}\.00\)\s*{{\$(.*?)\$}};'
    cliffords = {r'$\frac{\pi}{2}$': r'$+$', r'$\frac{3\pi}{2}$': r'$-$'}
    content = content.replace(r'\begin{tikzpicture}', rf'\begin{{tikzpicture}}[scale={scale}]')
    content = [line.replace(r'\pi', symbol) if re.search(pattern, line) else line for line in content.splitlines()]
    content = '\n'.join(content)
    for key in cliffords:
        content = content.replace(f'{key}', f'{cliffords[key]}')
    for key in tikz_styles:
        content = content.replace(f'style={key}', f'style={tikz_styles[key]}')
    with open('tikz/template.tex', 'r') as file:
        tex_output = file.read()
        tex_output = tex_output.replace('TIKZ_PICTURE', content.strip())
    return tex_output
