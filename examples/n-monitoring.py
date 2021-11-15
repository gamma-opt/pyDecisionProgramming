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
    f"F",
    ["L", *[f"A{i}" for i in range(N)]],
    ["failure", "success"]
)
diagram.add_node(Fail_state_node)

value_node = pdp.ValueNode(
    f"T",
    ["F", *[f"A{i}" for i in range(N)]]
)
diagram.add_node(value_node)

diagram.generate_arcs()

r = np.random.random()
probs = [r, 1.0-r]
diagram.set_probabilities("L", probs)

for i in range(N):
    x, y = np.random.random(2)
    x = np.max([x, 1-x])
    y = np.max([y, 1-y])
    probs = pdp.ProbabilityMatrix(diagram, f"R{i}")
    probs["high", "high"] = x
    probs["high", "low"] = 1 - x
    probs["low", "low"] = y
    probs["low", "high"] = 1 - y
    diagram.set_probabilities(f"R{i}", probs)

P_f = pdp.ProbabilityMatrix(diagram, "F")
x, y = np.random.random(2)

for path in pdp.Paths([2]*N):
    forticications = [fortification(k, a) for k, a in enumerate(path)]
    denominator = np.exp(b * np.sum(forticications))
    P_f[(0, *path, 0)] = max(x, 1-x) / denominator
    P_f[(0, *path, 1)] = 1.0 - max(x, 1-x) / denominator
    P_f[(1, *path, 0)] = min(y, 1-y) / denominator
    P_f[(1, *path, 1)] = 1.0 - min(y, 1-y) / denominator

diagram.set_probabilities("F", P_f)

Utilities = pdp.UtilityMatrix(diagram, 'T')

for path in pdp.Paths([2]*N):
    forticications = [fortification(k, a) for k, a in enumerate(path)]
    cost = -sum(forticications)
    Utilities[(0, *path)] = 0 + cost
    Utilities[(1, *path)] = 100 + cost

diagram.set_utility('T', Utilities)

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

S_probabilities.print(["L"])

report_nodes = [f"R{i}" for i in range(N)]
S_probabilities.print(report_nodes)

reinforcement_nodes = [f"A{i}" for i in range(N-1)]
S_probabilities.print(reinforcement_nodes)

S_probabilities.print(["F"])

U_distribution.print_distribution()
U_distribution.print_statistics()
