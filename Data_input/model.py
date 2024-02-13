import pandas as pd
import pyomo.environ as pyomo
from retrieve_SOC_battery import retrieve_SOC

class model:
    def __init__(self, model, allocation_trading, onbalanskosten, ZWC, temperature, current_interval):
        self.model = model
        self.retrieve_SOC_battery = retrieve_SOC()
        self.time_lists_param = {}
        self.allocation_trading = allocation_trading
        self.ZWC = ZWC
        self.onbalanskosten = onbalanskosten
        self.current_interval = current_interval
        # Get the right data into the variables
        self.epex = self.allocation_trading['EPEX_EurMWh']
        self.temperature_actual = temperature
        self.solar_forecast = self.ZWC['Forecast_solar']
        self.solar_actual = self.ZWC['Allocation_solar']
        self.wind_forecast = self.ZWC['Forecast_wind']
        self.wind_actual = self.ZWC['Allocation_wind']
        self.consumption_forecast = self.ZWC['Forecast_consumption']
        self.consumption_actual = self.ZWC['Allocation_consumption']
        self.trading_volume = self.allocation_trading['Traded_Volume_MWh']
        self.totaal_allocatie = self.allocation_trading['Total_Allocation_MWh_both_tenants']
        # Drop some of the onbalans columns
        columns_to_drop = ['datum', 'PTE', 'periode_van', 'periode_tm', 'indicatie noodvermogen op', 'indicatie noodvermogen af', 'prikkelcomponent']
        self.onbalanskosten = self.onbalanskosten.drop(columns=columns_to_drop)
        self.onbalanskosten = self.onbalanskosten.fillna(0)
        self.regeltoestanden = [1, -1, 0, 2]
        self.total_hour_variable = 0


    def run_model(self, batterij, time_list_valid):
        self.variable(batterij=batterij)
        self.parameters(batterij, time_list_valid)
        self.constraints()

    def variable(self, batterij):
        #Imbalance costs variables
        self.model.imbalance_costs_before_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_after_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_before_flex_total = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_before_flex_epex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_before_flex_comp = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_before_flex_total_comp = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_costs_before_flex_epex_comp = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_afregelen = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_opregelen = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.onvermijdbaar_imbalance = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.onvermijdbaar_imbalance_totaal = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.used_price = pyomo.Var(self.model.Time, within=pyomo.Any)

        #onbalans volumes variables
        self.model.difference_MWh_afregelen = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_opregelen = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_plot = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.Reals)
        self.model.boolean_difference_afregelen = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.boolean_difference_opregelen = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.difference_MWh_afregelen_comp = pyomo.Var(self.model.Time, bounds=(-100, 100),within=pyomo.NonNegativeReals)
        self.model.difference_MWh_opregelen_comp = pyomo.Var(self.model.Time, bounds=(-100, 100),within=pyomo.NonNegativeReals)
        self.model.difference_MWh_plot_comp = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.Reals)
        self.model.boolean_difference_afregelen_comp = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.boolean_difference_opregelen_comp = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.difference_MWh_afregelen_onvermijdbaar = pyomo.Var(self.model.Time, bounds=(-100, 100),within=pyomo.NonNegativeReals)
        self.model.difference_MWh_opregelen_onvermijdbaar = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_plot_onvermijdbaar = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.Reals)
        self.model.boolean_difference_afregelen_onvermijdbaar = pyomo.Var(self.model.Time, within=pyomo.Binary)
        self.model.boolean_difference_opregelen_onvermijdbaar = pyomo.Var(self.model.Time, within=pyomo.Binary)

        #allocatie forecasts and actuals
        self.model.total_forecast = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_forecast_trading = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_forecast_trading_adapted = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_after_flex = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_forecast_hour_v_programma = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_forecast_hour_v_programma_comp = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_forecast_hour_e_programma = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.total_allocation_hour = pyomo.Var(self.model.Time, within=pyomo.Any)

        # Select boolean to select the right imbalance price
        self.model.range_options_onbalans = pyomo.Set(initialize=range(self.onbalanskosten.shape[1]-1))
        self.model.boolean_select_imbalance = pyomo.Var(self.model.Time,self.model.range_options_onbalans, within=pyomo.Binary)

        # Calculate predicted difference variables
        self.model.solar_difference = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.Reals)
        self.model.wind_difference = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.Reals)
        self.model.relevant_difference = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.Reals)

        # Battery variables
        self.model.number_batteries = pyomo.Set(initialize=range(len(batterij)))
        self.model.batterij_SOC = pyomo.Var(self.model.Time,self.model.number_batteries, within=pyomo.Any)
        self.model.batterij_activation_boolean_charge = pyomo.Var(self.model.Time,self.model.number_batteries, within=pyomo.Binary)
        self.model.batterij_activation_boolean_discharge = pyomo.Var(self.model.Time, self.model.number_batteries, within=pyomo.Binary)
        self.model.batterij_energyNotServed = pyomo.Var(self.model.Time, self.model.number_batteries)
        self.model.batterij_energyNotServedFactor = pyomo.Var(self.model.Time, self.model.number_batteries)

    def parameters(self, batterij, time_list_valid):
        self.batterij = batterij
        self.batterij = self.retrieve_SOC_battery.get_SOC_battery(batterij)
        self.time_lists = pd.DataFrame.from_dict(time_list_valid)
        #print(self.batterij.to_string())
        #print(self.time_lists.to_string())

        # Get data from variables into a parameter
        self.epex_price_dict = {}
        for index, value in enumerate(self.epex):
            self.epex_price_dict[index] = value
        self.model.epex_price = pyomo.Param(self.model.Time, initialize=self.epex_price_dict)

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

        self.trading_volume_dict = {}
        for index, value in enumerate(self.trading_volume):
            self.trading_volume_dict[index] = value
        self.model.trading_volume = pyomo.Param(self.model.Time, initialize=self.trading_volume_dict)

        self.totaal_allocatie_dict = {}
        for index, value in enumerate(self.totaal_allocatie):
            self.totaal_allocatie_dict[index] = value
        self.model.totaal_allocatie = pyomo.Param(self.model.Time, initialize=self.totaal_allocatie_dict)

        def time_list_batterij_metopwek(model, i, j):
            return self.time_lists.iloc[j, i]

        def info_batterij_metopwek(model, i, j):
            return self.batterij.iloc[j, i]

        def imbalance_costs(model, i, j):
            return self.onbalanskosten.iloc[i, j]

        #Get all the battery information into parameters
        self.model.range_options_batterij_metopwek = pyomo.Set(initialize=range(self.time_lists.shape[1]))
        self.model.range_options_info_shape_batterij_metopwek = pyomo.Set(initialize=range(self.batterij.shape[1]))
        self.model.time_valid_batterij_metopwek = pyomo.Param(self.model.range_options_batterij_metopwek, self.model.Time, mutable=True, initialize=time_list_batterij_metopwek, within=pyomo.Any)
        self.model.info_batterij_metopwek = pyomo.Param(self.model.range_options_info_shape_batterij_metopwek, self.model.range_options_batterij_metopwek, mutable=True, initialize=info_batterij_metopwek,within=pyomo.Any)

        # Get the imbalance prices into parameters
        self.model.range_options_onbalanskosten = pyomo.Set(initialize=range(self.onbalanskosten.shape[1]))
        self.model.onbalanskosten = pyomo.Param(self.model.Time,self.model.range_options_onbalanskosten, mutable=True, initialize=imbalance_costs, within=pyomo.Any)
        self.model.regeltoestand_options = pyomo.Param(self.model.Time, self.model.range_options_onbalans, mutable=True, initialize={(t,x): self.regeltoestanden[x] for t in self.model.Time for x in self.model.range_options_onbalans}, within=pyomo.Integers)



    def constraints(self):
        #Calculate the total forecasted and the total actual to compare
        def total_assumed(model,t):
            return model.total_forecast[t] == model.solar_forecast[t] + model.wind_forecast[t] + model.consumption_forecast[t]
        self.model.total_assumed = pyomo.Constraint(self.model.Time, rule=total_assumed)

        def total_assumed_hour_V(model,t):
            if t % 4 == 0:
                self.total_hour_variable = t
            return model.total_forecast_hour_v_programma[t] == ((model.total_forecast[0+self.total_hour_variable] + model.total_forecast[1+self.total_hour_variable] + model.total_forecast[2+self.total_hour_variable] + model.total_forecast[3+self.total_hour_variable])/4) + + model.trading_volume[t]
        self.model.total_assumed_hour_V = pyomo.Constraint(self.model.Time, rule=total_assumed_hour_V)

        def total_assumed_hour_E(model, t):
            if t % 4 == 0:
                self.total_hour_variable = t
            return model.total_forecast_hour_e_programma[t] == ((model.total_forecast[0 + self.total_hour_variable] + model.total_forecast[1 + self.total_hour_variable] +model.total_forecast[2 + self.total_hour_variable] + model.total_forecast[3 + self.total_hour_variable]) / 4)
        self.model.total_assumed_hour_E = pyomo.Constraint(self.model.Time, rule=total_assumed_hour_E)


        #Calculate the difference between forecasted total and actual total done seperately to be able to calculate imbalance cost.
        def difference_in_MWh_afregelen(model,t):
            return model.difference_MWh_afregelen[t] == (model.total_forecast_hour_v_programma[t] - model.totaal_allocatie[t]) * model.boolean_difference_afregelen[t]
        self.model.difference_in_MWh_afregelen = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_afregelen)

        def difference_in_MWh_opregelen(model,t):
            return model.difference_MWh_opregelen[t] == (model.totaal_allocatie[t]-model.total_forecast_hour_v_programma[t]) * model.boolean_difference_opregelen[t]
        self.model.difference_in_MWh_opregelen = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_opregelen)

        def difference_in_MWh_boolean(model,t):
            return model.boolean_difference_afregelen[t] + model.boolean_difference_opregelen[t] == 1
        self.model.difference_in_MWh_boolean = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_boolean)

        def difference_in_MWh_plot(model,t):
            return model.difference_MWh_plot[t] ==  model.total_forecast_hour_v_programma[t] - model.totaal_allocatie[t]
        self.model.difference_in_MWh_plot = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_plot)

        def select_onbalans_price(model,t):
            return model.onbalanskosten[t,4] == sum(model.regeltoestand_options[t,x]*model.boolean_select_imbalance[t,x] for x in model.range_options_onbalans)
        self.model.select_onbalans_price = pyomo.Constraint(self.model.Time, rule=select_onbalans_price)

        def select_onbalans_price_boolean(model,t):
            return sum(model.boolean_select_imbalance[t,x] for x in model.range_options_onbalans) == 1
        self.model.select_onbalans_price_boolean = pyomo.Constraint(self.model.Time, rule=select_onbalans_price_boolean)

        def used_pricing(model,t):
            return model.used_price[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+(((model.onbalanskosten[t,0]* model.boolean_difference_opregelen[t])+(model.onbalanskosten[t,1]* model.boolean_difference_afregelen[t]))*model.boolean_select_imbalance[t,3])
        self.model.used_pricing = pyomo.Constraint(self.model.Time, rule=used_pricing)

        # Calculate the imbalance cost per 15 minutes and in total
        def imbalance_cost(model,t):
            return model.imbalance_costs_before_flex[t] == (model.used_price[t]*-model.difference_MWh_plot[t])
        self.model.imbalance_cost = pyomo.Constraint(self.model.Time, rule=imbalance_cost)

        def imbalance_cost_epex(model,t):
            return model.imbalance_costs_before_flex_epex[t] == ((model.epex_price[t]-model.used_price[t])*model.difference_MWh_plot[t])
        self.model.imbalance_cost_epex = pyomo.Constraint(self.model.Time, rule=imbalance_cost_epex)

        def imbalance_costs_total(model,t):
            if t == 0:
                return model.imbalance_costs_before_flex_total[t] == model.imbalance_costs_before_flex_epex[t]
            elif t == self.current_interval:
                return model.imbalance_costs_before_flex_total[t] == model.imbalance_costs_before_flex_epex[t]
            else:
                return model.imbalance_costs_before_flex_total[t] == model.imbalance_costs_before_flex_total[t - 1] + model.imbalance_costs_before_flex_epex[t]
        self.model.imbalance_costs_total = pyomo.Constraint(self.model.Time, rule=imbalance_costs_total)

        # Seperate cost for opregelen and afregelen to show this data for the analysis
        def imbalance_cost_afregelen(model,t):
            return model.imbalance_afregelen[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+((model.onbalanskosten[t,1])*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost_afregelen = pyomo.Constraint(self.model.Time, rule=imbalance_cost_afregelen)

        def imbalance_cost_opregelen(model,t):
            return model.imbalance_opregelen[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+((model.onbalanskosten[t,0])*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost_opregelen = pyomo.Constraint(self.model.Time, rule=imbalance_cost_opregelen)

        def solar_dif(model,t):
            return model.solar_difference[t] == model.solar_actual[t] - model.solar_forecast[t]
        self.model.solar_dif = pyomo.Constraint(self.model.Time, rule=solar_dif)

        def wind_dif(model,t):
            return model.wind_difference[t] == model.wind_actual[t] - model.wind_forecast[t]
        self.model.wind_dif = pyomo.Constraint(self.model.Time, rule=wind_dif)

        def relevant_dif(model,t):
            return model.relevant_difference[t] ==  model.wind_difference[t] + model.solar_difference[t]
        self.model.relevant_dif = pyomo.Constraint(self.model.Time, rule=relevant_dif)

        def battery_SOC(model, t, x):
            if t == 0:
                return model.batterij_SOC[t,x] == model.info_batterij_metopwek[9,x] * model.info_batterij_metopwek[4,x]
            elif t == self.current_interval:
                return model.batterij_SOC[t,x] == model.info_batterij_metopwek[9,x] * model.info_batterij_metopwek[4,x]
            else:
                return model.batterij_SOC[t,x] == model.batterij_SOC[t-1,x] + (model.info_batterij_metopwek[4,x]* model.time_valid_batterij_metopwek[x,t]) * (model.batterij_activation_boolean_charge[t,x]+(-model.batterij_activation_boolean_discharge[t,x]))
        self.model.battery_SOC = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_SOC)

        def battery_SOC_boolean(model, t, x):
            return model.batterij_activation_boolean_charge[t,x]+model.batterij_activation_boolean_discharge[t,x] <= 1
        self.model.battery_SOC_boolean = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_SOC_boolean)

        ##Dit werkt nog niet, want absoluut werkt hier niet, kijken hoe ik dit aanpak
        # def battery_SOC_notservedfactor(model, t, x):
        #     return model.battery_SOC_notservedfactor[t,x] == model.batterij_SOC[t,x]-(model.info_batterij_metopwek[4,x]*model.info_batterij_metopwek[5,x])
        # self.model.battery_SOC_notservedfactor = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_SOC_notservedfactor)

        ##### ANALYSIS PART THIS PART ANALYSES WHAT THE ONVERMIJDBAAR IMBALANCE IS AND WHAT HAPPENS IF WE COMPENSATE BASED ON WEATHER DATA
        ##### ASSUMING THAT THE FORECAST IS VERY CLOSE TO THE ACTUALS

        ##### WEATHER COMPENSATION CALCULATION

        def allocatie_adapted(model,t):
            return model.total_forecast_trading_adapted[t] == model.total_forecast[t] + model.relevant_difference[t]
        self.model.allocatie_adapted = pyomo.Constraint(self.model.Time, rule=allocatie_adapted)

        def total_assumed_hour_V_compensated(model,t):
            if t % 4 == 0:
                self.total_hour_variable = t
            return model.total_forecast_hour_v_programma_comp[t] == ((model.total_forecast_trading_adapted[0+self.total_hour_variable] + model.total_forecast_trading_adapted[1+self.total_hour_variable] + model.total_forecast_trading_adapted[2+self.total_hour_variable] + model.total_forecast_trading_adapted[3+self.total_hour_variable])/4) + model.trading_volume[t]
        self.model.total_assumed_hour_V_compensated = pyomo.Constraint(self.model.Time, rule=total_assumed_hour_V_compensated)

        # Calculate the difference between forecasted total and actual total done seperately to be able to calculate imbalance cost.
        def difference_in_MWh_afregelen_comp(model, t):
            return model.difference_MWh_afregelen_comp[t] == (model.total_forecast_hour_v_programma_comp[t] - model.totaal_allocatie[t]) * model.boolean_difference_afregelen_comp[t]
        self.model.difference_in_MWh_afregelen_comp = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_afregelen_comp)

        def difference_in_MWh_opregelen_comp(model, t):
            return model.difference_MWh_opregelen_comp[t] == (model.totaal_allocatie[t] - model.total_forecast_hour_v_programma_comp[t]) * model.boolean_difference_opregelen_comp[t]
        self.model.difference_in_MWh_opregelen_comp = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_opregelen_comp)

        def difference_in_MWh_boolean_comp(model, t):
            return model.boolean_difference_afregelen_comp[t] + model.boolean_difference_opregelen_comp[t] == 1
        self.model.difference_in_MWh_boolean_comp = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_boolean_comp)

        def difference_in_MWh_plot_comp(model, t):
            return model.difference_MWh_plot_comp[t] == model.total_forecast_hour_v_programma_comp[t] - model.totaal_allocatie[t]
        self.model.difference_in_MWh_plot_comp = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_plot_comp)

        # Calculate the imbalance cost per 15 minutes and in total
        def imbalance_cost_comp(model, t):
            return model.imbalance_costs_before_flex_comp[t] == (model.onbalanskosten[t, 0] * model.boolean_select_imbalance[t, 0] * -model.difference_MWh_plot_comp[t]) + \
                   (model.onbalanskosten[t, 1] * model.boolean_select_imbalance[t, 1] * - model.difference_MWh_plot_comp[t]) + \
                   (((model.onbalanskosten[t, 0] * model.difference_MWh_opregelen_comp[t]) +
                     (model.onbalanskosten[t, 1] * -model.difference_MWh_afregelen_comp[t])) * model.boolean_select_imbalance[t, 3]) + \
                   (model.onbalanskosten[t, 3] * model.boolean_select_imbalance[t, 2] * - model.difference_MWh_plot_comp[t])
                    # +(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2]*((model.difference_MWh_afregelen[t]* model.boolean_difference_afregelen[t])+(model.difference_MWh_opregelen[t]* model.boolean_difference_opregelen[t])))
        self.model.imbalance_cost_comp = pyomo.Constraint(self.model.Time, rule=imbalance_cost_comp)

        def imbalance_cost_epex_comp(model, t):
            return model.imbalance_costs_before_flex_epex_comp[t] == ((model.epex_price[t] - model.onbalanskosten[t, 0]) * model.boolean_select_imbalance[t, 0] * (model.difference_MWh_plot_comp[t])) + \
                   ((model.epex_price[t] - model.onbalanskosten[t, 1]) * model.boolean_select_imbalance[t, 1] * (model.difference_MWh_plot_comp[t])) + \
                   ((model.epex_price[t] - model.onbalanskosten[t, 3]) * model.boolean_select_imbalance[t, 2] * (model.difference_MWh_plot_comp[t])) + \
                   ((((model.epex_price[t] - model.onbalanskosten[t, 0]) * -model.difference_MWh_opregelen_comp[t]) +
                     ((model.epex_price[t] - model.onbalanskosten[t, 1]) *model.difference_MWh_afregelen_comp[t])) * model.boolean_select_imbalance[t, 3])
        self.model.imbalance_cost_epex_comp = pyomo.Constraint(self.model.Time, rule=imbalance_cost_epex_comp)

        def imbalance_costs_total_comp(model, t):
            if t == 0:
                return model.imbalance_costs_before_flex_total_comp[t] == model.imbalance_costs_before_flex_epex_comp[t]
            elif t == self.current_interval:
                return model.imbalance_costs_before_flex_total_comp[t] == model.imbalance_costs_before_flex_epex_comp[t]
            else:
                return model.imbalance_costs_before_flex_total_comp[t] == model.imbalance_costs_before_flex_total_comp[t - 1] + model.imbalance_costs_before_flex_epex_comp[t]
        self.model.imbalance_costs_total_comp = pyomo.Constraint(self.model.Time, rule=imbalance_costs_total_comp)

        ##### ONVERMIJDBAAR ONBALANS CALCULATION

        def total_assumed_hour_allocatie(model,t):
            if t % 4 == 0:
                self.total_hour_variable = t
            return model.total_allocation_hour[t] == ((model.totaal_allocatie[0+self.total_hour_variable] + model.totaal_allocatie[1+self.total_hour_variable] + model.totaal_allocatie[2+self.total_hour_variable] + model.totaal_allocatie[3+self.total_hour_variable])/4)
        self.model.total_assumed_hour_allocatie = pyomo.Constraint(self.model.Time, rule=total_assumed_hour_allocatie)

        # Calculate the difference between forecasted total and actual total done seperately to be able to calculate imbalance cost.
        def difference_in_MWh_afregelen_onvermijdbaar(model, t):
            return model.difference_MWh_afregelen_onvermijdbaar[t] == (model.total_allocation_hour[t] - model.totaal_allocatie[t]) * model.boolean_difference_afregelen_onvermijdbaar[t]
        self.model.difference_in_MWh_afregelen_onvermijdbaar = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_afregelen_onvermijdbaar)

        def difference_in_MWh_opregelen_onvermijdbaar(model, t):
            return model.difference_MWh_opregelen_onvermijdbaar[t] == (model.totaal_allocatie[t] - model.total_allocation_hour[t]) * model.boolean_difference_opregelen_onvermijdbaar[t]
        self.model.difference_in_MWh_opregelen_onvermijdbaar = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_opregelen_onvermijdbaar)

        def difference_in_MWh_boolean_onvermijdbaar(model, t):
            return model.boolean_difference_afregelen_onvermijdbaar[t] + model.boolean_difference_opregelen_onvermijdbaar[t] == 1
        self.model.difference_in_MWh_boolean_onvermijdbaar = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_boolean_onvermijdbaar)

        def difference_in_MWh_plot_onvermijdbaar(model, t):
            return model.difference_MWh_plot_onvermijdbaar[t] == model.total_allocation_hour[t] - model.totaal_allocatie[t]
        self.model.difference_in_MWh_plot_onvermijdbaar = pyomo.Constraint(self.model.Time, rule=difference_in_MWh_plot_onvermijdbaar)

        def imbalance_cost_epex_onvermijdbaar(model, t):
            return model.onvermijdbaar_imbalance[t] == ((model.epex_price[t] - model.onbalanskosten[t, 0]) * model.boolean_select_imbalance[t, 0] * (model.difference_MWh_plot_onvermijdbaar[t])) + \
                   ((model.epex_price[t] - model.onbalanskosten[t, 1]) * model.boolean_select_imbalance[t, 1] * (model.difference_MWh_plot_onvermijdbaar[t])) + \
                   ((model.epex_price[t] - model.onbalanskosten[t, 3]) * model.boolean_select_imbalance[t, 2] * (model.difference_MWh_plot_onvermijdbaar[t])) + \
                   ((((model.epex_price[t] - model.onbalanskosten[t, 0]) * -model.difference_MWh_opregelen_onvermijdbaar[t]) +
                     ((model.epex_price[t] - model.onbalanskosten[t, 1]) *model.difference_MWh_afregelen_onvermijdbaar[t])) * model.boolean_select_imbalance[t, 3])
        self.model.imbalance_cost_epex_onvermijdbaar = pyomo.Constraint(self.model.Time, rule=imbalance_cost_epex_onvermijdbaar)

        def imbalance_costs_total_onvermijdbaar(model, t):
            if t == 0:
                return model.onvermijdbaar_imbalance_totaal[t] == model.onvermijdbaar_imbalance[t]
            elif t == self.current_interval:
                return model.onvermijdbaar_imbalance_totaal[t] == model.onvermijdbaar_imbalance[t]
            else:
                return model.onvermijdbaar_imbalance_totaal[t] == model.onvermijdbaar_imbalance_totaal[t - 1] + model.onvermijdbaar_imbalance[t]
        self.model.imbalance_costs_total_onvermijdbaar = pyomo.Constraint(self.model.Time, rule=imbalance_costs_total_onvermijdbaar)



