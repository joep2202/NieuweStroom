import pandas as pd

data = []
month = ['02', '03']
dates = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
Good_day = ['0206', '0212', '0218', '0224', '0229', '0301', '0307','0313','0319','0325','0331']

# for x in range(len(Good_day)):
#     #for y in range(1):
#     data_1 = pd.read_csv(f"data/solar_data/solar_data_2024{Good_day[x]}.csv")
#     column_names = data_1['stationname'].to_list()
#     # transpose df and set reset index
#     data_1 = data_1.T
#     data_1.columns = column_names
#     data_1 = data_1.drop('stationname')
#     data_1 = data_1.reset_index()
#     data_1 = data_1[~data_1['index'].str.contains('Unnamed')]
#     data.append(data_1)
#     print(x)
#
# concatenated_df = pd.concat(data, ignore_index=True)
#
# concatenated_df.to_csv('data/solar_data/solar_data_FebMarch.csv')
# print(concatenated_df)

# for x in range(len(Good_day)):
#     #for y in range(1):
#     data_1 = pd.read_csv(f"data/temperature_data/temperature_data_2024{Good_day[x]}.csv")
#     column_names = data_1['stationname'].to_list()
#     # transpose df and set reset index
#     data_1 = data_1.T
#     data_1.columns = column_names
#     data_1 = data_1.drop('stationname')
#     data_1 = data_1.reset_index()
#     data_1 = data_1[~data_1['index'].str.contains('Unnamed')]
#     data.append(data_1)
#     #print(x)
#
# concatenated_df = pd.concat(data, ignore_index=True)
#
# concatenated_df.to_csv('data/temperature_data/temperature_data_FebMarch.csv')
# print(concatenated_df)


data_dec = pd.read_csv(f"data/temperature_data/temperature_data_december.csv")

data_feb = pd.read_csv(f"data/temperature_data/temperature_data_FebMarch.csv")

data_total = pd.concat([data_dec, data_feb.reset_index(drop=True)], ignore_index=True, axis=0)
#data_total.reset_index(drop=True, inplace=True)
data_total.to_csv('data/temperature_data/temperature_data_complete.csv')
print(data_total)