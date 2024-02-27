from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import pyomo.environ as pyomo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import model

class optimizer:
    def __init__(self, allocation_trading, batterij, onbalanskosten, ZWC, temperature, current_interval, date):
        self.horizon = 96
        self.model = pyomo.ConcreteModel()
        self.current_interval = current_interval
        # initialize model
        self.batterij = batterij
        #self.batterij = self.batterij.iloc[0:1]
        self.model_imbalance = model(self.model, allocation_trading=allocation_trading, onbalanskosten=onbalanskosten, ZWC=ZWC, temperature=temperature, current_interval=self.current_interval)
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
        self.objective_list = ['end_time_bat_PTE', 'end_time2_bat_PTE']
        self.check = 0

    # Optimizer, add this to objectives
    def ObjectiveFunction(self, model):
        return sum([model.batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z] *100 for z in model.number_timeslots for x in model.number_batteries] +\
                    [model.imbalance_costs_after_flex_total[95]])
                    #[model.batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z] *100 for z in model.number_timeslots for x in model.number_batteries] +\
                    #[model.imbalance_costs_after_flex_total[95]]) [model.batterij_powerDischarge_to_grid[t,x] for x in model.number_batteries for t in model.Time]
                   #[model.bat_elec_costs_total[95, x] for x in model.number_batteries] model.batterij_powerCharge_to_grid[95,x] for x in model.number_batteries]


    def run(self, time_list_valid):
        self.model_imbalance.run_model(batterij=self.batterij, time_list_valid=time_list_valid)
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
        total_forecast = pd.Series(self.model.total_forecast.extract_values(), name=self.model.total_forecast.name)
        total_forecast_hour_v_programma = pd.Series(self.model.total_forecast_hour_v_programma.extract_values(),name=self.model.total_forecast_hour_v_programma.name)
        total_after_flex = pd.Series(self.model.total_after_flex.extract_values(), name=self.model.total_after_flex.name)
        total_after_flex_hour = pd.Series(self.model.total_after_flex_hour.extract_values(),name=self.model.total_after_flex_hour.name)
        total_forecast_hour_e_programma = pd.Series(self.model.total_forecast_hour_e_programma.extract_values(),name=self.model.total_forecast_hour_e_programma.name)
        totaal_allocatie = pd.Series(self.model.totaal_allocatie.extract_values(),name=self.model.totaal_allocatie.name)
        total_allocation_hour = pd.Series(self.model.total_allocation_hour.extract_values(),name=self.model.total_allocation_hour.name)
        difference_MWh_plot = pd.Series(self.model.difference_MWh_plot.extract_values(),name=self.model.difference_MWh_plot.name)
        difference_MWh_plot_comp = pd.Series(self.model.difference_MWh_plot_comp.extract_values(),name=self.model.difference_MWh_plot_comp.name)
        difference_MWh_plot_onvermijdbaar = pd.Series(self.model.difference_MWh_plot_onvermijdbaar.extract_values(),name=self.model.difference_MWh_plot_onvermijdbaar.name)
        difference_MWh_plot_after_flex = pd.Series(self.model.difference_MWh_plot_after_flex.extract_values(),name=self.model.difference_MWh_plot_after_flex.name)
        imbalance_before_flex = pd.Series(self.model.imbalance_costs_before_flex.extract_values(),name=self.model.imbalance_costs_before_flex.name)
        imbalance_costs_before_flex_epex = pd.Series(self.model.imbalance_costs_before_flex_epex.extract_values(),name=self.model.imbalance_costs_before_flex_epex.name)
        imbalance_before_flex_total = pd.Series(self.model.imbalance_costs_before_flex_total.extract_values(),name=self.model.imbalance_costs_before_flex_total.name)
        imbalance_costs_after_flex = pd.Series(self.model.imbalance_costs_after_flex.extract_values(),name=self.model.imbalance_costs_after_flex.name)
        imbalance_costs_after_flex_epex = pd.Series(self.model.imbalance_costs_after_flex_epex.extract_values(),name=self.model.imbalance_costs_after_flex_epex.name)
        imbalance_costs_after_flex_total = pd.Series(self.model.imbalance_costs_after_flex_total.extract_values(),name=self.model.imbalance_costs_after_flex_total.name)
        imbalance_before_flex_comp = pd.Series(self.model.imbalance_costs_before_flex_comp.extract_values(),name=self.model.imbalance_costs_before_flex_comp.name)
        imbalance_costs_before_flex_epex_comp = pd.Series(self.model.imbalance_costs_before_flex_epex_comp.extract_values(),name=self.model.imbalance_costs_before_flex_epex_comp.name)
        imbalance_before_flex_total_comp = pd.Series(self.model.imbalance_costs_before_flex_total_comp.extract_values(),name=self.model.imbalance_costs_before_flex_total_comp.name)
        imbalance_afregelen = pd.Series(self.model.imbalance_afregelen.extract_values(),name=self.model.imbalance_afregelen.name)
        imbalance_opregelen = pd.Series(self.model.imbalance_opregelen.extract_values(),name=self.model.imbalance_opregelen.name)
        onvermijdbaar_imbalance_totaal = pd.Series(self.model.onvermijdbaar_imbalance_totaal.extract_values(),name=self.model.onvermijdbaar_imbalance_totaal.name)
        epex_price = pd.Series(self.model.epex_price.extract_values(), name=self.model.epex_price.name)
        used_price = pd.Series(self.model.used_price.extract_values(), name=self.model.used_price.name)
        trading_volume = pd.Series(self.model.trading_volume.extract_values(), name=self.model.trading_volume.name)
        solar_difference = pd.Series(self.model.solar_difference.extract_values(),name=self.model.solar_difference.name)
        wind_difference = pd.Series(self.model.wind_difference.extract_values(), name=self.model.wind_difference.name)
        relevant_difference = pd.Series(self.model.relevant_difference.extract_values(),name=self.model.relevant_difference.name)
        allocatie_adapted = pd.Series(self.model.total_forecast_trading_adapted.extract_values(),name=self.model.total_forecast_trading_adapted.name)
        total_forecast_hour_v_programma_comp = pd.Series(self.model.total_forecast_hour_v_programma_comp.extract_values(),name=self.model.total_forecast_hour_v_programma_comp.name)
        batterij_SOC = pd.Series(self.model.batterij_SOC.extract_values(), name=self.model.batterij_SOC.name)
        batterij_energyNotServedFactor = pd.Series(self.model.batterij_energyNotServedFactor.extract_values(),name=self.model.batterij_energyNotServedFactor.name)
        batterij_powerCharge = pd.Series(self.model.batterij_powerCharge.extract_values(),name=self.model.batterij_powerCharge.name)
        batterij_powerDischarge = pd.Series(self.model.batterij_powerDischarge.extract_values(),name=self.model.batterij_powerDischarge.name)
        batterij_powerCharge_to_grid = pd.Series(self.model.batterij_powerCharge_to_grid.extract_values(),name=self.model.batterij_powerCharge_to_grid.name)
        batterij_powerDischarge_to_grid = pd.Series(self.model.batterij_powerDischarge_to_grid.extract_values(),name=self.model.batterij_powerDischarge_to_grid.name)
        bat_elec_costs = pd.Series(self.model.bat_elec_costs.extract_values(),name=self.model.bat_elec_costs.name)
        bat_elec_costs_total = pd.Series(self.model.bat_elec_costs_total.extract_values(), name=self.model.bat_elec_costs_total.name)
        time_valid_batterij = pd.Series(self.model.time_valid_batterij.extract_values(), name=self.model.time_valid_batterij.name)

        self.onbalanskosten_check['cum'] = self.onbalanskosten_check['Imbalance_Costs'].cumsum()

        # for x in range(len(batterij_energyNotServedFactor[0,:,0])):
        #     for z in range(2):
        #         print(x, z, self.batterij[self.objective_list[z]].iloc[x], batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z])
        #         # print(self.batterij[self.objective_list[z]].iloc[x])
        #         self.check += batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z]
        # print('check', self.check)

        print(len(batterij_energyNotServedFactor[0,:,0]))
        print('finalsum', sum([batterij_energyNotServedFactor[self.batterij[self.objective_list[z]].iloc[x], x, z] for z in range(2) for x in range(len(batterij_energyNotServedFactor[0,:,0]))]))
        print('finalsum imbalance', imbalance_costs_after_flex_total[95], 'old', imbalance_before_flex_total[95], 'difference',imbalance_before_flex_total[95]- imbalance_costs_after_flex_total[95])

        # pd.set_option('display.max_rows', None)
        # print(total_after_flex_hour-total_forecast_hour_v_programma)
        # pd.reset_option('display.max_rows')

        #sum the charge/discharge schemes so they can be projected as 1
        batterij_powerCharge_to_grid_cum = []
        batterij_powerDischarge_to_grid_cum = []
        for t in self.model.Time:
            batterij_powerCharge_to_grid_cum.append(sum(batterij_powerCharge_to_grid[t,x] for x in range(len(batterij_energyNotServedFactor[0,:,0]))))
            batterij_powerDischarge_to_grid_cum.append(sum(batterij_powerDischarge_to_grid[t,x] for x in range(len(batterij_energyNotServedFactor[0,:,0]))))

        # X TICK LABELS
        x = np.arange(0, 96, 8)
        x = np.append(x, 96)
        x_ticks_labels = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00',
                          '20:00', '22:00', '00:00']
        x_ticks_labels = x_ticks_labels[int(self.current_interval / 8):]

        # plot necessary results
        fig, ax = plt.subplots(6, 1, figsize=(15, 12))
        fig, axes = plt.subplots(2, 1, figsize=(15, 12))
        fig, ax2 = plt.subplots(3, 1, figsize=(15, 12))

        ax[0].plot(temp_actual[self.current_interval:], label='Temperature actual', color='g')
        ax[0].set(xlabel='time (h)', ylabel='Temp [C]')
        ax[0].set_xticks(x)
        ax[0].set_xticklabels(x_ticks_labels)
        ax[0].grid()
        ax[0].legend()

        ax[1].plot(solar_forecast[self.current_interval:], label='Solar forecast', color='m')
        ax[1].plot(solar_actual[self.current_interval:], label='Solar actual', color='g')
        ax[1].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[1].set(xlabel='time (h)', ylabel='Prod in MWh')
        ax[1].set_xticks(x)
        ax[1].set_xticklabels(x_ticks_labels)
        ax[1].grid()
        ax[1].legend()

        ax[2].plot(wind_forecast[self.current_interval:], label='Wind forecast', color='m')
        ax[2].plot(wind_actual[self.current_interval:], label='Wind actual', color='g')
        ax[2].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[2].set(xlabel='time (h)', ylabel='Prod in MWh')
        ax[2].set_xticks(x)
        ax[2].set_xticklabels(x_ticks_labels)
        ax[2].grid()
        ax[2].legend()

        ax[3].plot(consumption_forecast[self.current_interval:], label='Consumption forecast', color='m')
        ax[3].plot(consumption_actual[self.current_interval:], label='Consumption actual', color='g')
        ax[3].set(xlabel='time (h)', ylabel='Prod in MWh')
        ax[3].set_xticks(x)
        ax[3].set_xticklabels(x_ticks_labels)
        ax[3].grid()
        ax[3].legend()

        ax[4].plot(imbalance_afregelen[self.current_interval:], label='Onbalans afregelen', color='m')
        ax[4].plot(self.price_check['Imbalance_Long_EurMWh'], label='Onbalans afregelen check', color='m', alpha=0.2)
        ax[4].plot(imbalance_opregelen[self.current_interval:], label='Onbalans opregelen', color='g')
        ax[4].plot(self.price_check['Imbalance_Short_EurMWh'], label='Onbalans opregelen check', color='g', alpha=0.2)
        ax[4].plot(epex_price[self.current_interval:], label='EPEX', color='b')
        ax[4].plot(self.price_check['EPEX_EurMWh'], label='EPEX check', color='b', alpha=0.2)
        ax[4].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[4].set(xlabel='time (h)', ylabel='eur/MWh')
        ax[4].set_xticks(x)
        ax[4].set_xticklabels(x_ticks_labels)
        ax[4].grid()
        # ax[4].legend()

        # ax[5].plot(difference_MWh_opregelen, label='Volume afregelen', color='m')
        ax[5].axhline(0, color='black', linestyle='--', linewidth=1)
        ax[5].plot(difference_MWh_plot[self.current_interval:], label='Volume verschil', color='b')
        ax[5].plot(difference_MWh_plot_onvermijdbaar[self.current_interval:], label='Volume verschil onvermijdbaar',
                   color='c')
        ax[5].plot(difference_MWh_plot_comp[self.current_interval:], label='Volume verschil comp', color='b', alpha=0.2)
        ax[5].plot(difference_MWh_plot_after_flex[self.current_interval:], label='after flex verschil', color='b', alpha=0.5)
        # ax[5].plot(-solar_difference[self.current_interval:], label='Solar difference', color='m')
        # ax[5].plot(-wind_difference[self.current_interval:], label='Wind difference', color='g')
        ax[5].plot(-relevant_difference[self.current_interval:], label='Total difference', color='r')
        ax[5].plot(self.volume_check['Imbalance_Volume_MWh'], label='Volume verschil check', color='g', alpha=0.5)
        ax[5].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[5].set_xticks(x)
        ax[5].set_xticklabels(x_ticks_labels)
        ax[5].grid()
        #ax[5].legend()

        axes[0].plot(total_forecast[self.current_interval:], label='Total forecast', color='r')
        axes[0].plot(total_forecast_hour_e_programma[self.current_interval:],label='Total forecast hour E program', color='r')
        axes[0].plot(total_forecast_hour_v_programma[self.current_interval:],label='Total forecast hour V program', color='b')
        # axes[0].plot(total_forecast_trading, label='Total forecast after trading', color='r')
        axes[0].plot(totaal_allocatie[self.current_interval:], label='Total allocatie', color='g')
        axes[0].plot(total_allocation_hour[self.current_interval:], label='Total allocatie per hour', color='g')
        axes[0].plot(trading_volume[self.current_interval:], label='Trading volume', color='y')
        axes[0].plot(total_after_flex[self.current_interval:], label='allocatie met imbalance', color='c')
        axes[0].plot(total_after_flex_hour[self.current_interval:], label='allocatie met imbalance hour',color='c')
        axes[0].set(xlabel='time (h)', ylabel='Production in MWh')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(x_ticks_labels)
        axes[0].grid()
        axes[0].legend(loc='upper left', bbox_to_anchor=(0, 1))

        axes[1].plot(imbalance_before_flex[self.current_interval:], label='Imbalance before flex', color='m')
        axes[1].plot(imbalance_costs_after_flex[self.current_interval:], label='Imbalance after flex', color='m', alpha=0.5)
        # axes[1].plot(imbalance_before_flex_comp[self.current_interval:], label='Imbalance before flex comp', color='m', alpha=0.5)
        #axes[1].plot(self.onbalanskosten_check['Tennet_Bill'], label='Imbalance before flex check', color='m',alpha=0.5)
        axes[1].plot(imbalance_costs_before_flex_epex[self.current_interval:], label='Imbalance before flex EPEX',color='g')
        axes[1].plot(imbalance_costs_after_flex_epex[self.current_interval:], label='Imbalance after flex EPEX',color='g', alpha=0.5)
        # axes[1].plot(imbalance_costs_before_flex_epex_comp[self.current_interval:], label='Imbalance before flex EPEX comp', color='g', alpha=0.5)
        #axes[1].plot(self.onbalanskosten_check['Imbalance_Costs'], label='Imbalance before flex EPEX check', color='g',alpha=0.5)
        axes[1].plot(imbalance_before_flex_total[self.current_interval:], label='imbalance cumulatief before', color='b')
        axes[1].plot(imbalance_costs_after_flex_total[self.current_interval:], label='imbalance cumulatief after', color='b', alpha=0.5)
        #axes[1].plot(imbalance_before_flex_total_comp[self.current_interval:], label='imbalance cumulatief comp', color='b', alpha=0.5)
        #axes[1].plot(self.onbalanskosten_check['cum'], label='imbalance cumulatief check', color='c')
        axes[1].plot(onvermijdbaar_imbalance_totaal[self.current_interval:], label='onvermijdbaar imbalans', color='r')
        axes[1].set(xlabel='time (h)', ylabel='Production in MWh')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(x_ticks_labels)
        axes[1].grid()
        axes[1].legend()


        colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'darkblue', 'darkgreen', 'darkred',
                  'darkcyan', 'darkmagenta', 'darkgoldenrod', 'lightblue', 'lightgreen', 'lightcoral', 'lightcyan',
                  'slategray']
        for z in range(5):
            ax2[0].plot(batterij_SOC[:, z][self.current_interval:], label='Battery SOC'+str(z), color=colors[z])
        ax3 = ax2[0].twinx()
        ax3.plot(epex_price[self.current_interval:], label='Epex', color='black')
        ax2[0].set(xlabel='time (h)', ylabel='kWh')
        ax2[0].set_xticks(x)
        ax2[0].set_xticklabels(x_ticks_labels)
        ax2[0].grid()
        ax2[0].legend()
        #
        # for z in range(len(batterij_SOC[0, :])):
        #     ax2[1].plot(batterij_powerCharge[:, z][self.current_interval:], label='Charge'+str(z), color=colors[z])
        #     ax2[1].plot(batterij_powerDischarge[:, z][self.current_interval:], label='Discharge'+str(z), color=colors[z])
        ax2[1].plot(batterij_powerCharge_to_grid_cum[self.current_interval:], label='Charge', color='blue')
        ax2[1].plot(batterij_powerDischarge_to_grid_cum[self.current_interval:], label='Discharge', color='green')
        ax2[1].set(xlabel='time (h)', ylabel='MW')
        ax2[1].set_xticks(x)
        ax2[1].set_xticklabels(x_ticks_labels)
        ax2[1].legend()
        ax2[1].grid()

        # for z in range(len(batterij_SOC[0, :])):
        #     ax2[2].plot(bat_elec_costs[:, z][self.current_interval:], label='bat_elec_costs'+str(z), color=colors[z])
        #     ax2[2].plot(bat_elec_costs_total[:, z][self.current_interval:], label='bat_elec_costs_total' + str(z),color=colors[z])
        # ax2[2].set(xlabel='time (h)', ylabel='Euro')
        # ax2[2].set_xticks(x)
        # ax2[2].set_xticklabels(x_ticks_labels)
        # #ax2[2].legend()
        # ax2[2].grid()

        plt.show()
