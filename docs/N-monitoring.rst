N-Monitoring
============

.. role:: python(code)
   :language: python

Description
...........

The :math:`N`-monitoring problem is described in  [#Salo]_,
sections 4.1 and 6.1.

Influence Diagram
.................

.. image:: figures/n-month-pig-breeding.svg
  :alt: The influence diagram of the N-monitoring problem described below

The influence diagram of the generalized
:math:`N`-monitoring problem where :math:`N\ge 1` and
indices :math:`k=1,...,N`. The nodes are associated with
states as follows. Load state :math:`L=\{high, low\}`
denotes the load on a structure, report states
:math:`R_k=\{high, low\}` report the load state to the
action states :math:`A_k=\{yes, no\}` which represent
different decisions to fortify the structure. The failure
state :math:`F=\{failure, success\}` represents whether or
not the (fortified) structure fails under the load
:math:`L`. Finally, the utility at target :math:`T` depends
on the fortification costs and whether F fails.

We begin by choosing :math:`N` and defining our
fortification cost function. We draw the cost of
fortification :math:`c_k∼U(0,1)` from a uniform
distribution, and the magnitude of fortification is
directly proportional to the cost. Fortification is defined
as

.. math::

   f(A_k = yes) = c_k\\
   f(A_k = no) = 0

.. code-block:: Python

  import pyDecisionProgramming as pdp
  import numpy as np

  pdp.activate()

  N = 4
  np.random.seed(13)
  c_k = np.random.random(N)
  b = 0.03

  def fortification(k, a):
      if not a:
          return c_k[k]
      else:
          return 0


Initialising the influence diagram
..................................

We initialise the influence diagram before adding nodes to
it.

.. code-block:: Python

  diagram = pdp.InfluenceDiagram()


Adding nodes
............

Add node :math:`L` which represents the load on the
structure. This node is the root node and thus, has an
empty information set. Its states describe the state of the
load, they are :math:`high` and :math:`low`.

.. code-block:: Python

  L = pdp.ChanceNode("L", [], ["high", "low"])
  diagram.add_node(L)

The report nodes :math:`R_k` and action nodes :math:`A_k`
are easily added with a for-loop. The report nodes have
node :math:`L` in their information sets and their states
are :math:`high` and :math:`low`. The actions are made
based on these reports, which is represented by the action
nodes :math:`A_k` having the report nodes :math:`R_k` in
their information sets. The action nodes have states
:math:`yes` and :math:`no`, which represents decisions
whether to fortify the structure or not.

.. code-block:: Python

  for i in range(N):
      R = pdp.ChanceNode(f"R{i}", ["L"], ["high", "low"])
      diagram.add_node(R)
      A = pdp.DecisionNode(f"A{i}", [f"R{i}"], ["yes", "no"])
      diagram.add_node(A)

The failure node :math:`F` has the load node :math:`L` and
all of the action nodes :math:`A_k`
in its information set. The failure node has states
:math:`failure` and :math:`success`.

.. code-block:: Python

  F = pdp.ChanceNode(
      "F",
      ["L", *[f"A{i}" for i in range(N)]],
      ["failure", "success"]
  )
  diagram.add_node(F)

The value node :math:`T` is added as follows.

.. code-block:: Python

  T = pdp.ValueNode("T", ["F", *[f"A{i}" for i in range(N)]])
  diagram.add_node(T)


Generating arcs
...............

Now that all of the nodes have been added to the influence
diagram we generate the arcs between the nodes. This step
automatically orders the nodes, gives them indices and
reorganises the information into the appropriate form.

.. code-block:: Python

  diagram.generate_arcs()


Load State Probabilities
........................

After generating the arcs, the probabilities and utilities
can be added. The probability that the load is high,
:math:`\mathcal P(L=high)`, is drawn from a uniform
distribution. For different syntax options for adding
probabilities and utilities, see the
`usage page <usage.html>`_.

.. code-block:: Python

   r = np.random.random()
   X_L = [r, 1.0-r]
   diagram.set_probabilities("L", X_L)


Reporting Probabilities
.......................

The probabilities of the report states correspond to the
load state. We draw the values :math:`x∼U(0,1)` and
:math:`y∼U(0,1)` from uniform distributions.

.. math::

   \mathcal P(R_k=high \mid L=high) = max\{x, 1-x\}\\
   \mathcal P(R_k=low \mid L=low) = max\{y, 1-y\}

The probability of a correct report is thus in the range
[0.5,1]. (This reflects the fact that a probability under
50% would not even make sense, since we would notice that
if the test suggests a high load, the load is more likely
to be low, resulting in that a low report "turns into" a
high report and vice versa.)

In Decision Programming we add these probabilities by
declaring probability matrices for nodes :math:`R_k`.
The probability matrix of a report node :math:`R_k` has
dimensions (2,2), where the rows correspond to the states
:math:`high` and :math:`low` of its predecessor node
:math:`L` and the columns to its own states :math:`high`
and :math:`low`.

.. code-block:: Python

   for i in range(N):
       x, y = np.random.random(2)
       x = np.max([x, 1-x])
       y = np.max([y, 1-y])
       X_R = diagram.construct_probability_matrix(f"R{i}")
       X_R["high", "high"] = x
       X_R["high", "low"] = 1 - x
       X_R["low", "low"] = y
       X_R["low", "high"] = 1 - y
       diagram.set_probabilities(f"R{i}", X_R)


Probability of Failure
......................

The probability of failure is decreased by fortification
actions. We draw the values :math:`x∼U(0,1)` and
:math:`y∼U(0,1)` from uniform distribution.

.. math::

   \mathcal P(F=failure \mid A_N,\dots,A_1,L=high) = \frac{\max\{x,1-x\}}{exp\left( b\sum_{k=1,\dots,N}f(A_k) \right)}\\
   \mathcal P(F=failure \mid A_N,\dots,A_1,L=high) = \frac{\max\{y,1-y\}}{exp\left( b\sum_{k=1,\dots,N}f(A_k) \right)}

First we initialise the probability matrix for node
:math:`F`.

.. code-block:: Python

   X_F = diagram.construct_probability_matrix("F")


.. role:: orangetext

This matrix has dimensions (2, :orangetext:`2, 2, 2, 2`, 2)
because node :math:`L` and nodes :math:`A_k`, which form
the information set of :math:`F`, all have 2 states and
node :math:`F` itself also has 2 states. The orange
colored dimensions correspond to the states of the action
nodes :math:`A_k`.

To set the probabilities we have to iterate over the
information states. Here it helps to know that in Decision
Programming the states of each node are mapped to numbers
in the back-end. For instance, the load states
:math:`high` and :math:`low` are referred to as 1 and 2.
The same applies for the action states :math:`yes` and
:math:`no`, they are states 1 and 2. The
:python:`pdp.Paths` class allows us to iterate over the
subpaths of specific nodes. In these paths, the states are
referred to by their indices. Using this information, we
can easily iterate over the information states using the
:python:`pdp.Paths` class and enter the probability
values into the probability matrix.

.. code-block:: Python

   x, y = np.random.random(2)
   for path in pdp.Paths([2]*N):
       forticications = [fortification(k, a) for k, a in enumerate(path)]
       denominator = np.exp(b * np.sum(forticications))
       X_F[(0, *path, 0)] = max(x, 1-x) / denominator
       X_F[(0, *path, 1)] = 1.0 - max(x, 1-x) / denominator
       X_F[(1, *path, 0)] = min(y, 1-y) / denominator
       X_F[(1, *path, 1)] = 1.0 - min(y, 1-y) / denominator

After declaring the probability matrix, we add it to the
influence diagram.

.. code-block:: Python

   diagram.set_probabilities("F", X_F)


Utility
.......

The utility from the different scenarios of the failure
state at target :math:`T` are

.. math::

   g(F=failure) = 0\\
   g(F=success) = 100.


Utilities from the action states :math:`A_k` at target
:math:`T` are

.. math::

   g(A_k=yes) = c_k\\
   g(A_k=no) = 0.

The total cost is thus

.. math::

   Y(F,A_N,\dots,A_1) = g(F)+(-f(A_N))+\dots+(-f(A_1))

We first declare the utility matrix for node :math:`T`.

.. code-block:: Python

  Y_T = diagram.construct_utility_matrix('T')


This matrix has dimensions (2, :orangetext:`2, 2, 2, 2`)
where the dimensions correspond to the numbers of states
the nodes in the information set have. Similarly as
before, the first dimension corresponds to the states of
node :math:`F` and the other 4 dimensions (in orange)
correspond to the states of the :math:`A_k` nodes. The
utilities are set and added similarly to how the
probabilities were added above.

.. code-block:: Python

  for path in pdp.Paths([2]*N):
      forticications = [fortification(k, a) for k, a in enumerate(path)]
      cost = -sum(forticications)
      Y_T[(0, *path)] = 0 + cost
      Y_T[(1, *path)] = 100 + cost

  diagram.set_utility('T', Y_T)

Generate Influence Diagram
..........................

The full influence diagram can now be generated. We use
the default path probabilities and utilities, which are
the default setting in this function. In the
`Contingent Portfolio Programming example <contingent-portfolio-programming.html>`_,
we show how to use a user-defined custom path utility
function.

In this particular problem, some of the path utilities are
negative. In this case, we choose to use the
`positive path utility`_
transformation, which translates the path
utilities to positive values. This allows us to exclude
the probability cut in the next section.

.. _positive path utility: https://gamma-opt.github.io/DecisionProgramming.jl/stable/decision-programming/decision-model/

.. code-block:: Python

  diagram.generate(positive_path_utility=True)

Decision Model
..............

We initialise the JuMP model and declare the decision and
path compatibility variables. Since we applied an affine
transformation to the utility function, the probability
cut can be excluded from the model formulation.

.. code-block:: Python

  model = pdp.Model()
  z = diagram.decision_variables(model)
  x_s = diagram.path_compatibility_variables(
      model, z,
      probability_cut=False
  )

The expected utility is used as the objective and the
problem is solved using Gurobi.

.. code-block:: Python

  EV = diagram.expected_value(model, x_s)
  model.objective(EV, "Max")

  model.setup_Gurobi_optimizer(
     ("IntFeasTol", 1e-9),
  )
  model.optimize()

Analyzing Results
.................

We obtain the decision strategy, state probabilities and
utility distribution from the solution.

.. code-block:: Python

  Z = z.decision_strategy()
  S_probabilities = diagram.state_probabilities(Z)
  U_distribution = diagram.utility_distribution(Z)

The decision strategy shows us that the optimal strategy
is to make all four fortifications regardless of the
reports.

.. code-block::

  In [1]: S_probabilities.print_decision_strategy()

  Out[2]:
  ┌────────────────┬────────────────┐
  │ State(s) of R1 │ Decision in A1 │
  ├────────────────┼────────────────┤
  │ high           │ yes            │
  │ low            │ yes            │
  └────────────────┴────────────────┘
  ┌────────────────┬────────────────┐
  │ State(s) of R2 │ Decision in A2 │
  ├────────────────┼────────────────┤
  │ high           │ yes            │
  │ low            │ yes            │
  └────────────────┴────────────────┘
  ┌────────────────┬────────────────┐
  │ State(s) of R3 │ Decision in A3 │
  ├────────────────┼────────────────┤
  │ high           │ yes            │
  │ low            │ yes            │
  └────────────────┴────────────────┘
  ┌────────────────┬────────────────┐
  │ State(s) of R4 │ Decision in A4 │
  ├────────────────┼────────────────┤
  │ high           │ yes            │
  │ low            │ yes            │
  └────────────────┴────────────────┘

The state probabilities for strategy :math:`Z` are also obtained. These tell the probability of each state in each node, given strategy :math:`Z`.

.. code-block::

  In [2]: S_probabilities.print(["L"])

  Out[2]:
  ┌────────┬──────────┬──────────┬─────────────┐
  │   Node │     high │      low │ Fixed state │
  │ String │  Float64 │  Float64 │      String │
  ├────────┼──────────┼──────────┼─────────────┤
  │      L │ 0.564449 │ 0.435551 │             │
  └────────┴──────────┴──────────┴─────────────┘

  In [3]: report_nodes = [f"R{i}" for i in range(N)]
  In [4]: S_probabilities.print(report_nodes)

  Out[4]:
  ┌────────┬──────────┬──────────┬─────────────┐
  │   Node │     high │      low │ Fixed state │
  │ String │  Float64 │  Float64 │      String │
  ├────────┼──────────┼──────────┼─────────────┤
  │     R1 │ 0.515575 │ 0.484425 │             │
  │     R2 │ 0.442444 │ 0.557556 │             │
  │     R3 │ 0.543724 │ 0.456276 │             │
  │     R4 │ 0.552515 │ 0.447485 │             │
  └────────┴──────────┴──────────┴─────────────┘

  In [5]: reinforcement_nodes = [f"A{i}" for i in range(N-1)]
  In [6]: S_probabilities.print(reinforcement_nodes)

  Out[6]:
  ┌────────┬──────────┬──────────┬─────────────┐
  │   Node │      yes │       no │ Fixed state │
  │ String │  Float64 │  Float64 │      String │
  ├────────┼──────────┼──────────┼─────────────┤
  │     A1 │ 1.000000 │ 0.000000 │             │
  │     A2 │ 1.000000 │ 0.000000 │             │
  │     A3 │ 1.000000 │ 0.000000 │             │
  │     A4 │ 1.000000 │ 0.000000 │             │
  └────────┴──────────┴──────────┴─────────────┘

  In [7]: S_probabilities.print(["F"])

  Out[7]:
  ┌────────┬──────────┬──────────┬─────────────┐
  │   Node │  failure │  success │ Fixed state │
  │ String │  Float64 │  Float64 │      String │
  ├────────┼──────────┼──────────┼─────────────┤
  │      F │ 0.633125 │ 0.366875 │             │
  └────────┴──────────┴──────────┴─────────────┘

We can also print the utility distribution for the optimal
strategy and some basic statistics for the distribution.

.. code-block::

  In [8]: U_distribution.print_distribution()

  Out[8]:
  ┌───────────┬─────────────┐
  │   Utility │ Probability │
  │   Float64 │     Float64 │
  ├───────────┼─────────────┤
  │ -2.881344 │    0.633125 │
  │ 97.118656 │    0.366875 │
  └───────────┴─────────────┘

  In [8]: U_distribution.print_statistics()

  Out[8]:
  ┌──────────┬────────────┐
  │     Name │ Statistics │
  │   String │    Float64 │
  ├──────────┼────────────┤
  │     Mean │  33.806192 │
  │      Std │  48.195210 │
  │ Skewness │   0.552439 │
  │ Kurtosis │  -1.694811 │
  └──────────┴────────────┘








.. rubric:: References

.. [#Salo] Salo, A., Andelmin, J., & Oliveira, F. (2019). Decision Programming for Multi-Stage Optimization under Uncertainty, 1–35. Retrieved from http://arxiv.org/abs/1910.09196
