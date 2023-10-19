import re
import pyzx as zx
import numpy as np

from numbers import Real
from typing import Literal
from collections.abc import Sequence

from openfermion import jordan_wigner, QubitOperator
from openfermion.circuits import pauli_exp_to_qasm
from openfermion.ops import FermionOperator

from zxfermion.exceptions import MissingDiscoData

VertexType = int
VertexRef = int


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


class DiscoData:
    """Class to parse results of DISCO-VQE algorithm"""
    def __init__(self, geometry: str, result_id: str):
        try:
            with open(f'DISCO_data/{geometry}/lowest.{result_id}') as file:
                data = file.read()
        except FileNotFoundError as exception:
            raise MissingDiscoData(exception)

        self.qubit_number = 8
        self.geometry = geometry
        self.result_id = result_id
        self.operator_pool = self._get_operator_pool()
        self.energy = float(re.search(r'energy=\s*([-+]?\d*\.\d+)', data).group(1))

        self.phases = [float(c.strip()) for c in data.splitlines()[2:]]
        self.operator_order = self._get_operator_order()
        self.operators = [self.operator_pool[i - 1] for i in self.operator_order]

        # NB: ordered list of data to be passed to the Ansatz class
        self.ansatz_data = [self.qubit_number, self.operators, self.phases,
                            self.energy, self.geometry, self.operator_order]

    def _get_operator_order(self):
        with open(f'DISCO_data/{self.geometry}/oporder.{self.result_id}') as file:
            return [int(op.strip()) for op in file.read().splitlines()]

    def _get_operator_pool(self) -> list[Operator]:
        with open(f'DISCO_data/{self.geometry}/operator_pool.txt') as file:
            raw_operators = file.read()

        # extract slice of text containing operators
        pattern = r"Generating operator matrices\.\.\.(.*?)Operator matrices saved to 'opmat'"
        match = re.search(pattern, raw_operators, re.DOTALL)
        extracted_text = '\n'.join(match.group(1).strip().splitlines()[:-1])

        # extract operator strings
        extracted_operators = [o.strip() for o in re.split(r'Operator\s+\d+:', extracted_text)[1:]]
        return [Operator(op) for op in extracted_operators]


class Ansatz:
    """Class to represent UPS ansätze. Required arguments: number of qubits, list of operators and list of phases."""
    def __init__(self,
                 qubit_number: int,
                 operators: list[Operator],
                 phases: list[float],
                 energy: float | str | None = 'undefined',
                 geometry: str | None = 'undefined',
                 operator_order: list[int] | None = None,
                 ):

        self.energy = energy
        self.geometry = geometry
        self.qubit_number = qubit_number
        self.operator_order = operator_order if operator_order else [None] * len(operators)

        self.operators = operators
        self.qubit_operators = [jordan_wigner(o) for o in self.operators]

        self.phases = phases
        self.phases_radians = [c / np.pi for c in self.phases]

        self.circuits: list[zx.Circuit] = self.generate_circuits()
        self.complete_circuit: zx.Circuit = self.generate_complete_circuit()
        self.complete_graph = self.generate_graph()

    def __str__(self):
        metadata_str = (f'Geometry: {self.geometry}        '
                        f'Number of Qubits: {self.qubit_number}        '
                        f'Lowest Energy: {self.energy} Ha \n\n')

        data_str = [f'({idx})      {c} π      {o}'
                    for idx, o, c in zip(self.operator_order, self.operators, self.phases_radians)]

        return metadata_str + '\n'.join(data_str)

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
            circuit = zx.Circuit(self.qubit_number)
            for gate in [_get_zx_gate(os) for os in operator_strings]:
                circuit.add_gate(*gate)
            return circuit

        return [_generate_circuit(o, p) for o, p in zip(self.qubit_operators, self.phases_radians)]

    def generate_complete_circuit(self) -> zx.Circuit:
        complete_circuit = self.circuits[0]
        for circuit in self.circuits[1:]:
            complete_circuit.add_circuit(circuit)
        return complete_circuit

    def generate_graph(self) -> zx.Graph:
        def _add_vertex(g: zx.Graph, ref: VertexRef,
                        ty: VertexType, qubit: int, row: int, phase: Real | None = None) -> VertexRef:
            new_ref = g.add_vertex(ty, qubit=qubit, row=row, phase=phase)
            g.add_edge((ref, new_ref))
            return new_ref

        def _pauli_gadget(g: zx.Graph,
                          refs: Sequence[VertexRef],
                          row: int,
                          phase: float,
                          ps: Sequence[tuple[int, Literal["X", "Y", "Z"]]], *,
                          row_size: Real = 1, end_pad: Real = 1) -> tuple[Sequence[VertexRef], int]:
            refs = list(refs)
            assert (n:=len(refs)) >= np.max([q for q, _ in ps])+1

            # 1. Change of basis to Z
            for q, p in ps:
                match p:
                    case "X":
                        refs[q] = _add_vertex(g, refs[q], ty=zx.VertexType.H_BOX, qubit=q, row=row)
                    case "Y":
                        refs[q] = _add_vertex(g, refs[q], ty=zx.VertexType.X, qubit=q, row=row, phase=1/2)

            # 2. Phase gadget
            for q, _ in ps:
                refs[q] = _add_vertex(g, refs[q], ty=zx.VertexType.Z, qubit=q, row=row+1*row_size)
            hub_ref = g.add_vertex(zx.VertexType.X, qubit=n, row=row+2*row_size)
            for q, _ in ps:
                g.add_edge((refs[q], hub_ref))
            tip_ref = g.add_vertex(zx.VertexType.Z, qubit=n+1, row=row+2*row_size, phase=phase)
            g.add_edge((hub_ref, tip_ref))

            # 3. Change of basis from Z
            for q, p in ps:
                match p:
                    case "X":
                        refs[q] = _add_vertex(g, refs[q], ty=zx.VertexType.H_BOX, qubit=q, row=row+2*row_size)
                    case "Y":
                        refs[q] = _add_vertex(g, refs[q], ty=zx.VertexType.X, qubit=q, row=row+2*row_size, phase=-1/2)
            return refs, row+3*row_size+end_pad

        def _jw_op(g: zx.Graph,
                   op: QubitOperator,
                   refs: Sequence[VertexRef],
                   row: int,
                   angle: Real, *,
                   row_size: Real = 1, end_pad: Real = 1) -> tuple[Sequence[VertexRef], int]:
            for ps, c in op.terms.items():
                phase = c.imag*angle
                refs, row = _pauli_gadget(g, refs, row, phase, ps, row_size=row_size, end_pad=end_pad)
            return refs, row

        def ansatz_to_graph(*, ops: Sequence[int] | None = None, row_size: Real = 1, end_pad: Real = 1) -> zx.Graph:
            if ops is None:
                ops = range(self.qubit_number)
            g = zx.Graph()
            refs = [g.add_vertex(qubit=q, row=0) for q in range(self.qubit_number)]
            row = 1
            all_ops_list = list(zip(self.qubit_operators, self.phases_radians))
            select_ops_list = [all_ops_list[idx] for idx in ops]
            for op, angle in select_ops_list:
                refs, row = _jw_op(g, op, refs, row, float(angle), row_size=row_size, end_pad=end_pad)
            out_refs = [g.add_vertex(qubit=q, row=row) for q in range(self.qubit_number)]
            g.add_edges(list(zip(refs, out_refs)))
            return g

        return ansatz_to_graph()
