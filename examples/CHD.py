import pyDecisionProgramming as pdp
import numpy as np
import pandas as pd
from types import SimpleNamespace

# pdp.setupProject()
pdp.activate()

orig_data = pd.read_csv("examples/risk_prediction_data.csv")

cost_TRS = -0.0034645
cost_GRS = -0.004

# Note: these include the cost of the treatmend
utility_CHD_treated = 6.89713671259061
utility_CHD_nottreated = 6.65436854256236
utility_noCHD_treated = 7.64528451705134
utility_noCHD_nottreated = 7.70088349200034

# To create a faster example, we bin the risk ranges into 2% intervals
risk_step = 2
chosen_risk_level = "12%" # The prior must be a multiple of risk_step
n_risk_levels = int(100/risk_step)+1
risk_levels = risk_step*np.array(range(n_risk_levels))

data = {"risk_levels": 0.01*risk_levels}
for type in "prior_risk_distribution", "TRS_if_healthy", "TRS_if_sick", "GRS_if_healthy", "GRS_if_sick":
    col = orig_data[type].to_numpy()
    res = [col[0]]
    for step in risk_levels[1:]:
        res.append(np.sum(col[step-risk_step+1:step+1]))
    res.append(col[100])
    data[type] = np.array(res)

data = SimpleNamespace(**data)


# Bayes posterior risk probabilities calculation function
# prior = prior risk level for which the posterior risk distribution is calculated for,
# t = test done
# returns a 100x1 vector with the probabilities of getting CHD given the prior risk level and test result
# for no test done (i.e. t = 3) returns a zero vector
def update_risk_distribution(prior, t):
    if t == 0:  # the test is TRS
        # P(TRS = result | sick) = P(TRS_if_sick = result) * P(sick) = P(TRS_if_sick = result) * P(prior_risk)
        numerators = data.TRS_if_sick * data.risk_levels[prior]

        # P(TRS = result) = P(TRS_if_sick = result) * P(sick) + P(TRS_if_healthy = result) * P(healthy)
        denominators = numerators + data.TRS_if_healthy * (1 - data.risk_levels[prior])

        posterior_risks = numerators/denominators

        # if the denominator is zero, post_risk is NaN, changing those to 0
        posterior_risks = np.nan_to_num(posterior_risks)

        return posterior_risks

    elif t == 1:  # the test is GRS
        numerators = data.GRS_if_sick * data.risk_levels[prior]
        denominators = data.GRS_if_sick * data.risk_levels[prior] + data.GRS_if_healthy * (1 - data.risk_levels[prior])

        posterior_risks = numerators/denominators

        # if the denominator is zero, post_risk is NaN, changing those to 0
        posterior_risks = np.nan_to_num(posterior_risks)

        return posterior_risks

    else:  # no test performed
        risks_unchanged = np.zeros(n_risk_levels)
        return risks_unchanged


# State probabilites calculation function
# risk_p = the resulting array from update_risk_distribution
# t = test done
# h = CHD or no CHD
# returns the probability distribution in risk_levelsx1 vector for the states of the R node given the prior risk level (must be same as to function update_risk_distribution), test t and health h
def state_probabilities(risk_p, t, h, prior):

    #if no test is performed, then the probabilities of moving to states (other than the prior risk level) are 0 and to the prior risk element is 1
    if t == 2:
        state_probabilites = np.zeros(n_risk_levels)
        state_probabilites[prior] = 1.0
        return state_probabilites

    # return vector
    state_probabilites = np.zeros(n_risk_levels)

    # copying the probabilities of the scores for ease of readability
    if h == 0 and t == 0:    # CHD and TRS
        p_scores = data.TRS_if_sick
    elif t == 0:    # no CHD and TRS
        p_scores = data.TRS_if_healthy
    elif h == 0 and t == 1:  # CHD and GRS
        p_scores = data.GRS_if_sick
    else:  # no CHD and GRS
        p_scores = data.GRS_if_healthy

    # Find p_scores within each risk level
    risk_below = data.risk_levels[:-1] <= risk_p[:,None]
    risk_above = data.risk_levels[1:] > risk_p[:,None]
    indeces = np.logical_and(risk_below, risk_above)

    for i in range(n_risk_levels-1):
        state_probabilites[i] = np.sum(p_scores[indeces[:, i]])

    # special case: the highest risk level[n_risk_levels-1] = 100%
    indexes = data.risk_levels[n_risk_levels-1] <= risk_p
    state_probabilites[n_risk_levels-1] = np.sum(p_scores[indexes])

    return state_probabilites


