
#
# import PySimpleGUI as sg
#
#
# layout = [
#     [sg.Text('Please enter your Name, Age, Phone')],
#     [sg.Text('Name', size =(15, 1)), sg.InputText()],
#     [sg.Text('Age', size =(15, 1)), sg.InputText()],
#     [sg.Text('Phone', size =(15, 1)), sg.InputText()],
#     [sg.Submit(), sg.Cancel()]
# ]
#
# layout1 = [
#     [sg.Text('Please enter your Name, Age, Phone')],
#     [sg.Text('Name', size =(15, 1)), sg.InputText()],
#     [sg.Text('Age', size =(15, 1)), sg.InputText()],
#     [sg.Text('Phone', size =(15, 1)), sg.InputText()],
#     [sg.Submit(), sg.Cancel()]
# ]
# layout2 = [
#     [sg.Text('Please enter your company')],
#     [sg.Text('branche', size =(15, 1)), sg.InputText()],
#     [sg.Text('KW', size =(15, 1)), sg.InputText()],
#     [sg.Text('Remarks', size =(15, 1)), sg.InputText()],
#     [sg.Submit(), sg.Cancel()]
# ]
#
# window = sg.Window(title="Flex data input", layout=layout, margins=(500, 400))
# layout = 1
#
# while True:
#     event, values = window.read()
#     # End program if user closes window or
#     # presses the OK button
#     if event == "Submit":
#         window[f'-COL{layout}-'].update(visible=False)
#         layout = layout + 1 if layout < 3 else 1
#         print(layout)
#         window[f'-COL{layout}-'].update(visible=True)
#         break
#     if event == sg.WIN_CLOSED:
#         break
#
# print(event, values[0], values[1], values[2])
#
# window.close()


import PySimpleGUI as sg

# ----------- Create the 3 layouts this Window will display -----------
layout1 = [[sg.Text('This is layout 1 - It is all Checkboxes')],
           *[[sg.CB(f'Checkbox {i}')] for i in range(5)],
           [sg.Button('Cycle Layout')]]

layout2 = [[sg.Text('This is layout 2')],
           [sg.Input(key='-IN-')],
           [sg.Input(key='-IN2-')],
           [sg.Button('Cycle Layout')]]

layout3 = [[sg.Text('This is layout 3 - It is all Radio Buttons')],
           *[[sg.R(f'Radio {i}', 1)] for i in range(8)],
           [sg.Button('Cycle Layout')]]

# ----------- Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-')],
          [sg.Button('1'), sg.Button('2'), sg.Button('3'), sg.Button('Exit')]]

window = sg.Window('Swapping the contents of a window', layout)

layout = 1  # The currently visible layout
while True:
    event, values = window.read()
    print(event, values)
    if event in (None, 'Exit'):
        break
    if event == 'Cycle Layout':
        window[f'-COL{layout}-'].update(visible=False)
        layout = layout + 1 if layout < 3 else 1
        window[f'-COL{layout}-'].update(visible=True)
    elif event in '123':
        window[f'-COL{layout}-'].update(visible=False)
        layout = int(event)
        window[f'-COL{layout}-'].update(visible=True)
window.close()