from datetime import datetime, timedelta
import pandas as pd

class time_intervals:
    def generate_time_intervals(self, start_time, end_time, start_time2, end_time2, interval_minutes=15):
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
        current_time = datetime.strptime('00:00', '%H:%M')
        if double == True:
            while current_time < datetime.strptime('23:59', '%H:%M'):
                time_intervals.append(int((start_time <= current_time < end_time) or (start_time2 <= current_time < end_time2)))
                current_time += timedelta(minutes=interval_minutes)
        if double == False:
            while current_time < datetime.strptime('23:59', '%H:%M'):
                time_intervals.append(int(start_time <= current_time < end_time))
                current_time += timedelta(minutes=interval_minutes)
        #print(time_intervals)
        return time_intervals

    def get_time_list(self, unique_types, appliance):
        self.time_lists_valid = {}
        filtered_columns = []
        #Iterate through the options for the appliance and make an time_list per individual appliance
        for option in unique_types:
            self.time_lists_valid[option] = {}
            #Check if a time list is necessary for the selected appliance
            filtered_columns = [col for col in appliance[option].columns.to_list() if 'start_time' in col or 'end_time' in col]
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