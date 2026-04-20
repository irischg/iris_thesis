import gurobipy as gp
from gurobipy import GRB

print("gurobipy version:", gp.gurobi.version())

m = gp.Model("sanity_check")

x = m.addVar(vtype=GRB.CONTINUOUS, name="x", lb=0.0)
y = m.addVar(vtype=GRB.CONTINUOUS, name="y", lb=0.0)

m.setObjective(x + y, GRB.MAXIMIZE)

m.addConstr(x + 2 * y <= 4, name="c1")
m.addConstr(4 * x + 2 * y <= 12, name="c2")

m.optimize()

if m.status == GRB.OPTIMAL:
    print("Optimization successful.")
    for v in m.getVars():
        print(f"{v.VarName} = {v.X}")
    print("Objective =", m.ObjVal)
else:
    print("Model did not solve to optimality. Status:", m.status)