import re
import pyzx as zx
import numpy as np

from numbers import Real
from typing import Literal
from collections.abc import Sequence

from openfermion import jordan_wigner, QubitOperator
from openfermion.circuits import pauli_exp_to_qasm
from openfermion.ops import FermionOperator

from helpers import get_operator_pool


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

    def __repr__(self):
        return str(super().__str__())


class Ansatz:
    def __init__(self, system: str, result_id: str):
        with open(f'DISCO_data/{system}/lowest.{result_id}') as file:
            data = file.read()

        self.qubit_number = 8

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
        self.full_graph = self.generate_graph()

    def __str__(self):
        data = enumerate(zip(self.operators, self.phases_radians))
        return f'Result: {self.result_id} \n' + '\n'.join([f'({idx})      {c} π      {o}' for idx, (o, c) in data])

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
            circuit = zx.Circuit(self.qubit_number)
            for gate in [_get_zx_gate(os) for os in operator_strings]:
                circuit.add_gate(*gate)
            return circuit

        return [_generate_circuit(o, p) for o, p in zip(self.qubit_operators, self.phases_radians)]

    def generate_full_circuit(self) -> zx.Circuit:
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

        def ansatz_to_graph(*,
                            ops: Sequence[int] | None = None,
                            row_size: Real = 1, end_pad: Real = 1) -> zx.Graph:
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
