import PySimpleGUI as sg
import pandas as pd
import numpy as np
import csv

number_layouts = [1,2,3]
appliances = ['Types', ['Batterij', 'EV laadpaal', 'Warmtepomp', 'Koelcel', 'AC', 'Warm water boiler', 'Overig']]
type_flex = ['File', ['Gebruik', ['Limiteren van gebruik', 'Verschuiven van gebruik', ['Uitstellen', 'Naar voren schuiven', 'Beide']],
                      'Opslag', ['Mobiel (EV)', 'Batterij', ['Met opwek', 'Zonder opwek']],
                      ]]

type_flex2 = ['Gebruik','Opslag']
type_flex3 = ['Limiteren van gebruik', 'Verschuiven van gebruik']
type_flexibiliteit = None
size = (35, 1)
filled_in = True
first = False
gebruik = True
data = pd.DataFrame()
check = np.array([])
value_type = ''
time_in_day = pd.date_range("00:00", "23:45", freq="15min").time


# ----------- Create the 3 layouts this Window will display -----------
layout1 = [[sg.Text('Welcome to the data entry sheet for flex options', background_color = 'darkblue')],
            [sg.Text('Company name', size =size), sg.Input(key='company_name_main')],
            [sg.Text('Customer id', size =size), sg.Input(key='customer_id_main')],
            [sg.Text('Branche', size =size), sg.Input(key='Branche_main')],
            [sg.Text('Piek aansluiting', size =size), sg.Input(key='PiekAansluiting_main')],
            [sg.Text('Access link smartmeter', size =size), sg.Input(key='ICT_METER_main')],
            [sg.Text('Selecteer categorie', size=size), sg.ButtonMenu('Categorieën', menu_def=type_flex, key='type_flex_main')],
            #[sg.Text('Type of appliance (indien niet in lijst vul zelf in)', size=size), sg.Combo(values=appliances, key='Appliance')],
            [sg.Text('Type appliance', size=size), sg.ButtonMenu('Type', menu_def=appliances, key='type_appl_main')],
            #[sg.Text('Branche', size=size), sg.OptionMenu(values=menu_def_2, key='Branche')],
            # [sg.Text('Needed information', background_color = 'darkblue')],
            # #[sg.Text('Type of appliance', size=size), sg.OptionMenu(values=appliances, key='Appliance')],
            #
            # #[sg.Text('Indien overig', size =size), sg.Input(key='overig_type')],
            # [sg.Text('Maximale capaciteit in kW', size =size), sg.Input(key='max_KW')],
            # [sg.Text('Gemiddelde gebruikstijd in uur', size =size), sg.Input(key='duration')],
            # [sg.Text('Type flexibiliteit', size=size), sg.ButtonMenu('type', menu_def=type_flex, key='type_flex')],
            #

            #
            # [sg.Text('Gebruiksvoorwaarden', background_color = 'darkblue')],
            # [sg.Text('Start van flex', size =size), sg.OptionMenu(values=time_in_day, key='start_time')],
            # [sg.Text('Eind van flex', size =size), sg.OptionMenu(values=time_in_day, key='end_time')],
            # [sg.Text('Access link smartmeter', size =size), sg.Input(key='ICT_METER')],
            # [sg.Text('Remarks', size =size), sg.Input(key='Remarks_gebruik')],
            # [sg.Text('Extra', background_color = 'darkblue')],
            # [sg.Text('Remarks', size =size), sg.Input(key='Remarks')]
           ]