diagram = pdp.InfluenceDiagram()

H_states = ["CHD", "no CHD"]
T_states = ["TRS", "GRS", "no test"]
TD_states = ["treatment", "no treatment"]
R_states = [str(risk_step*x) + "%" for x in range(n_risk_levels)]

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

X_R0 = diagram.construct_probability_matrix("R0")
X_R0[chosen_risk_level] = 1
diagram.set_probabilities("R0", X_R0)

X_H = diagram.construct_probability_matrix("H")
X_H[:, "CHD"] = data.risk_levels.tolist()
X_H[:, "no CHD"] = (1-data.risk_levels).tolist()
diagram.set_probabilities("H", X_H)

X_R = diagram.construct_probability_matrix("R1")
for s_R0 in range(n_risk_levels):
    for s_H in range(2):
        for s_T1 in range(3):
            risk = update_risk_distribution(s_R0, s_T1)
            probs = state_probabilities(risk, s_T1, s_H, s_R0)
            X_R[s_R0, s_H, s_T1, :] = probs.tolist()

diagram.set_probabilities("R1", X_R)
diagram.set_probabilities("R2", X_R)


forbidden = 0   # the cost of forbidden test combinations is neglected
Y_TC = diagram.construct_utility_matrix("TC")
Y_TC["TRS", "TRS"] = forbidden
Y_TC["TRS", "GRS"] = cost_TRS + cost_GRS
Y_TC["TRS", "no test"] = cost_TRS
Y_TC["GRS", "TRS"] = cost_TRS + cost_GRS
Y_TC["GRS", "GRS"] = forbidden
Y_TC["GRS", "no test"] = cost_GRS
Y_TC["no test", "TRS"] = cost_TRS
Y_TC["no test", "GRS"] = cost_GRS
Y_TC["no test", "no test"] = 0
diagram.set_utility("TC", Y_TC)

Y_HB = diagram.construct_utility_matrix("HB")
Y_HB["CHD", "treatment"] = utility_CHD_treated
Y_HB["CHD", "no treatment"] = utility_CHD_nottreated
Y_HB["no CHD", "treatment"] = utility_noCHD_treated
Y_HB["no CHD", "no treatment"] = utility_noCHD_nottreated
diagram.set_utility("HB", Y_HB)

diagram.generate()

model = pdp.Model()
z = diagram.decision_variables(model)

forbidden_tests = diagram.forbidden_path(["T1", "T2"], [("TRS", "TRS"), ("GRS", "GRS"), ("no test", "TRS"), ("no test", "GRS")])

fixed_R0 = diagram.fixed_path({"R0": chosen_risk_level})
scale_factor = 10000.0

x_s = diagram.path_compatibility_variables(
    model, z,
    fixed=fixed_R0,
    forbidden_paths=[forbidden_tests],
    probability_cut=False,
    probability_scale_factor=scale_factor
)

EV = diagram.expected_value(model, x_s)
model.objective(EV, "Max")

model.setup_Gurobi_optimizer(
   ("MIPFocus", 3),
   ("MIPGap", 1e-6)
)
model.optimize()

Z = z.decision_strategy()
S_probabilities = diagram.state_probabilities(Z)
U_distribution = diagram.utility_distribution(Z)

S_probabilities.print_decision_strategy()
S_probabilities.print(["R0", "R1", "R2"])

U_distribution.print_distribution()
U_distribution.print_statistics()


