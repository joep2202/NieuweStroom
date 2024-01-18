import pyomo.environ as pyomo

class model:
    def __init__(self, model):
        self.model = model
        self.time_lists_param = {}

    def run_model(self, batterij, time_list_valid):
        self.variable()
        self.parameters(batterij, time_list_valid)
        self.constraints()

    def variable(self):
        self.model.varA = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)
        self.model.varB = pyomo.Var(self.model.Time, bounds=(5, 10), within=pyomo.NonNegativeIntegers)
        self.model.varC = pyomo.Var(self.model.Time, bounds=(1, 5), within=pyomo.NonNegativeIntegers)

    def parameters(self, batterij, time_list_valid):
        print(batterij)
        print(time_list_valid)
        print(len(time_list_valid))
        #self.model.range_options = pyomo.Set(initialize=range(len(self.options_dict[0])))
        #print(batterij)
        #print(time_list_valid)


    def constraints(self):
        def time_constraint(model, t):
            return model.varA[t] == model.varB[t] * model.varC[t]
        self.model.time_constraint = pyomo.Constraint(self.model.Time, rule=time_constraint)

        def try_1(model, t):
            if t == 0:
                return model.varA[t] == 20
            else:
                return model.varA[t] == model.varA[t-1]
        self.model.try_1 = pyomo.Constraint(self.model.Time, rule=try_1)