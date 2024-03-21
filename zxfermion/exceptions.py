class MissingDiscoData(Exception):
    """Data file not found"""
    pass


class IncompatibleQubitDimension(Exception):
    """Raised when adding two objects with different num_qubits"""
    pass


class IncompatibleType(Exception):
    """Raised when attempting to add non Gadget/GadgetCircuit type"""
    pass
