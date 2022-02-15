import DecisionProgramming as dp

# dp.setupProject()
dp.activate()
N = 4

diagram = dp.InfluenceDiagram()

health_outcomes = dp.ChanceNode("H0", [], ["ill", "healthy"])
diagram.add_node(health_outcomes)

for i in range(N-1):
    # testing result
    test_outcomes = dp.ChanceNode(f"T{i}", [f"H{i}"], ["positive", "negative"])
    diagram.add_node(test_outcomes)

    # Decision to treat
    treatment_decision = dp.DecisionNode(f"D{i}", [f"T{i}"], ["treat", "pass"])
    diagram.add_node(treatment_decision)

    # Cost of treatment
    treatment_cost = dp.ValueNode(f"C{i}", [f"D{i}"])
    diagram.add_node(treatment_cost)

    # Health of next period
    test_outcomes = dp.ChanceNode(f"H{i+1}", [f"H{i}", f"D{i}"], ["ill", "healthy"])
    diagram.add_node(test_outcomes)

# Final market price
treatment_cost = dp.ValueNode("MP", [f"H{N-1}"])
diagram.add_node(treatment_cost)

diagram.generate_arcs()

diagram.set_probabilities("H0", [0.1, 0.9])

# The probability matrix for rest of the health nodes
X_H = diagram.construct_probability_matrix("H1")
X_H["healthy", "pass", :] = [0.2, 0.8]
X_H["healthy", "treat", :] = [0.1, 0.9]
X_H["ill", "pass", :] = [0.9, 0.1]
X_H["ill", "treat", :] = [0.5, 0.5]

# The probability matrix for the treatment outcomes
X_T = diagram.construct_probability_matrix("T1")
X_T["ill", "positive"] = 0.8
X_T["ill", "negative"] = 0.2
X_T["healthy", "negative"] = 0.9
X_T["healthy", "positive"] = 0.1

for i in range(N-1):
    diagram.set_probabilities(f"T{i}", X_T)
    diagram.set_probabilities(f"H{i+1}", X_H)

for i in range(N-1):
    diagram.set_utility(f"C{i}", [-100, 0])

diagram.set_utility("MP", [300, 1000])

diagram.generate(positive_path_utility=True)


model = dp.Model()
z = diagram.decision_variables(model)
x_s = diagram.path_compatibility_variables(model, z, probability_cut = False)
EV = diagram.expected_value(model, x_s)
model.objective(EV, "Max")

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
)
model.optimize()

Z = z.decision_strategy()
S_probabilities = diagram.state_probabilities(Z)
U_distribution = diagram.utility_distribution(Z)

S_probabilities.print_decision_strategy()

health_nodes = [f"H{i}" for i in range(N)]
S_probabilities.print(health_nodes)

test_nodes = [f"T{i}" for i in range(N-1)]
S_probabilities.print(test_nodes)

treatment_nodes = [f"D{i}" for i in range(N-1)]
S_probabilities.print(treatment_nodes)

U_distribution.print_distribution()
U_distribution.print_statistics()

