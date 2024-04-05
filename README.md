# ZxFermion
<img src="figures/logo.png" width="150">

## Contents
- [1) What is ZxFermion?](#what-is-zxfermion?)
- [2) Getting Started](#getting-started)
  - [Creating Pauli Gadgets](#creating-pauli-gadgets)
  - [Creating Circuits of Gadgets](#creating-circuits-of-gadgets)
  - [Working with Cliffords](#working-with-cliffords)
- [3) Documentation](#documentation)
  - [BaseGraph](#class-basegraph)
  - [GadgetGraph](#class-gadgetgraph)

## What is ZxFermion?
ZxFermion is a Python package built on top of [PyZX](https://pyzx.readthedocs.io/en/latest/) designed for the manipulation and visualisation of circuits of Pauli gadgets. With built-in Clifford tableau logic using [Stim](https://github.com/quantumlib/Stim), ZxFermion allows users to quickly implement proofs and test ideas.

VQE algorithms used in quantum chemistry often utilise the [UCC](https://doi.org/10.48550/arXiv.2109.15176) framework in which excitation operators have a natural representation as Pauli gadgets. ZxFermion provides a comprehensive toolset designed to be used in a Jupyter notebook environment. Export functionality can be used to generated research paper quality diagrams.

The following diagrams were all made using ZxFermion.

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

#### _class_ `BaseGraph`
- The `BaseGraph` class extends the PyZX `GraphS` class. It implements a number of useful methods for handling ZX diagrams.
- [`min_qubit`](#property-minqubit)
- [`max_qubit`](#property-maxqubit)
- [`input_row`](#property-inputrow)
- [`output_row`](#property-outputrow)
- [`left_row`](#property-leftrow)
- [`right_row`](#property-rightrow)
- [`left_padding`](#property-leftpadding)
- [`right_padding`](#property-rightpadding)
- [`boundaries`](#property-boundaries)
- [`graph_rows`](#property-graphrows)
- [`graph_depth`](#property-graphdepth)
- [`left_end()`](#method-leftendqubit-int)
- [`right_end()`](#method-rightendqubit-int)
- [`left_row_within()`](#method-leftrowwithintop-int-bottom-int)
- [`right_row_within()`](#method-rightrowwithintop-int-bottom-int)
- [`bounded_vertices`](#property-boundaries)
- [`unbounded_vertices`](#property-unboundedvertices)
- [`vertices_on_qubit()`](#method-verticesonqubitqubit-int)
- [`remove_wire()`](#method-removewirequbit-int)
- [`connect_vertices()`](#method-connectverticesvertices-listint)
- [`set_input_row()`](#method-setinputrowrow-int)
- [`set_output_row()`](#method-setoutputrowrow-int)
- [`set_left_padding()`](#method-setleftpaddingpadding-int)
- [`set_right_padding()`](#method-setrightpaddingpadding-int)
- [`set_num_qubits()`](#method-setnumqubitsnumqubits-int)
- [`update_num_qubits()`](#method-updatenumqubitsnumqubits-int)
- [`compose()`](#method-composeother-basegraph-stack-bool--false)
- [`matrix()`](#method-matrixreturnlatex-bool--false-overridemax-bool--false)
- [`tikz()`](#method-tikzname-optionalstr--none-scale-float--05)
- [`tex()`](#method-texname-optionalstr--none-scale-float--05)
- [`pdf()`](#method-pdfname-optionalstr--none-scale-float--05)
- [`draw()`](#method-drawlabels-bool--false)
- [`qubits()`](#method-qubits)
- [`rows()`](#method-rows)
- [`inputs()`](#method-inputs)
- [`outputs()`](#method-outputs)
- [`num_inputs()`](#method-numinputs)
- [`num_outputs()`](#method-numoutsputs)
- [`num_vertices()`](#method-numvertices)
- [`num_edges()`](#method-numedges)
- [`set_inputs()`](#method-setinputs)
- [`set_outputs()`](#method-setoutputs)
- [`add_vertex()`](#method-addvertex)
- [`add_edge()`](#method-addedge)
- [`row()`](#method-row)
- [`qubit()`](#method-qubit)
- [`type()`](#method-type)
- [`phase()`](#method-phase)
- [`connected()`](#method-connected)
- [`remove_vertex()`](#method-removevertex)
- [`remove_edge()`](#method-removeedge)

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
- Returns the depth of the current graph from `input_row` to `output_row` (excluding vertices outside of graph bounds).
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
- Returns the vertex indices of the graph excluding the input and outputs vertices and excluding vertices positioned outside the graph bounds (greater/less than min/max qubits.)
- Return type: `list[int]`

##### _property_ `unbounded_vertices`
- Returns the vertex indices of the graph positioned outside the graph bounds (greater/less than min/max qubits) excluding the input and outputs vertices.
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
- Sets the number of qubits for the graph whilst maintaining the first `2 * num_qubits` vertex indices as the input and output indices.
- Return type: `None`

##### _method_ `update_num_qubits(num_qubits: int)`
- Sets the number of qubits for the graph if `num_qubits` is greater than the current number of qubits. 
- Return type: `None`

##### _method_ `compose(other: BaseGraph, stack: bool = False)`
- Overrides the PyZX `GraphS` compose method to allow for the adding of graphs with different number of qubits. Setting the `stack` parameter as `True` will stack graphs acting on disjoint set of qubits. 
- Return type: `None`

##### _method_ `matrix(return_latex: bool = False, override_max: bool = False)`

##### _method_ `tikz(name: Optional[str] = None, scale: float = 0.5)`

##### _method_ `tex(name: Optional[str] = None, scale: float = 0.5)`

##### _method_ `pdf(name: Optional[str] = None, scale: float = 0.5)`

##### _method_ `draw(labels: bool = False)`

##### _method_ `qubits()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `list[int]`

##### _method_ `rows()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `list[int]`

##### _method_ `inputs()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `list[int]`

##### _method_ `outputs()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `list[int]`

##### _method_ `num_inputs()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `num_outsputs()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `num_vertices()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `num_edges()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `set_inputs()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `None`

##### _method_ `set_outputs()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `None`

##### _method_ `add_vertex()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `add_edge()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).

##### _method_ `row()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int | float`

##### _method_ `qubit()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `type()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int`

##### _method_ `phase()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `int | float`

##### _method_ `connected()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `bool`

##### _method_ `remove_vertex()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `None`

##### _method_ `remove_edge()`
- Inherits from PyZX `GraphS` class. See [PyZX documentation](https://pyzx.readthedocs.io/en/latest/api.html#pyzx.graph.base.BaseGraph).
- Return type: `None`

### _class_ `GadgetGraph`

### _class_ `Gadget`

### _class_ `GadgetCircuit`
