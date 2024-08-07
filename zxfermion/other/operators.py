from zxfermion.circuits.circuits import GadgetCircuit

operators = [GadgetCircuit.from_dict(operator_dict) for operator_dict in [
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "IIIIYZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IIIIXZY", "phase": 1.5}},
            {"Gadget": {"pauli_string": "IIIIIYZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IIIIIXZY", "phase": 1.5}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "IIYZZZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IIXZZZY", "phase": 1.5}},
            {"Gadget": {"pauli_string": "IIIYZZZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IIIXZZZY", "phase": 1.5}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "IIYZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IIXZY", "phase": 1.5}},
            {"Gadget": {"pauli_string": "IIIYZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IIIXZY", "phase": 1.5}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "YZZZZZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "XZZZZZY", "phase": 1.5}},
            {"Gadget": {"pauli_string": "IYZZZZZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IXZZZZZY", "phase": 1.5}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "YZZZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "XZZZY", "phase": 1.5}},
            {"Gadget": {"pauli_string": "IYZZZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IXZZZY", "phase": 1.5}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "YZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "XZY", "phase": 1.5}},
            {"Gadget": {"pauli_string": "IYZX", "phase": 0.5}},
            {"Gadget": {"pauli_string": "IXZY", "phase": 1.5}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "IIIIYXXX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIIIYXYY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIIIXXYX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIIIXXXY", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIIIYYYX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIIIYYXY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIIIXYXX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIIIXYYY", "phase": 0.125}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "IIYXIIXX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIYXIIYY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXXIIYX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXXIIXY", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIYYIIYX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIYYIIXY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXYIIXX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXYIIYY", "phase": 0.125}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "IIYXXX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIYXYY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXXYX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXXXY", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIYYYX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "IIYYXY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXYXX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "IIXYYY", "phase": 0.125}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "YXIIIIXX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YXIIIIYY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XXIIIIYX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XXIIIIXY", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YYIIIIYX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YYIIIIXY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XYIIIIXX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XYIIIIYY", "phase": 0.125}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "YXIIXX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YXIIYY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XXIIYX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XXIIXY", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YYIIYX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YYIIXY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XYIIXX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XYIIYY", "phase": 0.125}}
        ]
    },
    {
        "num_qubits": 8,
        "gates": [
            {"Gadget": {"pauli_string": "YXXX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YXYY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XXYX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XXXY", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YYYX", "phase": 0.125}},
            {"Gadget": {"pauli_string": "YYXY", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XYXX", "phase": 1.875}},
            {"Gadget": {"pauli_string": "XYYY", "phase": 0.125}}
        ]
    }
]]
