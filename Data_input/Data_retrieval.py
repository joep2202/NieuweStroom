import pandas as pd


data = pd.read_csv("data/data2.csv")

zonder_opwek = data[data['type_flex'] == 'Zonder opwek']
met_opwek = data[data['type_flex'] == 'Met opwek']
limit_use = data[data['type_flex'] == 'Limiteren van gebruik']
uitstellen = data[data['type_flex'] == 'Uitstellen']
advance = data[data['type_flex'] == 'Naar voren schuiven']
beide = data[data['type_flex'] == 'Beide']
mobile = data[data['type_flex'] == 'Mobiel (EV)']
#self.filt_settings[i] = self.filt_deltaT[z][self.filt_deltaT[z]['HP_heating'] == setting]
#print(data.to_string())
print(met_opwek.to_string())
# print(limit_use)
# print(zonder_opwek)
# print(uitstellen)
# print(advance)
# print(beide)
# print(mobile)
#print(data.to_string())
met_opwek_wp = met_opwek[met_opwek['type_appl'] == 'Warmtepomp']
print(met_opwek_wp.to_string())


