import PySimpleGUI as sg
import pandas as pd
import numpy as np
import csv

number_layouts = [1,2,3]
appliances = ['Batterij', 'EV laadpaal', 'Warmtepomp', 'Koelcel', 'AC', 'Warm water boiler']
type_flex = ['File', ['Gebruik', ['Limiteren van gebruik', 'Verschuiven van gebruik', ['Uitstellen', 'Naar voren schuiven', 'Beide']],
                      'Opslag', ['Mobiel (EV)', 'Batterij', ['Met opwek', 'Zonder opwek']],
                      ]]

type_flex2 = ['Gebruik','Opslag']
type_flex3 = ['Limiteren van gebruik', 'Verschuiven van gebruik']
size = (35, 1)
filled_in = True
first = False
gebruik = True
data = pd.DataFrame()
check = np.array([])
value_type = ''
#header_list = ['company_name','customer_id','Branche','KW','Remarks','appl','appl0','appl1','appl2']

menu_def_2 = ['gas', 'mkb', 'industry']

# ----------- Create the 3 layouts this Window will display -----------
layout1 = [[sg.Text('Welcome to the data entry sheet for flex options', background_color = 'darkblue')],
            [sg.Text('Company name', size =size), sg.Input(key='company_name')],
            [sg.Text('Customer id', size =size), sg.Input(key='customer_id')],
            [sg.Text('Branche', size =size), sg.Input(key='Branche')],
            #[sg.Text('Branche', size=size), sg.OptionMenu(values=menu_def_2, key='Branche')],
            [sg.Text('Needed information', background_color = 'darkblue')],
            #[sg.Text('Type of appliance', size=size), sg.OptionMenu(values=appliances, key='Appliance')],
            [sg.Text('Type of appliance (indien niet in lijst vul zelf in)', size=size), sg.Combo(values=appliances, key='Appliance')],
            #[sg.Text('Indien overig', size =size), sg.Input(key='overig_type')],
            [sg.Text('Maximale capaciteit in kW', size =size), sg.Input(key='max_KW')],
            [sg.Text('Gemiddelde gebruikstijd in uur', size =size), sg.Input(key='duration')],
            [sg.Text('Type flexibiliteit', size=size), sg.ButtonMenu('type', menu_def=type_flex, key='type_flex')],
            [sg.Text('Piek aansluining', size =size), sg.Input(key='PiekAansluiting')],
            [sg.Text('ICT info', background_color = 'darkblue')],
            [sg.Text('IP address system', size =size), sg.Input(key='IP')],
            [sg.Text('Access link backend appliance', size =size), sg.Input(key='ICT_APPL')],
            [sg.Text('Access link smartmeter', size =size), sg.Input(key='ICT_METER')],
            [sg.Text('Extra', background_color = 'darkblue')],
            [sg.Text('Remarks', size =size), sg.Input(key='Remarks')]
           ]

# ----------- Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(layout1, key='-COL1-')],
          [sg.Button('Submit'), sg.Button('Exit')]]

#, sg.Column(layout4, visible=False, key='-COL4-')

window = sg.Window('Flex data input', layout) # , margins=(500, 400)


def retrive_data(events, value):
    if events == "Submit":
        with open('data/data.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=value.keys())
            if first == True:
                writer.writeheader()
            writer.writerow(value)


layout = 1  # The currently visible layout
while True:
    event, values = window.read()
    if event == 'Submit':
        # if filled_check == True:
        #     sg.popup_ok("Check if you filled in all the fields correctly")
        #     filled_check = False
        # elif filled_check == False:
        #     retrive_data(event, values)
        #     break
        for i, x in enumerate(values):
            # print(i, x)
            # print(values[x])
            if values[x] == '':
                filled_in = False
        if filled_in == True:
            # print(event, values)
            retrive_data(event, values)
            break
        elif filled_in == False:
            sg.popup_ok("You need to fill in all the fields")
        filled_in = True
    elif event in (None, 'Exit') or event == sg.WIN_CLOSED:
        break

window.close()