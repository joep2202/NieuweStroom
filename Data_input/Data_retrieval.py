import pandas as pd
from keys_creation import keys

class data_retrieval:
    def __init__(self):
        keys_order = keys()
        self.batterij_unique = {}
        self.EV_unique = {}
        self.AC_unique = {}
        self.KC_unique = {}
        self.WP_buffer_unique = {}
        self.WP_no_buffer_unique = {}
        self. WWB_unique = {}
        self.overig_unique = {}
        self.data = pd.read_csv("data/data2.csv")
        self.unique_type_flex = self.data['type_flex_main'].unique()
        self.main_keys, self.bat_keys, self.EV_keys, self.AC_keys, self.KC_keys, self.WP_keys_buf, self.WP_keys_no_buf, self.WWB_keys, self.overig_keys = keys_order.keys_creation(data=self.data)
        #print(unique_type_flex)

    def return_unique(self):
        return self.unique_type_flex


    def batterij(self):
        batterij = self.data[self.data['type_appl_main'] == 'Batterij']
        batterij = batterij.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.batterij_unique[type] = batterij[batterij['type_flex_main'] == type]
        #     print(self.batterij_unique[type].to_string())
        # print(batterij.to_string())
        return self.batterij_unique

    def EVlaadpaal(self):
        EV = self.data[self.data['type_appl_main'] == 'EV laadpaal']
        EV = EV.loc[:, self.main_keys + self.EV_keys]
        for type in self.unique_type_flex:
            self.EV_unique[type] = EV[EV['type_flex_main'] == type]
            # print(self.EV_unique[type].to_string())
        #print(EV.to_string())
        return self.EV_unique

    def AC(self):
        AC = self.data[self.data['type_appl_main'] == 'AC']
        AC = AC.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.AC_unique[type] = AC[AC['type_flex_main'] == type]
            # print(self.AC_unique[type].to_string())
        #print(AC.to_string())
        return self.AC_unique

    def KC(self):
        KC = self.data[self.data['type_appl_main'] == 'Koelcel']
        KC = KC.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.KC_unique[type] = KC[KC['type_flex_main'] == type]
            # print(self.KC_unique[type].to_string())
        #print(KC.to_string())
        return self.KC_unique

    def WP(self):
        warmtepomp = self.data[self.data['type_appl_main'] == 'Warmtepomp']
        warmtepomp_buf = warmtepomp[warmtepomp['buffer_ja_buf'] == True]
        warmtepomp_no_buf = warmtepomp[warmtepomp['buffer_ja_buf'] == False]
        warmtepomp_buf = warmtepomp_buf.loc[:, self.main_keys + self.WP_keys_buf]
        warmtepomp_no_buf = warmtepomp_no_buf.loc[:, self.main_keys + self.WP_keys_no_buf]
        for type in self.unique_type_flex:
            self.WP_buffer_unique[type] = warmtepomp_buf[warmtepomp_buf['type_flex_main'] == type]
            self.WP_no_buffer_unique[type] = warmtepomp_no_buf[warmtepomp_no_buf['type_flex_main'] == type]
            # print(self.WP_no_buffer_unique[type].to_string())
            # print(self.WP_buffer_unique[type].to_string())
        #print(warmtepomp_buf.to_string())
        #print(warmtepomp_no_buf.to_string())
        return self.WP_buffer_unique, self.WP_no_buffer_unique

    def WWB(self):
        WWB = self.data[self.data['type_appl_main'] == 'Warm water boiler']
        WWB = WWB.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.WWB_unique[type] = WWB[WWB['type_flex_main'] == type]
            # print(self.WWB_unique[type].to_string())
        #print(WWB.to_string())
        return self.WWB_unique

    def overig(self):
        overig = self.data[self.data['type_appl_main'] == 'Overig']
        overig = overig.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.overig_unique[type] = overig[overig['type_flex_main'] == type]
            # print(self.overig_unique[type].to_string())
        #print(overig.to_string())
        return self.overig_unique

    def get_all(self):
        return self.batterij(), self.EVlaadpaal(), self.AC(), self.KC(), self.WP(), self.WWB(), self.overig()