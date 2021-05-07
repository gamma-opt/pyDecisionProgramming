import pyDecisionProgramming as pd
import numpy as np

#pd.setupProject()
pd.activate()


o = 1
t = 2
r = 3
a = 4
O_states = ["lemon", "peach"]
T_states = ["no test", "test"]
R_states = ["no test", "lemon", "peach"]
A_states = ["buy without guarantee", "buy with guarantee", "don\'t buy"]

s = pd.States([
 (len(O_states), o),
 (len(T_states), t),
 (len(R_states), r),
 (len(A_states), a),
])
print(s)

c = pd.Vector('ChanceNode')
d = pd.Vector('DecisionNode')
v = pd.Vector('ValueNode')
x = pd.Vector('Probabilities')
y = pd.Vector('Consequences')

i_o = pd.Vector('Node')
cn = pd.ChanceNode(o, i_o)
c.push(cn)
probs = pd.Probabilities(o, [0.2, 0.8])
x.push(probs)

i_t = pd.Vector('Node')
dn = pd.DecisionNode(t, i_t)
d.push(dn)

i_r = [o, t]
x_r = np.zeros((s[o], s[t], s[r]))
x_r[0, 0, :] = [1.0, 0.0, 0.0]
x_r[0, 1, :] = [0.0, 1.0, 0.0]
x_r[1, 0, :] = [1.0, 0.0, 0.0]
x_r[1, 1, :] = [0.0, 0.0, 1.0]
cn = pd.ChanceNode(r, i_r)
c.push(cn)
pd.Main.p = probs
print(pd.Main.eval('typeof(p)'))
probs = pd.Probabilities(r, x_r)
pd.Main.p = probs
print(pd.Main.eval('typeof(p)'))
print(x)
x.push(probs)

i_a = [r]
dn = pd.DecisionNode(a, i_a)
d.push(dn)
print(d)

i_v1 = [t]
y_v1 = [0.0, -25.0]
vn = pd.ValueNode(5, i_v1)
v.push(vn)
print(v)
consequences = pd.Consequences(5, y_v1)
y.push(consequences)
print(y)

i_v2 = [a]
y_v2 = [100.0, 40.0, 0.0]
vn = pd.ValueNode(6, i_v2)
v.push(vn)
print(v)
consq = pd.Consequences(6, y_v2)
y.push(consq)
print(y)

i_v3 = [o, a]
y_v3 = [[-200.0, 0.0, 0.0],
        [-40.0, -20.0, 0.0]]
vn = pd.ValueNode(7, i_v3)
v.push(vn)
print(v)
consq = pd.Consequences(7, y_v3)
y.push(consq)
print(y)

pd.validate_influence_diagram(s, c, d, v)
for vec in (c, d, v, x, y):
    vec.sortByNode()

p = pd.DefaultPathProbability(c, x)
print(p)
u = pd.DefaultPathUtility(v, y)
print(u)

model = pd.Model()
print(model)
z_var = pd.DecisionVariables(model, s, d)
print(z_var)

pi_s = pd.PathProbabilityVariables(model, z_var, s, p)
