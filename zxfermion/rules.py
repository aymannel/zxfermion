from zxfermion.types import LegType

# commutation rules for the CX gate
cx_rules = {
    (LegType.X, LegType.X): (LegType.X, LegType.I),
    (LegType.X, LegType.Y): (LegType.Y, LegType.Z),
    (LegType.X, LegType.Z): (LegType.Y, LegType.Y),
    (LegType.X, LegType.I): (LegType.X, LegType.X),
    (LegType.Y, LegType.X): (LegType.Y, LegType.I),
    (LegType.Y, LegType.Y): (LegType.X, LegType.Z),
    (LegType.Y, LegType.Z): (LegType.X, LegType.Y),
    (LegType.Y, LegType.I): (LegType.Y, LegType.X),
    (LegType.Z, LegType.X): (LegType.Z, LegType.X),
    (LegType.Z, LegType.Y): (LegType.I, LegType.Y),
    (LegType.Z, LegType.Z): (LegType.I, LegType.Z),
    (LegType.Z, LegType.I): (LegType.Z, LegType.I),
    (LegType.I, LegType.X): (LegType.I, LegType.X),
    (LegType.I, LegType.Y): (LegType.Z, LegType.Y),
    (LegType.I, LegType.Z): (LegType.Z, LegType.Z),
    (LegType.I, LegType.I): (LegType.I, LegType.I),
}

# commutation rules for the CZ gate
cz_rules = {
    (LegType.X, LegType.X): (LegType.Y, LegType.Y),
    (LegType.X, LegType.Y): (LegType.Y, LegType.X),
    (LegType.X, LegType.Z): (LegType.X, LegType.I),
    (LegType.X, LegType.I): (LegType.X, LegType.Z),
    (LegType.Y, LegType.X): (LegType.X, LegType.Y),
    (LegType.Y, LegType.Y): (LegType.X, LegType.X),
    (LegType.Y, LegType.Z): (LegType.Y, LegType.I),
    (LegType.Y, LegType.I): (LegType.Y, LegType.Z),
    (LegType.Z, LegType.X): (LegType.I, LegType.X),
    (LegType.Z, LegType.Y): (LegType.I, LegType.Y),
    (LegType.Z, LegType.Z): (LegType.Z, LegType.Z),
    (LegType.Z, LegType.I): (LegType.Z, LegType.I),
    (LegType.I, LegType.X): (LegType.Z, LegType.X),
    (LegType.I, LegType.Y): (LegType.Z, LegType.Y),
    (LegType.I, LegType.Z): (LegType.I, LegType.Z),
    (LegType.I, LegType.I): (LegType.I, LegType.I),
}

# commutation rules for the Pauli Z gate
z_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (LegType.X, -1),
    LegType.Y: (LegType.Y, -1),
    LegType.Z: (LegType.Z, 1),
}

# commutation rules for the Pauli X gate
x_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (LegType.X, 1),
    LegType.Y: (LegType.Y, -1),
    LegType.Z: (LegType.Z, -1),
}

# commutation rules for the Hadamard gate
hadamard_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (LegType.Z, 1),
    LegType.Y: (LegType.Y, -1),
    LegType.Z: (LegType.X, 1)
}

# commutation rules for the Clifford Rz(π/2) gate
cliff_z_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (LegType.Y, -1),
    LegType.Y: (LegType.X, 1),
    LegType.Z: (LegType.Z, 1)
}

# commutation rules for the Clifford Rz(3π/2) gate
cliff_z_minus_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (),
    LegType.Y: (),
    LegType.Z: ()
}

# commutation rules for the Clifford Rx(π/2) gate
cliff_x_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (LegType.X, 1),
    LegType.Y: (LegType.Z, -1),
    LegType.Z: (LegType.Y, 1)
}

# commutation rules for the Clifford Rx(3π/2) gate
cliff_x_minus_rules = {
    LegType.I: (LegType.I, 1),
    LegType.X: (),
    LegType.Y: (),
    LegType.Z: ()
}
