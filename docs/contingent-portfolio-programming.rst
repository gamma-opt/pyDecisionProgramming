Contingent Portfolio Programming
================================

.. warning::

  This example discusses adding constraints and decision
  variables to the Decision Programming formulation, as
  well as custom path utility calculation. Because of this,
  it is quite advanced compared to the earlier ones.

Description
...........

[#Salo]_, section 4.2:

  For instance, assume that the first-stage decisions
  specify which technology development projects will be
  started to generate patent-based intellectual property
  :math:`(P)` for a platform. This intellectual property
  contributes subject to some uncertainties to the
  technical competitiveness :math:`(T)` of the platform. In
  the second stage, it is possible to carry out application
  :math:`(A)` development projects which, when completed,
  yield cash flows that depend on the market share of the
  platform. This market share :math:`(M)` depends on the
  competitiveness of the platform and the number of
  developed applications. The aim is to maximize the cash
  flows from application projects less the cost of
  technology and application development projects.


Influence Diagram: Projects
...........................

.. image:: figures/contingent-portfolio-programming.svg
  :alt: The influence diagram of the contingent portfolio portfolio problem described below.

The influence diagram of the contingent portfolio
programming (CPP) problem.

There are :math:`n_T` technology development projects and
:math:`n_A` application development projects.

Decision states to develop patents

.. math::

   d_i^P \in D_i^P = \left \{ [q_1^P,q_2^P), [q_2^P,q_3^P)  \dots, [q_{|D^P|}^P,q_{|D^P|+1}^P) \right \}.

Chance states of technical competitiveness
:math:`c_j^T \in C_j^T`.

Decision states to develop applications

.. math::

   d_k^A \in D^A = \left \{ [q_1^A,q_2^A), [q_2^A,q_3^A)  \dots, [q_{|D^A|}^A,q_{|D^A|+1}^A) \right \}.

Chance states of market size :math:`c_j^M \in C_j^M`.

.. code-block:: Python

  import pyDecisionProgramming as pdp
  import numpy as np

  pdp.activate()
  np.random.seed(42)


  diagram = pdp.InfluenceDiagram()

  DP = pdp.DecisionNode("DP", [], ["0-3 patents", "3-6 patents", "6-9 patents"])
  diagram.add_node(DP)

  CT = pdp.ChanceNode("CT", ["DP"], ["low", "medium", "high"])
  diagram.add_node(CT)

  DA = pdp.DecisionNode("DA", ["DP", "CT"], ["0-5 applications", "5-10 applications", "10-15 applications"])
  diagram.add_node(DA)

  CM = pdp.ChanceNode("CM", ["CT", "DA"], ["low", "medium", "high"])
  diagram.add_node(CM)

  diagram.generate_arcs()


Technical competitiveness probability
.....................................

Probability of technical competitiveness :math:`c^T_j`
given the range
:math:`d_i^P:\mathbb P(c_j^T\mid d_i^P) \in [0,1]`.
A high number of patents increases probability of high
competitiveness and a low number correspondingly increases
the probability of low competitiveness.

.. code-block:: Python

  X_CT = pdp.ProbabilityMatrix(diagram, "CT")
  X_CT[0, :] = [1/2, 1/3, 1/6]
  X_CT[1, :] = [1/3, 1/3, 1/3]
  X_CT[2, :] = [1/6, 1/3, 1/2]
  diagram.set_probabilities("CT", X_CT)

Market share probability
........................

Probability of market share :math:`c^M_l` given the
technical competitiveness :math:`c^T_j` and range
:math:`d_k^A:\mathbb P(c_l^M\mid d_j^T, d_k^A) \in [0,1]`.
Higher competitiveness and number of application projects
both increase the probability of high market share.

.. code-block:: Python

  X_CM = pdp.ProbabilityMatrix(diagram, "CM")
  X_CM[0, 0, :] = [2/3, 1/4, 1/12]
  X_CM[0, 1, :] = [1/2, 1/3, 1/6]
  X_CM[0, 2, :] = [1/3, 1/3, 1/3]
  X_CM[1, 0, :] = [1/2, 1/3, 1/6]
  X_CM[1, 1, :] = [1/3, 1/3, 1/3]
  X_CM[1, 2, :] = [1/6, 1/3, 1/2]
  X_CM[2, 0, :] = [1/3, 1/3, 1/3]
  X_CM[2, 1, :] = [1/6, 1/3, 1/2]
  X_CM[2, 2, :] = [1/12, 1/4, 2/3]
  diagram.set_probabilities("CM", X_CM)

Generating the Influence Diagram
................................

We are going to be using a custom objective function, and
don't need the default path utilities for that.

.. code-block:: Python

  diagram.generate(default_utility=False)

Decision Model: Portfolio Selection
...................................

We create the decision variables
:math:`z(s_j\mid s_{I(j)})`  and notice that the
activation of paths that are compatible with the decision
strategy is handled by the problem specific variables and
constraints together with the custom objective function,
eliminating the need for separate variables representing
path activation.

.. code-block:: Python

  model = pdp.Model()
  z = pdp.DecisionVariables(model, diagram)

Creating problem specific variables
...................................

In pyDecisionProgramming problems specific constraints
are defined as strings. The syntax is closer to Julia than
Python. First, it is convenient to define the variables
we will need in :python:`pdp.julia`. These will be
available when defining the constraints.

We recommend reading section 4.2. in [#Salo]_ for
motivation and details of the formulation.

Technology project :math:`t` costs
:math:`I_t\in \mathbb R^+` and generates
:math:`O_t\in \mathbb N` patents.

Application project :math:`a` costs
:math:`I_a\in \mathbb R^+` and generates
:math:`O_a\in \mathbb N` applications. If completed,
provides cash flow :math:`V(a\mid c_l^M)\in\mathbb R^+`.

.. code-block:: Python

  n_T = 5               # number of technology projects
  n_A = 5               # number of application projects

  # Here we set stuff in Julia name space directly
  I_t = np.random.random(n_T)*0.1   # costs of technology projects
  O_t = np.random.randint(1, 4, n_T)   # number of patents for each tech project
  I_a = np.random.random(n_T)*2     # costs of application projects
  O_a = np.random.randint(2, 5, n_T)   # number of applications for each appl. project

  # Set the names in pdp.julia to use them when setting constraints
  pdp.julia.I_t = I_t
  pdp.julia.O_t = O_t
  pdp.julia.I_a = I_a
  pdp.julia.O_a = O_a

  V_A = np.random.random((n_CM, n_A)) + 0.5  # Value of an application
  V_A[0, :] += -0.5           # Low market share: less value
  V_A[2, :] += 0.5            # High market share: more value

  pdp.julia.V_A = V_A



Decision variables :math:`x^T(t)\in \{ 0,1 \}` indicate
which technologies are selected.

Decision variables








.. rubric:: References

.. [#Salo] Salo, A., Andelmin, J., & Oliveira, F. (2019). Decision Programming for Multi-Stage Optimization under Uncertainty, 1–35. Retrieved from http://arxiv.org/abs/1910.09196

