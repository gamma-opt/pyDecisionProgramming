import pyDecisionProgramming as pdp

# pdp.setupProject()
pdp.activate()
N = 4

diagram = pdp.InfluenceDiagram()

health_outcomes = pdp.ChanceNode("H0", [], ["ill", "healthy"])
diagram.add_node(health_outcomes)

for i in range(N-1):
    # testing result
    test_outcomes = pdp.ChanceNode(f"T{i}", [f"H{i}"], ["positive", "negative"])
    diagram.add_node(test_outcomes)

    # Decision to treat
    treatment_decision = pdp.DecisionNode(f"D{i}", [f"T{i}"], ["treat", "pass"])
    diagram.add_node(treatment_decision)

    # Cost of treatment
    treatment_cost = pdp.ValueNode(f"C{i}", [f"D{i}"])
    diagram.add_node(treatment_cost)

    # Health of next period
    test_outcomes = pdp.ChanceNode(f"H{i+1}", [f"H{i}", f"D{i}"], ["ill", "healthy"])
    diagram.add_node(test_outcomes)

# Final market price
treatment_cost = pdp.ValueNode("MP", [f"H{N-1}"])
diagram.add_node(treatment_cost)

diagram.generate_arcs()

diagram.set_probabilities("H0", [0.1, 0.9])

# The probability matrix for rest of the health nodes
health_probs = pdp.ProbabilityMatrix(diagram, "H1")
health_probs["healthy", "pass", :] = [0.2, 0.8]
health_probs["healthy", "treat", :] = [0.1, 0.9]
health_probs["ill", "pass", :] = [0.9, 0.1]
health_probs["ill", "treat", :] = [0.5, 0.5]

# The probability matrix for the treatment outcomes
treatment_probs = pdp.ProbabilityMatrix(diagram, "T1")
treatment_probs["ill", "positive"] = 0.8
treatment_probs["ill", "negative"] = 0.2
treatment_probs["healthy", "negative"] = 0.9
treatment_probs["healthy", "positive"] = 0.1

for i in range(N-1):
    diagram.set_probabilities(f"T{i}", treatment_probs)
    diagram.set_probabilities(f"H{i+1}", health_probs)

for i in range(N-1):
    diagram.set_utility(f"C{i}", [-100, 0])

diagram.set_utility("MP", [300, 1000])

diagram.generate(positive_path_utility=True)


model = pdp.Model()
z = pdp.DecisionVariables(model, diagram)
x_s = pdp.PathCompatibilityVariables(model, diagram, z, probability_cut = False)

EV = pdp.ExpectedValue(model, diagram, x_s)
model.objective("Max", EV)

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
)
model.optimize()

Z = pdp.DecisionStrategy(z)
S_probabilities = pdp.StateProbabilities(diagram, Z)
U_distribution = pdp.UtilityDistribution(diagram, Z)

S_probabilities.print_decision_strategy()

health_nodes = [f"H{i}" for i in range(N)]
S_probabilities.print(health_nodes)

test_nodes = [f"T{i}" for i in range(N-1)]
S_probabilities.print(test_nodes)

treatment_nodes = [f"D{i}" for i in range(N-1)]
S_probabilities.print(treatment_nodes)

U_distribution.print_distribution()
U_distribution.print_statistics()

