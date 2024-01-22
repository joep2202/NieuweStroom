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


    def run_model(self, batterij, time_list_valid):
        self.variable()
        self.parameters(batterij, time_list_valid)
        self.constraints()

    def variable(self):
        self.model.varA = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)
        self.model.varB = pyomo.Var(self.model.Time, bounds=(5, 10), within=pyomo.NonNegativeIntegers)
        self.model.varC = pyomo.Var(self.model.Time, bounds=(1, 5), within=pyomo.NonNegativeIntegers)

    def parameters(self, batterij, time_list_valid):
        self.batterij = batterij
        self.time_lists = pd.DataFrame.from_dict(time_list_valid)
        print(batterij)

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

        self.model.range_options_batterij_metopwek = pyomo.Set(initialize=range(self.time_lists.shape[1]))
        #self.model.range_options_info_len_batterij_metopwek = pyomo.Set(initialize=range(len(self.batterij)))
        self.model.range_options_info_shape_batterij_metopwek = pyomo.Set(initialize=range(self.batterij.shape[1]))
        self.model.time_valid_batterij_metopwek = pyomo.Param(self.model.range_options_batterij_metopwek, self.model.Time, mutable=True, initialize=time_list_batterij_metopwek, within=pyomo.Any)
        self.model.info_batterij_metopwek = pyomo.Param(self.model.range_options_info_shape_batterij_metopwek, self.model.range_options_batterij_metopwek, mutable=True, initialize=info_batterij_metopwek,within=pyomo.Any)


    def constraints(self):
        def time_constraint(model, t):
            return model.varA[t] == sum(model.time_valid_batterij_metopwek[x, t] * model.varB[t] for x in self.model.range_options_batterij_metopwek)
        self.model.time_constraint = pyomo.Constraint(self.model.Time, rule=time_constraint)
