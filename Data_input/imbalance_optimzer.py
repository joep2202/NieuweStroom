from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import pyomo.environ as pyomo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import model
from activation_protocol import activation_appliances
from retrieve_current_state import retrieve_SOC

class optimizer:
    def __init__(self, allocation_trading, batterij, onbalanskosten, ZWC, temperature, current_interval,DA_bid, date, length_forecast):
        self.length_forecast = length_forecast
        self.horizon = self.length_forecast
        self.model = pyomo.ConcreteModel()
        self.retrieve_SOC_battery = retrieve_SOC()
        self.current_interval = current_interval
        # initialize model
        self.batterij = batterij
        self.batterij = self.batterij.iloc[0:5]
        self.batterij = self.retrieve_SOC_battery.get_SOC_battery(self.batterij)
        self.keys = self.batterij['appl_id_main'].to_list()
        self.model_imbalance = model(self.model, allocation_trading=allocation_trading, onbalanskosten=onbalanskosten, ZWC=ZWC, temperature=temperature, current_interval=self.current_interval, DA_bid=DA_bid)
        self.activate_appl = activation_appliances(batterij=self.batterij)
        self.model.horizon = self.horizon
        self.model.Time = pyomo.RangeSet(0, self.model.horizon - 1)
        self.solver_time_limit = 45
        self.onbalanskosten_check = pd.read_csv('data/Onbalanskosten_check.csv')
        self.onbalanskosten_check = self.onbalanskosten_check[
        self.onbalanskosten_check['From_NL'].str.contains(date)].reset_index(drop=True)
        self.volume_check = pd.read_csv('data/Volume Plot_check.csv')
        self.volume_check = self.volume_check[self.volume_check['From_NL'].str.contains(date)].reset_index(drop=True)
        self.price_check = pd.read_csv('data/Price plot.csv')
        self.price_check = self.price_check[self.price_check['From_NL'].str.contains(date)].reset_index(drop=True)
        self.objective_list = ['end_time_PTE_bat', 'end_time_PTE2_bat']
        self.check = 0

    # Objective function, what is the goal of the optimizer
    def ObjectiveFunction(self, model):
        return sum([model.batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z] *100 for z in model.number_timeslots for x in model.number_batteries] +\
                    [model.imbalance_costs_total[self.length_forecast-1,1,1]])
                    #[model.batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z] *100 for z in model.number_timeslots for x in model.number_batteries] +\
                    #[model.imbalance_costs_after_flex_total[95]]) [model.batterij_powerDischarge_to_grid[t,x] for x in model.number_batteries for t in model.Time]
                   #model.batterij_powerCharge_to_grid[95,x] for x in model.number_batteries]


    def run(self, time_list_valid):
        self.model_imbalance.run_model(batterij=self.batterij, time_list_valid=time_list_valid, keys=self.keys)
        # initiate Gurobi and load results
        self.model.total_imbalance = pyomo.Objective(rule=self.ObjectiveFunction, sense=pyomo.minimize)
        opt = SolverFactory('gurobi', model=self.model)
        opt.options['timelimit'] = self.solver_time_limit
        opt.options['NonConvex'] = 2
        print("send to solver")
        result = opt.solve(self.model)

        # catch if results are correctly solved or not
        if (result.solver.status == SolverStatus.ok) and (
                result.solver.termination_condition == TerminationCondition.optimal):
            print('1', result)
            # Do something when the solution in optimal and feasible
        elif (result.solver.termination_condition == TerminationCondition.infeasible):
            print('2', result)
            # Do something when model in infeasible
        else:
            # Something else is wrong
            print('3', result)
            print('Solver Status:', result.solver.status)

        # Turn model results to Pandas series to be able to plot them
        temp_actual = pd.Series(self.model.temp_actual.extract_values(), name=self.model.temp_actual.name)
        solar_forecast = pd.Series(self.model.solar_forecast.extract_values(), name=self.model.solar_forecast.name)
        solar_actual = pd.Series(self.model.solar_actual.extract_values(), name=self.model.solar_actual.name)
        wind_forecast = pd.Series(self.model.wind_forecast.extract_values(), name=self.model.wind_forecast.name)
        wind_actual = pd.Series(self.model.wind_actual.extract_values(), name=self.model.wind_actual.name)
        consumption_forecast = pd.Series(self.model.consumption_forecast.extract_values(),name=self.model.consumption_forecast.name)
        consumption_actual = pd.Series(self.model.consumption_actual.extract_values(),name=self.model.consumption_actual.name)
        imbalance_afregelen = pd.Series(self.model.imbalance_afregelen.extract_values(),name=self.model.imbalance_afregelen.name)
        imbalance_opregelen = pd.Series(self.model.imbalance_opregelen.extract_values(),name=self.model.imbalance_opregelen.name)
        epex_price = pd.Series(self.model.epex_price.extract_values(), name=self.model.epex_price.name)
        trading_volume = pd.Series(self.model.trading_volume.extract_values(), name=self.model.trading_volume.name)
        solar_difference = pd.Series(self.model.solar_difference.extract_values(),name=self.model.solar_difference.name)
        wind_difference = pd.Series(self.model.wind_difference.extract_values(), name=self.model.wind_difference.name)
        relevant_difference = pd.Series(self.model.relevant_difference.extract_values(),name=self.model.relevant_difference.name)
        batterij_SOC = pd.Series(self.model.batterij_SOC.extract_values(), name=self.model.batterij_SOC.name)
        batterij_energyNotServedFactor = pd.Series(self.model.batterij_energyNotServedFactor.extract_values(),name=self.model.batterij_energyNotServedFactor.name)
        batterij_powerCharge = pd.Series(self.model.batterij_powerCharge.extract_values(),name=self.model.batterij_powerCharge.name)
        batterij_powerDischarge = pd.Series(self.model.batterij_powerDischarge.extract_values(),name=self.model.batterij_powerDischarge.name)
        batterij_powerCharge_to_grid = pd.Series(self.model.batterij_powerCharge_to_grid.extract_values(),name=self.model.batterij_powerCharge_to_grid.name)
        batterij_powerDischarge_to_grid = pd.Series(self.model.batterij_powerDischarge_to_grid.extract_values(),name=self.model.batterij_powerDischarge_to_grid.name)
        time_valid_batterij = pd.Series(self.model.time_valid_batterij.extract_values(), name=self.model.time_valid_batterij.name)
        measured_line = pd.Series(self.model.measured_line.extract_values(), name=self.model.measured_line.name)
        measured_line_hour = pd.Series(self.model.measured_line_hour.extract_values(), name=self.model.measured_line_hour.name)
        totaal_allocatie_x = pd.Series(self.model.totaal_allocatie_x.extract_values(), name=self.model.totaal_allocatie_x.name)
        difference_MWh_plot_x = pd.Series(self.model.difference_MWh_plot_x.extract_values(), name=self.model.difference_MWh_plot_x.name)
        imbalance_costs = pd.Series(self.model.imbalance_costs.extract_values(), name=self.model.imbalance_costs.name)
        imbalance_costs_epex = pd.Series(self.model.imbalance_costs_epex.extract_values(), name=self.model.imbalance_costs_epex.name)
        imbalance_costs_total = pd.Series(self.model.imbalance_costs_total.extract_values(), name=self.model.imbalance_costs_total.name)
        # print(totaal_allocatie)
        # print(totaal_allocatie_x)

        self.onbalanskosten_check['cum'] = self.onbalanskosten_check['Imbalance_Costs'].cumsum()

        # print(len(batterij_energyNotServedFactor[self.current_interval, :, 0]))
        # print(batterij_energyNotServedFactor)
        # for x in range(len(batterij_energyNotServedFactor[0,:,0])):
        #     for z in range(2):
        #         print(x, z, self.batterij[self.objective_list[z]].iloc[x], batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z])
        #         # print(self.batterij[self.objective_list[z]].iloc[x])
        #         self.check += batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z]
        # print('check', self.check)

        print(len(batterij_energyNotServedFactor[self.current_interval,:,0]))
        print('finalsum', sum([batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z] for z in range(2) for x in range(len(batterij_energyNotServedFactor[self.current_interval,:,0]))]))
        print('finalsum imbalance', imbalance_costs_total[self.length_forecast-1,1,1], 'old', imbalance_costs_total[self.length_forecast-1,1,0], 'difference',imbalance_costs_total[self.length_forecast-1,1,0]- imbalance_costs_total[self.length_forecast-1,1,1])

        #sum the charge/discharge schemes so they can be projected as 1
        batterij_powerCharge_to_grid_cum = []
        batterij_powerDischarge_to_grid_cum = []
        for t in self.model.Time:
            batterij_powerCharge_to_grid_cum.append(sum(batterij_powerCharge_to_grid[t,x] for x in range(len(batterij_energyNotServedFactor[self.current_interval,:,0]))))
            batterij_powerDischarge_to_grid_cum.append(sum(batterij_powerDischarge_to_grid[t,x] for x in range(len(batterij_energyNotServedFactor[self.current_interval,:,0]))))
        change_to_grid_cum = [x + y for x, y in zip(batterij_powerCharge_to_grid_cum, batterij_powerDischarge_to_grid_cum)]


        charge = self.model.batterij_powerCharge.extract_values()
        discharge = self.model.batterij_powerDischarge.extract_values()
        self.activate_appl.activation_protocol(charge=charge,discharge=discharge, current_interval=self.current_interval, keys=self.keys, length_forecast=self.length_forecast)
        self.activate_appl.feedback_traders(change_to_grid_cum)

        # X TICK LABELS
        #x = np.arange(self.current_interval, self.length_forecast+self.current_interval, 8)

        if self.current_interval == 0:
            y=4
        else:
            y = self.current_interval % 4

        x = np.arange(0 + (4-y), self.length_forecast+ (4-y), 8)
        x = np.append(x, self.length_forecast+ (4-y))
        x_ticks_labels = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00',
                          '20:00', '22:00', '00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00',
                          '20:00', '22:00', '00:00']
        x_ticks_labels = x_ticks_labels[round(self.current_interval/8):(round(self.current_interval/8)+len(x))]

        # plot necessary results
        fig, ax = plt.subplots(6, 1, figsize=(15, 12))
        fig, axes = plt.subplots(2, 1, figsize=(15, 12))
        fig, ax2 = plt.subplots(2, 1, figsize=(15, 12))

        ax[0].plot(temp_actual, label='Temperature actual', color='g')
        ax[0].set(xlabel='time (h)', ylabel='Temp [C]')
        ax[0].set_xticks(x)
        ax[0].set_xticklabels(x_ticks_labels)
        ax[0].grid()
        ax[0].legend()

        ax[1].plot(solar_forecast, label='Solar forecast', color='m')
        ax[1].plot(solar_actual, label='Solar actual', color='g')
        ax[1].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[1].set(xlabel='time (h)', ylabel='Prod in MWh')
        ax[1].set_xticks(x)
        ax[1].set_xticklabels(x_ticks_labels)
        ax[1].grid()
        ax[1].legend()

        ax[2].plot(wind_forecast, label='Wind forecast', color='m')
        ax[2].plot(wind_actual, label='Wind actual', color='g')
        ax[2].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[2].set(xlabel='time (h)', ylabel='Prod in MWh')
        ax[2].set_xticks(x)
        ax[2].set_xticklabels(x_ticks_labels)
        ax[2].grid()
        ax[2].legend()

        ax[3].plot(consumption_forecast, label='Consumption forecast', color='m')
        ax[3].plot(consumption_actual, label='Consumption actual', color='g')
        ax[3].set(xlabel='time (h)', ylabel='Prod in MWh')
        ax[3].set_xticks(x)
        ax[3].set_xticklabels(x_ticks_labels)
        ax[3].grid()
        ax[3].legend()

        ax[4].plot(imbalance_afregelen, label='Onbalans afregelen', color='m')
        ax[4].plot(self.price_check['Imbalance_Long_EurMWh'], label='Onbalans afregelen check', color='m', alpha=0.2)
        ax[4].plot(imbalance_opregelen, label='Onbalans opregelen', color='g')
        ax[4].plot(self.price_check['Imbalance_Short_EurMWh'], label='Onbalans opregelen check', color='g', alpha=0.2)
        ax[4].plot(epex_price, label='EPEX', color='b')
        ax[4].plot(self.price_check['EPEX_EurMWh'], label='EPEX check', color='b', alpha=0.2)
        ax[4].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[4].set(xlabel='time (h)', ylabel='eur/MWh')
        ax[4].set_xticks(x)
        ax[4].set_xticklabels(x_ticks_labels)
        ax[4].grid()
        # ax[4].legend()

        # ax[5].plot(difference_MWh_opregelen, label='Volume afregelen', color='m')
        ax[5].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[5].plot(difference_MWh_plot_x[:,1,0], label='Volume verschil', color='b')
        ax[5].plot(difference_MWh_plot_x[:,2,0], label='Volume verschil onvermijdbaar',color='c')
        ax[5].plot(difference_MWh_plot_x[:,3,0], label='Volume verschil comp', color='b', alpha=0.2)
        ax[5].plot(difference_MWh_plot_x[:,1,1], label='after flex verschil', color='green', alpha=0.5)
        # ax[5].plot(-solar_difference, label='Solar difference', color='m')
        # ax[5].plot(-wind_difference, label='Wind difference', color='g')
        ax[5].plot(-relevant_difference, label='Total difference', color='r')
        #ax[5].plot(self.volume_check['Imbalance_Volume_MWh'], label='Volume verschil check', color='g', alpha=0.5)
        ax[5].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[5].set_xticks(x)
        ax[5].set_xticklabels(x_ticks_labels)
        ax[5].grid()
        #ax[5].legend()

        axes[0].plot(measured_line[:,0], label='E programma', color='r')
        axes[0].plot(measured_line_hour[:,0],label='Total forecast hour E program', color='r')
        axes[0].plot(measured_line_hour[:,1],label='Total forecast hour V program', color='b')
        # axes[0].plot(total_forecast_trading, label='Total forecast after trading', color='r')
        axes[0].plot(totaal_allocatie_x[:,0], label='Total allocatie', color='g')
        axes[0].plot(totaal_allocatie_x[:,1], label='Total allocatie after flex', color='c')
        axes[0].plot(trading_volume, label='Trading volume', color='y')
        # axes[0].plot(total_after_flex, label='allocatie met imbalance', color='c')
        # axes[0].plot(total_after_flex_hour, label='allocatie met imbalance hour',color='c')
        axes[0].set(xlabel='time (h)', ylabel='Production in MWh')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(x_ticks_labels)
        axes[0].grid()
        axes[0].legend(loc='upper left', bbox_to_anchor=(0, 1))

        axes[1].plot(imbalance_costs[:,1,0], label='Imbalance before flex', color='m')
        axes[1].plot(imbalance_costs[:,1,1], label='Imbalance after flex', color='m', alpha=0.5)
        # axes[1].plot(imbalance_before_flex_comp, label='Imbalance before flex comp', color='m', alpha=0.5)
        #axes[1].plot(self.onbalanskosten_check['Tennet_Bill'], label='Imbalance before flex check', color='m',alpha=0.5)
        axes[1].plot(imbalance_costs_epex[:,1,0], label='Imbalance before flex EPEX',color='g')
        axes[1].plot(imbalance_costs_epex[:,1,1], label='Imbalance after flex EPEX',color='g', alpha=0.5)
        # axes[1].plot(imbalance_costs_before_flex_epex_comp, label='Imbalance before flex EPEX comp', color='g', alpha=0.5)
        #axes[1].plot(self.onbalanskosten_check['Imbalance_Costs'], label='Imbalance before flex EPEX check', color='g',alpha=0.5)
        axes[1].plot(imbalance_costs_total[:,1,0], label='imbalance cumulatief before', color='b')
        axes[1].plot(imbalance_costs_total[:,1,1], label='imbalance cumulatief after', color='b', alpha=0.5) #imbalance_costs_after_flex_total
        #axes[1].plot(imbalance_before_flex_total_comp, label='imbalance cumulatief comp', color='b', alpha=0.5)
        #axes[1].plot(self.onbalanskosten_check['cum'], label='imbalance cumulatief check', color='c')
        #axes[1].plot(onvermijdbaar_imbalance_totaal, label='onvermijdbaar imbalans', color='r')
        axes[1].plot(imbalance_costs_total[:,2,0], label='onvermijdbaar imbalans', color='r')
        axes[1].set(xlabel='time (h)', ylabel='Production in MWh')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(x_ticks_labels)
        axes[1].grid()
        axes[1].legend()


        colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'darkblue', 'darkgreen', 'darkred',
                  'darkcyan', 'darkmagenta', 'darkgoldenrod', 'lightblue', 'lightgreen', 'lightcoral', 'lightcyan',
                  'slategray']
        for z in range(5):
            ax2[0].plot(batterij_SOC[:, z], label='Battery SOC'+str(z), color=colors[z])
        ax3 = ax2[0].twinx()
        ax3.plot(epex_price, label='Epex', color='black')
        ax2[0].set(xlabel='time (h)', ylabel='kWh')
        ax2[0].set_xticks(x)
        ax2[0].set_xticklabels(x_ticks_labels)
        ax2[0].grid()
        ax2[0].legend()

        indices = [i for i in range(0, self.length_forecast)]
        # for z in range(len(batterij_SOC[0, :])):
        #     ax2[1].plot(batterij_powerCharge[:, z], label='Charge'+str(z), color=colors[z])
        #     ax2[1].plot(batterij_powerDischarge[:, z], label='Discharge'+str(z), color=colors[z])
        ax2[1].plot(indices, batterij_powerCharge_to_grid_cum, label='Charge', color='blue')
        ax2[1].plot(indices, batterij_powerDischarge_to_grid_cum, label='Discharge', color='green')
        ax2[1].plot(indices, change_to_grid_cum, label='Total change', color='black')
        ax2[1].set(xlabel='time (h)', ylabel='MW')
        ax2[1].set_xticks(x)
        ax2[1].set_xticklabels(x_ticks_labels)
        ax2[1].legend()
        ax2[1].grid()

        plt.show()
