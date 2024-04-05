# ZxFermion
<img src="figures/logo.png" width="150">

## Contents
- [1) What is ZxFermion?](#what-is-zxfermion?)
- [2) Getting Started](#getting-started)
  - [Creating Pauli Gadgets](#creating-pauli-gadgets)
  - [Creating Circuits of Gadgets](#creating-circuits-of-gadgets)
  - [Working with Cliffords](#working-with-cliffords)
- [3) Documentation](#documentation)
  - [BaseGraph](#basegraph-class)

## What is ZxFermion?
ZxFermion is a Python package built on top of [PyZX](https://pyzx.readthedocs.io/en/latest/) designed for the manipulation and visualisation of circuits of Pauli gadgets. With built-in Clifford tableau logic using [Stim](https://github.com/quantumlib/Stim), ZxFermion allows users to quickly implement proofs and test ideas.

VQE algorithms used in quantum chemistry often utilise the [UCC](https://doi.org/10.48550/arXiv.2109.15176) framework in which excitation operators have a natural representation as Pauli gadgets. ZxFermion provides a comprehensive toolset designed to be using in a Jupyter notebook environment. Export functionality can be used to generated research paper quality diagrams.

All of the following diagrams were made using ZxFermion.

## Getting Started

### Creating Pauli gadgets
To begin... Then to export to pdf, run `gadget.pdf('file_name')`.

```python
from zxfermion import Gadget
gadget = Gadget('YZX', as_gadget=False)
gadget.graph.draw()
```
![expanded_yzzx_gadget](figures/expanded_yzzx_gadget.png)

By default gadgets are represented in the following more compact form.
```python
gadget = Gadget('YZX', phase=1/2, as_gadget=True)
gadget.draw()
```

### Creating circuits of gadgets

### Working with Cliffords

## Documentation

### `BaseGraph` class
The `BaseGraph` class extends the PyZX `GraphS` class. It implements a number of useful methods and properties handling ZX diagrams.

#### `min_qubit`
Returns the minimum qubit of the current graph.

Return type: `int`

#### `max_qubit` property
Returns the maximum qubit of the current graph.

Return type: `int`

#### `input_row` property
Returns the input row index of the current graph.

Return type: `int`

#### `output_row` property
Returns the output row index of the current graph.

Return type: `int | float`

#### `left_row` property
Returns the leftmost row index of the current graph

Return type: `int | float`

#### `right_row` property
Returns the rightmost row index of the current graph

Return type: `int | float`

#### `left_padding` property
Returns the left padding (separation between `BaseGraph.input_row` and `BaseGraph.left_row`) of the current graph.

Return type: `int | float`

#### `right_padding` property
Returns the right padding (separation between `BaseGraph.output_row` and `BaseGraph.right_row`) of the current graph.

Return type: `int | float`

#### `boundaries` property
Returns the combined vertex indices of the inputs and outputs of the current graph.

Return type: `list[int]`

#### `graph_rows` property
Returns the row indices of the current graph (from `BaseGraph.left_row` to `BaseGraph.right_row` inclusive).

Return type: `list[int]`

#### `graph_depth` property
Returns the depth of the current graph from `BaseGraph.input_row` to `BaseGraph.output_row` (excluding vertices outside of graph bounds).

Return type: `int | float`

#### `left_end(qubit: int)` method

#### `right_end(qubit: int)` method

#### `left_row_within(top: int, bottom: int)` method

#### `right_row_within(top: int, bottom: int)` method

#### `bounded_vertices` property

#### `unbounded_vertices` property

#### `vertices_on_qubit(qubit: int)` method

#### `remove_wire(qubit: int)` method

#### `connect_vertices(vertices: list[int])` method

#### `set_input_row(row: int)` method

#### `set_output_row(row: int)` method

#### `set_left_padding(padding: int)` method

#### `set_right_padding(padding: int)` method

#### `set_num_qubits(num_qubits: int)` method

#### `update_num_qubits(num_qubits: int)` method

#### `compose(other: BaseGraph, stack: bool = False)` method

#### `matrix(return_latex: bool = False, override_max: bool = False)` method

#### `tikz(name: Optional[str] = None, scale: float = 0.5)` method

#### `tex(name: Optional[str] = None, scale: float = 0.5)` method

#### `pdf(name: Optional[str] = None, scale: float = 0.5)` method

#### `draw(labels: bool = False)` method

#### `qubits()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `rows()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `inputs()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `outputs()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `qubits()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `num_inputs()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `num_outsputs()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `num_vertices()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `num_edges()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `set_inputs()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `set_outputs()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `add_vertex()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `add_edge()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `row()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `qubit()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `type()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `phase()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `connected()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `remove_vertex()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### `remove_edge()` method
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

### GadgetGraph

### Gadget

### GadgetCircuit

### Paulis

### Cliffords

#### CX & CZ

#### Hadamard