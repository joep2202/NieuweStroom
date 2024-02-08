import pandas as pd
import numpy as np
from datetime import datetime
import os
from TempAPICall import TemperatureAPICall

class retrieve_temp:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        #Get file with temperature data if it exists
        self.filename = f"data/temperature_data/temperature_data_{self.timestamp}.csv"
        #If there is no file call API to get the right temperature data
        if not os.path.exists(self.filename):
            run_api = TemperatureAPICall(timestamp=timestamp)
            run_api.main()
        # Read the CSV file into a DataFrame
        self.df = pd.read_csv(self.filename, index_col=0)
        self.column_names = self.df['stationname'].to_list()
        self.new_df = pd.DataFrame()
        #transpose df and set reset index
        self.df = self.df.T
        self.df.columns = self.column_names
        self.df = self.df.drop('stationname')
        self.df = self.df.reset_index()
        #create 3 lists to change 10 minute data into 15 minute data
        self.sequence_1 = np.array([])
        self.sequence_2A = np.array([])
        self.sequence_2 = np.array([])

    def clear_files(self):
        #Clear the temporary files
        directory = "TempAPIData"
        # Iterate over all files and subdirectories in the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            # Check if the item is a file
            if os.path.isfile(item_path):
                # Remove the file
                os.remove(item_path)

    def change_into_15min(self):
        #change the timestamp into correct time format
        date_object_start = datetime.strptime(str(self.timestamp), '%Y%m%d')
        date_object_end = date_object_start.replace(hour=23, minute=45, second=0)
        # Create the datetime index with a frequency of 15 minutes
        datetime_index = pd.date_range(start=date_object_start, end=date_object_end, freq='15min')
        #Set 15 minute intervals to a df
        self.new_df['time'] = datetime_index
        #create lists that are used to fill the data properly
        for n in range(1,144,3):
            self.sequence_1 = np.append(self.sequence_1, n)
            self.sequence_1 = np.append(self.sequence_1, n)
            self.sequence_2A = np.append(self.sequence_1, n)

        for n in range(0,144):
            self.sequence_2 = np.append(self.sequence_2, n)

        self.sequence_2 = [int(x) for x in self.sequence_2 if x not in self.sequence_2A]

        #fill the new df by selecting right data from 10 minutes interval using above sequences.
        for names in self.column_names:
            for index, date in enumerate(self.new_df.loc[:,'time']):
                self.new_df.loc[index, names] = ((self.df.loc[self.sequence_2[index], names]*2)+self.df.loc[self.sequence_1[index],names])/3

        self.clear_files()
        return self.new_df
