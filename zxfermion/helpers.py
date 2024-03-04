import numpy as np
from openfermion import FermionOperator


def pair_list(items: list[int]) -> list[tuple[int, int]]:
    return [(items[idx], items[idx + 1]) for idx in range(len(items) - 1)]


def latexify_operator(operator: FermionOperator) -> str:
    if not operator.terms:
        return '0'
    string_rep = list()
    for term, coeff in sorted(operator.terms.items()):
        if np.isclose(coeff, 0.0):
            continue
        elif coeff == 1:
            tmp_string = ''
        elif coeff == -1:
            tmp_string = '- '
        else:
            tmp_string = f'{coeff} × '
        for factor in term:
            index, action = factor
            action_string = ('^\\dagger', '')[operator.actions.index(action)]
            tmp_string += f'a{action_string}_{{({index})}}'
        string_rep.append(tmp_string.strip())
    return '$' + ' + '.join(string_rep).replace('+ -', '-') + '$'


def stringify_operator(operator: FermionOperator) -> str:
    if not operator.terms:
        return '0'
    string_rep = list()
    for term, coeff in sorted(operator.terms.items()):
        if np.isclose(coeff, 0.0):
            continue
        elif coeff == 1:
            tmp_string = ''
        elif coeff == -1:
            tmp_string = '- '
        else:
            tmp_string = f'{coeff} × '
        for factor in term:
            index, action = factor
            action_string = ('†', '')[operator.actions.index(action)]
            tmp_string += f'a{action_string}({index})'
        string_rep.append(tmp_string.strip())
    return ' + '.join(string_rep).replace('+ -', '-')