layout2 = [ [sg.Text('Informatie batterijen', background_color = 'darkblue')],
            [sg.Text('Type/model', size =size), sg.Input(key='model_bat')],
            [sg.Text('Charge capaciteit in kW', size =size), sg.Input(key='charge_KW_bat')],
            [sg.Text('Maximale capaciteit in kWh', size =size), sg.Input(key='size_kWh_bat')],
            [sg.Text('Tijdens welke tijdstippen is flex mogelijk', background_color = 'darkblue')],
            [sg.Text('Start van flex', size =size), sg.OptionMenu(values=time_in_day, key='start_time_bat')],
            [sg.Text('Eind van flex', size =size), sg.OptionMenu(values=time_in_day, key='end_time_bat')],
            [sg.Text('Start van flex tijdslot 2', size =size), sg.OptionMenu(values=time_in_day, key='start_time2_bat')],
            [sg.Text('Eind van flex tijdslot 2', size =size), sg.OptionMenu(values=time_in_day, key='end_time2_bat')],
            [sg.Text('ICT informatie', background_color = 'darkblue')],
            [sg.Text('IP address system', size =size), sg.Input(key='IP_bat')],
            [sg.Text('Access link backend appliance', size =size), sg.Input(key='ICT_APPL_bat')],
            [sg.Text('Functionele informatie', background_color = 'darkblue')],
            [sg.Text('Functie van de batterij', size =size), sg.Input(key='functie_batterij_bat')],
            [sg.Text('Opmerkingen', size =size), sg.Input(key='Remarks_bat')],
           ]

layout3 = [ [sg.Text('Informatie EV laadpalen', background_color = 'darkblue')],
            [sg.Text('Type/model', size=size), sg.Input(key='model_ev')],
            [sg.Text('Aantal palen', size=size), sg.Input(key='aantal_palen_ev')],
            [sg.Text('Max capaciteit per paal in kW', size=size), sg.Input(key='charge_KW_ev')],
            [sg.Text('Maximale capaciteit park in kW', size=size), sg.Input(key='size_kWh_ev')],
            [sg.Text('Tijdens welke tijdstippen is flex mogelijk', background_color='darkblue')],
            [sg.Text('Start piek gebruik palen', size=size), sg.OptionMenu(values=time_in_day, key='start_time_ev')],
            [sg.Text('Eind piek gebruik palen', size=size), sg.OptionMenu(values=time_in_day, key='end_time_ev')],
            [sg.Text('ICT informatie', background_color='darkblue')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_ev')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_ev')],
            [sg.Text('Extra', background_color='darkblue')],
            [sg.Text('Opmerkingen', size=size), sg.Input(key='Remarks_ev')],
            ]
layout4 = [ [sg.Text('Informatie AC', background_color = 'darkblue')],
            [sg.Text('Type/model', size=size), sg.Input(key='model_ac')],
            [sg.Text('Aantal ACs', size=size), sg.Input(key='aantal_ac')],
            [sg.Text('Max capaciteit per AC in kW', size=size), sg.Input(key='cap_1_ac')],
            [sg.Text('Maximale capaciteit alle AC in kW', size=size), sg.Input(key='cap_alle_ac')],
            [sg.Text('Tijdens welke tijdstippen is flex mogelijk', background_color='darkblue')],
            [sg.Text('Start piek gebruik AC', size=size), sg.OptionMenu(values=time_in_day, key='start_time_ac')],
            [sg.Text('Eind piek gebruik AC', size=size), sg.OptionMenu(values=time_in_day, key='end_time_ac')],
            [sg.Text('ICT informatie', background_color='darkblue')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_ac')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_ac')],
            [sg.Text('Extra', background_color='darkblue')],
            [sg.Text('Opmerkingen', size=size), sg.Input(key='Remarks_ac')],
            ]
layout5 = [ [sg.Text('Informatie koelcel', background_color = 'darkblue')],
            [sg.Text('Type/model', size=size), sg.Input(key='model_kc')],
            [sg.Text('Maximale verbruik in kW', size=size), sg.Input(key='verbruik_kc')],
            [sg.Text('Vereiste minimale temperatuur', size=size), sg.Input(key='min_temp_kc')],
            [sg.Text('Vereiste maximale temperatuur', size=size), sg.Input(key='max_temp_kc')],
            [sg.Text('ICT informatie', background_color='darkblue')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_kc')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_kc')],
            [sg.Text('Extra', background_color='darkblue')],
            [sg.Text('Opmerkingen', size=size), sg.Input(key='Remarks_kc')],
            ]
