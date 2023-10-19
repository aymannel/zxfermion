import re
import pyzx as zx
import numpy as np

from helpers import get_operator_pool

from openfermion import jordan_wigner, QubitOperator
from openfermion.circuits import pauli_exp_to_qasm
from openfermion.ops import FermionOperator


class Operator(FermionOperator):
    @classmethod
    def from_fermion_operator(cls, fermion_operator: FermionOperator) -> 'Operator':
        return Operator(str(fermion_operator))

    def __str__(self):
        if not self.terms:
            return '0'
        string_rep = list()
        for term, coeff in sorted(self.terms.items()):
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
                action_string = ('†', '')[self.actions.index(action)]
                tmp_string += f'a{action_string}({index})'
            string_rep.append(tmp_string.strip())
        return ' + '.join(string_rep).replace('+ -', '-')

    def __repr__(self):
        return str(super().__str__())


class Ansatz:
    def __init__(self, system: str, result_id: str):
        with open(f'DISCO_data/{system}/lowest.{result_id}') as file:
            data = file.read()

        self.system: str = system
        self.result_id: str = result_id
        self.step: int = int(re.search(r'found at step\s+(\d+)', data).group(1))
        self.energy: float = float(re.search(r'energy=\s*([-+]?\d*\.\d+)', data).group(1))

        self.phases: list[float] = [float(c.strip()) for c in data.splitlines()[2:]]
        self.phases_radians: list[float] = [c / np.pi for c in self.phases]
        self.operators: list[Operator] = self.get_operators()
        self.qubit_operators: list[QubitOperator] = [jordan_wigner(o) for o in self.operators]

        self.circuits: list[zx.Circuit] = self.generate_circuits()
        self.full_circuit: zx.Circuit = self.generate_full_circuit()

    def __str__(self):
        return (f'Result: {self.result_id} \n' +
                '\n'.join([f'({idx})    {c} π    {o}' for idx, (o, c)
                           in enumerate(zip(self.operators, self.phases_radians))]))

    def get_operators(self) -> list[Operator]:
        operator_pool = [Operator.from_fermion_operator(o) for o in get_operator_pool(system=self.system)]
        with open(f'DISCO_data/{self.system}/oporder.{self.result_id}') as file:
            operator_order = [int(op.strip()) for op in file.read().splitlines()]
            return [operator_pool[i - 1] for i in operator_order]

    def generate_circuits(self) -> list[zx.Circuit]:
        def _generate_circuit(qubit_operator: QubitOperator, phase: float) -> zx.Circuit:

            # convert operator string into zx gate e.g. ['Rx', '2', '3.145'] -> ['XPhase', 3.145, 2]
            def _get_zx_gate(operator_term: str):
                operator, params = operator_term.split()[0], operator_term.split()[1:]  # extract operator
                qubit_indices = [int(float(i)) for i in params if float(i).is_integer()]  # extract qubit_indices
                phase = [float(i) for i in params if not float(i).is_integer()]  # extract phase

                return {
                    'H': ('H', *qubit_indices),
                    'CNOT': ('CNOT', *qubit_indices),
                    'Rx': ('XPhase', *qubit_indices, *phase),
                    'Rz': ('ZPhase', *qubit_indices, *phase),
                }.get(operator)

            # transform qubit operator into operator strings e.g. ['H', '2']
            operator_strings = list(pauli_exp_to_qasm(qubit_operator, evolution_time=phase, qubit_list=None, ancilla=None))

            # construct zx.Circuit for a given qubit operator
            circuit = zx.Circuit(8)
            for gate in [_get_zx_gate(os) for os in operator_strings]:
                circuit.add_gate(*gate)
            return circuit

        return [_generate_circuit(o, p) for o, p in zip(self.qubit_operators, self.phases_radians)]

    def generate_full_circuit(self) -> zx.Circuit:
        complete_circuit = self.circuits[0]
        for circuit in self.circuits[1:]:
            complete_circuit.add_circuit(circuit)
        return complete_circuit
