# pyDecisionProgramming
Python interface for DecisionProgramming.jl

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


# TODO:

```

Main.eval('const O = 1')
Main.eval('const T = 2')
Main.eval('const R = 3')
Main.eval('const A = 4')
Main.eval('const O_states = ["lemon", "peach"]')
Main.eval('const T_states = ["no test", "test"]')
Main.eval('const R_states = ["no test", "lemon", "peach"]')
Main.eval('const A_states = ["buy without guarantee", "buy with guarantee", "don\'t buy"]')
Main.eval('''S = States([
                 (length(O_states), [O]),
                 (length(T_states), [T]),
                 (length(R_states), [R]),
                 (length(A_states), [A]),
             ])
          ''')
Main.eval('C = Vector{ChanceNode}()')
Main.eval('D = Vector{DecisionNode}()')
Main.eval('V = Vector{ValueNode}()')
Main.eval('X = Vector{Probabilities}()')
Main.eval('Y = Vector{Consequences}()')

Main.eval('I_O = Vector{Node}()')
Main.eval('X_O = [0.2, 0.8]')
Main.eval('push!(C, ChanceNode(O, I_O))')
Main.eval('push!(X, Probabilities(O, X_O))')

Main.eval('I_T = Vector{Node}()')
Main.eval('push!(D, DecisionNode(T, I_T))')

Main.eval('I_R = [O, T]')
Main.eval('X_R = zeros(S[O], S[T], S[R])')
Main.eval('X_R[1, 1, :] = [1,0,0]')
Main.eval('X_R[1, 2, :] = [0,1,0]')
Main.eval('X_R[2, 1, :] = [1,0,0]')
Main.eval('X_R[2, 2, :] = [0,0,1]')
Main.eval('push!(C, ChanceNode(R, I_R))')
Main.eval('push!(X, Probabilities(R, X_R))')

Main.eval('I_A = [R]')
Main.eval('push!(D, DecisionNode(A, I_A))')

Main.eval('I_V1 = [T]')
Main.eval('Y_V1 = [0.0, -25.0]')
Main.eval('push!(V, ValueNode(5, I_V1))')
Main.eval('push!(Y, Consequences(5, Y_V1))')

Main.eval('I_V2 = [A]')
Main.eval('Y_V2 = [100.0, 40.0, 0.0]')
Main.eval('push!(V, ValueNode(6, I_V2))')
Main.eval('push!(Y, Consequences(6, Y_V2))')

Main.eval('I_V3 = [O, A]')
Main.eval('''Y_V3 = [-200.0 0.0 0.0;
                    -40.0 -20.0 0.0]''')
Main.eval('push!(V, ValueNode(7, I_V3))')
Main.eval('push!(Y, Consequences(7, Y_V3))')

Main.eval('validate_influence_diagram(S, C, D, V)')
Main.eval('sort!.((C, D, V, X, Y), by = x -> x.j)')

Main.eval('P = DefaultPathProbability(C, X)')
Main.eval('U = DefaultPathUtility(V, Y)')

Main.eval('model = Model()')
Main.eval('z = DecisionVariables(model, S, D)')
Main.eval('π_s = PathProbabilityVariables(model, z, S, P)')
Main.eval('EV = expected_value(model, π_s, U)')
Main.eval('@objective(model, Max, EV)')

Main.eval('''optimizer = optimizer_with_attributes(
             () -> Gurobi.Optimizer(Gurobi.Env()),
             "IntFeasTol"      => 1e-9,
             "LazyConstraints" => 1,
             )
             ''')
Main.eval('set_optimizer(model, optimizer)')
Main.eval('optimize!(model)')

Main.eval('Z = DecisionStrategy(z)')

Main.eval('print_decision_strategy(S, Z)')

Main.eval('udist = UtilityDistribution(S, P, U, Z)')

Main.eval('print_utility_distribution(udist)')

Main.eval('print_statistics(udist)')
```



# To return a python object:

Assign:
```
udist = Main.eval('UtilityDistribution(S, P, U, Z)')
```

Set in Main:
```
Main.x = udist
Main.eval('print_utility_distribution(x)')
```
