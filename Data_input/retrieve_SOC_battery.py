import random

class retrieve_SOC:
    def __init__(self):
        self.random_soc = [0.58, 0.66, 0.47, 0.58, 0.75, 0.35, 0.27, 0.32, 0.7, 0.65, 0.56, 0.48, 0.27, 0.48, 0.42, 0.36, 0.7, 0.69]

    def get_SOC_battery(self, batterij):
        ##Here you can make calls to the necessary appliances to check availability and state of charge:
        ## use line below in a later stage but having the same numbers is nice for testing
        #self.random_soc = [round(random.uniform(0.25, 0.75),2) for i in range(len(batterij))]
        #print(self.random_soc)
        batterij['Availability'] = 'Yes'
        batterij['current_SOC'] = self.random_soc
        print(batterij.to_string())
        return batterij