from __future__ import annotations

import re
import pyzx as zx
import numpy as np

from numbers import Real
from typing import Literal
from collections.abc import Sequence

from IPython.display import display, Markdown
from openfermion import jordan_wigner, QubitOperator
from openfermion.circuits import pauli_exp_to_qasm
from openfermion.ops import FermionOperator

from DISCO_data.operator_graphs import operator_graphs
from zxfermion.exceptions import MissingDiscoData

VertexType = int
VertexRef = int


class Operator(FermionOperator):
    """Wrapper class for FermionOperator class with updated __str__ dunder and make type hashable"""
    @classmethod
    def from_fermion_operator(cls, fermion_operator: FermionOperator) -> Operator:
        return Operator(str(fermion_operator))

    # define Operator hash for use in set() and dict()
    def __hash__(self):
        return hash(tuple((self.terms.items())))

    # redefine __str__ dunder so us mere humans can understand the data
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

    @property
    def repr_latex(self):
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
                action_string = ('^\\dagger', '')[self.actions.index(action)]
                tmp_string += f'a{action_string}_{{({index})}}'
            string_rep.append(tmp_string.strip())
        return ' + '.join(string_rep).replace('+ -', '-')

    def _repr_latex_(self):
        return f'${self.repr_latex}$'

    def generate_graph(self) -> zx.Graph:
        def _add_vertex(graph: zx.Graph,
                        vtx_ref: VertexRef,
                        vtx_type: VertexType,
                        qubit: int,
                        row: int,
                        phase: Real | None = None) -> VertexRef:

            new_ref = graph.add_vertex(vtx_type, qubit=qubit, row=row, phase=phase)
            graph.add_edge((vtx_ref, new_ref))
            return new_ref

        def _pauli_gadget(graph: zx.Graph,
                          vtx_refs: Sequence[VertexRef],
                          row: int,
                          phase: float,
                          paulis: Sequence[tuple[int, Literal["X", "Y", "Z"]]],
                          # *,  # TODO
                          row_size: Real = 1,
                          end_pad: Real = 1) -> tuple[Sequence[VertexRef], int]:

            vtx_refs = list(vtx_refs)
            assert (n := len(vtx_refs)) >= np.max([q for q, _ in paulis]) + 1

            # 1. Change of basis to Z
            for qubit, pauli in paulis:
                match pauli:
                    case "X":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.H_BOX,
                                                      qubit=qubit,
                                                      row=row)
                    case "Y":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.X,
                                                      qubit=qubit,
                                                      row=row,
                                                      phase=1/2)

            # Phase gadget X spider hub
            hub_ref = graph.add_vertex(zx.VertexType.X, qubit=n, row=row + 2 * row_size)

            # Phase gadget Z spiders
            for qubit, _ in paulis:
                vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                              vtx_type=zx.VertexType.Z,
                                              qubit=qubit,
                                              row=row + 1 * row_size)

                graph.add_edge((vtx_refs[qubit], hub_ref))

            # Phase Z spider
            phase_hub_ref = graph.add_vertex(zx.VertexType.Z, qubit=n + 1, row=row + 2 * row_size, phase=phase)
            graph.add_edge((hub_ref, phase_hub_ref))

            # 3. Change of basis from Z
            for qubit, pauli in paulis:
                match pauli:
                    case "X":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.H_BOX,
                                                      qubit=qubit,
                                                      row=row + 2 * row_size)
                    case "Y":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.X,
                                                      qubit=qubit,
                                                      row=row + 2 * row_size,
                                                      phase=-1/2)

            return vtx_refs, row + 3 * row_size + end_pad

        def _jw_op(graph: zx.Graph,
                   op: QubitOperator,
                   vtx_refs: Sequence[VertexRef],
                   row: int,
                   phase: Real, *,  # TODO
                   row_size: Real = 1,
                   end_pad: Real = 1) -> tuple[Sequence[VertexRef], int]:

            for paulis, c in op.terms.items():
                phase = c.imag  # TODO plus or times?
                vtx_refs, row = _pauli_gadget(graph, vtx_refs, row, phase, paulis, row_size=row_size, end_pad=end_pad)

            return vtx_refs, row

        def ansatz_to_graph(*,
                            row: int = 1,
                            row_size: Real = 1,
                            end_pad: Real = 1,
                            qubit_number: int = 8) -> zx.Graph:

            graph = zx.Graph()

            # instantiate boundary vertices
            vtx_refs = [graph.add_vertex(qubit=q, row=0) for q in range(qubit_number)]

            vtx_refs, row = _jw_op(graph, jordan_wigner(self), vtx_refs,
                                   row=row, phase=float(0),
                                   row_size=row_size, end_pad=end_pad)

            out_refs = [graph.add_vertex(qubit=q, row=row + 1) for q in range(qubit_number)]
            graph.add_edges(list(zip(vtx_refs, out_refs)))
            return graph

        return ansatz_to_graph()


class OperatorPool:
    def __init__(self, geometry: str = 'H4_linear'):
        self.geometry = geometry
        self.operators = self._get_operators()
        self.graph = operator_graphs.get(self.geometry)

    def _get_operators(self) -> list[Operator]:
        with open(f'DISCO_data/{self.geometry}/operator_pool.txt') as file:
            raw_operators = file.read()

        # extract slice of text containing operators
        pattern = r"Generating operator matrices\.\.\.(.*?)Operator matrices saved to 'opmat'"
        match = re.search(pattern, raw_operators, re.DOTALL)
        extracted_text = '\n'.join(match.group(1).strip().splitlines()[:-1])

        # extract operator strings
        extracted_operators = [o.strip() for o in re.split(r'Operator\s+\d+:', extracted_text)[1:]]
        return [Operator(op) for op in extracted_operators]

    def get_index(self, operator: Operator) -> str:
        return {op: idx+1 for idx, op in enumerate(self.operators)}.get(operator)


