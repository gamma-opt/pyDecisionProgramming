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

n_DP = diagram.num_states("DP")
n_CT = diagram.num_states("CT")
n_DA = diagram.num_states("DA")
n_CM = diagram.num_states("CM")

n_T = 5               # number of technology projects
n_A = 5               # number of application projects
I_t = np.random.random(n_T)*0.1   # costs of technology projects
O_t = np.random.randint(1, 4, n_T)   # number of patents for each tech project
I_a = np.random.random(n_T)*2     # costs of application projects
O_a = np.random.randint(2, 5, n_T)   # number of applications for each appl. project

V_A = np.random.random((n_CM, n_A)) + 0.5  # Value of an application
V_A[0, :] += -0.5           # Low market share: less value
V_A[2, :] += 0.5            # High market share: more value

pdp.JuMP_Variable(model, [n_DP, n_T], binary=True)
pdp.JuMP_Variable(model, [n_DP, n_CT, n_DA, n_A], binary=True)

M = 20                      # a large constant
eps = 0.5*np.min([O_t, O_a])  # a helper variable, allows using ≤ instead of < in constraints (28b) and (29b)

q_P = [0, 3, 6, 9]          # limits of the technology intervals
q_A = [0, 5, 10, 15]        # limits of the application intervals

model.constraint("[i=1:n_DP]", "sum(x_T[i,t] for t in 1:n_T) <= z_dP[i]*n_T]")



