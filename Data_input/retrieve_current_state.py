import random

class retrieve_SOC:
    def __init__(self):
        self.random_soc = [0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69, 0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69,0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69,0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69, 0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69, 0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69,0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69, 0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42, 0.7, 0.65, 0.56, 0.88, 0.67, 0.58, 0.42, 0.86, 0.7, 0.69,0.80, 0.66, 0.77, 0.68, 0.75, 0.55, 0.77, 0.42]

    def get_SOC_battery(self, batterij):
        ##Here you can make calls to the necessary appliances to check availability and state of charge:
        ## use line below in a later stage but having the same numbers is nice for testing
        #self.random_soc = [round(random.uniform(0.25, 0.75),2) for i in range(len(batterij))]
        #print(self.random_soc)
        self.random_soc = self.random_soc[0:len(batterij)]
        #print('Random SOC', self.random_soc,len(batterij), batterij.shape[0])
        batterij['Availability'] = 'Yes'
        batterij['current_SOC'] = self.random_soc
        batterij['aansluiting ruimte'] = batterij['PiekAansluiting_main'] - (batterij['PiekAansluiting_main']*0.7)
        batterij.reset_index(inplace=True, drop=True)
        batterij = batterij[batterij['Availability'] == 'Yes']
        print('Batterij', batterij.to_string())
        return batterij

    def get_PV_status(self, zonnepanelen):
        zonnepanelen.reset_index(inplace=True, drop=True)
        zonnepanelen['productie'] = zonnepanelen['kwp_zon']*self.random_soc[random.randrange(0, len(self.random_soc), 1)]
        print('Zonnepanelen', zonnepanelen.to_string())
        per_park_forecast = 0
        return zonnepanelen, per_park_forecast