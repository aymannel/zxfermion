from zxfermion.gadget import Gadget, GadgetCircuit


class OperatorPool:
    def __init__(self):
        self.circuits = []
        self.H4_operator_data = [
            [('IIIIYZXI', 0), ('IIIIXZYI', 0), ('IIIIIYZX', 0), ('IIIIIXZY', 0)],
            [('IIYZZZXI', 0), ('IIXZZZYI', 0), ('IIIYZZZX', 0), ('IIIXZZZY', 0)],
            [('IIYZXIII', 0), ('IIXZYIII', 0), ('IIIYZXII', 0), ('IIIXZYII', 0)],
            [('YZZZZZXI', 0), ('XZZZZZYI', 0), ('IYZZZZZX', 0), ('IXZZZZZY', 0)],
            [('YZZZXIII', 0), ('XZZZYIII', 0), ('IYZZZXII', 0), ('IXZZZYII', 0)],
            [('YZXIIIII', 0), ('XZYIIIII', 0), ('IYZXIIII', 0), ('IXZYIIII', 0)],
            [('IIIIYXXX', 0), ('IIIIYXYY', 0), ('IIIIXXYX', 0), ('IIIIXXXY', 0),
             ('IIIIYYYX', 0), ('IIIIYYXY', 0), ('IIIIXYXX', 0), ('IIIIXYYY', 0)],
            [('IIYXIIXX', 0), ('IIYXIIYY', 0), ('IIXXIIYX', 0), ('IIXXIIXY', 0),
             ('IIYYIIYX', 0), ('IIYYIIXY', 0), ('IIXYIIXX', 0), ('IIXYIIYY', 0)],
            [('IIYXXXII', 0), ('IIYXYYII', 0), ('IIXXYXII', 0), ('IIXXXYII', 0),
             ('IIYYYXII', 0), ('IIYYXYII', 0), ('IIXYXXII', 0), ('IIXYYYII', 0)],
            [('YXIIIIXX', 0), ('YXIIIIYY', 0), ('XXIIIIYX', 0), ('XXIIIIXY', 0),
             ('YYIIIIYX', 0), ('YYIIIIXY', 0), ('XYIIIIXX', 0), ('XYIIIIYY', 0)],
            [('YXIIXXII', 0), ('YXIIYYII', 0), ('XXIIYXII', 0), ('XXIIXYII', 0),
             ('YYIIYXII', 0), ('YYIIXYII', 0), ('XYIIXXII', 0), ('XYIIYYII', 0)],
            [('YXXXIIII', 0), ('YXYYIIII', 0), ('XXYXIIII', 0), ('XXXYIIII', 0),
             ('YYYXIIII', 0), ('YYXYIIII', 0), ('XYXXIIII', 0), ('XYYYIIII', 0)]
        ]
        for operator in self.H4_operator_data:
            self.circuits.append(
                GadgetCircuit(
                    [Gadget(paulis, phase) for paulis, phase in operator],
                    num_qubits=8
                )
            )
