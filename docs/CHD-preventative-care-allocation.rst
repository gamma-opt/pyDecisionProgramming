CHD preventative care allocation
================================

.. role:: python(code)
   :language: python

Description
...........

The goal in this optimisation problem is to determine an
optimal decision strategy for the testing and treatment
decisions involved in providing preventative care for
coronary heart disease (CHD). The optimality is evaluated
from the perspective of the national health care system and
is measured in quality-adjusted life-years (QALY). The
tests available in this model are the traditional risk
score (TRS) and the genetic risk score (GRS) and the form
of preventative care is statin treatment. The description
of the CHD preventative care allocation problem is below.
This description is from [#Hankimaa]_ from section 3.2.

  The problem setting is such that the patient is assumed
  to have a prior risk estimate. A risk estimate is a
  prediction of the patient’s chance of having a CHD event
  in the next ten years. The risk estimates are grouped
  into risk levels, which range from 0% to 100%. The first
  testing decision is made based on the prior risk
  estimate. The first testing decision entails deciding
  whether TRS or GRS should be performed or if no testing
  is needed. If a test is conducted, the risk estimate is
  updated and based on the new information, the second
  testing decision is made. The second testing decision
  entails deciding whether further testing should be
  conducted or not. The second testing decision is
  constrained so that the same test which was conducted in
  the first stage cannot be repeated. If a second test is
  conducted, the risk estimate is updated again. The
  treatment decision – dictating whether the patient
  receives statin therapy or not – is made based on the
  resulting risk estimate of this testing process. Note
  that if no tests are conducted, the treatment decision is
  made based on the prior risk estimate.

In this example, we will showcase the subproblem, which
optimises the decision strategy given a single prior risk
level. The chosen risk level in this example is 12%. The
solution to the main problem is found in [#Hankimaa]_.

Influence diagram
.................

.. image:: figures/CHD_preventative_care.svg
  :alt: The influence diagram of the CHD preventative care problem described below.

The influence diagram representation of the problem is seen
above. The chance nodes RR represent the patient's risk
estimate – the prior risk estimate being :math:`R0`. The
risk estimate nodes :math:`R0`, :math:`R1` and :math:`R2`
have 101 states :math:`R = \{0\%, 1\%, ..., 100\%\}`, which
are the discretised risk levels for the risk estimates.

The risk estimate is updated according to the first and
second testing decisions, which are represented by decision
nodes :math:`T1` and :math:`T2`. These nodes have states
:math:`T = \{\text{TRS, GRS, no test}\}`. The health of the
patient, represented by chance node :math:`H`, also affects
the update of the risk estimate. In this model, the health
of the patient indicates whether they will have a CHD event
in the next ten years or not. Thus, the node has states
:math:`H = \{\text{CHD, no CHD}\}`. The treatment decision
is represented by node :math:`TD` and it has states
:math:`TD = \{\text{treatment, no treatment}\}`.

The prior risk estimate represented by node :math:`R0`
influences the health node :math:`H`, because in the model
we make the assumption that the prior risk estimate
accurately describes the probability of having a CHD event.

The value nodes in the model are :math:`TC` and :math:`HB`.
Node :math:`TC` represents the testing costs incurred due
to the testing decisions :math:`T1` and :math:`T2`. Node
:math:`HB` represents the health benefits achieved. The
testing costs and health benefits are measured in QALYs.
These parameter values were evaluated in the study
[#Hynninen]_.

We begin by declaring the chosen prior risk level and
reading the conditional probability data for the tests.
Note that the sample data in this repository is dummy data
due to distribution restrictions on the real data. We also
define functions :python:`update_risk_distribution` and
:math:`state_probabilities`. These functions will be
discussed in the following sections.






.. rubric:: References

.. [#Hankimaa] Hankimaa H. (2021). Optimising the use of genetic testing in prevention of CHD using Decision Programming. http://urn.fi/URN:NBN:fi:aalto-202103302644

.. [#Hynninen] Hynninen Y. (2019). Value of genetic testing in the prevention of coronary heart disease events. PLOS ONE, 14(1):1–16. https://doi.org/10.1371/journal.pone.0210010

