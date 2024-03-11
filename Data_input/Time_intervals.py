from datetime import datetime, timedelta
import pandas as pd

class time_intervals:
    def __init__(self,current_interval, timestamp, timestamp_hour, length_forecast):
        self.current_interval = current_interval
        self.date = timestamp
        self.timestamp_hour = timestamp_hour
        self.length_forecast =length_forecast
        self.x = 0

    def generate_time_intervals(self, start_time, end_time, start_time2, end_time2):
        counter = 0
        interval_minutes = 15
        double = False                                              #boolean if an appliance can be used in multiple timeframes
        start_time = datetime.strptime(start_time, '%H:%M')         #start/end time of flex availability
        end_time = datetime.strptime(end_time, '%H:%M')
        #initialize for a second timeframe if necessary
        if start_time2 != 0:
            double = True
            start_time2 = datetime.strptime(start_time2, '%H:%M')
            end_time2 = datetime.strptime(end_time2, '%H:%M')

        # Initialize a list of 1s and 0s for each 15-minute interval
        time_intervals = []

        # Generate 15-minute intervals and assign 1 to intervals within the specified time frame
        date_object_hour = datetime.strptime(self.timestamp_hour, '%H:%M')
        current_time = datetime.strptime(self.timestamp_hour, '%H:%M')
        datetime_start = datetime.combine(self.date.date(), date_object_hour.time())
        date_object_end = datetime_start + timedelta(minutes=15 * (self.length_forecast - 1))
        if double == True:
            while counter < self.length_forecast:
                time_intervals.append(int((start_time.time() <= current_time.time() < end_time.time()) or (start_time2.time() <= current_time.time() < end_time2.time())))
                current_time += timedelta(minutes=interval_minutes)
                counter += 1
        if double == False:
            while counter < self.length_forecast:
                time_intervals.append(int(start_time.time() <= current_time.time() < end_time.time()))
                current_time += timedelta(minutes=interval_minutes)
                counter += 1
        return time_intervals

    def get_time_list(self, unique_types, appliance):
        self.time_lists_valid = {}
        filtered_columns = []
        #Iterate through the options for the appliance and make an time_list per individual appliance
        for option in unique_types:
            self.time_lists_valid[option] = {}
            #Check if a time list is necessary for the selected appliance
            filtered_columns = [col for col in appliance[option].columns.to_list() if 'start_time' in col or 'end_time' in col]
            filtered_columns = filtered_columns[0:4]
            for index, row in appliance[option].iterrows():
                #If there is one timeframe
                if len(filtered_columns) > 0 and len(filtered_columns) <= 2:
                    #Check if the necessary data is there
                    if not pd.isna(row[filtered_columns[0]]) and not pd.isna(row[filtered_columns[1]]):
                        self.time_lists_valid[option][row['appl_id_main']] = self.generate_time_intervals(row[filtered_columns[0]], row[filtered_columns[1]], 0, 0)
                #if there is more then one timeframe
                if len(filtered_columns) > 2:
                    # Check if the necessary data is there
                    if not pd.isna(row[filtered_columns[0]]) and not pd.isna(row[filtered_columns[1]]) and not pd.isna(row[filtered_columns[2]]) and not pd.isna(row[filtered_columns[3]]):
                        self.time_lists_valid[option][row['appl_id_main']] = self.generate_time_intervals(row[filtered_columns[0]], row[filtered_columns[1]], row[filtered_columns[2]], row[filtered_columns[3]])
                    if not pd.isna(row[filtered_columns[0]]) and not pd.isna(row[filtered_columns[1]]) and pd.isna(row[filtered_columns[2]]) and pd.isna(row[filtered_columns[3]]):
                        self.time_lists_valid[option][row['appl_id_main']] = self.generate_time_intervals(row[filtered_columns[0]], row[filtered_columns[1]], 0,0)
        return self.time_lists_valid