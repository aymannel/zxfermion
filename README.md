# TODO
- move project to ~/Documents/Dev/zxfermion/ and create alias for Obsidian folder
- fix BaseGraph.update_rows() method

## BaseGraph
- move graphing functionality of each gate type to methods of BaseGraph class. eg methods for adding CX, Gadget, X, etc
  - this way, each gate type (or gadget type)
  - only contains essential information about it

## Gadget
- add expand gadgets option/method
- fuse gadgets after 'stacking'. will require you to check gadgets in adjacent layers can't just use fuse_gadgets()

## GadgetCircuit
- for now, keep conjugate_ methods but eventually this functionality should be handled by GadgetCircuit class
- this should be done by a permutation method that swaps the order of two 'gadgets' in a circuit...
- then apply the necessary transformations. raises a not implemented error if not implemented

### Persistence Formats
- use pickle!
- create standard way of saving GadgetCircuits
- move disco.py into separate package or JSON. like come up with your own standard for saving gadgets and circuits

### TikZ Export
- replace \pi for \theta where not \frac{\pi}...

### PDF Export
- inspect tikz log file in tikzit
- write seperate python script that creates template

---


# ZxFermion

## Motivation
ZxFermion is a Python package for manipulating Pauli gadgets. It's intended purpose is to facilitate derivations and proofs relating to circuits of Pauli gadgets.

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
