from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import pyomo.environ as pyomo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import model


class optimizer:
    def __init__(self, data_grid, onbalanskosten):
        self.horizon = 96
        self.model = pyomo.ConcreteModel()
        self.model_imbalance = model(self.model, data_grid=data_grid, onbalanskosten=onbalanskosten)
        self.model.horizon = self.horizon
        self.model.Time = pyomo.RangeSet(0, self.model.horizon - 1)
        self.solver_time_limit = 60

    # Optimizer, add this to objectives
    def ObjectiveFunction(self, model):
        return sum([model.difference_MWh[t] for t in model.Time])

    def run(self, batterij, time_list_valid):
        self.model_imbalance.run_model(batterij=batterij, time_list_valid=time_list_valid)
        # initiate Gurobi and load results
        self.model.total_imbalance = pyomo.Objective(rule=self.ObjectiveFunction, sense=pyomo.minimize)
        #self.model.pprint()
        opt = SolverFactory('gurobi', model=self.model)
        opt.options['timelimit'] = self.solver_time_limit
        opt.options['NonConvex'] = 2
        print("send to solver")
        result = opt.solve(self.model)


        #print(model.select_heating_option_buffer.extract_values())

        # catch if results are correctly solved or not
        if (result.solver.status == SolverStatus.ok) and (result.solver.termination_condition == TerminationCondition.optimal):
            print('1', result)
            # Do something when the solution in optimal and feasible
        elif (result.solver.termination_condition == TerminationCondition.infeasible):
            print('2', result)
            # Do something when model in infeasible
        else:
            # Something else is wrong
            print('3', result)
            print('Solver Status:', result.solver.status)

        temp_forecast = pd.Series(self.model.temp_forecast.extract_values(), name=self.model.temp_forecast.name)
        temp_actual = pd.Series(self.model.temp_actual.extract_values(), name=self.model.temp_actual.name)
        solar_forecast = pd.Series(self.model.solar_forecast.extract_values(), name=self.model.solar_forecast.name)
        solar_actual = pd.Series(self.model.solar_actual.extract_values(), name=self.model.solar_actual.name)
        wind_forecast = pd.Series(self.model.wind_forecast.extract_values(), name=self.model.wind_forecast.name)
        wind_actual = pd.Series(self.model.wind_actual.extract_values(), name=self.model.wind_actual.name)
        consumption_forecast = pd.Series(self.model.consumption_forecast.extract_values(), name=self.model.consumption_forecast.name)
        consumption_actual = pd.Series(self.model.consumption_actual.extract_values(), name=self.model.consumption_actual.name)
        total_forecast = pd.Series(self.model.total_forecast.extract_values(), name=self.model.total_forecast.name)
        total_forecast_hour = pd.Series(self.model.total_forecast_hour.extract_values(), name=self.model.total_forecast_hour.name)
        total_actual = pd.Series(self.model.total_actual.extract_values(), name=self.model.total_actual.name)
        difference_MWh_afregelen = pd.Series(self.model.difference_MWh_afregelen.extract_values(), name=self.model.difference_MWh_afregelen.name)
        difference_MWh_opregelen = pd.Series(self.model.difference_MWh_opregelen.extract_values(), name=self.model.difference_MWh_opregelen.name)
        #difference_MWh_plot = pd.Series(self.model.difference_MWh_plot.extract_values(),name=self.model.difference_MWh_plot.name)
        imbalance_before_flex = pd.Series(self.model.imbalance_costs_before_flex.extract_values(), name=self.model.imbalance_costs_before_flex.name)
        imbalance_before_flex_total = pd.Series(self.model.imbalance_costs_before_flex_total.extract_values(),name=self.model.imbalance_costs_before_flex_total.name)
        imbalance_afregelen = pd.Series(self.model.imbalance_afregelen.extract_values(),name=self.model.imbalance_afregelen.name)
        imbalance_opregelen = pd.Series(self.model.imbalance_opregelen.extract_values(), name=self.model.imbalance_opregelen.name)
        # imbalance_biedprijs_afregelen = imbalance_biedprijs[0]
        #print(imbalance_opregelen.to_string())
        # print(imbalance_biedprijs.to_string())

        # print('epex', self.model.epex_price.extract_values())
        # print('temperature forecast', self.model.temp_forecast.extract_values())
        # print('temperature actual', self.model.temp_actual.extract_values())
        # print('solar forecast', self.model.solar_forecast.extract_values())
        # print('solar actual', self.model.solar_actual.extract_values())
        # print('wind forecast', self.model.wind_forecast.extract_values())
        # print('wind actual', self.model.wind_actual.extract_values())
        # print('consumption forecast', self.model.consumption_forecast.extract_values())
        # print('consumption actual', self.model.consumption_actual.extract_values())
        print('difference af', self.model.difference_MWh_afregelen.extract_values())
        print('difference op', self.model.difference_MWh_opregelen.extract_values())
        print('difference', self.model.difference_MWh.extract_values())
        print('onbalanskosten', self.model.onbalanskosten.extract_values())
        print('self.model.regeltoestand_options', self.model.regeltoestand_options.extract_values())
        print('model.boolean_select_imbalance', self.model.boolean_select_imbalance.extract_values())

        # X TICK LABELS
        x = np.arange(0, 96, 8)
        x = np.append(x, 96)
        x_ticks_labels = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00','20:00', '22:00', '00:00']
        # #x_ticks_labels = x_ticks_labels[int(current_interval / 8):]
        fig, ax = plt.subplots(6,1, figsize=(15,12))
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))

        ax[0].plot(temp_forecast, label='Temperature forecast', color='m')
        ax[0].plot(temp_actual, label='Temperature actual', color='g')
        ax[0].set(xlabel='time (h)', ylabel='Temp [C]')
        ax[0].set_xticks(x)
        ax[0].set_xticklabels(x_ticks_labels)
        ax[0].grid()
        ax[0].legend()

        ax[1].plot(solar_forecast, label='Solar forecast', color='m')
        ax[1].plot(solar_actual, label='Solar actual', color='g')
        ax[1].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[1].set_xticks(x)
        ax[1].set_xticklabels(x_ticks_labels)
        ax[1].grid()
        ax[1].legend()

        ax[2].plot(wind_forecast, label='Wind forecast', color='m')
        ax[2].plot(wind_actual, label='Wind actual', color='g')
        ax[2].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[2].set_xticks(x)
        ax[2].set_xticklabels(x_ticks_labels)
        ax[2].grid()
        ax[2].legend()

        ax[3].plot(consumption_forecast, label='Consumption forecast', color='m')
        ax[3].plot(consumption_actual, label='Consumption actual', color='g')
        ax[3].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[3].set_xticks(x)
        ax[3].set_xticklabels(x_ticks_labels)
        ax[3].grid()
        ax[3].legend()

        ax[4].plot(imbalance_afregelen, label='Onbalans afregelen', color='m')
        ax[4].plot(imbalance_opregelen, label='Onbalans opregelen', color='g')
        ax[4].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[4].set_xticks(x)
        ax[4].set_xticklabels(x_ticks_labels)
        ax[4].grid()
        ax[4].legend()

        ax[5].plot(difference_MWh_opregelen, label='Volume afregelen', color='m')
        #ax[5].plot(difference_MWh_plot, label='Volume verschil', color='b')
        ax[5].set(xlabel='time (h)', ylabel='Production in MWh')
        ax[5].set_xticks(x)
        ax[5].set_xticklabels(x_ticks_labels)
        ax[5].grid()
        ax[5].legend()

        axes[0].plot(total_forecast, label='Total forecast', color='m')
        axes[0].plot(total_forecast_hour, label='Total forecast hour', color='b')
        axes[0].plot(total_actual, label='Total actual', color='g')
        axes[0].set(xlabel='time (h)', ylabel='Production in MWh')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(x_ticks_labels)
        axes[0].grid()
        axes[0].legend()

        axes[1].plot(imbalance_before_flex, label='Imbalance before flex', color='m')
        axes[1].plot(imbalance_before_flex_total, label='imbalance total', color='g')
        axes[1].set(xlabel='time (h)', ylabel='Production in MWh')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(x_ticks_labels)
        axes[1].grid()
        axes[1].legend()

        plt.show()