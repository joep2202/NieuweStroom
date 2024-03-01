import pandas as pd

class activation_appliances:
    def __init__(self, batterij):
        self.batterij = batterij
        self.index = list(range(96))
        self.setting = {}

    def activation_receiver(self, ID, adress, value):
        self.ID = ID
        self.adress = adress
        self.value = value
        #print(self.ID, self.adress, self.value)

    def activation_protocol(self, charge, discharge, current_interval, keys):
        print("enter activation")
        self.keys = keys
        for index, appl in enumerate(self.keys):
            charge_list = []
            discharge_list = []
            for time_interval in range(current_interval,96):
                charge_list.append(charge[time_interval, index])
                discharge_list.append(discharge[time_interval, index])
            change = [x + y for x, y in zip(charge_list, discharge_list)]
            self.setting[appl] = change
            self.ICT_adress = self.batterij['ICT_APPL_bat'].iloc[index]
            self.activation_receiver(ID=appl, adress=self.ICT_adress, value=change[0])
        #print(self.setting)

    def feedback_traders(self, total_schedule):
        print('Provide flex schedule to traders')
        self.schedule = total_schedule
        #print(self.schedule)
