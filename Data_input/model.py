import pandas as pd
import pyomo.environ as pyomo

class model:
    def __init__(self, model, data_grid, onbalanskosten):
        self.model = model
        self.time_lists_param = {}
        self.data_grid = data_grid
        self.onbalanskosten = onbalanskosten
        self.epex = self.data_grid['EPEX']
        self.temperature_forecast = self.data_grid['temperature_forecast']
        self.temperature_actual = self.data_grid['temperature_actual']
        self.solar_forecast = self.data_grid['solar_forecast']
        self.solar_actual = self.data_grid['solar_actual']
        self.wind_forecast = self.data_grid['wind_forecast']
        self.wind_actual = self.data_grid['wind_actual']
        self.consumption_forecast = self.data_grid['consumption_forecast']
        self.consumption_actual = self.data_grid['consumption_actual']
        columns_to_drop = ['datum', 'PTE', 'periode_van', 'periode_tm', 'indicatie noodvermogen op', 'indicatie noodvermogen af', 'prikkelcomponent']
        self.onbalanskosten = self.onbalanskosten.drop(columns=columns_to_drop)
        self.onbalanskosten = self.onbalanskosten.fillna(0)
        self.regeltoestanden = [1, -1, 0, 2]
        self.total_hour_variable = 0


    def run_model(self, batterij, time_list_valid):
        self.variable()
        self.parameters(batterij, time_list_valid)
        self.constraints()

    def variable(self):
        self.model.imbalance_costs_before_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_after_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_before_flex_total = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_afregelen = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_opregelen = pyomo.Var(self.model.Time, within=pyomo.Any)

        self.model.difference_MWh = pyomo.Var(self.model.Time, bounds=(-100,100), within=pyomo.Any)
        self.model.difference_MWh_afregelen = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_opregelen = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_plot = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.NonNegativeReals)
        # self.model.difference_MWh_round_to_ten_opregelen = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)
        # self.model.round_to_ten_int = pyomo.Var(self.model.Time, within=pyomo.NonNegativeIntegers)
        # self.model.select_volume_boolean = pyomo.Var(self.model.Time,self.model.range_volumes, within=pyomo.Binary)

        self.model.total_forecast = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_after_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_actual = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_forecast_hour = pyomo.Var(self.model.Time, within=pyomo.Any)

        self.model.boolean_difference_afregelen = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.boolean_difference_opregelen = pyomo.Var(self.model.Time, within=pyomo.Binary)

        self.model.range_options_onbalans = pyomo.Set(initialize=range(self.onbalanskosten.shape[1]-1))
        self.model.boolean_select_imbalance = pyomo.Var(self.model.Time,self.model.range_options_onbalans, within=pyomo.Binary)

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

        def imbalance_costs(model, i, j):
            return self.onbalanskosten.iloc[i, j]

        self.model.range_options_batterij_metopwek = pyomo.Set(initialize=range(self.time_lists.shape[1]))
        #self.model.range_options_info_len_batterij_metopwek = pyomo.Set(initialize=range(len(self.batterij)))
        self.model.range_options_info_shape_batterij_metopwek = pyomo.Set(initialize=range(self.batterij.shape[1]))
        self.model.time_valid_batterij_metopwek = pyomo.Param(self.model.range_options_batterij_metopwek, self.model.Time, mutable=True, initialize=time_list_batterij_metopwek, within=pyomo.Any)
        self.model.info_batterij_metopwek = pyomo.Param(self.model.range_options_info_shape_batterij_metopwek, self.model.range_options_batterij_metopwek, mutable=True, initialize=info_batterij_metopwek,within=pyomo.Any)

        # self.model.range_options_biedprijsladder_volume = pyomo.Set(initialize=range(7))
        # self.model.range_options_biedprijsladder_columns = pyomo.Set(initialize=range(4))
        self.model.range_options_onbalanskosten = pyomo.Set(initialize=range(self.onbalanskosten.shape[1]))
        #print(self.onbalanskosten)
        #model.param_3d = Param(model.i, model.j, model.k,initialize={(i, j, k): biedprijsladder.iloc[7 * (i - 1) + j - 1, k - 1] for i in model.i for j in model.j for k in model.k})
        #self.model.biedprijsladder = pyomo.Param(self.model.Time,  self.model.range_options_biedprijsladder_volume, self.model.range_options_biedprijsladder_columns, mutable=True, initialize={(i, j, k): self.biedprijsladder.iloc[7 * (i) + j, k] for i in self.model.Time for j in self.model.range_options_biedprijsladder_volume for k in self.model.range_options_biedprijsladder_columns}, within=pyomo.Any)
        self.model.onbalanskosten = pyomo.Param(self.model.Time,self.model.range_options_onbalanskosten, mutable=True, initialize=imbalance_costs, within=pyomo.Any)
        self.model.regeltoestand_options = pyomo.Param(self.model.Time, self.model.range_options_onbalans, mutable=True, initialize={(t,x): self.regeltoestanden[x] for t in self.model.Time for x in self.model.range_options_onbalans}, within=pyomo.Integers)



    def constraints(self):
        #Calculate the total forecasted and the total actual to compare
        def total_assumed(model,t):
            return model.total_forecast[t] == model.solar_forecast[t] + model.wind_forecast[t] + model.consumption_forecast[t]
        self.model.total_assumed = pyomo.Constraint(self.model.Time, rule=total_assumed)

        def total_realized(model,t):
            return model.total_actual[t] == model.solar_actual[t] + model.wind_actual[t] + model.consumption_actual[t]
        self.model.total_realized = pyomo.Constraint(self.model.Time, rule=total_realized)

        def total_assumed_hour(model,t):
            if t % 4 == 0:
                self.total_hour_variable = t
            return model.total_forecast_hour[t] == (model.total_forecast[0+self.total_hour_variable] + model.total_forecast[1+self.total_hour_variable] + model.total_forecast[2+self.total_hour_variable] + model.total_forecast[3+self.total_hour_variable])/4
        self.model.total_assumed_hour = pyomo.Constraint(self.model.Time, rule=total_assumed_hour)


        #Calculate the difference between forecasted total and actual total done seperately to be able to calculate imbalance cost.
        def difference_in_MWh_afregelen(model,t):
            return model.difference_MWh_afregelen[t] == (model.total_forecast_hour[t] - model.total_actual[t]) * model.boolean_difference_afregelen[t]
        self.model.difference_in_MWh_afregelen = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_afregelen)

        def difference_in_MWh_opregelen(model,t):
            return model.difference_MWh_opregelen[t] == (model.total_actual[t]-model.total_forecast_hour[t]) * model.boolean_difference_opregelen[t]
        self.model.difference_in_MWh_opregelen = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_opregelen)

        def difference_in_MWh_boolean(model,t):
            return model.boolean_difference_afregelen[t] + model.boolean_difference_opregelen[t] == 1
        self.model.difference_in_MWh_boolean = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_boolean)

        def difference_in_MWh(model,t):
            return model.difference_MWh[t] == model.difference_MWh_afregelen[t] + model.difference_MWh_opregelen[t]
        self.model.difference_in_MWh = pyomo.Constraint(self.model.Time, rule=difference_in_MWh)

        # def difference_in_MWh_plot(model,t):
        #     return model.difference_MWh_plot[t] ==  model.difference_MWh_afregelen[t] + model.difference_MWh_opregelen[t]
        # self.model.difference_in_MWh_plot = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_plot)

        def select_onbalans_price(model,t):
            return model.onbalanskosten[t,4] == sum(model.regeltoestand_options[t,x]*model.boolean_select_imbalance[t,x] for x in model.range_options_onbalans)
        self.model.select_onbalans_price = pyomo.Constraint(self.model.Time, rule=select_onbalans_price)

        def select_onbalans_price_boolean(model,t):
            return sum(model.boolean_select_imbalance[t,x] for x in model.range_options_onbalans) == 1
        self.model.select_onbalans_price_boolean = pyomo.Constraint(self.model.Time, rule=select_onbalans_price_boolean)

        # Calculate the imbalance cost per 15 minutes and in total
        def imbalance_cost(model,t):
            return model.imbalance_costs_before_flex[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0]*model.difference_MWh[t])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1]*model.difference_MWh[t])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2]*model.difference_MWh[t])+(((model.onbalanskosten[t,0]*model.difference_MWh_opregelen[t])+(model.onbalanskosten[t,1]*model.difference_MWh_afregelen[t]))*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost = pyomo.Constraint(self.model.Time, rule=imbalance_cost)

        def imbalance_costs_total(model,t):
            if t == 0:
                return model.imbalance_costs_before_flex_total[t] == model.imbalance_costs_before_flex[t]
            else:
                return model.imbalance_costs_before_flex_total[t] == model.imbalance_costs_before_flex_total[t - 1] + model.imbalance_costs_before_flex[t]
        self.model.imbalance_costs_total = pyomo.Constraint(self.model.Time, rule=imbalance_costs_total)

        # Seperate cost for opregelen and afregelen to show this data for the analysis
        def imbalance_cost_afregelen(model,t):
            return model.imbalance_afregelen[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+((model.onbalanskosten[t,1])*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost_afregelen = pyomo.Constraint(self.model.Time, rule=imbalance_cost_afregelen)

        def imbalance_cost_opregelen(model,t):
            return model.imbalance_opregelen[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+((model.onbalanskosten[t,0])*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost_opregelen = pyomo.Constraint(self.model.Time, rule=imbalance_cost_opregelen)

        #Round up the difference to the nearest 10 to be able to select the right volume
        # def round_to_ten_opregelen(model,t):
        #     return model.difference_MWh_round_to_ten_opregelen[t] == 10 * model.round_to_ten_int[t]
        # self.model.round_to_ten_opregelen = pyomo.Constraint(self.model.Time, rule=round_to_ten_opregelen)
        #
        # def round_to_ten_opregelen_2(model,t):
        #     return model.difference_MWh_round_to_ten_opregelen[t] >= model.difference_MWh_opregelen[t]
        # self.model.round_to_ten_opregelen_2 = pyomo.Constraint(self.model.Time, rule=round_to_ten_opregelen_2)
        #
        # def round_to_ten_opregelen_3(model,t):
        #     return model.difference_MWh_round_to_ten_opregelen[t] <= model.difference_MWh_opregelen[t] + 10
        # self.model.round_to_ten_opregelen_3 = pyomo.Constraint(self.model.Time, rule=round_to_ten_opregelen_3)


        #Select the correct volumes to get the right price form the biedprijsladder as the ladder is in 10/20/30 etc.
        # def select_correct_volume(model,t):
        #     return model.difference_MWh_round_to_ten_opregelen[t] == sum(model.biedprijsladder[t,x,1] * model.select_volume_boolean[t,x] for x in self.model.range_options_biedprijsladder_volume)
        # self.model.select_correct_volume = pyomo.Constraint(self.model.Time, rule=select_correct_volume)
        #
        # def select_volume_booleans(model,t):
        #     return sum(model.select_volume_boolean[t, x] for x in self.model.range_options_biedprijsladder_volume) == 1
        # self.model.select_volume_booleans = pyomo.Constraint(self.model.Time, rule=select_volume_booleans)





