import pandas as pd

class data_retrieval_appliances:
    def __init__(self):
        #create dicts to store information from appliances per type of appliance
        self.batterij_unique = {}
        self.EV_unique = {}
        self.AC_unique = {}
        self.KC_unique = {}
        self.WP_buffer_unique = {}
        self.WP_no_buffer_unique = {}
        self. WWB_unique = {}
        self.overig_unique = {}
        #read data from flex input
        self.data = pd.read_csv("data/data2.csv")
        #get unique types of flex {curtailable, shiftable(advance, delay, both), mobile storage etc.}
        self.unique_type_flex = self.data['type_flex_main'].unique()
        #retrieve the keys per question from flex input
        self.main_keys, self.bat_keys, self.EV_keys, self.AC_keys, self.KC_keys, self.WP_keys_buf, self.WP_keys_no_buf, self.WWB_keys, self.overig_keys = self.keys_creation(data=self.data)

    def return_unique(self):
        #Function to easily call all the unique types
        return self.unique_type_flex

    def keys_creation(self, data):
        self.column_names = data.columns.tolist()
        #from the columns of the data divide the keys per type of appliance and return them
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
        return self.main_keys, self.bat_keys, self.EV_keys,self.AC_keys, self.KC_keys, self.WP_keys_buf, self.WP_keys_no_buf, self.WWB_keys, self.overig_keys


    #per type of appliance filter out non relevant information so the size of the df is decreased and logical
    def batterij(self):
        batterij = self.data[self.data['type_appl_main'] == 'Batterij']
        batterij = batterij.loc[:, self.main_keys + self.bat_keys]
        for type in self.unique_type_flex:
            self.batterij_unique[type] = batterij[batterij['type_flex_main'] == type]
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
        AC = AC.loc[:, self.main_keys + self.AC_keys]
        for type in self.unique_type_flex:
            self.AC_unique[type] = AC[AC['type_flex_main'] == type]
            # print(self.AC_unique[type].to_string())
        #print(AC.to_string())
        return self.AC_unique

    def KC(self):
        KC = self.data[self.data['type_appl_main'] == 'Koelcel']
        KC = KC.loc[:, self.main_keys + self.KC_keys]
        for type in self.unique_type_flex:
            self.KC_unique[type] = KC[KC['type_flex_main'] == type]
            # print(self.KC_unique[type].to_string())
        #print(KC.to_string())
        return self.KC_unique

    def WP_buf(self):
        warmtepomp = self.data[self.data['type_appl_main'] == 'Warmtepomp']
        warmtepomp_buf = warmtepomp[warmtepomp['buffer_ja_buf'] == True]
        warmtepomp_buf = warmtepomp_buf.loc[:, self.main_keys + self.WP_keys_buf]
        for type in self.unique_type_flex:
            self.WP_buffer_unique[type] = warmtepomp_buf[warmtepomp_buf['type_flex_main'] == type]
        return self.WP_buffer_unique

    def WP_no_buf(self):
        warmtepomp = self.data[self.data['type_appl_main'] == 'Warmtepomp']
        warmtepomp_no_buf = warmtepomp[warmtepomp['buffer_ja_buf'] == False]
        warmtepomp_no_buf = warmtepomp_no_buf.loc[:, self.main_keys + self.WP_keys_no_buf]
        for type in self.unique_type_flex:
            self.WP_no_buffer_unique[type] = warmtepomp_no_buf[warmtepomp_no_buf['type_flex_main'] == type]
        return self.WP_no_buffer_unique

    def WWB(self):
        WWB = self.data[self.data['type_appl_main'] == 'Warm water boiler']
        WWB = WWB.loc[:, self.main_keys + self.WWB_keys]
        for type in self.unique_type_flex:
            self.WWB_unique[type] = WWB[WWB['type_flex_main'] == type]
            # print(self.WWB_unique[type].to_string())
        #print(WWB.to_string())
        return self.WWB_unique

    def overig(self):
        overig = self.data[self.data['type_appl_main'] == 'Overig']
        overig = overig.loc[:, self.main_keys + self.overig_keys]
        for type in self.unique_type_flex:
            self.overig_unique[type] = overig[overig['type_flex_main'] == type]
            # print(self.overig_unique[type].to_string())
        #print(overig.to_string())
        return self.overig_unique

    def get_all(self):
        #activate all the type of appliances and there relevant information
        return self.batterij(), self.EVlaadpaal(), self.AC(), self.KC(), self.WP_buf(), self.WP_no_buf(), self.WWB(), self.overig()