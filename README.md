## Introduction
ZxFermion is a Python package built on top of [PyZX](https://pyzx.readthedocs.io/en/latest/) designed for the manipulation and visualisation of circuits of Pauli gadgets. With built-in Clifford tableau logic using [Stim](https://github.com/quantumlib/Stim), ZxFermion allows users to quickly implement proofs and test ideas.

VQE algorithms used in quantum chemistry often utilise the [UCC](https://doi.org/10.48550/arXiv.2109.15176) framework in which excitation operators have a natural representation as Pauli gadgets. ZxFermion provides a comprehensive toolset designed to be using in a Jupyter notebook environment. Export functionality can be used to generated research paper quality diagrams.

All of the following diagrams were made using ZxFermion.

## Getting Started

### Creating Pauli gadgets
To begin...
```python
from zxfermion.gates import Gadget

gadget = Gadget('YZX', phase=1/2)
gadget.draw(expand_gadget=True)
gadget.pdf('expanded_yzx_gadget')
```
<img src="figures/double.png" alt="expanded gadget" style="width: 100%; display: block">
<img src="figures/ex.png" alt="expanded gadget" style="width: 100%; display: block">
<img src="figures/ss.png" alt="expanded gadget" style="width: 100%; display: block">

By default gadgets are represented in the following more compact form.
```python
gadget = Gadget('YZX', phase=1/2)
gadget.draw()
gadget.pdf('yzx_gadget')
```
<img src="figures/nnew.png" alt="expanded gadget" style="width: 100%; display: block">
