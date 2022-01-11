import pyDecisionProgramming as pdp
import numpy as np

# pdp.setupProject()
pdp.activate()


N = 4
np.random.seed(13)
c_k = np.random.random(N)
b = 0.03


def fortification(k, a):
    if not a:
        return c_k[k]
    else:
        return 0


diagram = pdp.InfluenceDiagram()

load_node = pdp.ChanceNode("L", [], ["high", "low"])
diagram.add_node(load_node)

for i in range(N):
    report_node = pdp.ChanceNode(f"R{i}", ["L"], ["high", "low"])
    diagram.add_node(report_node)
    reinforcement_node = pdp.DecisionNode(f"A{i}", [f"R{i}"], ["yes", "no"])
    diagram.add_node(reinforcement_node)

Fail_state_node = pdp.ChanceNode(
    "F",
    ["L", *[f"A{i}" for i in range(N)]],
    ["failure", "success"]
)
diagram.add_node(Fail_state_node)

value_node = pdp.ValueNode("T", ["F", *[f"A{i}" for i in range(N)]])
diagram.add_node(value_node)

diagram.generate_arcs()

r = np.random.random()
X_L = [r, 1.0-r]
diagram.set_probabilities("L", X_L)

for i in range(N):
    x, y = np.random.random(2)
    x = np.max([x, 1-x])
    y = np.max([y, 1-y])
    X_R = diagram.construct_probability_matrix(f"R{i}")
    X_R["high", "high"] = x
    X_R["high", "low"] = 1 - x
    X_R["low", "low"] = y
    X_R["low", "high"] = 1 - y
    diagram.set_probabilities(f"R{i}", X_R)

X_F = diagram.construct_probability_matrix("F")

x, y = np.random.random(2)
for path in pdp.Paths([2]*N):
    forticications = [fortification(k, a) for k, a in enumerate(path)]
    denominator = np.exp(b * np.sum(forticications))
    X_F[(0, *path, 0)] = max(x, 1-x) / denominator
    X_F[(0, *path, 1)] = 1.0 - max(x, 1-x) / denominator
    X_F[(1, *path, 0)] = min(y, 1-y) / denominator
    X_F[(1, *path, 1)] = 1.0 - min(y, 1-y) / denominator

diagram.set_probabilities("F", X_F)

Y_T = diagram.construct_utility_matrix('T')

for path in pdp.Paths([2]*N):
    forticications = [fortification(k, a) for k, a in enumerate(path)]
    cost = -sum(forticications)
    Y_T[(0, *path)] = 0 + cost
    Y_T[(1, *path)] = 100 + cost

diagram.set_utility('T', Y_T)

diagram.generate(positive_path_utility=True)

model = pdp.Model()
z = diagram.decision_variables(model)
x_s = diagram.path_compatibility_variables(
    model, z,
    probability_cut=False
)

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

S_probabilities.print(["L"])

report_nodes = [f"R{i}" for i in range(N)]
S_probabilities.print(report_nodes)

reinforcement_nodes = [f"A{i}" for i in range(N-1)]
S_probabilities.print(reinforcement_nodes)

S_probabilities.print(["F"])

U_distribution.print_distribution()
U_distribution.print_statistics()