class Ansatz:
    """Class to represent UPS ansätze. Required arguments: number of qubits, list of operators and list of phases."""
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
            operator_strings = list(pauli_exp_to_qasm(qubit_operator,
                                                      evolution_time=phase,
                                                      qubit_list=None,
                                                      ancilla=None))

            # construct zx.Circuit for a given qubit operator
            circuit = zx.Circuit(self.qubit_number)
            for gate in [_get_zx_gate(os) for os in operator_strings]:
                circuit.add_gate(*gate)
            return circuit

        return [_generate_circuit(o, p) for o, p in zip(self.qubit_operators, self.phases_radians)]

    def generate_complete_circuit(self) -> zx.Circuit:
        circuits = self.generate_circuits()
        complete_circuit = circuits[0]
        for circuit in circuits[1:]:
            complete_circuit.add_circuit(circuit)
        return complete_circuit

    def generate_graph(self) -> zx.Graph:
        def _add_vertex(graph: zx.Graph,
                        vtx_ref: VertexRef,
                        vtx_type: VertexType,
                        qubit: int,
                        row: int,
                        phase: Real | None = None) -> VertexRef:

            new_ref = graph.add_vertex(vtx_type, qubit=qubit, row=row, phase=phase)
            graph.add_edge((vtx_ref, new_ref))
            return new_ref

        def _pauli_gadget(graph: zx.Graph,
                          vtx_refs: Sequence[VertexRef],
                          row: int,
                          phase: float,
                          paulis: Sequence[tuple[int, Literal["X", "Y", "Z"]]],
                          # *,  # TODO
                          row_size: Real = 1,
                          end_pad: Real = 1) -> tuple[Sequence[VertexRef], int]:

            vtx_refs = list(vtx_refs)
            assert (n := len(vtx_refs)) >= np.max([q for q, _ in paulis]) + 1

            # 1. Change of basis to Z
            for qubit, pauli in paulis:
                match pauli:
                    case "X":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.H_BOX,
                                                      qubit=qubit,
                                                      row=row)
                    case "Y":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.X,
                                                      qubit=qubit,
                                                      row=row,
                                                      phase=1/2)

            # Phase gadget X spider hub
            hub_ref = graph.add_vertex(zx.VertexType.X, qubit=n, row=row + 2 * row_size)

            # Phase gadget Z spiders
            for qubit, _ in paulis:
                vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                              vtx_type=zx.VertexType.Z,
                                              qubit=qubit,
                                              row=row + 1 * row_size)

                graph.add_edge((vtx_refs[qubit], hub_ref))

            # Phase Z spider
            phase_hub_ref = graph.add_vertex(zx.VertexType.Z, qubit=n + 1, row=row + 2 * row_size, phase=phase)
            graph.add_edge((hub_ref, phase_hub_ref))

            # 3. Change of basis from Z
            for qubit, pauli in paulis:
                match pauli:
                    case "X":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.H_BOX,
                                                      qubit=qubit,
                                                      row=row + 2 * row_size)
                    case "Y":
                        vtx_refs[qubit] = _add_vertex(graph, vtx_refs[qubit],
                                                      vtx_type=zx.VertexType.X,
                                                      qubit=qubit,
                                                      row=row + 2 * row_size,
                                                      phase=-1/2)

            return vtx_refs, row + 3 * row_size + end_pad

        def _jw_op(graph: zx.Graph,
                   op: QubitOperator,
                   vtx_refs: Sequence[VertexRef],
                   row: int,
                   phase: Real, *,  # TODO
                   row_size: Real = 1,
                   end_pad: Real = 1) -> tuple[Sequence[VertexRef], int]:

            for paulis, c in op.terms.items():
                phase = c.imag + phase  # TODO plus or times?
                vtx_refs, row = _pauli_gadget(graph, vtx_refs, row, phase, paulis, row_size=row_size, end_pad=end_pad)

            return vtx_refs, row

        def ansatz_to_graph(*,
                            row: int = 1,
                            ops: Sequence[int] | None = None,
                            row_size: Real = 1,
                            end_pad: Real = 1) -> zx.Graph:

            graph = zx.Graph()
            ops = range(self.qubit_number) if ops is None else ops

            # instantiate boundary vertices
            vtx_refs = [graph.add_vertex(qubit=q, row=0) for q in range(self.qubit_number)]

            # select operators
            all_ops_list = list(zip(self.qubit_operators, self.phases_radians))
            # select_ops_list = [all_ops_list[idx] for idx in ops]
            select_ops_list = all_ops_list

            for op, phase in select_ops_list:
                vtx_refs, row = _jw_op(graph, op, vtx_refs,
                                       row=row, phase=float(phase),
                                       row_size=row_size, end_pad=end_pad)

            out_refs = [graph.add_vertex(qubit=q, row=row + 1) for q in range(self.qubit_number)]
            graph.add_edges(list(zip(vtx_refs, out_refs)))
            return graph

        return ansatz_to_graph()
