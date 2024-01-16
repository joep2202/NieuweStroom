from Data_retrieval import data_retrieval
from keys_creation import keys
import pandas as pd


data_retr = data_retrieval()
keys = keys()


unique_types = data_retr.return_unique()
batterij, EVlaadpaal, AC, KC, WP, WWB, overig = data_retr.get_all()
time_list_valid = keys.get_time_list(unique_types=unique_types, batterij=batterij)
print(time_list_valid)





