import pandas as pd

data = []

dates = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']

for x in range(31):
    data_1 = pd.read_csv(f"data/temperature_data/temperature_data_202312{dates[x]}.csv")
    column_names = data_1['stationname'].to_list()
    # transpose df and set reset index
    data_1 = data_1.T
    data_1.columns = column_names
    data_1 = data_1.drop('stationname')
    data_1 = data_1.reset_index()
    data_1 = data_1[~data_1['index'].str.contains('Unnamed')]
    data.append(data_1)
    print(x)

concatenated_df = pd.concat(data, ignore_index=True)

concatenated_df.to_csv('data/temperature_data/temperature_data_december.csv')
print(concatenated_df)