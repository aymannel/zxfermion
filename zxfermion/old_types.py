from __future__ import annotations

import re

import numpy as np
from IPython.display import display, Markdown
from openfermion import jordan_wigner
from openfermion.ops import FermionOperator

from zxfermion.exceptions import MissingDiscoData

VertexType = int
VertexRef = int


class OperatorPoolS:
    def __init__(self, fermion_operators: list[FermionOperator]):
        self.fermion_operators = fermion_operators
        self.operators = [Operator(fermion_operator) for fermion_operator in self.fermion_operators]

    @staticmethod
    def from_disco_data(geometry: str = 'H4_linear') -> OperatorPoolS:
        with open(f'DISCO_data/{geometry}/operator_pool.txt') as file:
            raw_operators = file.read()

        # extract slice of text containing fermion_operators
        pattern = r"Generating operator matrices\.\.\.(.*?)Operator matrices saved to 'opmat'"
        match = re.search(pattern, raw_operators, re.DOTALL)
        extracted_text = '\n'.join(match.group(1).strip().splitlines()[:-1])
        fermion_operators = [FermionOperator(o.strip()) for o in re.split(r'Operator\s+\d+:', extracted_text)[1:]]
        return OperatorPoolS(fermion_operators)


class OperatorPool:
    def __init__(self, geometry: str = 'H4_linear'):
        self.geometry = geometry
        self.operators = self._get_operators()

    def _get_operators(self) -> list[FermionOperator]:
        with open(f'DISCO_data/{self.geometry}/operator_pool.txt') as file:
            raw_operators = file.read()

        # extract slice of text containing fermion_operators
        pattern = r"Generating operator matrices\.\.\.(.*?)Operator matrices saved to 'opmat'"
        match = re.search(pattern, raw_operators, re.DOTALL)
        extracted_text = '\n'.join(match.group(1).strip().splitlines()[:-1])

        # extract operator strings
        extracted_operators = [o.strip() for o in re.split(r'Operator\s+\d+:', extracted_text)[1:]]
        return [FermionOperator(op) for op in extracted_operators]

    def get_index(self, operator: FermionOperator) -> str:
        return {op: idx+1 for idx, op in enumerate(self.operators)}.get(operator)


class Ansatz:
    def __init__(self, result_id: str, geometry: str = 'H4_linear', qubit_number: int = 8):
        try:
            with open(f'DISCO_data/{geometry}/lowest.{result_id}') as file:
                ansatz_data = file.read()
        except FileNotFoundError as exception:
            raise MissingDiscoData(exception)

        self.result_id = result_id
        self.geometry = geometry
        self.qubit_number = qubit_number

        self.energy = float(re.search(r'energy=\s*([-+]?\d*\.\d+)', ansatz_data).group(1))
        self.phases = [float(c.strip()) for c in ansatz_data.splitlines()[2:][::-1]]
        self.phases_radians = [c / np.pi for c in self.phases]

        self.operator_pool = OperatorPool(self.geometry)
        self.operator_order = self._get_operator_order()
        self.operators = [self.operator_pool.operators[i - 1] for i in self.operator_order]
        self.qubit_operators = [jordan_wigner(o) for o in self.operators]

    def __str__(self):
        metadata_str = (f'Geometry: {self.geometry}        '
                        f'Number of Qubits: {self.qubit_number}        '
                        f'Lowest Energy: {self.energy} Ha \n\n')

        data_str = [f'({idx})      {c} π      {o}' for idx, o, c in zip(
            self.operator_order,
            self.operators,
            self.phases_radians)] if self.operator_order else [f'{c} π      {o}' for o, c in zip(
            self.operators,
            self.phases_radians)]

        return metadata_str + '\n'.join(data_str)

    def _repr_latex_(self):
        metadata_str = (rf'$'
                        rf'\text{{Result: }} {self.result_id} \qquad'
                        rf'\text{{Geometry: {self.geometry.replace("_", " ")}}} \qquad'
                        rf'\text{{Number of qubits: }} {self.qubit_number} \qquad'
                        rf'\text{{Lowest energy: }} {self.energy} \text{{ Ha}}' 
                        '$' + '\n\n')

        operator_order_str = (rf'$'
                              rf'\text{{Operator Order: }}' +
                              rf'\rightarrow'.join([str(self.operator_pool.get_index(o)) for o in self.operators]) +
                              '$' + '\n\n')

        operators_str = '\n\n'.join([rf'$'
                                     rf'\text{{phase}} = {ph:+.5f} \,\,\pi \qquad\qquad '
                                     rf'\text{{operator }} {self.operator_pool.get_index(op)} = {op.repr_latex}'
                                     rf'$' for op, ph in zip(self.operators, self.phases_radians)])

        display(Markdown(metadata_str + operator_order_str + operators_str))
        return None

    def _get_operator_order(self):
        with open(f'DISCO_data/{self.geometry}/oporder.{self.result_id}') as file:
            return [int(op.strip()) for op in file.read().splitlines()][::-1]
