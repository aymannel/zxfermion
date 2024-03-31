# ZxFermion

## Motivation
ZxFermion is a Python package for manipulating and visualising circuits of Pauli gadgets. It has built in Clifford tableau logic using [stim](https://github.com/quantumlib/Stim), allowing users to quickly implement proofs.
I built this package in response to a lack of a similar package whilst writing my thesis on the applications of the ZX calculus to quantum chemistry.
VQE algorithms for quantum chemistry make use of the unitary coupled cluster framework and are naturally expressed as circuits of phase gadgets.

Within the Unitary Coupled Cluster (UCC) and Variational Quantum Eigensolver (VQE) frameworks, molecules are simulated by constructing ansätze consisting of a sequence of fermionic excitation operators to account for electronic correlation. Generally, fermionic excitation operators are cast to quantum circuits as Pauli gadgets following exponentiation and the Jordan-Wigner transformation. Hence, ZxFermion serves as a tool to researchers for reasoning about the ansätze of molecules.

The `Gadget` and `GadgetCircuit` classes represent single Pauli gadgets and circuits of Pauli gadgets respectively. Each class comes equipped with methods describing the action of the members of the Pauli and Clifford groups on Pauli gadgets.

## Usage

### Decomposition of Double Fermionic Excitation to Triply Controlled Rotations

```python
circuit = GadgetCircuit(num_qubits=4, gadgets=[
  Gadget('YXXX', phase=1 / 4),
  Gadget('XYXX', phase=1 / 4),
  Gadget('XXYX', phase=-1 / 4),
  Gadget('YYYX', phase=-1 / 4),
  Gadget('YYXY', phase=1 / 4),
  Gadget('XXXY', phase=1 / 4),
  Gadget('XYYY', phase=-1 / 4),
  Gadget('YXYY', phase=-1 / 4),
])

circuit.graph()
circuit.surround_cx(control=3, target=0)
circuit.surround_cx(control=3, target=1)
circuit.surround_cx(control=3, target=2)
```

<img src="figures/first.png" alt="first" style="width: 80%; display: block; border-radius: 50%">
<img src="figures/second.png" alt="first" style="width: 80%; display: block; border-radius: 50%">
<img src="figures/third.png" alt="first" style="width: 80%; display: block; border-radius: 50%">
<img src="figures/fourth.png" alt="first" style="width: 80%; display: block; border-radius: 50%">


### Other Examples
See [Jupyter Notebook](notebook.ipynb)
