from pyomo.environ import ConcreteModel, Param, RangeSet, Var, Objective, Constraint, SolverFactory
import pandas as pd

# Create a concrete Pyomo model
model = ConcreteModel()
onbalanskosten = pd.read_csv('data/onbalanskosten_28_11_23.csv')
columns_to_drop = ['datum', 'PTE','periode_van', 'periode_tm', 'indicatie noodvermogen op', 'indicatie noodvermogen af', 'prikkelcomponent']
onbalanskosten = onbalanskosten.drop(columns=columns_to_drop)
#onbalanskosten = onbalanskosten.reset_index(drop=True)
print(onbalanskosten)
#print(biedprijsladders)
# Define index sets for the three dimensions
model.i = RangeSet(96)  # First dimension
model.j = RangeSet(7)  # Second dimension
model.k = RangeSet(4)  # Third dimension


def biedprijsladder_def(model, i, j):
    return biedprijsladder.iloc[j, i]

# Create a 3D parameter that depends on all three dimensions
#model.param_3d = Param(model.i, model.j, model.k, initialize={(i, j, k): i + j + k for i in model.i for j in model.j for k in model.k})
model.param_3d = Param(model.i, model.j, model.k, initialize={(i, j, k): biedprijsladder.iloc[7*(i-1)+j-1, k-1] for i in model.i for j in model.j for k in model.k})
# Display the Pyomo model
model.display()
#model.pprint()

#print(model.param_3d.extract_values())
# Accessing parameter values
# for i in model.i:
#     for j in model.j:
#         for k in model.k:
#             #print(biedprijsladder.iloc[7*(i-1)+j-1, k-1])
#             print(f"param_3d[{i},{j},{k}] = {model.param_3d[i, j, k]}")
#             # print(7*(i-1)+j, k)
