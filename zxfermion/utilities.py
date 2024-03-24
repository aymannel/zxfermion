import numpy as np


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
