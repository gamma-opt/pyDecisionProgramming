Usage
=====


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







