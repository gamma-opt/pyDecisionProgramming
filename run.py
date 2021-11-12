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

S_probabilities.print()
U_distribution.print_distribution()
U_distribution.print_statistics()
