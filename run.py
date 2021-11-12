import pyDecisionProgramming as pdp
import numpy as np

# pdp.setupProject()
pdp.activate()

diagram = pdp.InfluenceDiagram()

car_results = pdp.ChanceNode("O", [], ["lemon", "peach"])
diagram.add_node(car_results)

test_options = pdp.DecisionNode("T", [], ["no test", "test"])
diagram.add_node(test_options)

test_outcomes = pdp.ChanceNode("R", ["O", "T"], ["no test", "lemon", "peach"])
diagram.add_node(test_outcomes)

buy_options = pdp.DecisionNode("A", ["R"], ["buy without guarantee", "buy with guarantee", "don't buy"])
diagram.add_node(buy_options)


value_node = pdp.ValueNode("V1", ["T"])
diagram.add_node(value_node)
value_node = pdp.ValueNode("V2", ["A"])
diagram.add_node(value_node)
value_node = pdp.ValueNode("V3", ["O", "A"])
diagram.add_node(value_node)

diagram.generate_arcs()

# A probability or utility matrix can be set to a Numpy list
diagram.set_probabilities('O', [0.8, 0.2])

# You can also get the current matrix and change it
R_probs = diagram.probability_matrix('R')
R_probs[0, 0, :] = [1, 0, 0]
R_probs[0, 1, :] = [0, 1, 0]
R_probs[1, 0, :] = [1, 0, 0]
R_probs[1, 1, :] = [0, 0, 1]
diagram.set_probabilities('R', R_probs)

V1_utilities = diagram.utility_matrix('V1')
print(V1_utilities)
V1_utilities[0] = -25
V1_utilities[1] = 0
print(V1_utilities)
diagram.set_utility('V1', V1_utilities)

V2_utilities = diagram.utility_matrix('V2')
print(V2_utilities)
V2_utilities[0] = 100
V2_utilities[1] = 40
V2_utilities[2] = 0
print(V2_utilities)
diagram.set_utility('V2', V2_utilities)

V3_utilities = diagram.utility_matrix('V3')
print(V3_utilities)
V3_utilities[0, 0] = -200
V3_utilities[0, 1] = 0
V3_utilities[0, 2] = 0
V3_utilities[1, :] = [-40, -20, 0]
print(V3_utilities)
diagram.set_utility('V3', V3_utilities)

diagram.generate()

model = pdp.Model()
z = pdp.DecisionVariables(model, diagram)
print(z)
x_s = pdp.PathCompatibilityVariables(model, diagram, z)
print(x_s)
EV = model.expected_value(diagram, x_s)
print(EV)

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
   ("LazyConstraints", 1)
)

model.optimize()

Z = pdp.DecisionStrategy(z)
print(Z)
S_probabilities = pdp.StateProbabilities(diagram, Z)
print(S_probabilities)
U_distribution = pdp.UtilityDistribution(diagram, Z)
print(U_distribution)


import sys
sys.exit()

o = 1
t = 2
r = 3
a = 4
O_states = ["lemon", "peach"]
T_states = ["no test", "test"]
R_states = ["no test", "lemon", "peach"]
A_states = ["buy without guarantee", "buy with guarantee", "don\'t buy"]

s = pdp.States([
 (len(O_states), o),
 (len(T_states), t),
 (len(R_states), r),
 (len(A_states), a),
])
print(s)

c = pdp.Vector('ChanceNode')
d = pdp.Vector('DecisionNode')
v = pdp.Vector('ValueNode')
x = pdp.Vector('Probabilities')
y = pdp.Vector('Consequences')

i_o = pdp.Vector('Node')
cn = pdp.ChanceNode(o, i_o)
c.push(cn)
probs = pdp.Probabilities(o, [0.2, 0.8])
x.push(probs)

i_t = pdp.Vector('Node')
dn = pdp.DecisionNode(t, i_t)
d.push(dn)

i_r = [o, t]
x_r = np.zeros((s[o], s[t], s[r]))
x_r[0, 0, :] = [1.0, 0.0, 0.0]
x_r[0, 1, :] = [0.0, 1.0, 0.0]
x_r[1, 0, :] = [1.0, 0.0, 0.0]
x_r[1, 1, :] = [0.0, 0.0, 1.0]
cn = pdp.ChanceNode(r, i_r)
c.push(cn)
pdp.Main.p = probs
print(pdp.Main.eval('typeof(p)'))
probs = pdp.Probabilities(r, x_r)
pdp.Main.p = probs
print(pdp.Main.eval('typeof(p)'))
print(x)
x.push(probs)

i_a = [r]
dn = pdp.DecisionNode(a, i_a)
d.push(dn)
print(d)

i_v1 = [t]
y_v1 = [0.0, -25.0]
vn = pdp.ValueNode(5, i_v1)
v.push(vn)
print(v)
consequences = pdp.Consequences(5, y_v1)
y.push(consequences)
print(y)

i_v2 = [a]
y_v2 = [100.0, 40.0, 0.0]
vn = pdp.ValueNode(6, i_v2)
v.push(vn)
consq = pdp.Consequences(6, y_v2)
y.push(consq)

i_v3 = [o, a]
y_v3 = [[-200.0, 0.0, 0.0],
        [-40.0, -20.0, 0.0]]
vn = pdp.ValueNode(7, i_v3)
v.push(vn)
print(v)
consq = pdp.Consequences(7, y_v3)
y.push(consq)
print(y)

pdp.validate_influence_diagram(s, c, d, v)
for vec in (c, d, v, x, y):
    vec.sortByNode()

p = pdp.DefaultPathProbability(c, x)
u = pdp.DefaultPathUtility(v, y)

model = pdp.Model()
z_var = pdp.DecisionVariables(model, s, d)
pi_s = pdp.PathProbabilityVariables(model, z_var, s, p)
ev = pdp.expected_value(model, pi_s, u)
pdp.set_objective(model, 'Max', ev)

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
   ("LazyConstraints", 1)
)

model.optimize()

z = pdp.DecisionStrategy(z_var)
pdp.print_decision_strategy(s, z)

udist = pdp.UtilityDistribution(s, p, u, z)
pdp.print_utility_distribution(udist)
pdp.print_statistics(udist)
