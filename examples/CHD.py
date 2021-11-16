import pyDecisionProgramming as pdp
import numpy as np
import pandas as pd

# pdp.setupProject()
pdp.activate()

np.random.seed(42)

chosen_risk_level = 0.12
data = pd.read_csv("examples/risk_prediction_data.csv")

diagram = pdp.InfluenceDiagram()

H_states = ["CHD", "no CHD"]
T_states = ["TRS", "GRS", "no test"]
TD_states = ["treatment", "no treatment"]
R_states = [str(x) + "%" for x in range(100)]

diagram.add_node(pdp.ChanceNode("R0", [], R_states))
diagram.add_node(pdp.ChanceNode("R1", ["R1", "H", "T2"], R_states))
diagram.add_node(pdp.ChanceNode("R2", ["R1", "H", "T2"], R_states))
diagram.add_node(pdp.ChanceNode("H",  ["R0"], H_states))

diagram.add_node(pdp.DecisionNode("T1",  ["R0"], T_states))
diagram.add_node(pdp.DecisionNode("T2",  ["R1"], T_states))
diagram.add_node(pdp.DecisionNode("TD",  ["R2"], TD_states))

diagram.add_node(pdp.ValueNode("TC",  ["T1", "T2"]))
diagram.add_node(pdp.ValueNode("HB",  ["H", "TD"]))

diagram.generate_arcs()

X_R0 = pdp.ProbabilityMatrix(diagram, "R0")
X_R0[chosen_risk_level] = 1
diagram.add_probabilities("R0", X_R0)

X_H = pdp.ProbabilityMatrix(diagram, "H")
X_H[:, "CHD"] = data.risk_levels.to_numpy()
X_H[:, "no CHD"] = 1 - data.risk_levels.to_numpy()
diagram.add_probabilities("H", X_H)

X_R = pdp.ProbabilityMatrix(diagram, "R1")
for s_R0 in range(101):
   for s_H in range(2):
      for s_T1 in range(3):
         X_R[s_R0, s_H, s_T1, :] =

diagram.add_probabilities("R2", X_R)

