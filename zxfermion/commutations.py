from zxfermion.types import PauliType

# commutation rules for the CX gate
cx_rules = {
    (PauliType.X, PauliType.X): (PauliType.X, PauliType.I),
    (PauliType.X, PauliType.Y): (PauliType.Y, PauliType.Z),
    (PauliType.X, PauliType.Z): (PauliType.Y, PauliType.Y),
    (PauliType.X, PauliType.I): (PauliType.X, PauliType.X),
    (PauliType.Y, PauliType.X): (PauliType.Y, PauliType.I),
    (PauliType.Y, PauliType.Y): (PauliType.X, PauliType.Z),
    (PauliType.Y, PauliType.Z): (PauliType.X, PauliType.Y),
    (PauliType.Y, PauliType.I): (PauliType.Y, PauliType.X),
    (PauliType.Z, PauliType.X): (PauliType.Z, PauliType.X),
    (PauliType.Z, PauliType.Y): (PauliType.I, PauliType.Y),
    (PauliType.Z, PauliType.Z): (PauliType.I, PauliType.Z),
    (PauliType.Z, PauliType.I): (PauliType.Z, PauliType.I),
    (PauliType.I, PauliType.X): (PauliType.I, PauliType.X),
    (PauliType.I, PauliType.Y): (PauliType.Z, PauliType.Y),
    (PauliType.I, PauliType.Z): (PauliType.Z, PauliType.Z),
    (PauliType.I, PauliType.I): (PauliType.I, PauliType.I),
}

# commutation rules for the CZ gate
cz_rules = {
    (PauliType.X, PauliType.X): (PauliType.Y, PauliType.Y),
    (PauliType.X, PauliType.Y): (PauliType.Y, PauliType.X),
    (PauliType.X, PauliType.Z): (PauliType.X, PauliType.I),
    (PauliType.X, PauliType.I): (PauliType.X, PauliType.Z),
    (PauliType.Y, PauliType.X): (PauliType.X, PauliType.Y),
    (PauliType.Y, PauliType.Y): (PauliType.X, PauliType.X),
    (PauliType.Y, PauliType.Z): (PauliType.Y, PauliType.I),
    (PauliType.Y, PauliType.I): (PauliType.Y, PauliType.Z),
    (PauliType.Z, PauliType.X): (PauliType.I, PauliType.X),
    (PauliType.Z, PauliType.Y): (PauliType.I, PauliType.Y),
    (PauliType.Z, PauliType.Z): (PauliType.Z, PauliType.Z),
    (PauliType.Z, PauliType.I): (PauliType.Z, PauliType.I),
    (PauliType.I, PauliType.X): (PauliType.Z, PauliType.X),
    (PauliType.I, PauliType.Y): (PauliType.Z, PauliType.Y),
    (PauliType.I, PauliType.Z): (PauliType.I, PauliType.Z),
    (PauliType.I, PauliType.I): (PauliType.I, PauliType.I),
}

# commutation rules for the Pauli Z gate
z_rules = {
    PauliType.X: -1,
    PauliType.Y: -1,
    PauliType.Z: 1,
}

# commutation rules for the Pauli X gate
x_rules = {
    PauliType.X: 1,
    PauliType.Y: -1,
    PauliType.Z: -1,
}

# commutation rules for the Hadamard gate
hadamard_rules = {
    PauliType.X: (PauliType.Z, 1),
    PauliType.Y: (PauliType.Y, -1),
    PauliType.Z: (PauliType.X, 1)
}

# commutation rules for the Clifford Rz(π/2) gate
z_plus_rules = {
    PauliType.X: (PauliType.Y, -1),
    PauliType.Y: (PauliType.X, 1),
    PauliType.Z: (PauliType.Z, 1)
}

# commutation rules for the Clifford Rz(3π/2) gate
cliff_z_minus_rules = {
    PauliType.X: (),
    PauliType.Y: (),
    PauliType.Z: ()
}

# commutation rules for the Clifford Rx(π/2) gate
x_plus_rules = {
    PauliType.X: (PauliType.X, 1),
    PauliType.Y: (PauliType.Z, -1),
    PauliType.Z: (PauliType.Y, 1)
}

# commutation rules for the Clifford Rx(3π/2) gate
cliff_x_minus_rules = {
    PauliType.X: (),
    PauliType.Y: (),
    PauliType.Z: ()
}
