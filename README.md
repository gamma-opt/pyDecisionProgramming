# pyDecisionProgramming
[![Docs Image](https://img.shields.io/badge/docs-latest-blue.svg)](https://gamma-opt.github.io/pyDecisionProgramming/)

Python interface for DecisionProgramming.jl.

[DecisionProgramming.jl](https://github.com/gamma-opt/DecisionProgramming.jl)
is a [Julia](https://julialang.org/) package for solving
multi-stage decision problems under uncertainty, modeled
using influence diagrams. Internally, it relies on
mathematical optimization. Decision models can be embedded
within other optimization models. We designed the package
as [JuMP](https://jump.dev/) extension.

## Installation
### Ubuntu 20.04:

1. Install Julia

   Download julia at [https://julialang.org/downloads].
   Follow the instructions at Platform Specific
   Instructions.

2. Install pyDecisionProgramming:

   ```
   pip install DecisionProgramming
   ```

3. Install Julia requirements

   After installing the Python package, running the command

   ```
   pdp_setup_julia.py
   ```

   should be sufficient to install the required Julia
   packages. Alternatively, install the DecisionProgramming
   package in Julia:

   ```
   using Pkg
   Pkg.add(url="https://github.com/gamma-opt/DecisionProgramming.jl.git")

   ```

## Usage

See the
[documentation](https://gamma-opt.github.io/pyDecisionProgramming/usage/)
for details on constructing a graph and finding the optimal
path through a graph.

# Environments

Set up the a Julia environment in the current folder run
the Python script
```
import DecisionProgramming as dp
dp.setup_project()
```

To use this environment in a Python script, use

```
import DecisionProgramming as dp
dp.activate()
```


