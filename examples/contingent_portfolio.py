import pyDecisionProgramming as pdp
import numpy as np

# pdp.setupProject()
pdp.activate()

np.random.seed(42)


diagram = pdp.InfluenceDiagram()

decision_node = pdp.DecisionNode("DP", [], ["0-3 patents", "3-6 patents", "6-9 patents"])
diagram.add_node(decision_node)

outcome_node = pdp.ChanceNode("CT", ["DP"], ["low", "medium", "high"])
diagram.add_node(outcome_node)

decision_node = pdp.DecisionNode("DA", ["DP", "CT"], ["0-5 applications", "5-10 applications", "10-15 applications"])
diagram.add_node(decision_node)

outcome_node = pdp.ChanceNode("CM", ["CT", "DA"], ["low", "medium", "high"])
diagram.add_node(outcome_node)

diagram.generate_arcs()

probs = pdp.ProbabilityMatrix(diagram, "CT")
probs[0, :] = [1/2, 1/3, 1/6]
probs[1, :] = [1/3, 1/3, 1/3]
probs[2, :] = [1/6, 1/3, 1/2]
diagram.set_probabilities("CT", probs)

probs = pdp.ProbabilityMatrix(diagram, "CM")
probs[0, 0, :] = [2/3, 1/4, 1/12]
probs[0, 1, :] = [1/2, 1/3, 1/6]
probs[0, 2, :] = [1/3, 1/3, 1/3]
probs[1, 0, :] = [1/2, 1/3, 1/6]
probs[1, 1, :] = [1/3, 1/3, 1/3]
probs[1, 2, :] = [1/6, 1/3, 1/2]
probs[2, 0, :] = [1/3, 1/3, 1/3]
probs[2, 1, :] = [1/6, 1/3, 1/2]
probs[2, 2, :] = [1/12, 1/4, 2/3]
diagram.set_probabilities("CM", probs)

diagram.generate(default_utility=False)
model = pdp.Model()
z = pdp.DecisionVariables(model, diagram)

n_DP = diagram.num_states(diagram, "DP")
n_CT = diagram.num_states(diagram, "CT")
n_DA = diagram.num_states(diagram, "DA")
n_CM = diagram.num_states(diagram, "CM")

