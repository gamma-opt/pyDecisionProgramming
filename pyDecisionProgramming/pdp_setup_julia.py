#!/usr/bin/env python

from julia import Julia

# Create an instance of julia without incremental precompilation.
# This does not seem to affect performance much
base_julia = Julia(compiled_modules=False)

# These must be imported after creating the julia name space
from julia import Pkg

Pkg.add("PyCall")
Pkg.add("Gurobi")
Pkg.add(url="https://github.com/gamma-opt/DecisionProgramming.jl.git")
