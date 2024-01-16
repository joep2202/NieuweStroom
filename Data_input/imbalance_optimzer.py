from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
import pyomo.environ as pyomo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import model


class optimzer:
    def __init__(self):
        self.model = model()
        self.horizon = 97
        self.model = pyomo.ConcreteModel()
        self.model.horizon = self.horizon
        self.model.Time = pyomo.RangeSet(0, self.model.horizon - 1)
        self.solver_time_limit = 60

    # Optimizer, add this to objectives
    def ObjectiveFunction(model):
        return sum()

    def run(self):
        # initiate Gurobi and load results
        self.model.total_costs = pyomo.Objective(rule=self.ObjectiveFunction, sense=pyomo.maximize)
        opt = SolverFactory('gurobi', model=self.model)
        opt.options['timelimit'] = self.solver_time_limit
        print("send to solver")
        result = opt.solve(self.model)


        #print(model.select_heating_option_buffer.extract_values())

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



        # X TICK LABELS
        x = np.arange(0, 96, 8)
        x = np.append(x, 96)
        x_ticks_labels = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00',
                          '20:00', '22:00', '00:00']
        #x_ticks_labels = x_ticks_labels[int(current_interval / 8):]
        fig, ax = plt.subplots(1, figsize=(15, 7))

        # ax.plot(heat[current_interval:], label='heating SP', color='m')
        # ax.plot(heat_setting[current_interval:]+Buffer_Discharge[current_interval:], label='to builing', color='g')
        # ax.plot(-cold_setting[current_interval:], label='cooling SP', color='c')
        # ax.plot(heat_setting[current_interval:], label='building heating', color='k')
        # ax.plot(Buffer_charge[current_interval:], label='buffer heating', color='y')
        # ax.set(xlabel='time (s)', ylabel='Setpoint [W]', title='Heat pump operations over time')
        # ax.set_xticks(x)
        # ax.set_xticklabels(x_ticks_labels)
        # ax.grid()
        # ax.legend()