layout6 = [ [sg.Text('Informatie Warmtepomp', background_color = 'darkblue')],
            [sg.Text('Type/model', size=size), sg.Input(key='model_wp')],
            [sg.Text('Aantal warmtepompen', size=size), sg.Input(key='aantal_wp')],
            [sg.Text('Max capaciteit per warmtepomp in kW', size=size), sg.Input(key='cap_1_wp')],
            [sg.Text('Maximale capaciteit alle warmtepomp in kW', size=size), sg.Input(key='cap_alle_wp')],
            [sg.Text('Tijdens welke tijdstippen is flex mogelijk', background_color='darkblue')],
            [sg.Text('Start piek gebruik warmtepomp', size=size), sg.OptionMenu(values=time_in_day, key='start_time_wp')],
            [sg.Text('Eind piek gebruik warmtepomp', size=size), sg.OptionMenu(values=time_in_day, key='end_time_wp')],
            [sg.Text('ICT informatie', background_color='darkblue')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_wp')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_wp')],
            [sg.Text('Buffer', background_color='darkblue')],
            [sg.Text('Ik heb een warmtebuffer bij mijn warmtepomp')],
            [sg.Radio('Ja', 1, enable_events=True, key='buffer_ja_buf'), sg.Radio('Nee', 1, enable_events=True, key='buffer_nee_buf')],
            [sg.Text('Indien ja vul de volgende vragen in:')],
            [sg.Text('Type/model', size =size), sg.Input(key='model_buf')],
            [sg.Text('Charge capaciteit in kW', size =size), sg.Input(key='charge_KW_buf')],
            [sg.Text('Maximale capaciteit in kWh', size =size), sg.Input(key='size_kWh_buf')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_buf')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_buf')],
            [sg.Text('Extra', background_color='darkblue')],
            [sg.Text('Opmerkingen', size=size), sg.Input(key='Remarks_wp_buf')],
            ]
layout7 = [ [sg.Text('Informatie warm water boiler', background_color = 'darkblue')],
            [sg.Text('Type/model', size=size), sg.Input(key='model_wwb')],
            [sg.Text('Max capaciteit boiler in liters', size=size), sg.Input(key='cap_liters_wwb')],
            [sg.Text('Maximale charge capaciteit in kW', size=size), sg.Input(key='cap_kw_wwb')],
            [sg.Text('Tijdens welke tijdstippen is flex mogelijk', background_color='darkblue')],
            [sg.Text('Vereiste minimale temperatuur', size=size), sg.Input(key='min_temp_wwb')],
            [sg.Text('Vereiste maximale temperatuur', size=size), sg.Input(key='max_temp_wwb')],
            [sg.Text('ICT informatie', background_color='darkblue')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_wwb')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_wwb')],
            [sg.Text('Extra', background_color='darkblue')],
            [sg.Text('Opmerkingen', size=size), sg.Input(key='Remarks_wwb')],
            ]
layout8 = [ [sg.Text('Overige apparaten', background_color = 'darkblue')],
            [sg.Text('Wat voor apparaat is het', size=size), sg.Input(key='appl_overig')],
            [sg.Text('Type/model', size=size), sg.Input(key='model_overig')],
            [sg.Text('Functie apparaat', size=size), sg.Input(key='functie_overig')],
            [sg.Text('Vul volgende vragen indien relevant', background_color = 'darkblue')],
            [sg.Text('Charge capaciteit in kW', size=size), sg.Input(key='charge_KW_overig')],
            [sg.Text('Maximale capaciteit in kWh', size=size), sg.Input(key='size_kWh_overig')],
            [sg.Text('Tijdens welke tijdstippen is flex mogelijk')],
            [sg.Text('Start van flex', size=size), sg.OptionMenu(values=time_in_day, key='start_time_overig')],
            [sg.Text('Eind van flex', size=size), sg.OptionMenu(values=time_in_day, key='end_time_overig')],
            [sg.Text('Start van flex tijdslot 2', size=size), sg.OptionMenu(values=time_in_day, key='start_time2_overig')],
            [sg.Text('Eind van flex tijdslot 2', size=size), sg.OptionMenu(values=time_in_day, key='end_time2_overig')],
            [sg.Text('Start piek gebruik', size=size), sg.OptionMenu(values=time_in_day, key='start_time_overig')],
            [sg.Text('Eind piek gebruik', size=size), sg.OptionMenu(values=time_in_day, key='end_time_overig')],
            [sg.Text('Vereiste minimale temperatuur', size=size), sg.Input(key='min_temp_overig')],
            [sg.Text('Vereiste maximale temperatuur', size=size), sg.Input(key='max_temp_overig')],
            [sg.Text('ICT informatie', background_color='darkblue')],
            [sg.Text('IP address system', size=size), sg.Input(key='IP_overig')],
            [sg.Text('Access link backend appliance', size=size), sg.Input(key='ICT_APPL_overig')],
            [sg.Text('Extra', background_color='darkblue')],
            [sg.Text('Opmerkingen', size=size), sg.Input(key='Remarks_overig')],
            ]

