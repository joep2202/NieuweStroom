import PySimpleGUI as sg

number_layouts = [1,2,3]
appliances = ['batterij', 'EV laadpaal', 'Warmtepomp', 'Koelcel']
size = (20, 1)
filled_in = True

# ----------- Create the 3 layouts this Window will display -----------
layout1 = [[sg.Text('Welcome to the data entry sheet for flex options')],
            [sg.Text('Please enter your company', size =size), sg.Input(key='company_name')],
            [sg.Text('Customer id', size =size), sg.Input(key='customer_id')],
            [sg.Text('branche', size =size), sg.Input(key='Branche')],
            [sg.Text('KW', size =size), sg.Input(key='KW')],
            [sg.Text('Remarks', size =size), sg.Input(key='Remarks')],
            [sg.Text('Welke type apparaat?')],
            *[[sg.R(f'{appliances[i]}', 1, key="appl")] for i in range(len(appliances))]
           ]

# layout3 = [[sg.Text('Welke apparaten heb je?')],
#            *[[sg.CB(f' {appliances[i]}')] for i in range(4)]]

layout3 = [[sg.Text('Welke type apparaat?')],
           *[[sg.R(f'{appliances[i]}', 1)] for i in range(len(appliances))]]

# layout4 = [[sg.Text('Submit your application')],
#            [sg.Button('Previous'), sg.Button('Submit')]]

# ----------- Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(layout1, key='-COL1-')],
          [sg.Button('Submit'), sg.Button('Exit')]]

#, sg.Column(layout4, visible=False, key='-COL4-')

window = sg.Window('Flex data input', layout) # , margins=(500, 400)

layout = 1  # The currently visible layout
while True:
    event, values = window.read()
    if event == 'Submit':
        for i, x in enumerate(values):
            # print(i, x)
            # print(values[x])
            if values[x] == '':
                filled_in = False
        if filled_in == True:
            print(event, values)
            break
        elif filled_in == False:
            print('I need a pop up to say fill in everything')
        filled_in = True
    elif event in (None, 'Exit') or event == sg.WIN_CLOSED:
        break


window.close()