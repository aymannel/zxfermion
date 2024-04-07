# ZxFermion
[![Generic badge](https://img.shields.io/badge/python-3.9+-green.svg)](https://docs.python.org/3.9/)

<img src="figures/logo.png" width="150">

## Contents
- [1) What is ZxFermion?](#what-is-zxfermion?)
- [2) Getting Started](#getting-started)
  - [Creating Pauli Gadgets](#creating-pauli-gadgets)
  - [Creating Circuits of Gadgets](#creating-circuits-of-pauli-gadgets)
  - [Analysis of Quantum Stabiliser Circuits](#analysis-of-quantum-stabiliser-circuits)
- [3) Documentation](#documentation)
  - [BaseGraph](#class-basegraph)
  - [GadgetGraph](#class-gadgetgraph)
  - [GadgetCircuit](#class-gadgetcircuit)
  - [Tableau](#class-tableau)
  - [Gadget](#class-gadget)
  - [Gates](#gates)

## What is ZxFermion?
ZxFermion is a Python package built on top of [PyZX](https://pyzx.readthedocs.io/en/latest/) designed for the manipulation and visualisation of circuits of Pauli gadgets. With built-in Clifford tableau logic using [Stim](https://github.com/quantumlib/Stim), ZxFermion allows users to quickly implement proofs and test ideas.

VQE algorithms used in quantum chemistry often utilise the [UCC](https://doi.org/10.48550/arXiv.2109.15176) framework in which excitation operators have a natural representation as Pauli gadgets. ZxFermion provides a comprehensive toolset designed to be used in a Jupyter notebook environment. Export functionality can be used to generated research paper quality diagrams.

## Getting Started
All of the following diagrams were made using ZxFermion's `pdf(name='filename')` method.

### Creating Pauli gadgets
The `Gadget` class is used to represent Pauli gadgets [cite]. By default, Pauli gadgets are represented in their more compact form in the ZX calculus [cite].
```python
from zxfermion import Gadget
gadget = Gadget('YZX', phase=1/2)
gadget.draw()
```
![](figures/readme2.png)

Setting `as_gadget=False` allows users to visualise Pauli gadgets in their expanded form. 
```python
gadget = Gadget('YZX', phase=1/2, as_gadget=False)
gadget.draw()
```
![](figures/readme1.png)

### Creating circuits of Pauli gadgets
Circuits of Pauli gadgets are defined by the `GadgetCircuit` class. The `variable` parameter allows users to specify the symbol for the gadget phase when rendering PDF figures.
```python
from zxfermion import GadgetCircuit
gadget1 = Gadget('YZX', phase=1/2, variable='theta')
gadget2 = Gadget('XZY', phase=1/2, variable='phi')
circuit = GadgetCircuit([gadget1, gadget2])
circuit.draw()
```
![](figures/readme3.png)

Setting `as_gadgets=False` allows users to extract the corresponding quantum circuit.
```python
gadget1 = Gadget('YZX', phase=1/2, variable='theta')
gadget2 = Gadget('XZY', phase=1/2, variable='phi')
circuit = GadgetCircuit([gadget1, gadget2])
circuit.draw(as_gadgets=False)
```
![](figures/readme4.png)

The `GadgetCircuit` class also allows users to represent circuits of standard quantum gates.
```python
from zxfermion.gates import CX, CZ, X, XPhase, ZPhase
circuit = GadgetCircuit([CX(0, 1), CZ(1, 2), X(1), ZPhase(0, 3/4), XPhase(0, 1/2), CX(0, 2), CX(0, 1), CZ(1, 2)])
circuit.draw(stack=True)
```

### Analysis of Quantum Stabiliser Circuits
Using [Stim](https://github.com/quantumlib/Stim) as a backend, users can easily observe the effect of Pauli and Clifford gates on Pauli gadgets. Consider the following circuit of Pauli gadgets, which represents a paired double excitation operator.
```python
circuit = GadgetCircuit([
    Gadget('YXXX', phase=1/4),
    Gadget('XYXX', phase=1/4),
    Gadget('XXYX', phase=-1/4),
    Gadget('YYYX', phase=-1/4),
    Gadget('YYXY', phase=1/4),
    Gadget('XXXY', phase=1/4),
    Gadget('XYYY', phase=-1/4),
    Gadget('YXYY', phase=-1/4)
])
circuit.draw()
```

It is easy to show that conjugating the circuit by controlled-not gates yields a triply-controlled rotation.
```python
circuit.apply(CX(0, 3))
circuit.apply(CX(0, 2))
circuit.apply(CX(0, 1))
circuit.draw()
```

## Documentation

#### _class_ `BaseGraph`
- Extends the `pyzx.GraphS` class. Implements a number of additional methods for handling ZX diagrams.
- Please see the [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

##### _property_ `min_qubit`
- Returns the minimum qubit of the current graph.
- Return type: `int`

##### _property_ `max_qubit`
- Returns the maximum qubit of the current graph.
- Return type: `int`

##### _property_ `input_row`
- Returns the input row index of the current graph.
- Return type: `int | float`

##### _property_ `output_row`
- Returns the output row index of the current graph.
- Return type: `int | float`

##### _property_ `left_row`
- Returns the leftmost row index of the current graph
- Return type: `int | float`

##### _property_ `right_row`
- Returns the rightmost row index of the current graph
- Return type: `int | float`

##### _property_ `left_padding`
- Returns the left padding (separation between `input_row` and `left_row`) of the current graph.
- Return type: `int | float`

##### _property_ `right_padding`
- Returns the right padding (separation between `output_row` and `right_row`) of the current graph.
- Return type: `int | float`

##### _property_ `boundaries`
- Returns the combined vertex indices of the inputs and outputs of the current graph.
- Return type: `list[int]`

##### _property_ `graph_rows`
- Returns the row indices of the current graph (from `left_row` to `right_row` inclusive).
- Return type: `list[int | float]`

##### _property_ `graph_depth`
- Returns the depth of the current graph from `input_row` to `output_row`.
- Excludes vertices outside of graph bounds.
- Return type: `int | float`

##### _method_ `left_end(qubit: int)`
- Returns the leftmost row index of the graph along the specified qubit.
- Return type: `int | float`

##### _method_ `right_end(qubit: int)`
- Returns the rightmost row index of the graph along the specified qubit.
- Return type: `int | float`

##### _method_ `left_row_within(top: int, bottom: int)`
- Returns the leftmost row index of the graph between the specified qubits.
- Return type: `int | float`

##### _method_ `right_row_within(top: int, bottom: int)`
- Returns the rightmost row index of the graph between the specified qubits.
- Return type: `int | float`

##### _property_ `bounded_vertices`
- Returns the vertex indices of the graph excluding vertices positioned outside the graph bounds.
- Excludes input and outputs vertices.
- Return type: `list[int]`

##### _property_ `unbounded_vertices`
- Returns the vertex indices of the graph positioned outside the graph bounds.
- Excludes input and outputs vertices.
- Return type: `list[int]`

##### _method_ `vertices_on_qubit(qubit: int)`
- Return the vertex indices along the specified qubit and excluding the input and output vertices.
- Return type: `list[int]`

##### _method_ `remove_wire(qubit: int)`
- Removes the edge connecting the input and output vertices for the specified qubit.
- Return type: `None`

##### _method_ `connect_vertices(vertices: list[int])`
- Creates simple edges between the specified vertex indices.
- Return type: `None`

##### _method_ `set_input_row(row: int)`
- Positions the input row at the specified row index.
- Return type: `None`

##### _method_ `set_output_row(row: int)`
- Positions the output row at the specified row index.
- Return type: `None`

##### _method_ `set_left_padding(padding: int)`
- Sets the left padding (separation between input row and left row) of the graph.
- Return type: `None`

##### _method_ `set_right_padding(padding: int)`
- Sets the right padding (separation between output row and right row) of the graph.
- Return type: `None`

##### _method_ `set_num_qubits(num_qubits: int)`
- Sets the number of qubits for the graph.
- Maintains first `2 * num_qubits` vertex indices as the input and output indices.
- Return type: `None`

##### _method_ `update_num_qubits(num_qubits: int)`
- Sets the number of qubits for the graph if `num_qubits` is greater than the current number of qubits. 
- Return type: `None`

##### _method_ `compose(other: BaseGraph, stack: bool = False)`
- Overrides the `pyzx.GraphS.compose()` to allow addition of graphs of different dimension.
- Setting `stack` parameter as `True` will stack graphs acting on disjoint set of qubits. 
- Return type: `None`

##### _method_ `matrix(return_latex: bool = False, override_max: bool = False)`
- Displays a latex matrix for the current gate, `Gadget` or `GadgetCircuit`.
- Return type: `str | None`

##### _method_ `tikz(name: Optional[str] = None, scale: float = 0.5)`
- Generates a tikz file for the current gate, `Gadget` or `GadgetCircuit`.
- Return type: `str | None`

##### _method_ `tex(name: Optional[str] = None, scale: float = 0.5)`
- Generates a tex file for the current gate, `Gadget` or `GadgetCircuit`.
- Return type: `None`

##### _method_ `pdf(name: Optional[str] = None, scale: float = 0.5)`
- Generates a pdf file for the current gate, `Gadget` or `GadgetCircuit`.
- Return type: `None`

##### _method_ `draw(labels: bool = False)`
- Draws the current gate, `Gadget` or `GadgetCircuit`.
- Return type: `None`

#### _class_ `GadgetGraph`
- Inherits from the `zxfermion.BaseGraph` class (see above).
- Implements methods for handling the graphing of the `Gadget` class and other quantum gates.

#### _class_ `Tableau`
- Class for handling the interaction of the `Gadget` class with the Pauli and Clifford gates.
- Built on top of [Stim](https://github.com/quantumlib/Stim).

#### _class_ `GadgetCircuit`
- Class for representing circuits of Pauli gadgets and other quantum gates.

#### _class_ `Gadget`
- Class for representing Pauli gadgets.

#### Gates
##### _class_ `CX(control: int, target: int)`
- Class for representing the CX gate.

##### _class_ `CZ(control: int, target: int)`
- Class for representing the CZ gate.

##### _class_ `X(qubit: int)`
- Class for representing the X gate.

##### _class_ `Z(qubit: int)`
- Class for representing the Z gate.
