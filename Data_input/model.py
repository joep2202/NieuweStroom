import pandas as pd
import pyomo.environ as pyomo

class model:
    def __init__(self, model, allocation_trading, onbalanskosten, ZWC, temperature, current_interval, DA_bid):
        self.model = model
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
        # In een forecaster wordt totaal_allocatie vervangen door de verwachte positie
        self.totaal_allocatie = self.allocation_trading['Total_Allocation_MWh_both_tenants']
        self.DA_bid = DA_bid['Abs_E_Volume_MWh_both_tenants']
        # Drop some of the onbalans columns
        columns_to_drop = ['datum', 'PTE', 'periode_van', 'periode_tm', 'indicatie noodvermogen op', 'indicatie noodvermogen af', 'prikkelcomponent']
        self.onbalanskosten = self.onbalanskosten.drop(columns=columns_to_drop)
        self.onbalanskosten = self.onbalanskosten.fillna(0)
        self.regeltoestanden = [1, -1, 0, 2]
        self.total_hour_variable = 0
        self.bigM = 1000
        # If you are running rolling you should save the last total imbalance and then enter them into the variables below
        self.last_total_imbalance = 0
        self.last_total_imbalance_after_flex = 0
        self.last_total_imbalance_onvermijdbaar = 0


    def run_model(self, batterij, time_list_valid, keys):
        self.batterij = batterij
        self.time_list_valid = time_list_valid
        self.keys = keys
        self.time_list_valid = {key: self.time_list_valid[key] for key in self.keys}
        print(self.time_list_valid)
        self.variable(batterij=self.batterij)
        self.parameters(batterij=self.batterij, time_list_valid=self.time_list_valid)
        self.constraints()

    def variable(self, batterij):
        self.batterij = batterij

        #imbalance prices
        self.model.imbalance_afregelen = pyomo.Var(self.model.Time, within=pyomo.Any)
        self.model.imbalance_opregelen = pyomo.Var(self.model.Time, within=pyomo.Any)

        # Select boolean to select the right imbalance price
        self.model.range_options_onbalans = pyomo.Set(initialize=range(self.onbalanskosten.shape[1] - 1))
        self.model.boolean_select_imbalance = pyomo.Var(self.model.Time, self.model.range_options_onbalans,within=pyomo.Binary)

        # #allocatie forecasts and actuals
        self.model.total_forecast = pyomo.Var(self.model.Time, within=pyomo.Any)


        # #0 is DA_bid (E) #1 is V_program #2 onvermijdbaar #3 weather
        self.model.number_measured = pyomo.Set(initialize=range(4))
        self.model.number_of_allocations = pyomo.Set(initialize=range(2))
        self.model.measured_line = pyomo.Var(self.model.Time, self.model.number_measured, within=pyomo.Any)
        self.model.measured_line_hour = pyomo.Var(self.model.Time, self.model.number_measured, within=pyomo.Any)
        self.model.imbalance_costs = pyomo.Var(self.model.Time,self.model.number_measured,self.model.number_of_allocations, within=pyomo.Any)
        self.model.imbalance_costs_epex = pyomo.Var(self.model.Time, self.model.number_measured,self.model.number_of_allocations, within=pyomo.Any)
        self.model.imbalance_costs_total = pyomo.Var(self.model.Time, self.model.number_measured,self.model.number_of_allocations, within=pyomo.Any)
        self.model.used_price_x = pyomo.Var(self.model.Time,self.model.number_measured,self.model.number_of_allocations, within=pyomo.Any)
        self.model.difference_MWh_afregelen_x = pyomo.Var(self.model.Time,self.model.number_measured,self.model.number_of_allocations,bounds=(-100,100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_opregelen_x = pyomo.Var(self.model.Time,self.model.number_measured,self.model.number_of_allocations,bounds=(-100,100), within=pyomo.NonNegativeReals)
        self.model.difference_MWh_plot_x = pyomo.Var(self.model.Time,self.model.number_measured,self.model.number_of_allocations,bounds=(-100,100), within=pyomo.Reals)
        self.model.boolean_difference_afregelen_x = pyomo.Var(self.model.Time,self.model.number_measured, self.model.number_of_allocations,within=pyomo.Binary)
        self.model.boolean_difference_opregelen_x = pyomo.Var(self.model.Time,self.model.number_measured, self.model.number_of_allocations,within=pyomo.Binary)
        self.model.totaal_allocatie_x = pyomo.Var(self.model.Time, self.model.number_of_allocations, within=pyomo.Any)

        # Calculate predicted difference variables
        self.model.solar_difference = pyomo.Var(self.model.Time,bounds=(-100,100), within=pyomo.Reals)
        self.model.wind_difference = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.Reals)
        self.model.relevant_difference = pyomo.Var(self.model.Time, bounds=(-100, 100), within=pyomo.Reals)

        # Battery variables
        self.model.number_batteries = pyomo.Set(initialize=range(len(self.batterij)))
        self.model.batterij_SOC = pyomo.Var(self.model.Time,self.model.number_batteries, within=pyomo.Any)

        # Charge/discharge variables
        self.model.batterij_powerCharge = pyomo.Var(self.model.Time, self.model.number_batteries, within=pyomo.NonNegativeReals)
        self.model.batterij_powerDischarge = pyomo.Var(self.model.Time, self.model.number_batteries, within=pyomo.NonPositiveReals)
        self.model.batterij_powerCharge_final = pyomo.Var(self.model.Time, self.model.number_batteries,within=pyomo.NonNegativeReals)
        self.model.batterij_powerDischarge_final = pyomo.Var(self.model.Time, self.model.number_batteries,within=pyomo.NonPositiveReals)
        self.model.batterij_powerCharge_to_grid = pyomo.Var(self.model.Time, self.model.number_batteries,within=pyomo.NonNegativeReals)
        self.model.batterij_powerDischarge_to_grid = pyomo.Var(self.model.Time, self.model.number_batteries,within=pyomo.NonPositiveReals)
        self.model.batterij_boolChar = pyomo.Var(self.model.Time, self.model.number_batteries, within=pyomo.Binary)
        self.model.batterij_boolDis = pyomo.Var(self.model.Time, self.model.number_batteries, within=pyomo.Binary)

        # variables to assure the  batteries end in the desired state
        self.model.number_timeslots = pyomo.Set(initialize=range(2))
        self.model.batterij_energyNotServedFactor = pyomo.Var(self.model.Time, self.model.number_batteries,self.model.number_timeslots)
        self.model.batterij_energyNotServedFactor_below = pyomo.Var(self.model.Time, self.model.number_batteries,self.model.number_timeslots, bounds=(0,1000), within=pyomo.NonNegativeReals)
        self.model.batterij_energyNotServedFactor_higher = pyomo.Var(self.model.Time, self.model.number_batteries,self.model.number_timeslots, bounds=(0,1000), within=pyomo.NonNegativeReals)
        self.model.batterij_energyNotServedFactor_below_boolean = pyomo.Var(self.model.Time, self.model.number_batteries, self.model.number_timeslots, within=pyomo.Binary)
        self.model.batterij_energyNotServedFactor_higher_boolean = pyomo.Var(self.model.Time, self.model.number_batteries, self.model.number_timeslots, within=pyomo.Binary)




    def parameters(self, batterij, time_list_valid):
        self.batterij = batterij
        self.time_lists = pd.DataFrame.from_dict(time_list_valid)
        self.time_lists_copy = self.time_lists.T
        self.time_lists_copy.reset_index(inplace=True, drop=True)

        # Get data from variables into a parameter
        self.epex_price_dict = {}
        for index, value in self.epex.items():
            self.epex_price_dict[index] = value
        self.model.epex_price = pyomo.Param(self.model.Time, initialize=self.epex_price_dict)

        self.temp_actual_dict = {}
        for index, value in self.temperature_actual.items():
            #print(index, value)
            self.temp_actual_dict[index] = value
        self.model.temp_actual = pyomo.Param(self.model.Time, initialize=self.temp_actual_dict)

        self.solar_forecast_dict = {}
        for index, value in self.solar_forecast.items():
            self.solar_forecast_dict[index] = value
        self.model.solar_forecast = pyomo.Param(self.model.Time, initialize=self.solar_forecast_dict)

        self.solar_actual_dict = {}
        for index, value in self.solar_actual.items():
            self.solar_actual_dict[index] = value
        self.model.solar_actual = pyomo.Param(self.model.Time, initialize=self.solar_actual_dict)

        self.wind_forecast_dict = {}
        for index, value in self.wind_forecast.items():
            self.wind_forecast_dict[index] = value
        self.model.wind_forecast = pyomo.Param(self.model.Time, initialize=self.wind_forecast_dict)

        self.wind_actual_dict = {}
        for index, value in self.wind_actual.items():
            self.wind_actual_dict[index] = value
        self.model.wind_actual = pyomo.Param(self.model.Time, initialize=self.wind_actual_dict)

        self.consumption_forecast_dict = {}
        for index, value in self.consumption_forecast.items():
            self.consumption_forecast_dict[index] = value
        self.model.consumption_forecast = pyomo.Param(self.model.Time, initialize=self.consumption_forecast_dict)

        self.consumption_actual_dict = {}
        for index, value in self.consumption_actual.items():
            self.consumption_actual_dict[index] = value
        self.model.consumption_actual = pyomo.Param(self.model.Time, initialize=self.consumption_actual_dict)

        self.trading_volume_dict = {}
        for index, value in self.trading_volume.items():
            self.trading_volume_dict[index] = value
        self.model.trading_volume = pyomo.Param(self.model.Time, initialize=self.trading_volume_dict)

        self.totaal_allocatie_dict = {}
        for index, value in self.totaal_allocatie.items():
            self.totaal_allocatie_dict[index] = value
        self.model.totaal_allocatie = pyomo.Param(self.model.Time, initialize=self.totaal_allocatie_dict)

        self.DA_bid_dict = {}
        for index, value in self.DA_bid.items():
            self.DA_bid_dict[index] = value
        self.model.E_program = pyomo.Param(self.model.Time, initialize=self.DA_bid_dict)

        def time_list_batterij_metopwek(model, i, j):
            return self.time_lists_copy.iloc[j, i]

        def info_batterij_metopwek(model, i, j):
            return self.batterij.iloc[j, i]

        def imbalance_costs(model, i, j):
            return self.onbalanskosten.iloc[i, j]

        #Get all the battery information into parameters
        self.model.range_options_batterij_time_list = pyomo.Set(initialize=range(self.time_lists.shape[1]))
        self.model.range_options_batterij = pyomo.Set(initialize=range(self.batterij.shape[0]))
        self.model.range_options_info_shape_batterij = pyomo.Set(initialize=range(self.batterij.shape[1]))
        self.model.info_batterij = pyomo.Param(self.model.range_options_info_shape_batterij, self.model.range_options_batterij, mutable=False, initialize=info_batterij_metopwek,within=pyomo.Any)
        self.model.time_valid_batterij = pyomo.Param(self.model.Time, self.model.range_options_batterij_time_list,mutable=True, initialize=time_list_batterij_metopwek, within=pyomo.Any)

        # Get the imbalance prices into parameters
        self.model.range_options_onbalanskosten = pyomo.Set(initialize=range(self.onbalanskosten.shape[1]))
        self.model.onbalanskosten = pyomo.Param(self.model.Time,self.model.range_options_onbalanskosten, mutable=True, initialize=imbalance_costs, within=pyomo.Any)
        self.model.regeltoestand_options = pyomo.Param(self.model.Time, self.model.range_options_onbalans, mutable=True, initialize={(t,x): self.regeltoestanden[x] for t in self.model.Time for x in self.model.range_options_onbalans}, within=pyomo.Integers)

        # Battery parameters (
        self.model.batterij_DoD = pyomo.Param(initialize = 0.1)
        self.model.batterij_efficiency = pyomo.Param(initialize = 0.9)


    def constraints(self):
        #Calculate the total forecasted and the total actual to compare
        def total_assumed(model,t):
            return model.total_forecast[t] == model.solar_forecast[t] + model.wind_forecast[t] + model.consumption_forecast[t]
        self.model.total_assumed = pyomo.Constraint(self.model.Time, rule=total_assumed)

        # Seperate cost for opregelen and afregelen to show this data for the analysis
        def imbalance_cost_afregelen(model,t):
            return model.imbalance_afregelen[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+((model.onbalanskosten[t,1])*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost_afregelen = pyomo.Constraint(self.model.Time, rule=imbalance_cost_afregelen)

        def imbalance_cost_opregelen(model,t):
            return model.imbalance_opregelen[t] == (model.onbalanskosten[t,0]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,1]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+((model.onbalanskosten[t,0])*model.boolean_select_imbalance[t,3])
        self.model.imbalance_cost_opregelen = pyomo.Constraint(self.model.Time, rule=imbalance_cost_opregelen)

        ## Battery constraints
        def battery_SOC(model, t, x):
            if t == 0:
                return model.batterij_SOC[t,x] == model.info_batterij[13,x] * model.info_batterij[4,x]
            elif t == self.current_interval:
                return model.batterij_SOC[t,x] == model.info_batterij[13,x] * model.info_batterij[4,x]
            else:
                return model.batterij_SOC[t,x] == model.batterij_SOC[t-1,x] + ((model.batterij_powerCharge_final[t,x] + model.batterij_powerDischarge_final[t,x])/4)
        self.model.battery_SOC = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_SOC)

        # Only charge/discharge if the time slots allow it
        def battery_charge_if_valid(model, t, x):
            return model.batterij_powerCharge_final[t,x] == ((model.batterij_powerCharge[t,x]/4)*model.batterij_efficiency)*model.time_valid_batterij[t,x]
        self.model.battery_charge_if_valid = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_charge_if_valid)

        def battery_discharge_if_valid(model, t, x):
            return model.batterij_powerDischarge_final[t,x] == ((model.batterij_powerDischarge[t,x]/4))*model.time_valid_batterij[t,x]
        self.model.battery_discharge_if_valid = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_discharge_if_valid)

        # If batteries are charged this is a discharge from the grid and reversed also go from kW to MWh
        def battery_charge_to_grid(model, t, x):
            return model.batterij_powerCharge_to_grid[t,x] == ((model.batterij_powerCharge[t,x]/4)/100) *model.time_valid_batterij[t,x]
        self.model.battery_charge_to_grid = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_charge_to_grid)

        def battery_discharge_to_grid(model, t, x):
            return model.batterij_powerDischarge_to_grid[t,x] == (((model.batterij_powerDischarge[t,x]/4)*model.batterij_efficiency)/100) *model.time_valid_batterij[t,x]
        self.model.battery_discharge_to_grid = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_discharge_to_grid)

        # To prevent charging and discharging simultaneously
        # http://www.eseslab.com/posts/blogPost_batt_schedule_optimal
        def BatteryBigMRule1(model, t,x):
            bigM=self.bigM
            return(model.batterij_powerCharge[t,x] <= bigM * (1-model.batterij_boolDis[t,x]))
        self.model.BatteryBigMRule1 = pyomo.Constraint(self.model.Time,self.model.number_batteries, rule=BatteryBigMRule1)

        def BatteryBigMRule2(model, t,x):
            bigM=self.bigM
            return(model.batterij_powerCharge[t,x] >= -bigM * model.batterij_boolChar[t,x])
        self.model.BatteryBigMRule2 = pyomo.Constraint(self.model.Time,self.model.number_batteries, rule=BatteryBigMRule2)

        def BatteryBigMRule3(model, t,x):
            bigM=self.bigM
            return(model.batterij_powerDischarge[t,x] >= -bigM * model.batterij_boolDis[t,x])
        self.model.BatteryBigMRule3 = pyomo.Constraint(self.model.Time,self.model.number_batteries, rule=BatteryBigMRule3)

        def BatteryBigMRule4(model, t,x):
            bigM=self.bigM
            return(model.batterij_powerDischarge[t,x] <= bigM * (1-model.batterij_boolChar[t,x]))
        self.model.BatteryBigMRule4 = pyomo.Constraint(self.model.Time,self.model.number_batteries, rule=BatteryBigMRule4)

        def BatteryBigMRule5(model, t,x):
            return(model.batterij_boolChar[t,x] + model.batterij_boolDis[t,x] == 1)
        self.model.BatteryBigMRule5 = pyomo.Constraint(self.model.Time,self.model.number_batteries, rule=BatteryBigMRule5)

        ## limit charging and discharging
        def battery_charge_max(model, t, x):
            return model.batterij_powerCharge[t,x] <= model.info_batterij[3,x]
        self.model.battery_charge_max = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_charge_max)

        def battery_charge_min(model, t, x):
            return model.batterij_powerCharge[t,x] >= 0
        self.model.battery_charge_min = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_charge_min)

        def battery_discharge_max(model, t, x):
            return model.batterij_powerDischarge[t,x] >= -model.info_batterij[3,x]
        self.model.battery_discharge_max = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_discharge_max)

        def battery_discharge_min(model, t, x):
            return model.batterij_powerDischarge[t,x] <= 0
        self.model.battery_discharge_min = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_discharge_min)


        ## Make sure that the DoD are adheres
        def battery_SOC_max(model, t, x):
            return model.batterij_SOC[t,x] <= (1-model.batterij_DoD)*model.info_batterij[4,x]
        self.model.battery_SOC_max = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_SOC_max)

        def battery_SOC_min(model, t, x):
            return model.batterij_SOC[t,x] >= model.batterij_DoD* model.info_batterij[4,x]
        self.model.battery_SOC_min = pyomo.Constraint(self.model.Time, self.model.number_batteries, rule=battery_SOC_min)

        ## assure it adheres the moment it needs to be at the final SOC to not limit users
        def battery_SOC_notservedfactor_high(model, t, x, z):
            return model.batterij_energyNotServedFactor_higher[t,x,z] == ((model.batterij_SOC[t,x]-(model.info_batterij[4,x]*model.info_batterij[5+(z*3),x])) * model.batterij_energyNotServedFactor_higher_boolean[t,x,z])
        self.model.battery_SOC_notservedfactor_high = pyomo.Constraint(self.model.Time, self.model.number_batteries,self.model.number_timeslots, rule=battery_SOC_notservedfactor_high)

        def battery_SOC_notservedfactor_low(model, t, x, z):
            return model.batterij_energyNotServedFactor_below[t,x,z] == (((model.info_batterij[4,x]*model.info_batterij[5+(z*3),x])-model.batterij_SOC[t,x]) * model.batterij_energyNotServedFactor_below_boolean[t,x,z])
        self.model.battery_SOC_notservedfactor_low = pyomo.Constraint(self.model.Time, self.model.number_batteries,self.model.number_timeslots, rule=battery_SOC_notservedfactor_low)

        def battery_SOC_notservedfactor(model, t, x,z):
            return model.batterij_energyNotServedFactor[t,x,z] == model.batterij_energyNotServedFactor_higher[t,x,z] + model.batterij_energyNotServedFactor_below[t,x,z]
        self.model.battery_SOC_notservedfactor = pyomo.Constraint(self.model.Time, self.model.number_batteries,self.model.number_timeslots, rule=battery_SOC_notservedfactor)

        def battery_SOC_notservedfactor_bol(model, t, x, z):
            return model.batterij_energyNotServedFactor_below_boolean[t,x,z] + model.batterij_energyNotServedFactor_higher_boolean[t,x,z] == 1
        self.model.battery_SOC_notservedfactor_bol = pyomo.Constraint(self.model.Time, self.model.number_batteries,self.model.number_timeslots, rule=battery_SOC_notservedfactor_bol)

         ## Calculate the difference between forecast and reality
        def solar_dif(model,t):
            return model.solar_difference[t] == model.solar_actual[t] - model.solar_forecast[t]
        self.model.solar_dif = pyomo.Constraint(self.model.Time, rule=solar_dif)

        def wind_dif(model,t):
            return model.wind_difference[t] == model.wind_actual[t] - model.wind_forecast[t]
        self.model.wind_dif = pyomo.Constraint(self.model.Time, rule=wind_dif)

        def relevant_dif(model,t):
            return model.relevant_difference[t] == model.wind_difference[t] + model.solar_difference[t]
        self.model.relevant_dif = pyomo.Constraint(self.model.Time, rule=relevant_dif)

        ## Imbalance calculations
        def measured_line_0(model, t):
            return model.measured_line[t, 0] == model.E_program[t]
        self.model.measured_line_0 = pyomo.Constraint(self.model.Time, rule=measured_line_0)

        def measured_line_1(model, t):
            return model.measured_line[t, 1] == model.E_program[t] + model.trading_volume[t]
        self.model.measured_line_1 = pyomo.Constraint(self.model.Time, rule=measured_line_1)

        def measured_line_2(model, t):
            return model.measured_line[t, 2] == model.totaal_allocatie[t]
        self.model.measured_line_2 = pyomo.Constraint(self.model.Time, rule=measured_line_2)

        def measured_line_3(model, t):
            return model.measured_line[t, 3] == model.total_forecast[t] + model.relevant_difference[t]
        self.model.measured_line_3 = pyomo.Constraint(self.model.Time, rule=measured_line_3)
        #
        def total_assumed_hour(model,t,y):
            if t == 0:
                self.total_hour_variable = t
            elif t == self.current_interval:
                self.total_hour_variable = self.current_interval
            elif t % 4 == 0:
                self.total_hour_variable = t
            return model.measured_line_hour[t,y] == ((model.measured_line[0+self.total_hour_variable, y] + model.measured_line[1+self.total_hour_variable,y] + model.measured_line[2+self.total_hour_variable, y] + model.measured_line[3+self.total_hour_variable, y])/4)
        self.model.total_assumed_hour = pyomo.Constraint(self.model.Time, self.model.number_measured, rule=total_assumed_hour)

        def totaal_allocatie_0(model,t):
            return model.totaal_allocatie_x[t, 0] == model.totaal_allocatie[t]
        self.model.totaal_allocatie_0 = pyomo.Constraint(self.model.Time, rule=totaal_allocatie_0)

        def totaal_allocatie_1(model,t):
            return model.totaal_allocatie_x[t, 1] == model.totaal_allocatie[t] + sum(model.batterij_powerCharge_to_grid[t,x] for x in model.number_batteries) + sum(model.batterij_powerDischarge_to_grid[t,x] for x in model.number_batteries)
        self.model.totaal_allocatie_1 = pyomo.Constraint(self.model.Time, rule=totaal_allocatie_1)

        # #Calculate the difference between forecasted total and actual total done seperately to be able to calculate imbalance cost.
        def difference_in_MWh_afregelen(model,t, y, z):
            return model.difference_MWh_afregelen_x[t, y, z] == (model.measured_line_hour[t,y] - model.totaal_allocatie_x[t, z]) * model.boolean_difference_afregelen_x[t,y,z]
        self.model.difference_in_MWh_afregelen = pyomo.Constraint(self.model.Time, self.model.number_measured, self.model.number_of_allocations ,rule=difference_in_MWh_afregelen)

        def difference_in_MWh_opregelen(model,t, y, z):
            return model.difference_MWh_opregelen_x[t, y, z] == (model.totaal_allocatie_x[t,z]-model.measured_line_hour[t,y]) * model.boolean_difference_opregelen_x[t,y,z]
        self.model.difference_in_MWh_opregelen = pyomo.Constraint(self.model.Time, self.model.number_measured, self.model.number_of_allocations, rule=difference_in_MWh_opregelen)

        def difference_in_MWh_boolean(model,t, y, z):
            return model.boolean_difference_afregelen_x[t,y,z] + model.boolean_difference_opregelen_x[t,y,z] == 1
        self.model.difference_in_MWh_boolean = pyomo.Constraint(self.model.Time, self.model.number_measured, self.model.number_of_allocations, rule=difference_in_MWh_boolean)

        def difference_in_MWh_plot(model,t, y, z):
            return model.difference_MWh_plot_x[t,y,z] ==  model.measured_line_hour[t,y] - model.totaal_allocatie_x[t,z]
        self.model.difference_in_MWh_plot = pyomo.Constraint(self.model.Time,self.model.number_measured, self.model.number_of_allocations, rule=difference_in_MWh_plot)

        def select_onbalans_price(model,t):
            return model.onbalanskosten[t,4] == sum(model.regeltoestand_options[t,x]*model.boolean_select_imbalance[t,x] for x in model.range_options_onbalans)
        self.model.select_onbalans_price = pyomo.Constraint(self.model.Time, rule=select_onbalans_price)

        def select_onbalans_price_boolean(model,t):
            return sum(model.boolean_select_imbalance[t,x] for x in model.range_options_onbalans) == 1
        self.model.select_onbalans_price_boolean = pyomo.Constraint(self.model.Time, rule=select_onbalans_price_boolean)

        def used_pricing(model,t,y,z):
            return model.used_price_x[t,y,z] == (model.onbalanskosten[t,2]*model.boolean_select_imbalance[t,0])+(model.onbalanskosten[t,2]*model.boolean_select_imbalance[t,1])+(model.onbalanskosten[t,3]*model.boolean_select_imbalance[t,2])+(((model.onbalanskosten[t,2]* model.boolean_difference_opregelen_x[t,y,z])+(model.onbalanskosten[t,3]* model.boolean_difference_afregelen_x[t,y,z]))*model.boolean_select_imbalance[t,3])
        self.model.used_pricing = pyomo.Constraint(self.model.Time,self.model.number_measured, self.model.number_of_allocations, rule=used_pricing)

        # Calculate the imbalance cost per 15 minutes and in total
        def imbalance_cost(model,t,y,z):
            return model.imbalance_costs[t,y,z] == (model.used_price_x[t,y,z]*-model.difference_MWh_plot_x[t,y,z])
        self.model.imbalance_cost = pyomo.Constraint(self.model.Time,self.model.number_measured, self.model.number_of_allocations, rule=imbalance_cost)

        def imbalance_cost_epex(model,t,y,z):
            return model.imbalance_costs_epex[t,y,z] == ((model.epex_price[t]-model.used_price_x[t,y,z])*model.difference_MWh_plot_x[t,y,z])
        self.model.imbalance_cost_epex = pyomo.Constraint(self.model.Time,self.model.number_measured, self.model.number_of_allocations, rule=imbalance_cost_epex)

        def imbalance_cost_total(model,t,y,z):
            if t == 0:
                return model.imbalance_costs_total[t,y,z] == model.imbalance_costs_epex[t,y,z]
            elif t == self.current_interval:
                return model.imbalance_costs_total[t,y,z] == model.imbalance_costs_epex[t,y,z] + self.last_total_imbalance
            else:
                return model.imbalance_costs_total[t,y,z] == model.imbalance_costs_total[t - 1,y,z] + model.imbalance_costs_epex[t,y,z]
        self.model.imbalance_cost_total = pyomo.Constraint(self.model.Time,self.model.number_measured, self.model.number_of_allocations, rule=imbalance_cost_total)
