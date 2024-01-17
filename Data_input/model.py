import pyomo.environ as pyomo

class model:
    def __init__(self, model):
        self.model = model

    def run_model(self):
        self.variable()
        self.parameters()
        self.constraints()

    def variable(self):
        self.model.varA = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)
        self.model.varB = pyomo.Var(self.model.Time, bounds=(5, 10), within=pyomo.NonNegativeIntegers)
        self.model.varC = pyomo.Var(self.model.Time, bounds=(1, 5), within=pyomo.NonNegativeIntegers)

    def parameters(self):
        self.model.time_frames = pyomo.Param(self.model.Time, initialize=1)

    def constraints(self):
        def time_constraint(model, t):
            return model.varA[t] == model.varB[t] * model.varC[t]
        self.model.time_constraint = pyomo.Constraint(self.model.Time, rule=time_constraint)