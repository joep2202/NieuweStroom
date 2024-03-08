import pandas as pd
#filepath = 'data/EDM_emailadressen.csv'

# data = pd.read_csv(filepath, encoding='windows-1252')
# columns_to_keep = ['Tenant','ContractGeactiveerd','TypeContract','Bedrijfsnaam','e-mail','Plaats','Aanduiding','DatumLeveringEinde','JaarVerbruik','Meetmethode','TypeNota','MetertypeOmschrijving','soort','Type Levering','SupplyType']
#
# data = data.loc[:,columns_to_keep]
# data = data[data['soort'] == 'ELEK']
# data = data[data['Tenant'] == 'NieuweStroom']
# data.reset_index(inplace=True, drop=True)
#
# data.to_csv('data/reduced_email_list.csv', index=True)
#
# print(data)

filepath = 'data/reduced_email_list.csv'
data = pd.read_csv(filepath, encoding='windows-1252', index_col=0)
data = data.drop_duplicates(subset=['e-mail'])
data = data.fillna(0)
data = data[data['DatumLeveringEinde'] == 0]
#print(data)
data_sep = {}
aantal_mailadressen = 90
#print(data)
already_used = pd.read_csv('data/50_mail_list.csv')

filtered_data = data[~data['e-mail'].isin(already_used['e-mail'])]
print(filtered_data)
print(len(filtered_data), len(data))

unique_values = {}
for column in data.columns:
    unique_values[column] = data[column].unique()
    #print(unique_values[column])

for unique_val in unique_values['SupplyType']:
    data_sep[unique_val] = data[data['SupplyType'] == unique_val]
    #print('unique val', data_sep[unique_val])
    for unique_soort in unique_values['Aanduiding']:
        data_sep[unique_val + unique_soort] = data_sep[unique_val][data_sep[unique_val]['Aanduiding'] == unique_soort]
        #print('unique soort',data_sep[unique_val + unique_soort])
        for unique_meter in unique_values['MetertypeOmschrijving'][1:]:
            #print(unique_meter)
            data_sep[unique_val + unique_soort + unique_meter] = data_sep[unique_val + unique_soort][data_sep[unique_val + unique_soort]['MetertypeOmschrijving'] == unique_meter]
            #print('unique meter',data_sep[unique_val + unique_soort + unique_meter])

save_correct = [data_sep['ConsumptionGV0 - Domme meter'][0:aantal_mailadressen], data_sep['ConsumptionKV3 - Slimme meter'][0:aantal_mailadressen], data_sep['ConsumptionKV0 - Domme meter'][0:aantal_mailadressen], data_sep['ProsumptionGV0 - Domme meter'][0:aantal_mailadressen], data_sep['ProsumptionKV3 - Slimme meter'][0:aantal_mailadressen], data_sep['ProsumptionKV0 - Domme meter'][0:aantal_mailadressen]]
final_mail_list = pd.concat([save_correct[x] for x, value in enumerate(save_correct)], axis=0)
final_mail_list.reset_index(inplace=True, drop=True)
#print(save_correct)
print(final_mail_list.to_string())
final_mail_list.to_csv('data/500_mail_list.csv', index=True)
#print(data_sep)
#print(data_Consumption.to_string())