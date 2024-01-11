import pandas as pd

batterij_unique = {}
EV_unique = {}
AC_unique = {}
KC_unique = {}
WP_buffer_unique = {}
WP_no_buffer_unique = {}
WWB_unique = {}
overig_unique = {}

data = pd.read_csv("data/data2.csv")
main_keys = ['company_name','customer_id','Branche','PiekAansluiting','ICT_METER','type_flex','type_appl']
bat_keys = ['model_bat','charge_KW_bat','size_kWh_bat','start_time_bat','end_time_bat','start_time2_bat','end_time2_bat','IP_bat','ICT_APPL_bat','functie_batterij_bat','Remarks_bat']
EV_keys = ['model_ev','aantal_palen','charge_KW_ev','size_kWh_ev','start_time_ev','end_time_ev','IP_ev','ICT_APPL_ev','Remarks_ev']
AC_keys = ['model_ac','aantal_ac','cap_1_ac','cap_alle_ac','start_time_ac','end_time_ac','IP_ac','ICT_APPL_ac','Remarks_ac']
KC_keys = ['model_kc','verbruik_kc','min_temp_kc','max_temp_kc','IP_kc','ICT_APPL_kc','Remarks_kc']
WP_keys_buf = ['model_wp','aantal_wp','cap_1_wp','cap_alle_wp','start_time_wp','end_time_wp','IP_wp','ICT_APPL_wp','buffer_ja','buffer_nee','model_buf','charge_KW_buf','size_kWh_buf','IP_buf','ICT_APPL_buf','Remarks_wp']
WP_keys_no_buf = ['model_wp','aantal_wp','cap_1_wp','cap_alle_wp','start_time_wp','end_time_wp','IP_wp','ICT_APPL_wp','Remarks_wp']
WWB_keys = ['model_wwb','cap_liters_wwb','cap_kw_wwb','min_temp_wwb','max_temp_wwb','IP_wwb','ICT_APPL_wwb','Remarks_wwb']
overig_keys = ['model_overig','functie_overig','charge_KW_overig','size_kWh_overig','start_time_overig','end_time_overig','start_time2_overig','end_time2_overig','start_time_overig0','end_time_overig1','min_temp_overig','max_temp_overig','IP_overig','ICT_APPL_overig','Remarks_overig']
unique_type_flex = data['type_flex'].unique()
#print(unique_type_flex)


def batterij():
    batterij = data[data['type_appl'] == 'Batterij']
    batterij = batterij.loc[:, main_keys + bat_keys]
    for type in unique_type_flex:
        batterij_unique[type] = batterij[batterij['type_flex'] == type]
        print(batterij_unique[type].to_string())
    print(batterij.to_string())


def EVlaadpaal():
    EV = data[data['type_appl'] == 'EV laadpaal']
    EV = EV.loc[:, main_keys + EV_keys]
    for type in unique_type_flex:
        EV_unique[type] = EV[EV['type_flex'] == type]
        print(EV_unique[type].to_string())
    #print(EV.to_string())

def AC():
    AC = data[data['type_appl'] == 'AC']
    AC = AC.loc[:, main_keys + bat_keys]
    for type in unique_type_flex:
        AC_unique[type] = AC[AC['type_flex'] == type]
        print(AC_unique[type].to_string())
    #print(AC.to_string())

def KC():
    KC = data[data['type_appl'] == 'Koelcel']
    KC = KC.loc[:, main_keys + bat_keys]
    for type in unique_type_flex:
        KC_unique[type] = KC[KC['type_flex'] == type]
        print(KC_unique[type].to_string())
    #print(KC.to_string())

def WP():
    warmtepomp = data[data['type_appl'] == 'Warmtepomp']
    warmtepomp_buf = warmtepomp[warmtepomp['buffer_ja'] == True]
    warmtepomp_no_buf = warmtepomp[warmtepomp['buffer_ja'] == False]
    warmtepomp_buf = warmtepomp_buf.loc[:, main_keys + WP_keys_buf]
    warmtepomp_no_buf = warmtepomp_no_buf.loc[:, main_keys + WP_keys_no_buf]
    for type in unique_type_flex:
        WP_buffer_unique[type] = warmtepomp_buf[warmtepomp_buf['type_flex'] == type]
        WP_no_buffer_unique[type] = warmtepomp_no_buf[warmtepomp_no_buf['type_flex'] == type]
        print(WP_no_buffer_unique[type].to_string())
        print(WP_buffer_unique[type].to_string())
    #print(warmtepomp_buf.to_string())
    #print(warmtepomp_no_buf.to_string())

def WWB():
    WWB = data[data['type_appl'] == 'Warm water boiler']
    WWB = WWB.loc[:, main_keys + bat_keys]
    for type in unique_type_flex:
        WWB_unique[type] = WWB[WWB['type_flex'] == type]
        print(WWB_unique[type].to_string())
    #print(WWB.to_string())

def overig():
    overig = data[data['type_appl'] == 'Overig']
    overig = overig.loc[:, main_keys + bat_keys]
    for type in unique_type_flex:
        overig_unique[type] = overig[overig['type_flex'] == type]
        print(overig_unique[type].to_string())
    #print(overig.to_string())


batterij()
EVlaadpaal()
AC()
KC()
WP()
WWB()
overig()