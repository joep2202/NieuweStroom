from Data_retrieval import data_retrieval
from keys_creation import keys
from imbalance_optimzer import optimizer
import pandas as pd

day_one = True
current_interval = 0

if day_one:
    data_grid = pd.read_csv('data/ExtData_10-12-23.csv', index_col=0)
    onbalanskosten = pd.read_csv('data/onbalanskosten_10_12_23.csv')
elif not day_one:
    data_grid = pd.read_csv('data/ExtData_28-11-23.csv', index_col=0)
    onbalanskosten = pd.read_csv('data/onbalanskosten_28_11_23.csv')

data_retr = data_retrieval()
keys = keys()
optimizer_imbalance = optimizer(data_grid=data_grid, onbalanskosten=onbalanskosten, current_interval=current_interval)

appl = ['batterij', 'EVlaadpaal', 'AC', 'KC', 'WP_buf', 'WP_no_buf', 'WWB', 'overig']
main_keys = ['appl_id_main','PiekAansluiting_main', 'type_flex_main']
bat_keys = ['charge_KW_bat','size_kWh_bat','SOC_eind_1_bat','SOC_eind_2_bat']
time_list_valid = {}

unique_types = data_retr.return_unique()
#batterij, EVlaadpaal, AC, KC, WP_buf, WP_no_buf, WWB, overig = data_retr.get_all()
all_appliances = {}
for index, appliance in enumerate(data_retr.get_all()):
    #print(index)
    time_list_valid[appl[index]] = keys.get_time_list(unique_types=unique_types, appliance=appliance)
    all_appliances[appl[index]] = appliance

# for appliance in appl:
#     print(time_list_valid[appliance])
#     for types in unique_types:
#         print(len(time_list_valid[appliance][types]))
#     print(all_appliances['batterij']['Met opwek'].to_string())
#     print(all_appliances['batterij']['Zonder opwek'].to_string())


all_appliances['batterij']['Zonder opwek'].fillna(999, inplace=True)
#print(all_appliances['batterij']['Met opwek'].to_string())

#print(all_appliances['batterij']['Met opwek'].loc[:, main_keys + bat_keys].to_string())
#batterij = all_appliances['batterij']['Met opwek'].loc[:, main_keys + bat_keys]
#print(batterij.to_string())
optimizer_imbalance.run(batterij=all_appliances['batterij']['Zonder opwek'].loc[:, main_keys + bat_keys], time_list_valid=time_list_valid['batterij']['Zonder opwek'])







