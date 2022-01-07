Pig Breeding
============

The pig breeding problem as described in [#Lauritzen]_.

  A pig breeder is growing pigs for a period of four months and subsequently selling them. During this period the pig may or may not develop a certain disease. If the pig has the disease at the time it must be sold, the pig must be sold for slaughtering, and its expected market price is then 300 DKK (Danish kroner). If it is disease free, its expected market price as a breeding animal is 1000 DKK

  Once a month, a veterinary doctor sees the pig and makes a test for presence of the disease. If the pig is ill, the test will indicate this with probability 0.80, and if the pig is healthy, the test will indicate this with probability 0.90. At each monthly visit, the doctor may or may not treat the pig for the disease by injecting a certain drug. The cost of an injection is 100 DKK.

  A pig has the disease in the first month with probability 0.10. A healthy pig develops the disease in the subsequent month with probability 0.20 without injection, whereas a healthy and treated pig develops the disease with probability 0.10, so the injection has some preventive effect. An untreated pig that is unhealthy will remain so in the subsequent month with probability 0.90, whereas the similar probability is 0.50 for an unhealthy pig that is treated. Thus spontaneous cure is possible, but treatment is beneficial on average.

Influence diagram
.................

.. image:: figures/n-month-pig-breeding.svg
  :alt: The influence diagram of the simple car buyer example with 3 nodes.

The influence diagram for the generalized
:math:`N`-month pig breeding problem. The nodes
are associated with the following states. **Health
states** :math:`h_k=\{ill,healthy\}` represent the
health of the pig at month
:math:`k=1,...,N`. **Test states**
:math:t_k=\{positive,negative\}`
represent the result from testing the pig at month
:math:`k=1,...,N-1`. **Treatment states**
:math:`d_k=\{treat, pass\}` represent the decision
to treat the pig with an injection at month
:math:`k=1,...,N-1`.

  The dashed arcs represent the no-forgetting
  principle. The no-forgetting assumption does not
  hold without them and they are not included in
  the following model. They could be included by
  changing the information sets of nodes.

In this example, we solve the 4 month pig breeding
problem and thus, declare :math:`N = 4`.



.. rubric:: References

.. [#Lauritzen] Lauritzen, S. L., & Nilsson, D. (2001). Representing and solving decision problems with limited information. Management Science, 47(9), 1235–1251. https://doi.org/10.1287/mnsc.47.9.1235.9779
