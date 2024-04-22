import pandas as pd
import numpy as np
from datetime import datetime
import os
#from TempAPICall import TemperatureAPICall
from datetime import datetime, timedelta

class retrieve_temp:
    def __init__(self, timestamp, current_interval, length_forecast, timestamp_hour):
        self.timestamp = timestamp
        self.current_interval = current_interval
        self.length_forecast = length_forecast
        self.timestamp_hour = timestamp_hour
        print(self.timestamp_hour)
        self.time_object = datetime.strptime(self.timestamp_hour, '%H:%M')
        minute = self.time_object.minute
        if minute in [15, 45]:
            self.time_object -= timedelta(minutes=minute % 10)
        self.formatted_time = self.time_object.strftime('%H:%M')
        # self.rounded_time = (self.time_object - timedelta(minutes=5)).replace(second=0, microsecond=0)
        # self.rounded_time -= timedelta(minutes=self.rounded_time.minute % 10)
        # self.rounded_time_string = self.rounded_time.strftime('%H:%M')
        self.date_object = datetime.strptime(str(self.timestamp), '%Y%m%d')
        self.formatted_date = self.date_object.strftime('%d/%m/%Y')
        #Get file with temperature data if it exists
        #self.filename = f"data/temperature_data/temperature_data_{self.timestamp}.csv"
        #If there is no file call API to get the right temperature data
        # if not os.path.exists(self.filename):
        #     run_api = TemperatureAPICall(timestamp=timestamp)
        #     run_api.main()
        # Read the CSV file into a DataFrame
        #self.filename = f"data/temperature_data/temperature_data_december.csv"
        self.filename = f"data/temperature_data/temperature_data_complete.csv"
        self.temp = pd.read_csv(self.filename, index_col=0)
        self.column_names = self.temp.columns
        self.column_names = self.column_names[1:]
        self.start_temp = self.temp[self.temp['Date'].str.contains(self.formatted_date+' ' + self.formatted_time)]
        self.start_temp = self.start_temp.index[0]
        self.temp = self.temp.iloc[self.start_temp:self.start_temp + int(self.length_forecast*1.6)]
        self.temp.reset_index(inplace=True, drop=True)


        self.new_df = pd.DataFrame()
        #transpose df and set reset index
        # self.temp = self.temp.T
        # self.temp.columns = self.column_names
        # self.temp = self.temp.drop('stationname')
        # self.temp = self.temp.reset_index()
        #create 3 lists to change 10 minute data into 15 minute data
        self.sequence_1 = np.array([])
        self.sequence_2A = np.array([])
        self.sequence_2 = np.array([])

    def clear_files(self):
        #Clear the temporary files
        directory = "data/temperature_data/TempAPIData"
        # Iterate over all files and subdirectories in the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            # Check if the item is a file
            if os.path.isfile(item_path):
                # Remove the file
                os.remove(item_path)

    def change_into_15min(self):
        #change the timestamp into correct time format
        datetime_str = str(self.formatted_date+' ' + self.timestamp_hour)
        date_object_start = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M') #'%Y-%m-%d %H:%M'
        date_object_end = date_object_start + timedelta(minutes=15 * (self.length_forecast-1))
        # Create the datetime index with a frequency of 15 minutes
        datetime_index = pd.date_range(start=date_object_start, end=date_object_end, freq='15min')
        #Set 15 minute intervals to a df
        self.new_df['time'] = datetime_index
        #create lists that are used to fill the data properly
        for n in range(1,len(self.temp)+1,3):
            self.sequence_1 = np.append(self.sequence_1, n)
            self.sequence_1 = np.append(self.sequence_1, n)
            self.sequence_2A = np.append(self.sequence_1, n)

        for n in range(0,len(self.temp)):
            self.sequence_2 = np.append(self.sequence_2, n)

        self.sequence_2 = [int(x) for x in self.sequence_2 if x not in self.sequence_2A]

        # print(len(self.temp))
        # print(len(self.sequence_1),self.sequence_1)
        # print(len(self.sequence_2),self.sequence_2)
        # print(self.temp)

        #fill the new df by selecting right data from 10 minutes interval using above sequences.
        for names in self.column_names:
            for index, date in enumerate(self.new_df.loc[:,'time']):
                self.new_df.loc[index, names] = ((self.temp.loc[self.sequence_2[index], names]*2)+self.temp.loc[self.sequence_1[index],names])/3

        self.clear_files()
        #print('new_df', self.new_df)
        return self.new_df
