class MissingDiscoData(Exception):
    """Data file not found"""
    pass


class DifferentQubitDimensionException(Exception):
    """Raised when adding two objects with different num_qubits"""
    pass
