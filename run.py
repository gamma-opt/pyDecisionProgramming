import pyDecisionProgramming as pd
import numpy as np

# pd.setupProject()
pd.activate()

diagram = pd.InfluenceDiagram()

car_results = pd.ChanceNode("O", [], ["lemon", "peach"])
diagram.add_node(car_results)

test_options = pd.DecisionNode("T", [], ["no test", "test"])
diagram.add_node(test_options)

test_outcomes = pd.ChanceNode("R", ["O", "T"], ["no test", "lemon", "peach"])
diagram.add_node(test_outcomes)

buy_options = pd.DecisionNode("A", ["R"], ["buy without guarantee", "buy with guarantee", "don't buy"])
diagram.add_node(buy_options)


value_node = pd.ValueNode("V1", ["T"])
diagram.add_node(value_node)
value_node = pd.ValueNode("V2", ["A"])
diagram.add_node(value_node)
value_node = pd.ValueNode("V3", ["O", "A"])
diagram.add_node(value_node)

diagram.generate_arcs()

matrix = diagram.probability_matrix('O')
diagram.set_probabilities('O', [0.8, 0.2])

matrix = diagram.probability_matrix('R')
matrix[0, 0, :] = [1, 0, 0]
matrix[0, 1, :] = [0, 1, 0]
matrix[1, 0, :] = [1, 0, 0]
matrix[1, 1, :] = [0, 0, 1]
diagram.set_probabilities('R', matrix)

matrix = diagram.utility__matrix('V1')
print(matrix)
matrix[0] = -25
matrix[1] = 0
print(matrix)
diagram.set_utility('V1', matrix)

# Y_V1 = UtilityMatrix(diagram, "V1")
# Y_V1["test"] = -25
# Y_V1["no test"] = 0
# add_utilities!(diagram, "V1", Y_V1)

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

s = pd.States([
 (len(O_states), o),
 (len(T_states), t),
 (len(R_states), r),
 (len(A_states), a),
])
print(s)

c = pd.Vector('ChanceNode')
d = pd.Vector('DecisionNode')
v = pd.Vector('ValueNode')
x = pd.Vector('Probabilities')
y = pd.Vector('Consequences')

i_o = pd.Vector('Node')
cn = pd.ChanceNode(o, i_o)
c.push(cn)
probs = pd.Probabilities(o, [0.2, 0.8])
x.push(probs)

i_t = pd.Vector('Node')
dn = pd.DecisionNode(t, i_t)
d.push(dn)

i_r = [o, t]
x_r = np.zeros((s[o], s[t], s[r]))
x_r[0, 0, :] = [1.0, 0.0, 0.0]
x_r[0, 1, :] = [0.0, 1.0, 0.0]
x_r[1, 0, :] = [1.0, 0.0, 0.0]
x_r[1, 1, :] = [0.0, 0.0, 1.0]
cn = pd.ChanceNode(r, i_r)
c.push(cn)
pd.Main.p = probs
print(pd.Main.eval('typeof(p)'))
probs = pd.Probabilities(r, x_r)
pd.Main.p = probs
print(pd.Main.eval('typeof(p)'))
print(x)
x.push(probs)

i_a = [r]
dn = pd.DecisionNode(a, i_a)
d.push(dn)
print(d)

i_v1 = [t]
y_v1 = [0.0, -25.0]
vn = pd.ValueNode(5, i_v1)
v.push(vn)
print(v)
consequences = pd.Consequences(5, y_v1)
y.push(consequences)
print(y)

i_v2 = [a]
y_v2 = [100.0, 40.0, 0.0]
vn = pd.ValueNode(6, i_v2)
v.push(vn)
consq = pd.Consequences(6, y_v2)
y.push(consq)

i_v3 = [o, a]
y_v3 = [[-200.0, 0.0, 0.0],
        [-40.0, -20.0, 0.0]]
vn = pd.ValueNode(7, i_v3)
v.push(vn)
print(v)
consq = pd.Consequences(7, y_v3)
y.push(consq)
print(y)

pd.validate_influence_diagram(s, c, d, v)
for vec in (c, d, v, x, y):
    vec.sortByNode()

p = pd.DefaultPathProbability(c, x)
u = pd.DefaultPathUtility(v, y)

model = pd.Model()
z_var = pd.DecisionVariables(model, s, d)
pi_s = pd.PathProbabilityVariables(model, z_var, s, p)
ev = pd.expected_value(model, pi_s, u)
pd.set_objective(model, 'Max', ev)

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
   ("LazyConstraints", 1)
)

model.optimize()

z = pd.DecisionStrategy(z_var)
pd.print_decision_strategy(s, z)

udist = pd.UtilityDistribution(s, p, u, z)
pd.print_utility_distribution(udist)
pd.print_statistics(udist)
