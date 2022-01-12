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

1. Install manual requirements
 * Python3: install using `sudo apt install python3 python3-pip`
 * Julia: Download and follow setup instructions
 * Gurobi: download and follow the setup instructions

2. Install Julia-side dependencies:
```
julia setup.jl
```

3. Install python dependencies:
```
pip3 install -r requirements.txt
```

## Usage

To run REPL use `python-jl` (or `python-jl -m IPython`).

Set up the a new project using
```
import pyDecisionProgramming as pd
pd.setup_project()
```


