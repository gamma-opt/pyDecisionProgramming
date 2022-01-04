Usage
=====

.. role:: python(code)
   :language: python

Here we show you how to construct a simple influence
diagram and create a decision model using
pyDecisionProgramming.

First we import pyDecisionProgramming and activate
the Julia environment.

.. code-block:: Python

  import pyDecisionProgramming as pdp
  pdp.activate()

Adding Nodes
............

.. image:: figures/2chance_1decision_1value.svg
  :alt: An influence diagram with 4 nodes.

We will create the influence diagram pictures above.
First we create a new influence diagram.

.. code-block:: Python

  diagram = pdp.InfluenceDiagram()

Next we define each node as a
:python:`DecisionNode`, a :python:`ChanceNode` or
:python:`ValueNode` and add them to the diagram.
Creating a :python:`DecisionNode` or a
:python:`ChanceNode` requires giving it a unique
name, its information set and its states. If the
node is a root node, its information set is an
empty list (:python:`[]`). The order in which the
nodes are added does not matter.

Use the add_node method to add nodes to the diagram.

.. code-block:: Python

  D1 = pdp.DecisionNode("D1", [], ["a", "b"])
  diagram.add_node(D1)

  C2 = pdp.ChanceNode("C2", ["D1", "C1"], ["v", "w"])
  diagram.add_node(C2)

  C1 = pdp.ChanceNode("C1", [], ["x", "y", "z"])
  diagram.add_node(C1)

Value nodes only need a name and their information
set. They do not have a state, since their purpose
is to map their information state to utility values.

.. code-block:: Python

  V = pdp.ValueNode("V", ["C2"])
  diagram.add_node(V)

Once all the nodes have been added, we generate the
arcs in the diagram. This orders the nodes and
numbers them such that each nodes predecessors will
have a smaller number than they do. In effect,
the change and decision nodes are numbered such
that :math:`C \bigcup D = \{ 1, \dots, n\}`,
where :math:`n=|C|+|D|`. For more details see
`the page on influence diagrams`_ in the
documentation for DecisionProgramming.jl.

.. _the page on influence diagrams: https://gamma-opt.github.io/DecisionProgramming.jl/stable/decision-programming/influence-diagram/

.. code-block:: Python

  diagram.generate_arcs()


The fields :code:`Names`, :code:`I_j`,
:code:`States`, :code:`S`, :code:`C`, :code:`D`
and :code:`V` in the influence diagram have been
defined. The names field holds the names of
all nodes in the order of they numbers. From
this we can see that node D1 has been numbered 1,
node C1 has been numbered 2 and node C2 has been
numbered 3. The field :code:`I_j` holds the
information sets of each node. Notice, that the
nodes are identified by their numbers. The field
:code:`States` holds the names of the states of
each node and field :code:`S` holds the number of
states each node has. Fields :code:`C`,
:code:`D` and :code:`V` contain
the chance, decision and value nodes respectively.


.. code-block:: Python

  In [1]: diagram.Names
  Out[1]: ["D1", "C1", "C2", "V"]

  In [2]: diagram.I_j
  Out[2]: Vector{Int16}[[], [], [1, 2], [3]]

  In [3]: diagram.States
  Out[3]: [["a", "b"], ["x", "y", "z"], ["v", "w"]]

  In [4]: diagram.S
  Out[4]: Int16[2, 3, 2]

  In [5]: diagram.C
  Out[5]: Int16[2, 3]

  In [6]: diagram.D
  Out[6]: Int16[1]

  In [7]: diagram.V
  Out[7]: Int16[4]


Probability Matrices
....................





