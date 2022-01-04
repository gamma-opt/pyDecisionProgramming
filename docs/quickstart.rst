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


.. note::
  Importing pyDecisionProgramming can take a while.
  This is partly because of the way Julia works.
  In Julia, functions are compiled during runtime,
  and this requires some special set up.

  The python Julia package comes with an
  executable called `python-jl`. Using it instead
  of the standard `python` executable speeds things
  up a little bit. It has little effect on the
  actual calculation, though.

