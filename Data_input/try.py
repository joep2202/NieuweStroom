from pyomo.environ import ConcreteModel, Param, RangeSet, Var, Objective, Constraint, SolverFactory
import pandas as pd

# Create a concrete Pyomo model
model = ConcreteModel()
biedprijsladder = pd.read_csv('data/biedprijsladder.csv')
columns_to_drop = ['Datum', 'Start', 'Einde']
biedprijsladder = biedprijsladder[biedprijsladder['Volume'] <= 70]
biedprijsladder = biedprijsladder.drop(columns=columns_to_drop)
biedprijsladder = biedprijsladder.reset_index(drop=True)
biedprijsladders = {}
print(biedprijsladder)
for x in range(96):
     biedprijsladders[x] = biedprijsladder[biedprijsladder['ISP'] == x]
     biedprijsladders[x] = biedprijsladders[x].reset_index()

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
