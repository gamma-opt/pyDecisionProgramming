Installation
============

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



