import PySimpleGUI as sg


def run():
    #sg.theme('DarkAmber')
    
    layout = [
        [sg.Text("Recipe name:")],
        [sg.InputText("recipe_0")],
        [sg.Text("Imaging:")],
        [sg.Text("Start"), sg.Text("End"), sg.Text("Number"), sg.Text("Interval")],
        [sg.InputText(key="start", enable_events=True), sg.InputText(key="end", enable_events=True),
         sg.InputText(key="number", enable_events=True), sg.InputText(key="interval", enable_events=True),
         sg.Button("Calculate")],
        [sg.Text("Temperature:")],
        [sg.Text("Temp")],
        [sg.InputText()],
        [sg.Text("Lighting:")],
        [sg.Text("Red"), sg.Text("White"), sg.Text("Blue")],
        [sg.InputText(), sg.InputText(), sg.InputText()],
        [sg.Button("Save")]
    ]

    window = sg.Window("Recipe Creator", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Save":
            break
        elif event == "Calculate":
            raw_params = [values["start"], values["end"], values["number"], values["interval"]]
            img_params = ["" if (len(param) == 0) else float(param) for param in raw_params]
            print("recorded", img_params)
            if img_params[0] == "" and not ("" in img_params[1:]):
                img_params[0] = img_params[1] - (img_params[2] * img_params[3])
            elif img_params[1] == "" and not ("" in (img_params[:1] + img_params[2:])):
                img_params[1] = img_params[0] + (img_params[2] * img_params[3])
            elif img_params[2] == "" and not ("" in (img_params[:2] + img_params[3:])):
                img_params[2] = (img_params[1] - img_params[0]) / img_params[3]
            elif img_params[3] == "" and not ("" in img_params[:3]):
                img_params[3] = (img_params[1] - img_params[0]) / img_params[2]
            window["start"].update(img_params[0])
            window["end"].update(img_params[1])
            window["number"].update(img_params[2])
            window["interval"].update(img_params[3])
            print("recorded", img_params)
        print("event", event)
    if event == "Save":
        sg.popup("Recipe saved as ", values[0])


if __name__ == "__main__":
    run()
