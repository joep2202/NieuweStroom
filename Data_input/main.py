#import classes from other files
from Data_retrieval_appliances import data_retrieval_appliances
from Time_intervals import time_intervals
from imbalance_optimzer import optimizer
from TempDataRetrieval import retrieve_temp
from SolarDataRetrieval import retrieve_solar
from Data_retrieval_Tennet_situation import import_data_per_day
import pandas as pd

#import libraries
from datetime import datetime

#20240201 20231201
timestamp= 20240229                            #select the data for which the code runs
current_interval = 24                                  #select interval from which the code runs
length_forecast = 72

# for i in range(1,32):
#     print(i)
#change dates to usable format
date_temp = datetime.strptime(str(timestamp), '%Y%m%d')
date = date_temp.strftime('%d/%m/%Y')

#initialize classes
import_data_base_situation = import_data_per_day()
timestamp_hour = import_data_base_situation.interval_to_time(current_interval)
temperature_call = retrieve_temp(timestamp=timestamp, current_interval=current_interval, length_forecast=length_forecast, timestamp_hour=timestamp_hour)
solar_radiation_call = retrieve_solar(timestamp=timestamp, current_interval=current_interval, length_forecast=length_forecast, timestamp_hour=timestamp_hour)
data_retr_appl = data_retrieval_appliances(current_interval=current_interval, length_forecast=length_forecast)
time_interval = time_intervals(current_interval=current_interval, timestamp=date_temp, timestamp_hour=timestamp_hour, length_forecast=length_forecast)

#get the outside data
allocation_trading, onbalanskosten, ZWC, DA_bid = import_data_base_situation.get_data(day=date, current_interval=current_interval, length_forecast=length_forecast)
temperature = temperature_call.change_into_15min()
solar_radiation = solar_radiation_call.change_into_15min()
unique_types = data_retr_appl.return_unique()

solar_average = solar_radiation.columns[1:]
solar_avg = solar_radiation[solar_average].mean(axis=1)
temperature_average = temperature.columns[1:]
temp_avg = temperature[temperature_average].mean(axis=1)

#Create two dicts that holds the appliance information
time_list_valid = {}
all_appliances = {}
#Create lists to select the relevant data needed for the optimizer
appl = ['batterij', 'EVlaadpaal', 'AC', 'KC', 'WP_buf', 'WP_no_buf', 'WWB', 'overig', 'Zonnepanelen']
main_keys = ['appl_id_main','PiekAansluiting_main', 'type_flex_main']
bat_keys = ['charge_KW_bat','size_kWh_bat','SOC_eind_1_bat','end_time_PTE_bat', 'SOC_eind_2_bat','end_time_PTE2_bat', 'kwh_costs_bat', 'efficiency_bat', 'ICT_APPL_bat']
zon_keys = ['model_zon', 'kwp_zon', 'm2_zon', 'ICT_APPL_zon']


#retrieve the data per appliance and create a list per appliance when flex is available
for index, appliance in enumerate(data_retr_appl.get_all()):
    #print(index)
    time_list_valid[appl[index]] = time_interval.get_time_list(unique_types=unique_types, appliance=appliance)
    all_appliances[appl[index]] = appliance
    for types in unique_types:
        all_appliances[appl[index]][types].fillna(0, inplace=True)

#Initialize and run the optimizer
time_list = {**time_list_valid['batterij']['Zonder opwek'], **time_list_valid['batterij']['Met opwek']}
#print(all_appliances['batterij']['Zonder opwek'].loc[:, main_keys + bat_keys].to_string())
appliance_list_bat = pd.concat([all_appliances['batterij']['Zonder opwek'].loc[:, main_keys + bat_keys],all_appliances['batterij']['Met opwek'].loc[:, main_keys + bat_keys]])
appliance_list_zon = all_appliances['Zonnepanelen']['Limiteren van gebruik'].loc[:, main_keys + zon_keys]
#appliance_list = all_appliances['batterij']['Zonder opwek'].loc[:, main_keys + bat_keys]

optimizer_imbalance = optimizer(allocation_trading=allocation_trading,batterij=appliance_list_bat, PV=appliance_list_zon, onbalanskosten=onbalanskosten, ZWC=ZWC, temperature=temp_avg, radiation=solar_avg, current_interval=current_interval, DA_bid=DA_bid,date=date, length_forecast=length_forecast, timestamp=timestamp)
optimizer_imbalance.run(time_list_valid=time_list)





