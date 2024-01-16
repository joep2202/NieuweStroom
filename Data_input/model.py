import pyomo.environ as pyomo

class model:
    def __init__(self, model):
        self.model = model

    def run_model(self):
        self.variable()

    def variable(self):
        self.model.varA = pyomo.Var(self.model.Time, bounds=(0, 10), within=pyomo.NonNegativeIntegers)

    def parameters(self):
        self.model.time_frames = pyomo.Param(self.model.Time, initialize=self.import_price_dict)

    def constraints(self):
        def time_constraint(model, t):
            return model.heat[t] == model.heat_setting[t] + model.buffer_powerCharge[t]
        self.model.time_constraint = pyomo.Constraint(self.model.Time, rule=time_constraint)