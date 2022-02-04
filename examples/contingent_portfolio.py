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

X_CT = diagram.construct_probability_matrix("CT")
X_CT[0, :] = [1/2, 1/3, 1/6]
X_CT[1, :] = [1/3, 1/3, 1/3]
X_CT[2, :] = [1/6, 1/3, 1/2]
diagram.set_probabilities("CT", X_CT)

X_CM = diagram.construct_probability_matrix("CM")
X_CM[0, 0, :] = [2/3, 1/4, 1/12]
X_CM[0, 1, :] = [1/2, 1/3, 1/6]
X_CM[0, 2, :] = [1/3, 1/3, 1/3]
X_CM[1, 0, :] = [1/2, 1/3, 1/6]
X_CM[1, 1, :] = [1/3, 1/3, 1/3]
X_CM[1, 2, :] = [1/6, 1/3, 1/2]
X_CM[2, 0, :] = [1/3, 1/3, 1/3]
X_CM[2, 1, :] = [1/6, 1/3, 1/2]
X_CM[2, 2, :] = [1/12, 1/4, 2/3]
diagram.set_probabilities("CM", X_CM)

diagram.generate(default_utility=False)


model = pdp.Model()
z = diagram.decision_variables(model)

n_DP = diagram.num_states("DP")
n_CT = diagram.num_states("CT")
n_DA = diagram.num_states("DA")
n_CM = diagram.num_states("CM")

n_T = 5               # number of technology projects
n_A = 5               # number of application projects

# Here we set stuff in Julia name space directly
I_t = np.random.random(n_T)*0.1   # costs of technology projects
O_t = np.random.randint(1, 4, n_T)   # number of patents for each tech project
I_a = np.random.random(n_T)*2     # costs of application projects
O_a = np.random.randint(2, 5, n_T)   # number of applications for each appl. project

# Set the names in julia to use them when setting constraints
pdp.julia.I_t = I_t
pdp.julia.O_t = O_t
pdp.julia.I_a = I_a
pdp.julia.O_a = O_a

V_A = np.random.random((n_CM, n_A)) + 0.5  # Value of an application
V_A[0, :] += -0.5           # Low market share: less value
V_A[2, :] += 0.5            # High market share: more value

pdp.julia.V_A = V_A


x_T = pdp.JuMP.Array(model, [n_DP, n_T], binary=True)
x_A = pdp.JuMP.Array(model, [n_DP, n_CT, n_DA, n_A], binary=True)
pdp.julia.x_T = x_T
pdp.julia.x_A = x_A


pdp.julia.M = 20                      # a large constant
pdp.julia.eps = 0.5*np.min([O_t, O_a])  # a helper variable, allows using ≤ instead of < in constraints (28b) and (29b)

pdp.julia.q_P = [0, 3, 6, 9]          # limits of the technology intervals
pdp.julia.q_A = [0, 5, 10, 15]        # limits of the application intervals

pdp.julia.diagram = diagram
pdp.julia.z_dP = z.z[0]
pdp.julia.z_dA = z.z[1]

model.constraint(
    f"[i=1:{n_DP}]",
    f"sum(x_T[i,t] for t in 1:{n_T}) <= z_dP[i]*{n_T}"
)
model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"sum(x_A[i,j,k,a] for a in 1:{n_A}) <= z_dP[i]*{n_A}"
)
model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"sum(x_A[i,j,k,a] for a in 1:{n_A}) <= z_dA[i,j,k]*{n_A}"
)

model.constraint(
    f"[i=1:{n_DP}]",
    f"q_P[i] - (1 - z_dP[i])*M <= sum(x_T[i,t]*O_t[t] for t in 1:{n_T})"
)
model.constraint(
    f"[i=1:{n_DP}]",
    f"sum(x_T[i,t]*O_t[t] for t in 1:{n_T}) <= q_P[i+1] + (1 - z_dP[i])*M - eps"
)
model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"q_A[k] - (1 - z_dA[i,j,k])*M <= sum(x_A[i,j,k,a]*O_a[a] for a in 1:{n_A})"
)
model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"sum(x_A[i,j,k,a]*O_a[a] for a in 1:{n_A}) <= q_A[k+1] + (1 - z_dA[i,j,k])*M - eps"
)

model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"x_A[i,j,k,1] <= x_T[i,1]"
)
model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"x_A[i,j,k,2] <= x_T[i,1]"
)
model.constraint(
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"x_A[i,j,k,2] <= x_T[i,2]"
)


pdp.julia.patent_investment_cost = pdp.JuMP.Expression(
    model,
    f"[i=1:{n_DP}]",
    f"sum(x_T[i, t] * I_t[t] for t in 1:{n_T})"
)

pdp.julia.application_investment_cost = pdp.JuMP.Expression(
    model,
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}]",
    f"sum(x_A[i, j, k, a] * I_a[a] for a in 1:{n_A})"
)

pdp.julia.application_value = pdp.JuMP.Expression(
    model,
    f"[i=1:{n_DP}, j=1:{n_CT}, k=1:{n_DA}, l=1:{n_CM}]",
    f"sum(x_A[i, j, k, a] * V_A[l, a] for a in 1:{n_A})"
)


model.objective(
    f"sum( sum( diagram.P(convert.(State, (i,j,k,l))) * (application_value[i,j,k,l] - application_investment_cost[i,j,k]) for j in 1:{n_CT}, k in 1:{n_DA}, l in 1:{n_CM} ) - patent_investment_cost[i] for i in 1:{n_DP} )"
)

model.setup_Gurobi_optimizer(
   ("IntFeasTol", 1e-9),
   ("LazyConstraints", 1)
)
model.optimize()

Z = z.decision_strategy()
S_probabilities = diagram.state_probabilities(Z)
S_probabilities.print_decision_strategy()

# We save the integer indeces of the nodes into Julia namespace.
# Note that indexing in Julia starts from 1, so we must add 1 to
# each index
pdp.julia.DP_i = diagram.index_of("DP") + 1
pdp.julia.CT_i = diagram.index_of("CT") + 1
pdp.julia.DA_i = diagram.index_of("DA") + 1
pdp.julia.CM_i = diagram.index_of("CM") + 1
path_utilities = pdp.Diagram.ExpressionPathUtilities(
    model, diagram,
    f'''sum(x_A[s[index_of(diagram, "DP")], s[index_of(diagram, "CT")], s[index_of(diagram, "DA")], a] * (V_A[s[index_of(diagram, "CM")], a] - I_a[a]) for a in 1:{n_A}) -
        sum(x_T[s[index_of(diagram, "DP")], t] * I_t[t] for t in 1:{n_T})
    ''',
    path_name="s"
)

diagram.set_path_utilities(path_utilities)

U_distribution = diagram.utility_distribution(Z)
U_distribution.print_distribution()
U_distribution.print_statistics()
