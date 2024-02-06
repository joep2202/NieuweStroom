import pandas as pd

# Assuming 'filename' is the path to your CSV file
filename = "data/temperature_data/temperature_data_20231201.csv"
# Read the CSV file into a DataFrame
df = pd.read_csv(filename, index_col=0)
column_names = df['stationname'].to_list()
x= 0

df = df.T
df.columns = column_names
df = df.drop('stationname')
df = df.reset_index()
print(df.to_string())

# Specify the start date and time
start_datetime = '2023-12-01 00:00:00'

# Specify the end date and time (assuming a full day)
end_datetime = '2023-12-01 23:45:00'

# Create the datetime index with a frequency of 15 seconds
datetime_index = pd.date_range(start=start_datetime, end=end_datetime, freq='15min')

# Create a DataFrame with the datetime index
new_df = pd.DataFrame()
new_df['time'] = datetime_index
#print(new_df)

#dit moet gefixt worden, staat dingen in mijn schrift.
for names in column_names:
    for index, date in enumerate(new_df.loc[:,'time']):
        new_df.loc[index, names] = ((df.loc[x,names]*2)+df.loc[x+1,names])/3
        new_df.loc[index, names] = ((df.loc[x, names]) + (df.loc[x + 1, names]*2)) / 3
print(new_df.to_string())