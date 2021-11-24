import pyDecisionProgramming as pdp

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

X_O = diagram.construct_probability_matrix("O")
X_O["peach"] = 0.8
X_O["lemon"] = 0.2
diagram.set_probabilities("O", X_O)

# You can also get the current matrix and change it
X_R = diagram.construct_probability_matrix('R')
X_R["lemon", "no test", :] = [1, 0, 0]
X_R["lemon", "test", :] = [0, 1, 0]
X_R["peach", "no test", :] = [1, 0, 0]
X_R["peach", "test", :] = [0, 0, 1]
diagram.set_probabilities('R', X_R)

Y_V1 = diagram.construct_utility_matrix('V1')
Y_V1["test"] = -25
Y_V1["no test"] = 0
diagram.set_utility('V1', Y_V1)

Y_V2 = diagram.construct_utility_matrix('V2')
Y_V2["buy without guarantee"] = 100
Y_V2["buy with guarantee"] = 40
Y_V2["don't buy"] = 0
diagram.set_utility('V2', Y_V2)

Y_V3 = diagram.construct_utility_matrix('V3')
Y_V3["lemon", "buy without guarantee"] = -200
Y_V3["lemon", "buy with guarantee"] = 0
Y_V3["lemon", "don't buy"] = 0
Y_V3["peach", :] = [-40, -20, 0]
diagram.set_utility('V3', Y_V3)

diagram.generate()

model = pdp.Model()
z = diagram.decision_variables(model)
x_s = diagram.path_compatibility_variables(model, z)
EV = diagram.expected_value(model, x_s)
model.objective(EV, "Max")

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
   ("LazyConstraints", 1)
)
model.optimize()

Z = z.decision_strategy()
S_probabilities = diagram.state_probabilities(Z)
U_distribution = diagram.utility_distribution(Z)

S_probabilities.print_decision_strategy()
U_distribution.print_distribution()
U_distribution.print_statistics()
