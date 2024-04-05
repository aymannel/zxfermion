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

#### Property `min_qubit`
Returns the minimum qubit of the current graph.

Return type: `int`

#### _property_ `max_qubit`
Returns the maximum qubit of the current graph.

Return type: `int`

#### Property `input_row`
Returns the input row index of the current graph.

Return type: `int`

#### Property `output_row`
Returns the output row index of the current graph.

Return type: `int | float`

#### Property `left_row`
Returns the leftmost row index of the current graph

Return type: `int | float`

#### Property `right_row`
Returns the rightmost row index of the current graph

Return type: `int | float`

#### Property `left_padding`
Returns the left padding (separation between `BaseGraph.input_row` and `BaseGraph.left_row`) of the current graph.

Return type: `int | float`

#### Property `right_padding`
Returns the right padding (separation between `BaseGraph.output_row` and `BaseGraph.right_row`) of the current graph.

Return type: `int | float`

#### Property `boundaries`
Returns the combined vertex indices of the inputs and outputs of the current graph.

Return type: `list[int]`

#### Property `graph_rows`
Returns the row indices of the current graph (from `BaseGraph.left_row` to `BaseGraph.right_row` inclusive).

Return type: `list[int]`

#### Property `graph_depth`
Returns the depth of the current graph from `BaseGraph.input_row` to `BaseGraph.output_row` (excluding vertices outside of graph bounds).

Return type: `int | float`

#### Method `left_end(qubit: int)`

#### Method `right_end(qubit: int)`

#### Method `left_row_within(top: int, bottom: int)`

#### Method `right_row_within(top: int, bottom: int)`

#### Property `bounded_vertices`

#### Property `unbounded_vertices`

#### `vertices_on_qubit(qubit: int)` method

#### Method `remove_wire(qubit: int)`

#### Method `connect_vertices(vertices: list[int])`

#### Method `set_input_row(row: int)`

#### Method `set_output_row(row: int)`

#### Method `set_left_padding(padding: int)`

#### Method `set_right_padding(padding: int)`

#### Method `set_num_qubits(num_qubits: int)`

#### Method `update_num_qubits(num_qubits: int)`

#### Method `compose(other: BaseGraph, stack: bool = False)`

#### Method `matrix(return_latex: bool = False, override_max: bool = False)`

#### Method `tikz(name: Optional[str] = None, scale: float = 0.5)`

#### Method `tex(name: Optional[str] = None, scale: float = 0.5)`

#### Method `pdf(name: Optional[str] = None, scale: float = 0.5)`

#### Method `draw(labels: bool = False)`

#### Method `qubits()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `rows()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `inputs()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `outputs()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `qubits()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `num_inputs()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `num_outsputs()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `num_vertices()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `num_edges()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `set_inputs()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `set_outputs()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `add_vertex()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `add_edge()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `row()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `qubit()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `type()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `phase()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `connected()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `remove_vertex()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

#### Method `remove_edge()`
Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

### GadgetGraph

### Gadget

### GadgetCircuit

### Paulis

### Cliffords

#### CX & CZ

#### Hadamard