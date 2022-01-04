Quickstart
==========

Installation
------------

Step 1: Install Julia
.....................

Download julia at `https://julialang.org/downloads`_.
Follow the instructions at `Platform Specific Instructions`_.

.. _https://julialang.org/downloads: https://julialang.org/downloads/
.. _Platform Specific Instructions: https://julialang.org/downloads/platform.html

Step 2: Install pyDecisionProgramming
.....................................

PyDecisionProgramming works with python3. To
install it via pip, run

.. code-block:: bash

  pip install https://github.com/gamma-opt/pyDecisionProgramming.git


Step 2: Install Julia Requirements
.....................................

You also need the actual DecisionProgramming Julia
package and its requirements. For convenience, the
pyDecisionProgramming package includes a script to
install these. Just run

.. code-block:: bash

  pdp_setup_julia.py

in your terminal to install them. Alternatively,
install the DecisionProgramming package in Julia:

.. code-block:: Julia

  using Pkg
  Pkg.add(url="https://github.com/gamma-opt/DecisionProgramming.jl.git")



Usage
-----

This is a simple but complete example of building a
decision tree and solving it. For more details see
the :doc:`introduction` section and the
:doc:`examples <used-car-buyer>`.

.. usage: usage


First create a new influence diagram.

.. code-block:: Python

  import pyDecisionProgramming as pdp
  diagram = pdp.InfluenceDiagram()

Use the add_node method to add nodes to the diagram.

.. code-block:: Python

  D1 = pdp.DecisionNode("D1", [], ["a", "b"])
  diagram.add_node(D1)

  C2 = pdp.ChanceNode("C2", ["D1", "C1"], ["v", "w"])
  diagram.add_node(C2)

  C1 = pdp.ChanceNode("C1", ["x", "y", "z"])
  diagram.add_node(C1)

You need to add at least one value node.

.. code-block:: Python

  V = pdp.ValueNode("V", ["C2])
  diagram.add_node(V)

Now that the diagram is built, we generate the 

