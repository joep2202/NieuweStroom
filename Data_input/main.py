#import classes from other files
from Data_retrieval_appliances import data_retrieval_appliances
from Time_intervals import time_intervals
from imbalance_optimzer import optimizer
from TempDataRetrieval import retrieve_temp
from Data_retrieval_Tennet_situation import import_data_per_day
import pandas as pd

#import libraries
from datetime import datetime

timestamp= 20231207                               #select the data for which the code runs
current_interval = 0                                    #select interval from which the code runs

#change dates to usable format
date_temp = datetime.strptime(str(timestamp), '%Y%m%d')
date = date_temp.strftime('%d/%m/%Y')

#initialize classes
temperature_call = retrieve_temp(timestamp=timestamp)
import_data_base_situation = import_data_per_day()
data_retr_appl = data_retrieval_appliances(current_interval=current_interval)
time_interval = time_intervals()

#get the outside data
allocation_trading, onbalanskosten, ZWC, DA_bid = import_data_base_situation.get_data(date)
temperature = temperature_call.change_into_15min()
unique_types = data_retr_appl.return_unique()

#Create two dicts that holds the appliance information
time_list_valid = {}
all_appliances = {}
#Create lists to select the relevant data needed for the optimizer
appl = ['batterij', 'EVlaadpaal', 'AC', 'KC', 'WP_buf', 'WP_no_buf', 'WWB', 'overig']
main_keys = ['appl_id_main','PiekAansluiting_main', 'type_flex_main']
bat_keys = ['charge_KW_bat','size_kWh_bat','SOC_eind_1_bat','end_time_bat_PTE', 'SOC_eind_2_bat','end_time2_bat_PTE', 'ICT_APPL_bat']


#retrieve the data per appliance and create a list per appliance when flex is available
for index, appliance in enumerate(data_retr_appl.get_all()):
    #print(index)
    time_list_valid[appl[index]] = time_interval.get_time_list(unique_types=unique_types, appliance=appliance)
    all_appliances[appl[index]] = appliance
    for types in unique_types:
        all_appliances[appl[index]][types].fillna(0, inplace=True)

#Initialize and run the optimizer
time_list = {**time_list_valid['batterij']['Zonder opwek'], **time_list_valid['batterij']['Met opwek']}
#time_list = time_list_valid['batterij']['Zonder opwek']
appliance_list = pd.concat([all_appliances['batterij']['Zonder opwek'].loc[:, main_keys + bat_keys],all_appliances['batterij']['Met opwek'].loc[:, main_keys + bat_keys]])
#appliance_list = all_appliances['batterij']['Zonder opwek'].loc[:, main_keys + bat_keys]

optimizer_imbalance = optimizer(allocation_trading=allocation_trading,batterij=appliance_list, onbalanskosten=onbalanskosten, ZWC=ZWC, temperature=temperature['DE BILT AWS'], current_interval=current_interval, DA_bid=DA_bid,date=date)
optimizer_imbalance.run(time_list_valid=time_list)





