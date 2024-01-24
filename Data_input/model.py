import pandas as pd
import pyomo.environ as pyomo

class model:
    def __init__(self, model):
        self.model = model
        self.time_lists_param = {}
        self.data_grid = pd.read_csv('data/ExtData.csv', index_col=0)
        self.epex = self.data_grid['EPEX']
        self.temperature_forecast = self.data_grid['temperature_forecast']
        self.temperature_actual = self.data_grid['temperature_actual']
        self.solar_forecast = self.data_grid['solar_forecast']
        self.solar_actual = self.data_grid['solar_actual']
        self.wind_forecast = self.data_grid['wind_forecast']
        self.wind_actual = self.data_grid['wind_actual']
        self.consumption_forecast = self.data_grid['consumption_forecast']
        self.consumption_actual = self.data_grid['consumption_actual']
        self.biedprijsladder = pd.read_csv('data/biedprijsladder.csv')
        self.columns_to_drop = ['Datum', 'Start', 'Einde']
        self.biedprijsladder = self.biedprijsladder[self.biedprijsladder['Volume'] <= 70]
        self.biedprijsladder = self.biedprijsladder.drop(columns=self.columns_to_drop)
        self.biedprijsladder = self.biedprijsladder.reset_index(drop=True)


    def run_model(self, batterij, time_list_valid):
        self.variable()
        self.parameters(batterij, time_list_valid)
        self.constraints()

    def variable(self):
        self.model.imbalance_costs_before_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_after_flex = pyomo.Var(self.model.Time, within=pyomo.Any)

        self.model.difference_MWh = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.difference_MWh_afregelen = pyomo.Var(self.model.Time, within=pyomo.NonNegativeReals)
        self.model.difference_MWh_opregelen = pyomo.Var(self.model.Time, within=pyomo.NonNegativeReals)
        self.model.difference_MWh_round_to_ten_opregelen = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)
        self.model.try_boolean = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)

        self.model.total_forecast = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_after_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_actual = pyomo.Var(self.model.Time, within=pyomo.Any)

        self.model.boolean_difference_afregelen = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.boolean_difference_opregelen = pyomo.Var(self.model.Time, within=pyomo.Binary)

    def parameters(self, batterij, time_list_valid):
        self.batterij = batterij
        self.time_lists = pd.DataFrame.from_dict(time_list_valid)
        #print(batterij)

        self.epex_price_dict = {}
        for index, value in enumerate(self.epex):
            self.epex_price_dict[index] = value
        self.model.epex_price = pyomo.Param(self.model.Time, initialize=self.epex_price_dict)

        # import the outside temperature
        self.temp_forecast_dict = {}
        for index, value in enumerate(self.temperature_forecast):
            self.temp_forecast_dict[index] = value
        self.model.temp_forecast = pyomo.Param(self.model.Time, initialize=self.temp_forecast_dict)

        self.temp_actual_dict = {}
        for index, value in enumerate(self.temperature_actual):
            self.temp_actual_dict[index] = value
        self.model.temp_actual = pyomo.Param(self.model.Time, initialize=self.temp_actual_dict)

        self.solar_forecast_dict = {}
        for index, value in enumerate(self.solar_forecast):
            self.solar_forecast_dict[index] = value
        self.model.solar_forecast = pyomo.Param(self.model.Time, initialize=self.solar_forecast_dict)

        self.solar_actual_dict = {}
        for index, value in enumerate(self.solar_actual):
            self.solar_actual_dict[index] = value
        self.model.solar_actual = pyomo.Param(self.model.Time, initialize=self.solar_actual_dict)

        self.wind_forecast_dict = {}
        for index, value in enumerate(self.wind_forecast):
            self.wind_forecast_dict[index] = value
        self.model.wind_forecast = pyomo.Param(self.model.Time, initialize=self.wind_forecast_dict)

        self.wind_actual_dict = {}
        for index, value in enumerate(self.wind_actual):
            self.wind_actual_dict[index] = value
        self.model.wind_actual = pyomo.Param(self.model.Time, initialize=self.wind_actual_dict)

        self.consumption_forecast_dict = {}
        for index, value in enumerate(self.consumption_forecast):
            self.consumption_forecast_dict[index] = value
        self.model.consumption_forecast = pyomo.Param(self.model.Time, initialize=self.consumption_forecast_dict)

        self.consumption_actual_dict = {}
        for index, value in enumerate(self.consumption_actual):
            self.consumption_actual_dict[index] = value
        self.model.consumption_actual = pyomo.Param(self.model.Time, initialize=self.consumption_actual_dict)

        def time_list_batterij_metopwek(model, i, j):
            return self.time_lists.iloc[j, i]

        def info_batterij_metopwek(model, i, j):
            return self.batterij.iloc[j, i]

        # def biedprijsladder(model, i, j):
        #     return self.biedprijsladder.iloc[j, i]

        self.model.range_options_batterij_metopwek = pyomo.Set(initialize=range(self.time_lists.shape[1]))
        #self.model.range_options_info_len_batterij_metopwek = pyomo.Set(initialize=range(len(self.batterij)))
        self.model.range_options_info_shape_batterij_metopwek = pyomo.Set(initialize=range(self.batterij.shape[1]))
        self.model.time_valid_batterij_metopwek = pyomo.Param(self.model.range_options_batterij_metopwek, self.model.Time, mutable=True, initialize=time_list_batterij_metopwek, within=pyomo.Any)
        self.model.info_batterij_metopwek = pyomo.Param(self.model.range_options_info_shape_batterij_metopwek, self.model.range_options_batterij_metopwek, mutable=True, initialize=info_batterij_metopwek,within=pyomo.Any)

        self.model.range_options_biedprijsladder_1 = pyomo.Set(initialize=range(7))
        self.model.range_options_biedprijsladder_2 = pyomo.Set(initialize=range(4))
        #print(self.biedprijsladder)
        #model.param_3d = Param(model.i, model.j, model.k,initialize={(i, j, k): biedprijsladder.iloc[7 * (i - 1) + j - 1, k - 1] for i in model.i for j in model.j for k in model.k})
        self.model.biedprijsladder = pyomo.Param(self.model.Time,  self.model.range_options_biedprijsladder_1, self.model.range_options_biedprijsladder_2, mutable=True, initialize={(i, j, k): self.biedprijsladder.iloc[7 * (i) + j, k] for i in self.model.Time for j in self.model.range_options_biedprijsladder_1 for k in self.model.range_options_biedprijsladder_2}, within=pyomo.Any)


    def constraints(self):
        def total_assumed(model,t):
            return model.total_forecast[t] == model.solar_forecast[t] + model.wind_forecast[t] + model.consumption_forecast[t]
        self.model.total_assumed = pyomo.Constraint(self.model.Time, rule=total_assumed)

        def total_realized(model,t):
            return model.total_actual[t] == model.solar_actual[t] + model.wind_actual[t] + model.consumption_actual[t]
        self.model.total_realized = pyomo.Constraint(self.model.Time, rule=total_realized)

        def difference_in_MWh_afregelen(model,t):
            return model.difference_MWh_afregelen[t] == (model.total_forecast[t] - model.total_actual[t]) * model.boolean_difference_afregelen[t]
        self.model.difference_in_MWh_afregelen = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_afregelen)

        def difference_in_MWh_opregelen(model,t):
            return model.difference_MWh_opregelen[t] == (model.total_actual[t]-model.total_forecast[t]) * model.boolean_difference_opregelen[t]
        self.model.difference_in_MWh_opregelen = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_opregelen)

        def difference_in_MWh_boolean(model,t):
            return  model.boolean_difference_afregelen[t] + model.boolean_difference_opregelen[t] == 1
        self.model.difference_in_MWh_boolean = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_boolean)

        def difference_in_MWh(model,t):
            return model.difference_MWh[t] == model.difference_MWh_afregelen[t] + model.difference_MWh_opregelen[t]
        self.model.difference_in_MWh = pyomo.Constraint(self.model.Time, rule=difference_in_MWh)

        def round_to_ten_opregelen(model,t):
            return model.difference_MWh_round_to_ten_opregelen[t] == 10*model.try_boolean[t]
        self.model.round_to_ten_opregelen = pyomo.Constraint(self.model.Time, rule=round_to_ten_opregelen)

        def round_to_ten_opregelen_2(model,t):
            return model.difference_MWh_round_to_ten_opregelen[t] >= model.difference_MWh_opregelen[t]
        self.model.round_to_ten_opregelen_2 = pyomo.Constraint(self.model.Time, rule=round_to_ten_opregelen_2)

        def round_to_ten_opregelen_3(model,t):
            return model.difference_MWh_round_to_ten_opregelen[t] <= model.difference_MWh_opregelen[t] + 10
        self.model.round_to_ten_opregelen_3 = pyomo.Constraint(self.model.Time, rule=round_to_ten_opregelen_3)



        def imbalance_cost(model,t):
            return model.imbalance_costs_before_flex[t] == (model.difference_MWh_opregelen[t] * model.biedprijsladder[t,0,3]) + (model.difference_MWh_afregelen[t] * model.biedprijsladder[t,0,2])
        self.model.imbalance_cost = pyomo.Constraint(self.model.Time, rule=imbalance_cost)