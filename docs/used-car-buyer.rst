Used Car Buyer
==============

Description
...........

To illustrate the basic functionality of Decision
Programming, we implement a version of the used car
buyer problem in [#Howard]_. In this problem, Joe
is buying a used car. The car's price is 1000 USD
(US dollars), and its value is 1100 USD. Joe's base
profit on the car is thus 100 USD. However, Joe
knows that the car is a "lemon", meaning that it
has defects in 6 major systems, with a 20%
probability. With the remaining 80% probability,
the car is a "peach", and it has a defect in only
one of the systems.

The repair costs for a peach are only 40 USD,
decreasing Joe's profit to 60 USD. However, the
costs for a lemon are 200 USD, resulting in a total
loss of 100 USD. We can now formulate an influence
diagram of Joe's initial problem. We present the
influence diagram in the figure below. In an
influence diagram, circle nodes such as :math:`O`
are called **chance nodes**, representing
uncertainty. Node :math:`O` is a chance node
representing the state of the car, lemon or peach.
Square nodes such as :math:`A` are
**decision nodes**, representing decisions.
Node :math:`A` represents the decision to buy or
not to buy the car. The diamond-shaped
**value node** :math:`V` denotes the utility
calculation in the problem. For Joe, the utility
function is the expected monetary value. The arrows
or **arcs** show connections between nodes. The two
arcs in this diagram point to the value node,
meaning that the monetary value depends on the
state of the car and the purchase decision.

.. image:: figures/used-car-buyer-1.svg
  :alt: The influence diagram of the simple car buyer example with 3 nodes.

We can easily determine the optimal strategy for this problem. If Joe decides not to buy the car, his profit is zero. If he buys the car, with 20% probability he loses 100 USD and with an 80% probability he profits 60 USD. Therefore, the expected profit for buying the car is 28 USD, which is higher than the zero profit of not buying. Thus, Joe should buy the car.

We now add two new features to the problem. A stranger approaches Joe and offers to tell Joe whether the car is a lemon or a peach for 25 USD. Additionally, the car dealer offers a guarantee plan which costs 60 USD and covers 50% of the repair costs. Joe notes that this is not a very good deal, and the dealer includes an anti-lemon feature: if the total repair cost exceeds 100 USD, the quarantee will fully cover the repairs.

Influence diagram
.................

.. image:: figures/used-car-buyer-1.svg
  :alt: The more complicated diagram described below.

We present the new influence diagram above. The
decision node :math:`T` denotes the decision to
accept or decline the stranger's offer, and
:math:`R` is the outcome of the test. We introduce
new value nodes :math:`V_1` and :math:`V_2`
to represent the testing costs and the base profit
from purchasing the car. Additionally, the decision
node :math:`A` now can choose to buy with a
guarantee.

We start by defining the influence diagram
structure. The nodes, as well as their information
sets and states, are defined in the first block.
Next, the influence diagram parameters consisting
of the probabilities and utilities are defined.

Car's state
...........

The chance node :math:`O` is defined by its name,
its information set :math:`I(O)` and its states
*lemon* and *peach*. As seen in the influence
diagram, the information set is empty and the node
is a root node.

.. code-block:: Python

  pdp.activate()

  diagram = pdp.InfluenceDiagram()

  car_results = pdp.ChanceNode("O", [], ["lemon", "peach"])
  diagram.add_node(car_results)

.. rubric:: References

.. [#Howard] Howard, R. A. (1977). The used car buyer. Reading in Decision Analysis, 2nd Ed. Stanford Research Institute, Menlo Park, CA.
