import pyDecisionProgramming as pdp
import numpy as np
import pandas as pd
from numba import jit

# pdp.setupProject()
pdp.activate()

chosen_risk_level = "12%"
data = pd.read_csv("examples/risk_prediction_data.csv")


# Bayes posterior risk probabilities calculation function
# prior = prior risk level for which the posterior risk distribution is calculated for,
# t = test done
# returns a 100x1 vector with the probabilities of getting CHD given the prior risk level and test result
# for no test done (i.e. t = 3) returns a zero vector
@jit
def update_risk_distribution(prior, t):
    if t == 1:  # the test is TRS
        # P(TRS = result | sick) = P(TRS_if_sick = result) * P(sick) = P(TRS_if_sick = result) * P(prior_risk)
        numerators = data.TRS_if_sick * data.risk_levels[prior]

        # P(TRS = result) = P(TRS_if_sick = result) * P(sick) + P(TRS_if_healthy = result) * P(healthy)
        denominators = numerators + data.TRS_if_healthy * (1 - data.risk_levels[prior])

        posterior_risks = numerators/denominators

        # if the denominator is zero, post_risk is NaN, changing those to 0
        posterior_risks = posterior_risks.replace([np.nan], 0)

        return posterior_risks

    elif t == 2:  # the test is GRS
        numerators = data.GRS_if_sick * data.risk_levels[prior]
        denominators = data.GRS_if_sick * data.risk_levels[prior] + data.GRS_if_healthy * (1 - data.risk_levels[prior])

        posterior_risks = numerators/denominators

        # if the denominator is zero, post_risk is NaN, changing those to 0
        posterior_risks = posterior_risks.replace([np.nan], 0)

        return posterior_risks

    else:  # no test performed
        risks_unchanged = np.zeros(101)
        return risks_unchanged


# State probabilites calculation function
# risk_p = the resulting array from update_risk_distribution
# t = test done
# h = CHD or no CHD
# returns the probability distribution in 101x1 vector for the states of the R node given the prior risk level (must be same as to function update_risk_distribution), test t and health h
@jit
def state_probabilities(risk_p, t, h, prior):

    #if no test is performed, then the probabilities of moving to states (other than the prior risk level) are 0 and to the prior risk element is 1
    if t == 3:
        state_probabilites = np.zeros(101)
        state_probabilites[prior] = 1.0
        return state_probabilites

    # return vector
    state_probabilites = np.zeros(101)

    # copying the probabilities of the scores for ease of readability
    if h == 1 and t == 1:    # CHD and TRS
        p_scores = data.TRS_if_sick.to_numpy()
    elif t == 1:    # no CHD and TRS
        p_scores = data.TRS_if_healthy.to_numpy()
    elif h == 1 and t == 2:  # CHD and GRS
        p_scores = data.GRS_if_sick.to_numpy()
    else:  # no CHD and GRS
        p_scores = data.GRS_if_healthy.to_numpy()

    for i in range(100):  # iterating through all risk levels 0%, 1%, ..., 99%, 99% in data.risk_levels
        risk_level = data.risk_levels[i]
        next_risk_level = data.risk_levels[i+1]
        indexes = np.logical_and(risk_level <= risk_p, risk_p < next_risk_level)

        state_probabilites[i] += np.sum(p_scores[indexes])

    # special case: the highest risk level[101] = 100%
    indexes = data.risk_levels[100] <= risk_level
    state_probabilites[indexes] += np.sum(p_scores[indexes])

    return state_probabilites


diagram = pdp.InfluenceDiagram()

H_states = ["CHD", "no CHD"]
T_states = ["TRS", "GRS", "no test"]
TD_states = ["treatment", "no treatment"]
R_states = [str(x) + "%" for x in range(101)]

diagram.add_node(pdp.ChanceNode("R0", [], R_states))
diagram.add_node(pdp.ChanceNode("R1", ["R0", "H", "T1"], R_states))
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
diagram.set_probabilities("R0", X_R0)

X_H = pdp.ProbabilityMatrix(diagram, "H")
X_H[:, "CHD"] = data.risk_levels.to_list()
X_H[:, "no CHD"] = (1-data.risk_levels).to_list()
diagram.set_probabilities("H", X_H)

X_R = pdp.ProbabilityMatrix(diagram, "R1")
for s_R0 in range(101):
    print(s_R0)
    for s_H in range(2):
        for s_T1 in range(3):
            risk = update_risk_distribution(s_R0, s_T1)
            probs = state_probabilities(risk, s_T1, s_H, s_R0)
            X_R[s_R0, s_H, s_T1, :] = probs.tolist()

diagram.set_probabilities("R1", X_R)
diagram.set_probabilities("R2", X_R)