#['Batterij', 'EV laadpaal', 'Warmtepomp', 'Koelcel', 'AC', 'Warm water boiler', 'Overig']
# ----------- Create actual layout using Columns and a row of Buttons

layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-'), sg.Column(layout4, visible=False, key='-COL4-'), sg.Column(layout5, visible=False, key='-COL5-'), sg.Column(layout6, visible=False, key='-COL6-'), sg.Column(layout7, visible=False, key='-COL7-'), sg.Column(layout8, visible=False, key='-COL8-')],
          [sg.Button('Submit'), sg.Button('Previous'), sg.Button('Exit')]]

#, sg.Column(layout4, visible=False, key='-COL4-')

window = sg.Window('Flex data input', layout) # , margins=(500, 400)


def retrive_data(events, value):
    global first
    if events == "Submit":
        with open('data/data.csv', mode='r') as file:
            checkFile = csv.reader(file)
            line_count = 0
            for lines in checkFile:
                if line_count == 0:
                    checkLine = lines
                    line_count = 1
        oldLines = list(value.keys())
        if checkLine == oldLines:
            print('equal')
            mode = 'a'
        else:
            print('not equal')
            mode = 'w'
            first = True
        with open('data/data.csv', mode=mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=value.keys())
            if first == True:
                writer.writeheader()
            writer.writerow(value)


layout = 1  # The currently visible layout
while True:
    event, values = window.read()
    print(event)
    if event == 'Submit':
        retrive_data(event, values)
        break
        # if filled_check == True:
        #     sg.popup_ok("Check if you filled in all the fields correctly")
        #     filled_check = False
        # elif filled_check == False:
        #     retrive_data(event, values)
        #     break
        # for i, x in enumerate(values):
        #     # print(i, x)
        #     # print(values[x])
        #     if values[x] == '':
        #         filled_in = False
        # if filled_in == True:
        #     # print(event, values)
        #     retrive_data(event, values)
        #     break
        # elif filled_in == False:
        #     sg.popup_ok("You need to fill in all the fields")
        # filled_in = True
    if event == 'type_appl_main':
        if values['type_appl_main'] == 'Batterij':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 2
            window[f'-COL{layout}-'].update(visible=True)
        elif values['type_appl_main'] == 'EV laadpaal':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 3
            window[f'-COL{layout}-'].update(visible=True)
        elif values['type_appl_main'] == 'Warmtepomp':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 6
            window[f'-COL{layout}-'].update(visible=True)
        elif values['type_appl_main'] == 'Koelcel':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 5
            window[f'-COL{layout}-'].update(visible=True)
        elif values['type_appl_main'] == 'AC':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 4
            window[f'-COL{layout}-'].update(visible=True)
        elif values['type_appl_main'] == 'Warm water boiler':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 7
            window[f'-COL{layout}-'].update(visible=True)
        elif values['type_appl_main'] == 'Overig':
            window[f'-COL{layout}-'].update(visible=False)
            layout = 8
            window[f'-COL{layout}-'].update(visible=True)
    # if event == 'type_flex':
    #     print(values['type_flex'])
    #     type_flexibiliteit = values['type_flex']
    elif event in (None, 'Exit') or event == sg.WIN_CLOSED:
        break
    elif event == 'Previous':
        window[f'-COL{layout}-'].update(visible=False)
        layout = 1
        window[f'-COL{layout}-'].update(visible=True)

window.close()