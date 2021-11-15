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

X_O = pdp.ProbabilityMatrix(diagram, "O")
X_O["peach"] = 0.8
X_O["lemon"] = 0.2
diagram.set_probabilities("O", X_O)

# You can also get the current matrix and change it
R_probs = pdp.ProbabilityMatrix(diagram, 'R')
R_probs["lemon", "no test", :] = [1, 0, 0]
R_probs["lemon", "test", :] = [0, 1, 0]
R_probs["peach", "no test", :] = [1, 0, 0]
R_probs["peach", "test", :] = [0, 0, 1]
diagram.set_probabilities('R', R_probs)

V1_utilities = pdp.UtilityMatrix(diagram, 'V1')
V1_utilities["test"] = -25
V1_utilities["no test"] = 0
diagram.set_utility('V1', V1_utilities)

V2_utilities = pdp.UtilityMatrix(diagram, 'V2')
V2_utilities["buy without guarantee"] = 100
V2_utilities["buy with guarantee"] = 40
V2_utilities["don't buy"] = 0
diagram.set_utility('V2', V2_utilities)

V3_utilities = pdp.UtilityMatrix(diagram, 'V3')
V3_utilities["lemon", "buy without guarantee"] = -200
V3_utilities["lemon", "buy with guarantee"] = 0
V3_utilities["lemon", "don't buy"] = 0
V3_utilities["peach", :] = [-40, -20, 0]
diagram.set_utility('V3', V3_utilities)

diagram.generate()

model = pdp.Model()
z = pdp.DecisionVariables(model, diagram)
x_s = pdp.PathCompatibilityVariables(model, diagram, z)
EV = pdp.ExpectedValue(model, diagram, x_s)

model.objective("Max", EV)

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
   ("LazyConstraints", 1)
)

model.optimize()

Z = pdp.DecisionStrategy(z)
S_probabilities = pdp.StateProbabilities(diagram, Z)
U_distribution = pdp.UtilityDistribution(diagram, Z)

S_probabilities.print_decision_strategy()
U_distribution.print_distribution()
U_distribution.print_statistics()
