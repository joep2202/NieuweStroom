from Data_retrieval import data_retrieval
from datetime import datetime, timedelta
import pandas as pd


data_retr = data_retrieval()
unique_types = data_retr.return_unique()
time_lists_valid = {}


def generate_time_intervals(start_time, end_time, interval_minutes=15):
    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')

    # Initialize a list of 1s and 0s for each 15-minute interval
    time_intervals = []

    # Generate 15-minute intervals and assign 1 to intervals within the specified time frame
    current_time = datetime.strptime('00:00', '%H:%M')
    while current_time < datetime.strptime('23:59', '%H:%M'):
        time_intervals.append(int(start_time <= current_time < end_time))
        current_time += timedelta(minutes=interval_minutes)
    return time_intervals

#batterij = data_retr.batterij()
batterij, EVlaadpaal, AC, KC, WP, WWB, overig = data_retr.get_all()
print(batterij['Met opwek'].to_string())
print(batterij['Zonder opwek'].to_string())
for option in ['Met opwek','Zonder opwek']:
    print(option)
    for index, row in batterij[option].iterrows():
        time_lists_valid[str(index)] = generate_time_intervals(row['start_time_bat'], row['end_time_bat'])
        if not pd.isna(row['start_time2_bat']):
            time_lists_valid[str(index)+'A'] = generate_time_intervals(row['start_time2_bat'], row['end_time2_bat'])

print(time_lists_valid)





