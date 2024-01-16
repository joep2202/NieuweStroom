
from datetime import datetime, timedelta
import pandas as pd


class keys:
    def __init__(self):
        self.time_lists_valid = {}
       # self.main_keys = ['company_name','customer_id','Branche','PiekAansluiting','ICT_METER','type_flex','type_appl']
       # self.bat_keys = ['model_bat','charge_KW_bat','size_kWh_bat','start_time_bat','end_time_bat','start_time2_bat','end_time2_bat','IP_bat','ICT_APPL_bat','functie_batterij_bat','Remarks_bat']
       # self.EV_keys = ['model_ev','aantal_palen','charge_KW_ev','size_kWh_ev','start_time_ev','end_time_ev','IP_ev','ICT_APPL_ev','Remarks_ev']
       # self.AC_keys = ['model_ac','aantal_ac','cap_1_ac','cap_alle_ac','start_time_ac','end_time_ac','IP_ac','ICT_APPL_ac','Remarks_ac']
       # self.KC_keys = ['model_kc','verbruik_kc','min_temp_kc','max_temp_kc','IP_kc','ICT_APPL_kc','Remarks_kc']
       # self.WP_keys_buf = ['model_wp','aantal_wp','cap_1_wp','cap_alle_wp','start_time_wp','end_time_wp','IP_wp','ICT_APPL_wp','buffer_ja','buffer_nee','model_buf','charge_KW_buf','size_kWh_buf','IP_buf','ICT_APPL_buf','Remarks_wp']
       # self.WP_keys_no_buf = ['model_wp','aantal_wp','cap_1_wp','cap_alle_wp','start_time_wp','end_time_wp','IP_wp','ICT_APPL_wp','Remarks_wp']
       # self.WWB_keys = ['model_wwb','cap_liters_wwb','cap_kw_wwb','min_temp_wwb','max_temp_wwb','IP_wwb','ICT_APPL_wwb','Remarks_wwb']
       # self.overig_keys = ['model_overig','functie_overig','charge_KW_overig','size_kWh_overig','start_time_overig','end_time_overig','start_time2_overig','end_time2_overig','start_time_overig0','end_time_overig1','min_temp_overig','max_temp_overig','IP_overig','ICT_APPL_overig','Remarks_overig']

    def keys_creation(self, data):
        self.column_names = data.columns.tolist()
        self.main_keys = [names for names in self.column_names if 'main' in names]
        self.bat_keys = [names for names in self.column_names if 'bat' in names]
        self.EV_keys = [names for names in self.column_names if 'ev' in names]
        self.AC_keys = [names for names in self.column_names if 'ac' in names]
        self.KC_keys = [names for names in self.column_names if 'kc' in names]
        self.WP_keys_no_buf = [names for names in self.column_names if 'wp' in names]
        self.WP_keys_buf = [names for names in self.column_names if 'buf' in names]
        self.WP_keys_buf =  self.WP_keys_no_buf + self.WP_keys_buf
        self.WWB_keys = [names for names in self.column_names if 'wwb' in names]
        self.overig_keys = [names for names in self.column_names if 'overig' in names]
        self.check = self.main_keys+ self.bat_keys+ self.EV_keys+self.AC_keys+ self.KC_keys+ self.WP_keys_buf+ self.WWB_keys+ self.overig_keys
        # print(self.column_names)
        # print(self.check)
        return self.main_keys, self.bat_keys, self.EV_keys,self.AC_keys, self.KC_keys, self.WP_keys_buf, self.WP_keys_no_buf, self.WWB_keys, self.overig_keys

    def generate_time_intervals(self, start_time, end_time, interval_minutes=15):
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

    def get_time_list(self,unique_types, batterij):
        #print(batterij['Met opwek'].to_string())
        #print(batterij['Zonder opwek'].to_string())
        for option in unique_types:
            #print(option)
            for index, row in batterij[option].iterrows():
                self.time_lists_valid[str(index)] = self.generate_time_intervals(row['start_time_bat'], row['end_time_bat'])
                if not pd.isna(row['start_time2_bat']):
                    self.time_lists_valid[str(index) + 'A'] = self.generate_time_intervals(row['start_time2_bat'],row['end_time2_bat'])
        return self.time_lists_valid