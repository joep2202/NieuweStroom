import pandas as pd

class data_retrieval:
    def __init__(self):
        self.batterij_unique = {}
        self.EV_unique = {}
        self.AC_unique = {}
        self.KC_unique = {}
        self.WP_buffer_unique = {}
        self.WP_no_buffer_unique = {}
        self. WWB_unique = {}
        self.overig_unique = {}

        self.data = pd.read_csv("data/data2.csv")
        self.main_keys = ['company_name','customer_id','Branche','PiekAansluiting','ICT_METER','type_flex','type_appl']
        self.bat_keys = ['model_bat','charge_KW_bat','size_kWh_bat','start_time_bat','end_time_bat','start_time2_bat','end_time2_bat','IP_bat','ICT_APPL_bat','functie_batterij_bat','Remarks_bat']
        self.EV_keys = ['model_ev','aantal_palen','charge_KW_ev','size_kWh_ev','start_time_ev','end_time_ev','IP_ev','ICT_APPL_ev','Remarks_ev']
        self.AC_keys = ['model_ac','aantal_ac','cap_1_ac','cap_alle_ac','start_time_ac','end_time_ac','IP_ac','ICT_APPL_ac','Remarks_ac']
        self.KC_keys = ['model_kc','verbruik_kc','min_temp_kc','max_temp_kc','IP_kc','ICT_APPL_kc','Remarks_kc']
        self.WP_keys_buf = ['model_wp','aantal_wp','cap_1_wp','cap_alle_wp','start_time_wp','end_time_wp','IP_wp','ICT_APPL_wp','buffer_ja','buffer_nee','model_buf','charge_KW_buf','size_kWh_buf','IP_buf','ICT_APPL_buf','Remarks_wp']
        self.WP_keys_no_buf = ['model_wp','aantal_wp','cap_1_wp','cap_alle_wp','start_time_wp','end_time_wp','IP_wp','ICT_APPL_wp','Remarks_wp']
        self.WWB_keys = ['model_wwb','cap_liters_wwb','cap_kw_wwb','min_temp_wwb','max_temp_wwb','IP_wwb','ICT_APPL_wwb','Remarks_wwb']
        self.overig_keys = ['model_overig','functie_overig','charge_KW_overig','size_kWh_overig','start_time_overig','end_time_overig','start_time2_overig','end_time2_overig','start_time_overig0','end_time_overig1','min_temp_overig','max_temp_overig','IP_overig','ICT_APPL_overig','Remarks_overig']
        self.unique_type_flex = self.data['type_flex'].unique()
        #print(unique_type_flex)

    def return_unique(self):
        return self.unique_type_flex


    def batterij(self):
        batterij = self.data[self.data['type_appl'] == 'Batterij']
        batterij = batterij.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.batterij_unique[type] = batterij[batterij['type_flex'] == type]
        #     print(self.batterij_unique[type].to_string())
        # print(batterij.to_string())
        return self.batterij_unique


    def EVlaadpaal(self):
        EV = self.data[self.data['type_appl'] == 'EV laadpaal']
        EV = EV.loc[:, self.main_keys + self.EV_keys]
        for type in self.unique_type_flex:
            self.EV_unique[type] = EV[EV['type_flex'] == type]
            # print(self.EV_unique[type].to_string())
        #print(EV.to_string())
        return self.EV_unique

    def AC(self):
        AC = self.data[self.data['type_appl'] == 'AC']
        AC = AC.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.AC_unique[type] = AC[AC['type_flex'] == type]
            # print(self.AC_unique[type].to_string())
        #print(AC.to_string())
        return self.AC_unique

    def KC(self):
        KC = self.data[self.data['type_appl'] == 'Koelcel']
        KC = KC.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.KC_unique[type] = KC[KC['type_flex'] == type]
            # print(self.KC_unique[type].to_string())
        #print(KC.to_string())
        return self.KC_unique

    def WP(self):
        warmtepomp = self.data[self.data['type_appl'] == 'Warmtepomp']
        warmtepomp_buf = warmtepomp[warmtepomp['buffer_ja'] == True]
        warmtepomp_no_buf = warmtepomp[warmtepomp['buffer_ja'] == False]
        warmtepomp_buf = warmtepomp_buf.loc[:, self.main_keys + self.WP_keys_buf]
        warmtepomp_no_buf = warmtepomp_no_buf.loc[:, self.main_keys + self.WP_keys_no_buf]
        for type in self.unique_type_flex:
            self.WP_buffer_unique[type] = warmtepomp_buf[warmtepomp_buf['type_flex'] == type]
            self.WP_no_buffer_unique[type] = warmtepomp_no_buf[warmtepomp_no_buf['type_flex'] == type]
            # print(self.WP_no_buffer_unique[type].to_string())
            # print(self.WP_buffer_unique[type].to_string())
        #print(warmtepomp_buf.to_string())
        #print(warmtepomp_no_buf.to_string())
        return self.WP_buffer_unique, self.WP_no_buffer_unique

    def WWB(self):
        WWB = self.data[self.data['type_appl'] == 'Warm water boiler']
        WWB = WWB.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.WWB_unique[type] = WWB[WWB['type_flex'] == type]
            # print(self.WWB_unique[type].to_string())
        #print(WWB.to_string())
        return self.WWB_unique

    def overig(self):
        overig = self.data[self.data['type_appl'] == 'Overig']
        overig = overig.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.overig_unique[type] = overig[overig['type_flex'] == type]
            # print(self.overig_unique[type].to_string())
        #print(overig.to_string())
        return self.overig_unique

    def run(self):
        self.batterij()
        self.EVlaadpaal()
        self.AC()
        self.KC()
        self.WP()
        self.WWB()
        self.overig()